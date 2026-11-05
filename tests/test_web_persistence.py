import pytest

fakeredis = pytest.importorskip("fakeredis")

from web.service import GameService


def test_moves_survive_new_backend_instances():
    database = fakeredis.FakeRedis()
    first = GameService(database)
    created = first.create_game(["Alice", "Bob"])
    game_id = created["gameId"]
    bet = GameService(database).place_bet(game_id, "r")
    assert bet["players"][0]["bets"] == [{"color": "r", "value": 5}]
    assert bet["tickets"]["r"] == [3, 2, 2]
    rolled = GameService(database).roll(game_id)
    assert rolled["players"][1]["money"] == 4
    assert len(rolled["remainingDice"]) == 4
    assert GameService(database).get_state(game_id) == rolled
    assert 0 < database.ttl(first._games.prefix + "game:" + game_id) <= 604800


def test_complete_race_with_fresh_instance_for_every_request():
    database = fakeredis.FakeRedis()
    state = GameService(database).create_game(["Alice", "Bob"])
    game_id = state["gameId"]
    for _ in range(100):
        if state["status"] == "finished":
            break
        service = GameService(database)
        if state["status"] == "leg_complete":
            state = service.start_next_leg(game_id)
        else:
            state = service.roll(game_id)
    assert state["status"] == "finished"
    assert state["raceWinner"] in "rbgyp"
    assert state["winningPlayers"]
    assert GameService(database).get_state(game_id) == state


def test_missing_game_remains_not_found():
    with pytest.raises(KeyError, match="Game not found"):
        GameService(fakeredis.FakeRedis()).get_state("missing")
