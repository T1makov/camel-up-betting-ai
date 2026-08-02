import {
    useEffect,
    useMemo,
    useRef,
    useState,
  } from "react";
  import type {
    AnimationEvent,
    CSSProperties,
  } from "react";
  
  import type { CamelColor } from "../../types/game";
  import { CamelPiece } from "../icons/CamelPiece";
  
  import "./RaceBoard.css";
  
  export interface RaceMoveAnimation {
    id: number;
    color: CamelColor;
    steps: number;
  }
  
  interface RaceBoardProps {
    track: CamelColor[][];
    move?: RaceMoveAnimation | null;
    onMoveComplete?: () => void;
  }
  
  interface MovementDetails {
    sourcePosition: number;
    sourceStackIndex: number;
    movingStack: CamelColor[];
    baseTrack: CamelColor[][];
    steps: number;
  }
  
  function getMovementDetails(
    track: CamelColor[][],
    move: RaceMoveAnimation | null | undefined,
  ): MovementDetails | null {
    if (!move || move.steps < 1) {
      return null;
    }
  
    for (
      let position = 0;
      position < track.length;
      position += 1
    ) {
      const sourceStack = track[position];
      const sourceStackIndex = sourceStack.indexOf(move.color);
  
      if (sourceStackIndex === -1) {
        continue;
      }
  
      const baseTrack = track.map((stack) => [...stack]);
      const movingStack = sourceStack.slice(sourceStackIndex);
  
      baseTrack[position] = sourceStack.slice(
        0,
        sourceStackIndex,
      );
  
      return {
        sourcePosition: position,
        sourceStackIndex,
        movingStack,
        baseTrack,
        steps: Math.max(1, Math.floor(move.steps)),
      };
    }
  
    return null;
  }
  
  export function RaceBoard({
    track,
    move = null,
    onMoveComplete,
  }: RaceBoardProps) {
    const [hopIndex, setHopIndex] = useState(0);
    const timerRef = useRef<number | null>(null);
    const completedMoveIdRef = useRef<number | null>(null);
    const onMoveCompleteRef = useRef(onMoveComplete);
  
    const movement = useMemo(
      () => getMovementDetails(track, move),
      [track, move],
    );
  
    useEffect(() => {
      onMoveCompleteRef.current = onMoveComplete;
    }, [onMoveComplete]);
  
    useEffect(() => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
        timerRef.current = null;
      }
  
      setHopIndex(0);
      completedMoveIdRef.current = null;
    }, [move?.id]);
  
    useEffect(() => {
      if (!move) {
        return;
      }
  
      const shouldSkipAnimation =
        !movement ||
        window.matchMedia(
          "(prefers-reduced-motion: reduce)",
        ).matches;
  
      if (!shouldSkipAnimation) {
        return;
      }
  
      timerRef.current = window.setTimeout(() => {
        if (completedMoveIdRef.current === move.id) {
          return;
        }
  
        completedMoveIdRef.current = move.id;
        onMoveCompleteRef.current?.();
      }, 0);
  
      return () => {
        if (timerRef.current !== null) {
          window.clearTimeout(timerRef.current);
          timerRef.current = null;
        }
      };
    }, [move, movement]);
  
    useEffect(
      () => () => {
        if (timerRef.current !== null) {
          window.clearTimeout(timerRef.current);
        }
      },
      [],
    );
  
    function finishMove() {
      if (
        !move ||
        completedMoveIdRef.current === move.id
      ) {
        return;
      }
  
      completedMoveIdRef.current = move.id;
      onMoveCompleteRef.current?.();
    }
  
    function handleHopEnd(
      event: AnimationEvent<HTMLDivElement>,
    ) {
      if (
        event.target !== event.currentTarget ||
        event.animationName !== "camel-stack-hop" ||
        !movement
      ) {
        return;
      }
  
      const isLastHop =
        hopIndex >= movement.steps - 1;
  
      timerRef.current = window.setTimeout(() => {
        if (isLastHop) {
          finishMove();
          return;
        }
  
        setHopIndex((currentHop) => currentHop + 1);
      }, isLastHop ? 90 : 70);
    }
  
    const renderedTrack = movement
      ? movement.baseTrack
      : track;
  
    const lastPosition = track.length - 1;
    const currentPosition = movement
      ? Math.min(
          movement.sourcePosition + hopIndex,
          lastPosition,
        )
      : -1;
    const nextPosition = movement
      ? Math.min(currentPosition + 1, lastPosition)
      : -1;
    const isInPlaceHop =
      movement !== null &&
      currentPosition === nextPosition;
  
    const isLastHop =
      movement !== null &&
      hopIndex >= movement.steps - 1;
  
    const currentObstacleSize = movement
      ? movement.baseTrack[currentPosition].length
      : 0;
    const nextObstacleSize = movement
      ? movement.baseTrack[nextPosition].length
      : 0;
  
    /*
     * The moving stack only truly lands on another stack at the
     * final destination. An occupied intermediate space is treated
     * as an obstacle: the moving stack stays slightly above it and
     * immediately begins the next hop instead of visually merging.
     */
    const startBaseSize = movement
      ? hopIndex === 0
        ? movement.sourceStackIndex
        : currentObstacleSize
      : 0;
    const landingBaseSize = movement
      ? nextObstacleSize
      : 0;
    const startClearance =
      movement && hopIndex > 0 && currentObstacleSize > 0
        ? 10
        : 0;
    const landingClearance =
      movement && !isLastHop && nextObstacleSize > 0
        ? 10
        : 0;
    const hopClearance = Math.min(
      82,
      52 +
        Math.max(
          currentObstacleSize,
          nextObstacleSize,
        ) *
          7,
    );
  
    return (
      <section
        className="race-board"
        aria-label="Camel race track"
      >
        <div className="race-board__header">
          <div>
            <p className="eyebrow">Race track</p>
            <h2>Current positions</h2>
          </div>
  
          <div className="race-board__markers">
            <span>Start</span>
            <span>Finish</span>
          </div>
        </div>
  
        <div className="race-board__track">
          {renderedTrack.map((stack, position) => (
            <div className="race-space" key={position}>
              <span className="race-space__number">
                {position + 1}
              </span>
  
              <div
                className="camel-stack"
                style={
                  {
                    "--stack-size": stack.length,
                  } as CSSProperties
                }
              >
                {stack.map((color, stackIndex) => (
                  <CamelPiece
                    className="camel-piece"
                    color={color}
                    key={`${color}-${stackIndex}`}
                    style={
                      {
                        "--stack-index": stackIndex,
                      } as CSSProperties
                    }
                  />
                ))}
              </div>
  
              {movement &&
                position === currentPosition && (
                  <div
                    className={`camel-stack camel-stack--moving${
                      isInPlaceHop
                        ? " camel-stack--in-place"
                        : ""
                    }`}
                    key={`${move?.id ?? 0}-${hopIndex}`}
                    onAnimationEnd={handleHopEnd}
                    style={
                      {
                        "--stack-size":
                          movement.movingStack.length,
                        "--start-base-size":
                          startBaseSize,
                        "--landing-base-size":
                          landingBaseSize,
                        "--start-clearance":
                          `${startClearance}px`,
                        "--landing-clearance":
                          `${landingClearance}px`,
                        "--hop-clearance":
                          `${hopClearance}px`,
                      } as CSSProperties
                    }
                  >
                    {movement.movingStack.map(
                      (color, stackIndex) => (
                        <CamelPiece
                          animateLegs={stackIndex === 0}
                          className="camel-piece"
                          color={color}
                          key={`${color}-${stackIndex}`}
                          style={
                            {
                              "--stack-index": stackIndex,
                            } as CSSProperties
                          }
                        />
                      ),
                    )}
                  </div>
                )}
            </div>
          ))}
        </div>
  
        {movement && (
          <p
            className="visually-hidden"
            aria-live="polite"
          >
            Moving the {move?.color} camel, hop{" "}
            {hopIndex + 1} of {movement.steps}.
          </p>
        )}
      </section>
    );
  }