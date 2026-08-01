import { DieFace } from "../components/dice/DieFace";
import {
    useCallback,
    useEffect,
    useState,
  } from "react";
  import { Link, useParams } from "react-router-dom";
  
  import {
    getAdvice,
    getGame,
    rollDie,
    startNextLeg,
  } from "../api/client";
  import { RaceBoard } from "../components/board/RaceBoard";
  import type {
    AdviceItem,
    GameState,
  } from "../types/game";
  
  export function GamePage() {
    const { gameId } = useParams<{ gameId: string }>();
  
    const [game, setGame] = useState<GameState | null>(null);
    const [advice, setAdvice] = useState<AdviceItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isActing, setIsActing] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const loadGame = useCallback(async () => {
      if (!gameId) {
        setError("No game ID was provided.");
        setIsLoading(false);
        return;
      }
  
      try {
        setError(null);
        setGame(await getGame(gameId));
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "The game could not be loaded.",
        );
      } finally {
        setIsLoading(false);
      }
    }, [gameId]);
  
    useEffect(() => {
      void loadGame();
    }, [loadGame]);
  
    async function performAction(
      action: () => Promise<GameState>,
    ) {
      setIsActing(true);
      setError(null);
  
      try {
        const nextGame = await action();
        setGame(nextGame);
        setAdvice([]);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "The action could not be completed.",
        );
      } finally {
        setIsActing(false);
      }
    }
  
    async function handleAdvice() {
      if (!gameId) {
        return;
      }
  
      setIsActing(true);
      setError(null);
  
      try {
        const response = await getAdvice(gameId);
        setAdvice(response.advice);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Advice could not be calculated.",
        );
      } finally {
        setIsActing(false);
      }
    }
  
    if (isLoading) {
      return (
        <main className="status-page">
          <p>Loading the caravan…</p>
        </main>
      );
    }
  
    if (!game || !gameId) {
      return (
        <main className="status-page">
          <h1>Game unavailable</h1>
          <p>{error ?? "This game could not be found."}</p>
  
          <Link className="primary-button" to="/setup">
            Create another game
          </Link>
        </main>
      );
    }
  
    const currentPlayer = game.players[game.currentPlayer];
  
    return (
      <main className="game-page">
        <header className="game-header">
          <div>
            <p className="eyebrow">Leg {game.leg}</p>
            <h1>Camel Up Strategy Lab</h1>
          </div>
  
          <Link className="secondary-button" to="/">
            Exit game
          </Link>
        </header>
  
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
  
        <section className="game-grid">
          <div className="game-main-column">
            <section className="panel turn-panel">
              <p className="eyebrow">Current turn</p>
              <h2>{currentPlayer.name}</h2>
  
              <p>
                {currentPlayer.money} coins ·{" "}
                {currentPlayer.bets.length} tickets
              </p>
  
              {game.status === "playing" ? (
                <div className="turn-actions">
                  <button
                    className="primary-button"
                    type="button"
                    disabled={isActing}
                    onClick={() =>
                      void performAction(() => rollDie(gameId))
                    }
                  >
                    Roll from pyramid
                  </button>
  
                  <button
                    className="secondary-button"
                    type="button"
                    disabled={isActing}
                    onClick={() => void handleAdvice()}
                  >
                    Analyze bets
                  </button>
                </div>
              ) : (
                <button
                  className="primary-button"
                  type="button"
                  disabled={isActing}
                  onClick={() =>
                    void performAction(() =>
                      startNextLeg(gameId),
                    )
                  }
                >
                  Start leg {game.leg + 1}
                </button>
              )}
            </section>
  
            <RaceBoard track={game.track} />
  
            {advice.length > 0 && (
              <section className="panel">
                <p className="eyebrow">Probability engine</p>
                <h2>Bet analysis</h2>
  
                <div className="advice-list">
                  {advice.map((item) => (
                    <article
                      className="advice-row"
                      key={item.color}
                    >
                      <strong>{item.colorName}</strong>
  
                      <span>
                        {(item.probabilityFirst * 100).toFixed(1)}%
                        first
                      </span>
  
                      <span>
                        EV {item.expectedValue.toFixed(2)}
                      </span>
                    </article>
                  ))}
                </div>
              </section>
            )}
          </div>
  
          <aside className="game-sidebar">
            <section className="panel">
              <p className="eyebrow">Players</p>
  
              <div className="player-cards">
                {game.players.map((player, index) => (
                  <article
                    className={
                      index === game.currentPlayer
                        ? "player-card active-player"
                        : "player-card"
                    }
                    key={`${player.name}-${index}`}
                  >
                    <div>
                      <strong>{player.name}</strong>
  
                      <span>
                        {index === game.currentPlayer
                          ? "Current turn"
                          : `${player.bets.length} bets`}
                      </span>
                    </div>
  
                    <strong>{player.money}¢</strong>
                  </article>
                ))}
              </div>
            </section>
  
            <section className="panel">
              <p className="eyebrow">Dice history</p>
  
              {game.rolledDice.length === 0 ? (
                <p className="empty-state">
                  No dice have been rolled this leg.
                </p>
              ) : (
                <div className="dice-list">
                  {game.rolledDice.map((die, index) => (
                    <DieFace
                        color={die.color}
                        value={die.value}
                        key={`${die.color}-${index}`}
                    />
                    ))}
                </div>
              )}
            </section>
  
            <section className="panel">
              <p className="eyebrow">Game log</p>
  
              <ol className="game-log">
                {[...game.log].reverse().map((entry, index) => (
                  <li key={`${entry}-${index}`}>
                    {entry}
                  </li>
                ))}
              </ol>
            </section>
          </aside>
        </section>
      </main>
    );
  }