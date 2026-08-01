from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any
from uuid import uuid4

from CamelUp import CamelUp
from Player import Player


STYLES = {color: "" for color in "rbgyp"}

COLOR_NAMES = {
    "r": "Red",
    "b": "Blue",
    "g": "Green",
    "y": "Yellow",
    "p": "Purple",
}


@dataclass
class GameSession:
    game: CamelUp
    current_player: int = 0
    leg: int = 1
    status: str = "playing"
    log: list[str] = field(
        default_factory=lambda: [
            "The caravan is ready. The first leg begins!"
        ]
    )


class GameService:
    def __init__(self) -> None:
        self._games: dict[str, GameSession] = {}
        self._lock = Lock()

    def create_game(self, names: list[str]) -> dict[str, Any]:
        cleaned_names = [
            name.strip()
            for name in names
            if isinstance(name, str) and name.strip()
        ]

        if not 2 <= len(cleaned_names) <= 6:
            raise ValueError("A game requires between 2 and 6 players.")

        players = [
            Player(name, STYLES)
            for name in cleaned_names
        ]

        game_id = uuid4().hex[:10]
        session = GameSession(
            game=CamelUp(STYLES, players)
        )

        with self._lock:
            self._games[game_id] = session

        return self.get_state(game_id)

    def get_state(self, game_id: str) -> dict[str, Any]:
        session = self._get_session(game_id)
        return self._serialize(game_id, session)

    def roll(self, game_id: str) -> dict[str, Any]:
        with self._lock:
            session = self._get_session(game_id)
            self._require_playing(session)

            player = session.game.players[session.current_player]
            die = session.game.roll_for_player(player)

            if die == ("", 0):
                raise RuntimeError("No dice remain in the pyramid.")

            session.log.append(
                f"{player.name} rolled "
                f"{COLOR_NAMES[die[0]]} {die[1]} and earned 1 coin."
            )

            self._advance_turn(session)

            return self._serialize(game_id, session)

    def place_bet(
        self,
        game_id: str,
        color: str,
    ) -> dict[str, Any]:
        with self._lock:
            session = self._get_session(game_id)
            self._require_playing(session)

            board = session.game.board

            if color not in board.ticket_tents:
                raise ValueError("Invalid camel color.")

            if not board.ticket_tents[color]:
                raise ValueError("That betting ticket is unavailable.")

            player = session.game.players[session.current_player]
            ticket = session.game.take_bet_for_player(player, color)

            session.log.append(
                f"{player.name} took the "
                f"{COLOR_NAMES[color]} {ticket[1]} ticket."
            )

            self._advance_turn(session)

            return self._serialize(game_id, session)

    def get_advice(self, game_id: str) -> dict[str, Any]:
        session = self._get_session(game_id)
        game = session.game
        probabilities = game.ai.run_enumerative_analysis()

        advice: list[dict[str, Any]] = []

        for color, tickets in game.board.ticket_tents.items():
            if not tickets:
                continue

            ticket_value = tickets[0]
            probability_first, probability_second = probabilities[color]

            advice.append(
                {
                    "color": color,
                    "colorName": COLOR_NAMES[color],
                    "value": ticket_value,
                    "probabilityFirst": probability_first,
                    "probabilitySecond": probability_second,
                    "expectedValue": game.ai.get_ticket_EV(
                        ticket_value,
                        probability_first,
                        probability_second,
                    ),
                }
            )

        advice.sort(
            key=lambda item: item["expectedValue"],
            reverse=True,
        )

        return {"advice": advice}

    def start_next_leg(self, game_id: str) -> dict[str, Any]:
        with self._lock:
            session = self._get_session(game_id)

            if session.status != "leg_complete":
                raise RuntimeError(
                    "The current leg has not finished."
                )

            session.game.board.reset_leg()
            session.leg += 1
            session.status = "playing"
            session.log.append(f"Leg {session.leg} begins.")

            return self._serialize(game_id, session)

    def _get_session(self, game_id: str) -> GameSession:
        session = self._games.get(game_id)

        if session is None:
            raise KeyError("Game not found.")

        return session

    @staticmethod
    def _require_playing(session: GameSession) -> None:
        if session.status != "playing":
            raise RuntimeError(
                "That action is unavailable in the current game state."
            )

    def _advance_turn(self, session: GameSession) -> None:
        game = session.game

        if game.board.is_leg_finished():
            first, second = game.process_leg_payouts()

            session.log.append(
                f"Leg {session.leg} finished: "
                f"{COLOR_NAMES[first]} leads and "
                f"{COLOR_NAMES[second]} is second."
            )
            session.status = "leg_complete"
            return

        session.current_player = (
            session.current_player + 1
        ) % len(game.players)

    @staticmethod
    def _serialize(
        game_id: str,
        session: GameSession,
    ) -> dict[str, Any]:
        game = session.game
        board = game.board
        rankings = list(board.get_rankings() or [])

        return {
            "gameId": game_id,
            "status": session.status,
            "currentPlayer": session.current_player,
            "leg": session.leg,
            "track": board.track,
            "rankings": rankings,
            "players": [
                {
                    "name": player.name,
                    "money": player.money,
                    "bets": [
                        {
                            "color": color,
                            "value": value,
                        }
                        for color, value in player.bets
                    ],
                }
                for player in game.players
            ],
            "tickets": board.ticket_tents,
            "rolledDice": [
                {
                    "color": color,
                    "value": value,
                }
                for color, value in board.dice_tents
            ],
            "remainingDice": board.pyramid.remaining_dice,
            "log": session.log[-60:],
            "capabilities": {
                "legBetting": True,
                "aiAdvice": True,
                "raceBetting": False,
                "spectatorTiles": False,
                "fullRace": False,
            },
        }