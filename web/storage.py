"""JSON game persistence shared by every serverless instance."""

import json
import os

from CamelUp import CamelUp
from Player import Player


class RedisGameStore:
    def __init__(self, client):
        self.client = client
        self.prefix = f"camel-up:{os.getenv('VERCEL_ENV', 'development')}:"

    def get(self, game_id):
        from web.service import GameSession, STYLES

        raw = self.client.get(self.prefix + "game:" + game_id)
        if raw is None:
            return None
        data = json.loads(raw)
        players = []
        for saved in data["players"]:
            player = Player(saved["name"], STYLES)
            player.money = saved["money"]
            player.bets = [tuple(bet) for bet in saved["bets"]]
            players.append(player)
        game = CamelUp(STYLES, players)
        for name, value in data["board"].items():
            if name == "remaining_dice":
                game.board.pyramid.remaining_dice = value
            elif name == "dice_tents":
                game.board.dice_tents = [tuple(die) for die in value]
            else:
                setattr(game.board, name, value)
        return GameSession(game=game, **data["session"])

    def __setitem__(self, game_id, session):
        game = session.game
        data = {
            "players": [
                {"name": p.name, "money": p.money, "bets": p.bets}
                for p in game.players
            ],
            "board": {
                "track": game.board.track,
                "race_finished": game.board.race_finished,
                "race_winner": game.board.race_winner,
                "ticket_tents": game.board.ticket_tents,
                "dice_tents": game.board.dice_tents,
                "remaining_dice": game.board.pyramid.remaining_dice,
            },
            "session": {
                "current_player": session.current_player,
                "leg": session.leg,
                "status": session.status,
                "race_winner": session.race_winner,
                "winning_players": session.winning_players,
                "last_payout": session.last_payout,
                "log": session.log[-60:],
            },
        }
        # Inactive games expire after seven days; every move refreshes the TTL.
        self.client.set(
            self.prefix + "game:" + game_id,
            json.dumps(data),
            ex=7 * 24 * 60 * 60,
        )

    def lock(self):
        # Serialize read/modify/write across instances as well as local threads.
        return self.client.lock(
            self.prefix + "moves", timeout=120, blocking_timeout=15
        )
