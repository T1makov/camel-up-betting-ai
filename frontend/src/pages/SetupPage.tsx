import {
    type FormEvent,
    useState,
  } from "react";
  import { Link, useNavigate } from "react-router-dom";
  
  import { createGame } from "../api/client";
  
  const INITIAL_PLAYERS = ["Player 1", "Player 2"];
  
  export function SetupPage() {
    const navigate = useNavigate();
  
    const [players, setPlayers] =
      useState<string[]>(INITIAL_PLAYERS);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    function updatePlayer(index: number, name: string) {
      setPlayers((currentPlayers) =>
        currentPlayers.map((player, playerIndex) =>
          playerIndex === index ? name : player,
        ),
      );
    }
  
    function addPlayer() {
      if (players.length >= 6) {
        return;
      }
  
      setPlayers((currentPlayers) => [
        ...currentPlayers,
        `Player ${currentPlayers.length + 1}`,
      ]);
    }
  
    function removePlayer(index: number) {
      if (players.length <= 2) {
        return;
      }
  
      setPlayers((currentPlayers) =>
        currentPlayers.filter(
          (_, playerIndex) => playerIndex !== index,
        ),
      );
    }
  
    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
      event.preventDefault();
      setError(null);
      setIsSubmitting(true);
  
      try {
        const game = await createGame(players);
        navigate(`/game/${game.gameId}`);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "The game could not be created.",
        );
      } finally {
        setIsSubmitting(false);
      }
    }
  
    return (
      <main className="setup-page">
        <section className="setup-card">
          <Link className="back-link" to="/">
            ← Back
          </Link>
  
          <p className="eyebrow">Prepare the caravan</p>
          <h1>Create a game</h1>
  
          <p className="setup-description">
            Add between two and six local players. Turns rotate
            automatically after every roll or bet.
          </p>
  
          <form onSubmit={handleSubmit}>
            <div className="player-list">
              {players.map((player, index) => (
                <div className="player-input-row" key={index}>
                  <span className="player-number">
                    {index + 1}
                  </span>
  
                  <label className="visually-hidden" htmlFor={`player-${index}`}>
                    Player {index + 1} name
                  </label>
  
                  <input
                    id={`player-${index}`}
                    value={player}
                    maxLength={24}
                    onChange={(event) =>
                      updatePlayer(index, event.target.value)
                    }
                    required
                  />
  
                  <button
                    className="remove-player-button"
                    type="button"
                    onClick={() => removePlayer(index)}
                    disabled={players.length <= 2}
                    aria-label={`Remove ${player}`}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
  
            <button
              className="add-player-button"
              type="button"
              onClick={addPlayer}
              disabled={players.length >= 6}
            >
              + Add player
            </button>
  
            {error && (
              <p className="error-message" role="alert">
                {error}
              </p>
            )}
  
            <button
              className="primary-button submit-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Creating game…" : "Begin the race"}
            </button>
          </form>
        </section>
      </main>
    );
  }