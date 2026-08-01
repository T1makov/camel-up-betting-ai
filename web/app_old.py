from __future__ import annotations
import json, os, sys, threading, uuid
from http import HTTPStatus
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
from Board import Board
from Player import Player
from CamelUp import CamelUp

STYLES = {c: "" for c in "rb gyp".replace(" ", "")}
GAMES: dict[str, dict] = {}
LOCK = threading.Lock()

COLOR_NAMES = {"r":"Ruby","b":"Azure","g":"Emerald","y":"Saffron","p":"Orchid"}

def serialize(game_id: str, data: dict) -> dict:
    game: CamelUp = data["game"]
    board = game.board
    rankings = list(board.get_rankings() or [])
    return {
        "gameId": game_id,
        "status": data["status"],
        "currentPlayer": data["current_player"],
        "leg": data["leg"],
        "track": board.track,
        "rankings": rankings,
        "players": [{"name":p.name,"money":p.money,"bets":[{"color":c,"value":v} for c,v in p.bets]} for p in game.players],
        "tickets": board.ticket_tents,
        "rolledDice": [{"color":c,"value":v} for c,v in board.dice_tents],
        "remainingDice": board.pyramid.remaining_dice,
        "log": data["log"][-60:],
        "capabilities": {
            "legBetting": True, "aiAdvice": True, "raceBetting": False,
            "spectatorTiles": False, "fullRace": False
        }
    }

def new_game(names):
    players = [Player(n.strip() or f"Player {i+1}", STYLES) for i,n in enumerate(names[:6])]
    game = CamelUp(STYLES, players)
    gid = uuid.uuid4().hex[:10]
    GAMES[gid] = {"game":game,"current_player":0,"leg":1,"status":"playing","log":["The caravan is ready. The first leg begins!"]}
    return gid

def advance(data):
    game = data["game"]
    if game.board.is_leg_finished():
        first, second = game.process_leg_payouts()
        data["log"].append(f"Leg {data['leg']} finished: {COLOR_NAMES[first]} leads, {COLOR_NAMES[second]} is second.")
        data["status"] = "leg_complete"
    else:
        data["current_player"] = (data["current_player"] + 1) % len(game.players)

def json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    return json.loads(handler.rfile.read(length) or b"{}")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(ROOT,"web","static"), **kwargs)
    def send_json(self, payload, status=200):
        body=json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path.startswith("/api/games/"):
            gid=path.split("/")[3]
            data=GAMES.get(gid)
            return self.send_json(serialize(gid,data) if data else {"error":"Game not found"}, 200 if data else 404)
        if path == "/api/health": return self.send_json({"ok":True})
        if path != "/" and not os.path.exists(os.path.join(ROOT,"web","static",path.lstrip("/"))): self.path="/"
        return super().do_GET()
    def do_POST(self):
        path=urlparse(self.path).path
        try: body=json_body(self)
        except Exception: return self.send_json({"error":"Invalid JSON"},400)
        with LOCK:
            if path == "/api/games":
                names=body.get("players") or ["Player 1","Player 2"]
                if not 2 <= len(names) <= 6: return self.send_json({"error":"Use 2–6 players"},400)
                gid=new_game(names); return self.send_json(serialize(gid,GAMES[gid]),201)
            parts=path.split("/")
            if len(parts) < 5 or parts[1:3] != ["api","games"]: return self.send_json({"error":"Unknown route"},404)
            gid, action=parts[3],parts[4]; data=GAMES.get(gid)
            if not data: return self.send_json({"error":"Game not found"},404)
            game=data["game"]
            if action == "roll" and data["status"] == "playing":
                p=game.players[data["current_player"]]; die=game.roll_for_player(p)
                data["log"].append(f"{p.name} rolled {COLOR_NAMES.get(die[0],die[0])} {die[1]} and earned 1 coin.")
                advance(data)
            elif action == "bet" and data["status"] == "playing":
                color=body.get("color"); p=game.players[data["current_player"]]
                if color not in game.board.ticket_tents or not game.board.ticket_tents[color]: return self.send_json({"error":"That ticket is unavailable"},400)
                ticket=game.take_bet_for_player(p,color); data["log"].append(f"{p.name} took the {COLOR_NAMES[color]} {ticket[1]} ticket."); advance(data)
            elif action == "next-leg" and data["status"] == "leg_complete":
                game.board.reset_leg(); data["leg"]+=1; data["status"]="playing"; data["log"].append(f"Leg {data['leg']} begins.")
            elif action == "advice":
                probs=game.ai.run_enumerative_analysis(); advice=[]
                for c, tickets in game.board.ticket_tents.items():
                    if tickets: advice.append({"color":c,"value":tickets[0],"first":probs[c][0],"second":probs[c][1],"ev":game.ai.get_ticket_EV(tickets[0],*probs[c])})
                advice.sort(key=lambda x:x["ev"],reverse=True); return self.send_json({"advice":advice})
            else: return self.send_json({"error":"Action unavailable in the current state"},409)
            return self.send_json(serialize(gid,data))

if __name__ == "__main__":
    port=int(os.environ.get("PORT","8000")); print(f"Camel Up at http://localhost:{port}"); ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
