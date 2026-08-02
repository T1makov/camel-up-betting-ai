import type { Ref } from "react";

import type {
  Bet,
  CamelColor,
} from "../../types/game";

import "./PlayerBetTickets.css";

interface PlayerBetTicketsProps {
  bets: Bet[];
  containerRef?: Ref<HTMLDivElement>;
  hideEmptyMessage?: boolean;
}

const CAMEL_NAMES: Record<CamelColor, string> = {
  r: "Red",
  b: "Blue",
  g: "Green",
  y: "Yellow",
  p: "Purple",
};

export function PlayerBetTickets({
  bets,
  containerRef,
  hideEmptyMessage = false,
}: PlayerBetTicketsProps) {
  const isEmpty = bets.length === 0;

  return (
    <div
      className={[
        "player-bets",
        isEmpty ? "player-bets--empty" : "",
        isEmpty && hideEmptyMessage
          ? "player-bets--pending"
          : "",
      ]
        .filter(Boolean)
        .join(" ")}
      ref={containerRef}
      aria-label="Player betting tickets"
    >
      {isEmpty ? (
        hideEmptyMessage ? null : (
          <p className="player-bets__empty">
            No betting tickets
          </p>
        )
      ) : (
        bets.map((bet, index) => (
          <div
            className={`player-bet-ticket player-bet-ticket--${bet.color}`}
            key={`${bet.color}-${bet.value}-${index}`}
            title={`${CAMEL_NAMES[bet.color]} ${bet.value} ticket`}
            aria-label={`${CAMEL_NAMES[bet.color]} ${bet.value} ticket`}
          >
            {bet.value}
          </div>
        ))
      )}
    </div>
  );
}