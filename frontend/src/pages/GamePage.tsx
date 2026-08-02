import {
    useCallback,
    useEffect,
    useRef,
    useState,
  } from "react";
  import { Link, useParams } from "react-router-dom";
  
  import {
    getAdvice,
    getGame,
    placeBet,
    rollDie,
    startNextLeg,
  } from "../api/client";
  import { BettingPanel } from "../components/betting/BettingPanel";
  import { RaceBoard } from "../components/board/RaceBoard";
  import { DieFace } from "../components/dice/DieFace";
  import { PlayerBetTickets } from "../components/player/PlayerBetTickets";
  import type {
    AdviceItem,
    CamelColor,
    GameState,
  } from "../types/game";
  
  const CAMEL_NAMES: Record<CamelColor, string> = {
    r: "Red",
    b: "Blue",
    g: "Green",
    y: "Yellow",
    p: "Purple",
  };

  interface PendingRollAnimation {
    id: number;
    color: CamelColor;
    steps: number;
    nextGame: GameState;
  }
  
  export function GamePage() {
    const { gameId } = useParams<{ gameId: string }>();
  
    const [game, setGame] = useState<GameState | null>(null);
    const [advice, setAdvice] = useState<AdviceItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isActing, setIsActing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [pendingRoll, setPendingRoll] =
      useState<PendingRollAnimation | null>(null);
    const rollSequence = useRef(0);
  
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
  
    async function handleRoll() {
      if (!gameId || !game || isActing) {
        return;
      }

      setIsActing(true);
      setError(null);
      setAdvice([]);

      try {
        const nextGame = await rollDie(gameId);
        const rolledDie =
          nextGame.rolledDice[
            nextGame.rolledDice.length - 1
          ];

        if (!rolledDie) {
          setGame(nextGame);
          setIsActing(false);
          return;
        }

        rollSequence.current += 1;

        setPendingRoll({
          id: rollSequence.current,
          color: rolledDie.color,
          steps: rolledDie.value,
          nextGame,
        });
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "The die could not be rolled.",
        );
        setIsActing(false);
      }
    }

    const completeRollAnimation = useCallback(() => {
      if (!pendingRoll) {
        return;
      }

      setGame(pendingRoll.nextGame);
      setPendingRoll(null);
      setIsActing(false);
    }, [pendingRoll]);

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
  
          <p>
            {error ?? "This game could not be found."}
          </p>
  
          <Link className="primary-button" to="/setup">
            Create another game
          </Link>
        </main>
      );
    }
  
    const currentPlayer = game.players[game.currentPlayer];
    const isFinished = game.status === "finished";
    const playerWinnerText =
      game.winningPlayers.length > 1
        ? `${game.winningPlayers.join(" and ")} tie`
        : `${game.winningPlayers[0] ?? "No player"} wins`;
  
    return (
      <main className="game-page">
        <header className="game-header">
          <div>
            <p className="eyebrow">
              {isFinished ? "Final results" : `Leg ${game.leg}`}
            </p>
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
              <div className="turn-panel__layout">
                <div className="turn-panel__player">
                  <p className="eyebrow">
                    {isFinished ? "Game over" : "Current turn"}
                  </p>
  
                  <h2>
                    {isFinished
                      ? playerWinnerText
                      : currentPlayer.name}
                  </h2>
  
                  <p>
                    {isFinished
                      ? "Final coin totals are shown in the player panel."
                      : `${currentPlayer.money} coins · ${currentPlayer.bets.length} tickets`}
                  </p>
                </div>
  
                <div className="turn-panel__analysis">
                  {isFinished ? (
                    <div className="game-over-summary">
                      <span className="game-over-summary__label">
                        Race winner
                      </span>
  
                      <strong
                        className={
                          game.raceWinner
                            ? `game-over-summary__camel camel-${game.raceWinner}`
                            : "game-over-summary__camel"
                        }
                      >
                        {game.raceWinner
                          ? `${CAMEL_NAMES[game.raceWinner]} camel`
                          : "Race complete"}
                      </strong>
  
                      <span className="game-over-summary__player">
                        {playerWinnerText}
                      </span>
                    </div>
                  ) : advice.length > 0 ? (
                    <>
                      <div className="turn-panel__analysis-heading">
                        <strong>Bet analysis</strong>
                        <span>Higher EV is better</span>
                      </div>
  
                      <div className="advice-list">
                        {advice.map((item) => (
                          <article
                            className={`advice-row advice-row--${item.color}`}
                            key={item.color}
                          >
                            <strong>{item.colorName}</strong>
  
                            <span>
                              {(
                                item.probabilityFirst * 100
                              ).toFixed(1)}
                              % first
                            </span>
  
                            <span>
                              EV {item.expectedValue.toFixed(2)}
                            </span>
                          </article>
                        ))}
                      </div>
                    </>
                  ) : null}
                </div>
  
                {game.status === "playing" ? (
                  <div className="turn-actions">
                    <button
                      className="primary-button"
                      type="button"
                      disabled={isActing}
                      onClick={() => void handleRoll()}
                    >
                      {pendingRoll
                        ? "Moving…"
                        : "Roll from pyramid"}
                    </button>
  
                    <button
                      className="secondary-button"
                      type="button"
                      disabled={isActing}
                      onClick={() => void handleAdvice()}
                    >
                      {isActing ? "Calculating…" : "Analyze bets"}
                    </button>
                  </div>
                ) : game.status === "leg_complete" ? (
                  <div className="turn-actions">
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
                  </div>
                ) : (
                  <div className="turn-actions">
                    <Link className="primary-button" to="/setup">
                      New game
                    </Link>
                  </div>
                )}
              </div>
            </section>
  
            <RaceBoard
              track={game.track}
              move={
                pendingRoll
                  ? {
                      id: pendingRoll.id,
                      color: pendingRoll.color,
                      steps: pendingRoll.steps,
                    }
                  : null
              }
              onMoveComplete={completeRollAnimation}
            />
  
            <BettingPanel
              tickets={game.tickets}
              disabled={
                isActing || game.status !== "playing"
              }
              onBet={(color) =>
                void performAction(() =>
                  placeBet(gameId, color),
                )
              }
            />
          </div>
  
          <aside className="game-sidebar">
            <section className="panel">
              <p className="eyebrow">
                {isFinished ? "Final scores" : "Players"}
              </p>
  
              <div className="player-cards">
                {game.players.map((player, index) => (
                  <article
                    className={
                      !isFinished &&
                      index === game.currentPlayer
                        ? "player-card active-player"
                        : "player-card"
                    }
                    key={`${player.name}-${index}`}
                  >
                    <div className="player-card__header">
                      <div className="player-card__identity">
                        <strong>{player.name}</strong>
  
                        <span>
                          {isFinished
                            ? game.winningPlayers.includes(
                                player.name,
                              )
                              ? "Game winner"
                              : "Final score"
                            : index === game.currentPlayer
                              ? "Current turn"
                              : `${player.bets.length} ${
                                  player.bets.length === 1
                                    ? "ticket"
                                    : "tickets"
                                }`}
                        </span>
                      </div>
  
                      <strong className="player-card__money">
                        {player.money}¢
                      </strong>
                    </div>
  
                    <PlayerBetTickets bets={player.bets} />
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
                {[...game.log]
                  .reverse()
                  .map((entry, index) => (
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