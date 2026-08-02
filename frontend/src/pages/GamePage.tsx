import {
    useCallback,
    useEffect,
    useRef,
    useState,
  } from "react";
  import type {
    AnimationEvent,
    CSSProperties,
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
  import { CamelPiece } from "../components/icons/CamelPiece";
  import { PlayerBetTickets } from "../components/player/PlayerBetTickets";
  import type {
    AdviceItem,
    CamelColor,
    GameState,
    LegPayoutSummary,
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
  
  interface ScreenRectangle {
    left: number;
    top: number;
    width: number;
    height: number;
  }
  
  interface PendingBetAnimation {
    id: number;
    color: CamelColor;
    value: number;
    sourceRect: ScreenRectangle;
    targetRect: ScreenRectangle;
    nextGame: GameState;
  }

  interface PendingPayoutAnimation {
    nextGame: GameState;
    summary: LegPayoutSummary;
  }

  interface PendingGameOverAnimation {
    nextGame: GameState;
  }

  interface TurnPlayerSnapshot {
    name: string;
    money: number;
    betCount: number;
  }

  interface TurnTransition {
    id: number;
    fromIndex: number;
    toIndex: number;
    fromPlayer: TurnPlayerSnapshot;
  }
  
  type DiceOverlayPhase =
    | "tumbling"
    | "revealed"
    | "exiting";

  type PayoutOverlayPhase =
    | "intro"
    | "details"
    | "exiting";

  type GameOverOverlayPhase =
    | "intro"
    | "ready"
    | "exiting";

  function formatSignedAmount(value: number): string {
    return value > 0 ? `+${value}` : `${value}`;
  }

  function getPayoutResultLabel(
    result: "first" | "second" | "other",
  ): string {
    if (result === "first") {
      return "1st";
    }

    if (result === "second") {
      return "2nd";
    }

    return "Other";
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
    const [queuedRoll, setQueuedRoll] =
      useState<PendingRollAnimation | null>(null);
    const [diceOverlayPhase, setDiceOverlayPhase] =
      useState<DiceOverlayPhase | null>(null);
    const [diceDisplayValue, setDiceDisplayValue] =
      useState(1);
    const [pendingBet, setPendingBet] =
      useState<PendingBetAnimation | null>(null);
    const [
      isBetSelectionInProgress,
      setIsBetSelectionInProgress,
    ] = useState(false);
    const [pendingPayout, setPendingPayout] =
      useState<PendingPayoutAnimation | null>(null);
    const [payoutOverlayPhase, setPayoutOverlayPhase] =
      useState<PayoutOverlayPhase | null>(null);
    const [pendingGameOver, setPendingGameOver] =
      useState<PendingGameOverAnimation | null>(null);
    const [
      gameOverOverlayPhase,
      setGameOverOverlayPhase,
    ] = useState<GameOverOverlayPhase | null>(null);
    const [
      displayedWinnerCoins,
      setDisplayedWinnerCoins,
    ] = useState(0);
    const [turnTransition, setTurnTransition] =
      useState<TurnTransition | null>(null);
  
    const rollSequence = useRef(0);
    const betSequence = useRef(0);
    const turnSequence = useRef(0);
    const currentPlayerBetTargetRef =
      useRef<HTMLDivElement | null>(null);
  
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
  
    useEffect(() => {
      if (!queuedRoll) {
        return;
      }
  
      const movement = queuedRoll;
      const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;
  
      const tumbleDuration = reducedMotion ? 80 : 820;
      const revealDuration = reducedMotion ? 380 : 620;
      const exitDuration = reducedMotion ? 80 : 180;
  
      let pipInterval: number | null = null;
  
      if (!reducedMotion) {
        pipInterval = window.setInterval(() => {
          setDiceDisplayValue((currentValue) =>
            currentValue >= 3
              ? 1
              : currentValue + 1,
          );
        }, 95);
      }
  
      const revealTimer = window.setTimeout(() => {
        if (pipInterval !== null) {
          window.clearInterval(pipInterval);
          pipInterval = null;
        }
  
        setDiceDisplayValue(movement.steps);
        setDiceOverlayPhase("revealed");
      }, tumbleDuration);
  
      const exitTimer = window.setTimeout(() => {
        setDiceOverlayPhase("exiting");
      }, tumbleDuration + revealDuration);
  
      const movementTimer = window.setTimeout(() => {
        setDiceOverlayPhase(null);
        setQueuedRoll(null);
        setPendingRoll(movement);
      }, tumbleDuration + revealDuration + exitDuration);
  
      return () => {
        if (pipInterval !== null) {
          window.clearInterval(pipInterval);
        }
  
        window.clearTimeout(revealTimer);
        window.clearTimeout(exitTimer);
        window.clearTimeout(movementTimer);
      };
    }, [queuedRoll]);
  
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
  
    const applyCompletedTurn = useCallback(
      (
        nextGame: GameState,
        skipAnimation = false,
      ) => {
        const reducedMotion = window.matchMedia(
          "(prefers-reduced-motion: reduce)",
        ).matches;
        const canAnimateTurn =
          !skipAnimation &&
          !reducedMotion &&
          game !== null &&
          game.status === "playing" &&
          nextGame.status === "playing" &&
          game.currentPlayer !== nextGame.currentPlayer;

        if (!canAnimateTurn || !game) {
          setGame(nextGame);
          setTurnTransition(null);
          setIsActing(false);
          return;
        }

        const previousPlayer =
          game.players[game.currentPlayer];

        turnSequence.current += 1;

        setGame(nextGame);
        setTurnTransition({
          id: turnSequence.current,
          fromIndex: game.currentPlayer,
          toIndex: nextGame.currentPlayer,
          fromPlayer: {
            name: previousPlayer.name,
            money: previousPlayer.money,
            betCount: previousPlayer.bets.length,
          },
        });
      },
      [game],
    );

    useEffect(() => {
      if (!turnTransition) {
        return;
      }

      const completeTimer = window.setTimeout(() => {
        setTurnTransition(null);
        setIsActing(false);
      }, 620);

      return () => {
        window.clearTimeout(completeTimer);
      };
    }, [turnTransition]);

    async function handleRoll() {
      if (
        !gameId ||
        !game ||
        isActing ||
        queuedRoll ||
        pendingRoll ||
        pendingBet ||
        pendingPayout ||
        pendingGameOver ||
        turnTransition
      ) {
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
  
        const movement: PendingRollAnimation = {
          id: rollSequence.current,
          color: rolledDie.color,
          steps: rolledDie.value,
          nextGame,
        };
  
        setDiceDisplayValue(
          rolledDie.value >= 3
            ? 1
            : rolledDie.value + 1,
        );
        setDiceOverlayPhase("tumbling");
        setQueuedRoll(movement);
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

      const nextGame = pendingRoll.nextGame;
      const payoutSummary = nextGame.payoutSummary;
      const shouldShowPayouts =
        payoutSummary !== null &&
        (nextGame.status === "leg_complete" ||
          nextGame.status === "finished");

      if (shouldShowPayouts && game) {
        /*
         * Keep the completed camel movement visible underneath
         * the payout overlay, but delay the money and ticket
         * changes until the payout animation has finished.
         */
        setGame({
          ...nextGame,
          status: game.status,
          currentPlayer: game.currentPlayer,
          raceWinner: game.raceWinner,
          winningPlayers: game.winningPlayers,
          players: game.players,
          log: game.log,
        });
        setPendingPayout({
          nextGame,
          summary: payoutSummary,
        });
        setPayoutOverlayPhase("intro");
        setPendingRoll(null);
        return;
      }

      setPendingRoll(null);
      applyCompletedTurn(nextGame);
    }, [applyCompletedTurn, game, pendingRoll]);

    useEffect(() => {
      if (!pendingPayout || !payoutOverlayPhase) {
        return;
      }

      const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

      if (payoutOverlayPhase === "intro") {
        if (reducedMotion) {
          setPayoutOverlayPhase("details");
          return;
        }

        const detailsTimer = window.setTimeout(() => {
          setPayoutOverlayPhase("details");
        }, 520);

        return () => {
          window.clearTimeout(detailsTimer);
        };
      }

      if (payoutOverlayPhase !== "exiting") {
        return;
      }

      const completeTimer = window.setTimeout(() => {
        const completedGame = pendingPayout.nextGame;

        setGame(completedGame);
        setPendingPayout(null);
        setPayoutOverlayPhase(null);

        if (
          completedGame.status === "finished" &&
          completedGame.raceWinner
        ) {
          setDisplayedWinnerCoins(0);
          setPendingGameOver({
            nextGame: completedGame,
          });
          setGameOverOverlayPhase("intro");
          return;
        }

        setIsActing(false);
      }, reducedMotion ? 0 : 260);

      return () => {
        window.clearTimeout(completeTimer);
      };
    }, [pendingPayout, payoutOverlayPhase]);

    function dismissPayoutOverlay() {
      if (
        !pendingPayout ||
        payoutOverlayPhase !== "details"
      ) {
        return;
      }

      setPayoutOverlayPhase("exiting");
    }

    useEffect(() => {
      if (!pendingGameOver) {
        return;
      }

      const winnerTotals =
        pendingGameOver.nextGame.players
          .filter((player) =>
            pendingGameOver.nextGame.winningPlayers.includes(
              player.name,
            ),
          )
          .map((player) => player.money);
      const finalCoinTotal =
        winnerTotals.length > 0
          ? Math.max(...winnerTotals)
          : 0;
      const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

      if (reducedMotion) {
        setDisplayedWinnerCoins(finalCoinTotal);
        return;
      }

      const delay = 320;
      const duration = 1050;
      let animationFrame = 0;
      let startTime: number | null = null;

      const updateCount = (timestamp: number) => {
        if (startTime === null) {
          startTime = timestamp;
        }

        const elapsed = timestamp - startTime;

        if (elapsed < delay) {
          animationFrame =
            window.requestAnimationFrame(updateCount);
          return;
        }

        const progress = Math.min(
          (elapsed - delay) / duration,
          1,
        );
        const easedProgress =
          1 - Math.pow(1 - progress, 3);

        setDisplayedWinnerCoins(
          Math.round(finalCoinTotal * easedProgress),
        );

        if (progress < 1) {
          animationFrame =
            window.requestAnimationFrame(updateCount);
        }
      };

      animationFrame =
        window.requestAnimationFrame(updateCount);

      return () => {
        window.cancelAnimationFrame(animationFrame);
      };
    }, [pendingGameOver]);

    useEffect(() => {
      if (
        !pendingGameOver ||
        !gameOverOverlayPhase
      ) {
        return;
      }

      const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

      if (gameOverOverlayPhase === "intro") {
        if (reducedMotion) {
          setGameOverOverlayPhase("ready");
          return;
        }

        const readyTimer = window.setTimeout(() => {
          setGameOverOverlayPhase("ready");
        }, 1450);

        return () => {
          window.clearTimeout(readyTimer);
        };
      }

      if (gameOverOverlayPhase !== "exiting") {
        return;
      }

      const completeTimer = window.setTimeout(() => {
        setPendingGameOver(null);
        setGameOverOverlayPhase(null);
        setIsActing(false);
      }, reducedMotion ? 0 : 260);

      return () => {
        window.clearTimeout(completeTimer);
      };
    }, [gameOverOverlayPhase, pendingGameOver]);

    function dismissGameOverOverlay() {
      if (
        !pendingGameOver ||
        gameOverOverlayPhase !== "ready"
      ) {
        return;
      }

      setGameOverOverlayPhase("exiting");
    }
  
    function getCurrentPlayerBetTarget(): ScreenRectangle | null {
      const target = currentPlayerBetTargetRef.current;
  
      if (!target) {
        return null;
      }
  
      const targetBounds = target.getBoundingClientRect();
      const existingTickets =
        target.querySelectorAll<HTMLElement>(
          ".player-bet-ticket",
        );
      const lastTicket =
        existingTickets.length > 0
          ? existingTickets[
              existingTickets.length - 1
            ]
          : null;
  
      const ticketSize = 42;
      const ticketGap = 7;
      const preferredLeft = lastTicket
        ? lastTicket.getBoundingClientRect().right +
          ticketGap
        : targetBounds.left;
  
      return {
        left: Math.max(
          targetBounds.left,
          Math.min(
            preferredLeft,
            targetBounds.right - ticketSize,
          ),
        ),
        top:
          targetBounds.top +
          Math.max(
            0,
            (targetBounds.height - ticketSize) / 2,
          ),
        width: ticketSize,
        height: ticketSize,
      };
    }
  
    async function handleBet(
      color: CamelColor,
      sourceRect: DOMRect,
    ) {
      if (
        !gameId ||
        !game ||
        isActing ||
        game.status !== "playing"
      ) {
        return;
      }
  
      const ticketValue = game.tickets[color]?.[0];
  
      if (ticketValue === undefined) {
        return;
      }
  
      setIsActing(true);
      setIsBetSelectionInProgress(true);
      setError(null);
      setAdvice([]);
  
      try {
        const nextGame = await placeBet(gameId, color);
        const targetRect = getCurrentPlayerBetTarget();
        const reducedMotion = window.matchMedia(
          "(prefers-reduced-motion: reduce)",
        ).matches;
  
        if (!targetRect || reducedMotion) {
          setIsBetSelectionInProgress(false);
          applyCompletedTurn(nextGame, reducedMotion);
          return;
        }
  
        betSequence.current += 1;
  
        setPendingBet({
          id: betSequence.current,
          color,
          value: ticketValue,
          sourceRect: {
            left: sourceRect.left,
            top: sourceRect.top,
            width: sourceRect.width,
            height: sourceRect.height,
          },
          targetRect,
          nextGame,
        });
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "The betting ticket could not be taken.",
        );
        setIsBetSelectionInProgress(false);
        setIsActing(false);
      }
    }
  
    const completeBetAnimation = useCallback(() => {
      if (!pendingBet) {
        return;
      }
  
      const nextGame = pendingBet.nextGame;

      setPendingBet(null);
      setIsBetSelectionInProgress(false);
      applyCompletedTurn(nextGame);
    }, [applyCompletedTurn, pendingBet]);
  
    function handleBetAnimationEnd(
      event: AnimationEvent<HTMLDivElement>,
    ) {
      if (
        event.target !== event.currentTarget ||
        event.animationName !== "bet-ticket-flight"
      ) {
        return;
      }
  
      completeBetAnimation();
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
  
    const rollButtonText = queuedRoll
      ? "Rolling…"
      : pendingRoll
        ? "Moving…"
        : pendingPayout
          ? "Paying out…"
          : pendingGameOver
            ? "Celebrating…"
            : turnTransition
              ? "Next turn…"
              : "Roll from pyramid";
  
    return (
      <main className="game-page">
        <header className="game-header">
          <div>
            <p className="eyebrow">
              {isFinished
                ? "Final results"
                : `Leg ${game.leg}`}
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
                <div
                  className={[
                    "turn-panel__player",
                    turnTransition
                      ? "turn-panel__player--transitioning"
                      : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  <p className="eyebrow">
                    {isFinished
                      ? "Game over"
                      : "Current turn"}
                  </p>

                  {isFinished ? (
                    <div className="turn-panel__player-content">
                      <h2>{playerWinnerText}</h2>

                      <p>
                        Final coin totals are shown in the
                        player panel.
                      </p>
                    </div>
                  ) : (
                    <div
                      className="turn-panel__player-swap"
                      aria-live="polite"
                    >
                      {turnTransition && (
                        <div
                          className="turn-panel__player-content turn-panel__player-content--leaving"
                          key={`leaving-${turnTransition.id}`}
                          aria-hidden="true"
                        >
                          <h2>
                            {turnTransition.fromPlayer.name}
                          </h2>

                          <p>
                            {turnTransition.fromPlayer.money}{" "}
                            coins ·{" "}
                            {turnTransition.fromPlayer.betCount}{" "}
                            tickets
                          </p>
                        </div>
                      )}

                      <div
                        className={[
                          "turn-panel__player-content",
                          turnTransition
                            ? "turn-panel__player-content--entering"
                            : "",
                        ]
                          .filter(Boolean)
                          .join(" ")}
                        key={`current-${game.currentPlayer}-${turnTransition?.id ?? 0}`}
                      >
                        <h2>{currentPlayer.name}</h2>

                        <p>
                          {currentPlayer.money} coins ·{" "}
                          {currentPlayer.bets.length} tickets
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="turn-panel__analysis">
                  {isFinished ? (
                    <div className="game-over-summary">
                      <span className="game-over-summary__label">
                        Race winner
                      </span>
  
                      {game.raceWinner ? (
                        <div
                          className="game-over-summary__camel"
                          role="img"
                          aria-label={`${CAMEL_NAMES[game.raceWinner]} camel won the race`}
                        >
                          <CamelPiece
                            className="game-over-summary__camel-icon"
                            color={game.raceWinner}
                          />
                        </div>
                      ) : (
                        <strong className="game-over-summary__camel">
                          Race complete
                        </strong>
                      )}
  
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
                              EV{" "}
                              {item.expectedValue.toFixed(2)}
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
                      {rollButtonText}
                    </button>
  
                    <button
                      className="secondary-button"
                      type="button"
                      disabled={isActing}
                      onClick={() => void handleAdvice()}
                    >
                      {isActing &&
                      !queuedRoll &&
                      !pendingRoll &&
                      !pendingBet &&
                      !pendingPayout &&
                      !pendingGameOver &&
                      !turnTransition
                        ? "Calculating…"
                        : "Analyze bets"}
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
                    <Link
                      className="primary-button"
                      to="/setup"
                    >
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
              animatingColor={
                pendingBet?.color ?? null
              }
              onBet={(color, sourceRect) =>
                void handleBet(color, sourceRect)
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
                    className={[
                      "player-card",
                      !isFinished &&
                      index === game.currentPlayer
                        ? "active-player"
                        : "",
                      turnTransition &&
                      index === turnTransition.toIndex
                        ? "player-card--turn-enter"
                        : "",
                      turnTransition &&
                      index === turnTransition.fromIndex
                        ? "player-card--turn-exit"
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
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
  
                    <PlayerBetTickets
                      bets={player.bets}
                      hideEmptyMessage={
                        isBetSelectionInProgress &&
                        !isFinished &&
                        index === game.currentPlayer
                      }
                      containerRef={
                        !isFinished &&
                        index === game.currentPlayer
                          ? currentPlayerBetTargetRef
                          : undefined
                      }
                    />
                  </article>
                ))}
              </div>
            </section>
  
            <section className="panel">
              <p className="eyebrow">
                Dice history
              </p>
  
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
              <p className="eyebrow">
                Game log
              </p>
  
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
  
        {queuedRoll && diceOverlayPhase && (
          <div
            className={`dice-roll-overlay dice-roll-overlay--${diceOverlayPhase}`}
            role="status"
            aria-live="polite"
            aria-label={
              diceOverlayPhase !== "tumbling"
                ? `${CAMEL_NAMES[queuedRoll.color]} die rolled ${queuedRoll.steps}`
                : "Rolling the die"
            }
          >
            <div className="dice-roll-overlay__stage">
              <div
                className="dice-roll-overlay__die-shell"
                aria-hidden="true"
              >
                <DieFace
                  color={queuedRoll.color}
                  value={diceDisplayValue}
                />
              </div>
  
              <p className="dice-roll-overlay__caption">
                {diceOverlayPhase === "tumbling"
                  ? "Rolling…"
                  : `${CAMEL_NAMES[queuedRoll.color]} · ${queuedRoll.steps}`}
              </p>
            </div>
          </div>
        )}
  
        {pendingPayout &&
          payoutOverlayPhase && (
            <div
              className={`leg-payout-overlay leg-payout-overlay--${payoutOverlayPhase}`}
              role="dialog"
              aria-modal="true"
              aria-labelledby="leg-payout-title"
              aria-describedby={
                payoutOverlayPhase !== "intro"
                  ? "leg-payout-instruction"
                  : undefined
              }
            >
              <section className="leg-payout-card">
                <div className="leg-payout-card__header">
                  <div>
                    <p className="eyebrow">
                      Leg {pendingPayout.summary.leg} complete
                    </p>
                    <h2 id="leg-payout-title">
                      Betting payouts
                    </h2>
                  </div>

                  <span className="leg-payout-card__caption">
                    Final standings
                  </span>
                </div>

                <div className="leg-payout-leaders">
                  <div className="leg-payout-leader">
                    <span>1st place</span>

                    <div
                      className="leg-payout-leader__camel"
                      role="img"
                      aria-label={`${CAMEL_NAMES[pendingPayout.summary.first]} camel`}
                    >
                      <CamelPiece
                        className="leg-payout-leader__camel-icon"
                        color={pendingPayout.summary.first}
                      />
                    </div>
                  </div>

                  <div className="leg-payout-leader">
                    <span>2nd place</span>

                    <div
                      className="leg-payout-leader__camel"
                      role="img"
                      aria-label={`${CAMEL_NAMES[pendingPayout.summary.second]} camel`}
                    >
                      <CamelPiece
                        className="leg-payout-leader__camel-icon"
                        color={pendingPayout.summary.second}
                      />
                    </div>
                  </div>
                </div>

                <div className="leg-payout-players">
                  {pendingPayout.summary.players.map(
                    (playerResult, playerIndex) => (
                      <article
                        className="leg-payout-player"
                        key={playerResult.playerName}
                        style={
                          {
                            "--payout-row-delay":
                              `${playerIndex * 120}ms`,
                            "--payout-total-delay":
                              `${320 + playerIndex * 120}ms`,
                          } as CSSProperties
                        }
                      >
                        <div className="leg-payout-player__identity">
                          <strong>
                            {playerResult.playerName}
                          </strong>

                          <span>
                            {playerResult.moneyBefore}¢ →{" "}
                            {playerResult.moneyAfter}¢
                          </span>
                        </div>

                        <div className="leg-payout-player__tickets">
                          {playerResult.tickets.length ===
                          0 ? (
                            <span className="leg-payout-player__empty">
                              No tickets
                            </span>
                          ) : (
                            playerResult.tickets.map(
                              (ticket, ticketIndex) => (
                                <div
                                  className={`leg-payout-ticket leg-payout-ticket--${ticket.color}`}
                                  key={`${ticket.color}-${ticket.value}-${ticketIndex}`}
                                  title={`${CAMEL_NAMES[ticket.color]} ${ticket.value}: ${getPayoutResultLabel(ticket.result)} ${formatSignedAmount(ticket.payout)}`}
                                  style={
                                    {
                                      "--payout-ticket-delay":
                                        `${180 + playerIndex * 120 + ticketIndex * 70}ms`,
                                    } as CSSProperties
                                  }
                                >
                                  <strong>
                                    {ticket.value}
                                  </strong>

                                  <span>
                                    {getPayoutResultLabel(
                                      ticket.result,
                                    )}
                                  </span>

                                  <em>
                                    {formatSignedAmount(
                                      ticket.payout,
                                    )}
                                  </em>
                                </div>
                              ),
                            )
                          )}
                        </div>

                        <strong
                          className={[
                            "leg-payout-player__total",
                            playerResult.totalPayout > 0
                              ? "leg-payout-player__total--positive"
                              : "",
                            playerResult.totalPayout < 0
                              ? "leg-payout-player__total--negative"
                              : "",
                          ]
                            .filter(Boolean)
                            .join(" ")}
                        >
                          {formatSignedAmount(
                            playerResult.totalPayout,
                          )}
                        </strong>
                      </article>
                    ),
                  )}
                </div>

                {payoutOverlayPhase !== "intro" && (
                  <footer className="leg-payout-card__footer">
                    <p id="leg-payout-instruction">
                      Review the results, then continue when
                      you are ready.
                    </p>

                    <button
                      className="primary-button"
                      type="button"
                      disabled={
                        payoutOverlayPhase !== "details"
                      }
                      onClick={dismissPayoutOverlay}
                    >
                      Continue
                    </button>
                  </footer>
                )}
              </section>
            </div>
          )}


        {pendingGameOver &&
          gameOverOverlayPhase &&
          pendingGameOver.nextGame.raceWinner && (
            <div
              className={`game-over-celebration game-over-celebration--${gameOverOverlayPhase}`}
              role="dialog"
              aria-modal="true"
              aria-labelledby="game-over-celebration-title"
              aria-describedby="game-over-celebration-description"
            >
              <section className="game-over-celebration__card">
                <div
                  className="game-over-celebration__coin-burst"
                  aria-hidden="true"
                >
                  {Array.from(
                    { length: 12 },
                    (_, index) => (
                      <span
                        key={index}
                        style={
                          {
                            "--coin-angle":
                              `${index * 30}deg`,
                            "--coin-distance":
                              `${78 + (index % 3) * 18}px`,
                            "--coin-delay":
                              `${260 + (index % 4) * 55}ms`,
                          } as CSSProperties
                        }
                      />
                    ),
                  )}
                </div>

                <p className="eyebrow">
                  {pendingGameOver.nextGame
                    .winningPlayers.length > 1
                    ? "Game winners"
                    : "Game winner"}
                </p>

                <div
                  className="game-over-celebration__camel"
                  role="img"
                  aria-label={`${CAMEL_NAMES[pendingGameOver.nextGame.raceWinner]} camel won the race`}
                >
                  <CamelPiece
                    className="game-over-celebration__camel-icon"
                    color={
                      pendingGameOver.nextGame.raceWinner
                    }
                  />
                </div>

                <h2 id="game-over-celebration-title">
                  {pendingGameOver.nextGame.winningPlayers.join(
                    " & ",
                  )}
                </h2>

                <p
                  className="game-over-celebration__description"
                  id="game-over-celebration-description"
                >
                  {pendingGameOver.nextGame
                    .winningPlayers.length > 1
                    ? "finish tied with"
                    : "finishes with"}
                </p>

                <div className="game-over-celebration__total">
                  <strong>{displayedWinnerCoins}</strong>
                  <span>coins</span>
                </div>

                <button
                  className="primary-button"
                  type="button"
                  disabled={
                    gameOverOverlayPhase !== "ready"
                  }
                  onClick={dismissGameOverOverlay}
                >
                  View final results
                </button>
              </section>
            </div>
          )}

        {pendingBet && (
          <div
            className="bet-ticket-flight-layer"
            aria-hidden="true"
          >
            <div
              className={`flying-bet-ticket flying-bet-ticket--${pendingBet.color}`}
              key={pendingBet.id}
              onAnimationEnd={handleBetAnimationEnd}
              style={
                {
                  "--bet-start-left":
                    `${pendingBet.sourceRect.left}px`,
                  "--bet-start-top":
                    `${pendingBet.sourceRect.top}px`,
                  "--bet-start-width":
                    `${pendingBet.sourceRect.width}px`,
                  "--bet-start-height":
                    `${pendingBet.sourceRect.height}px`,
                  "--bet-target-left":
                    `${pendingBet.targetRect.left}px`,
                  "--bet-target-top":
                    `${pendingBet.targetRect.top}px`,
                  "--bet-target-width":
                    `${pendingBet.targetRect.width}px`,
                  "--bet-target-height":
                    `${pendingBet.targetRect.height}px`,
                } as CSSProperties
              }
            >
              <div className="flying-bet-ticket__details">
                <span className="flying-bet-ticket__camel">
                  {CAMEL_NAMES[pendingBet.color]}
                </span>
  
                <span className="flying-bet-ticket__payout">
                  1st
                  <strong>+{pendingBet.value}</strong>
                </span>
              </div>
  
              <strong className="flying-bet-ticket__final-value">
                {pendingBet.value}
              </strong>
            </div>
          </div>
        )}
      </main>
    );
  }