import type { Bet, CamelColor } from "../../types/game";

import "./PlayerBetTickets.css";

interface PlayerBetTicketsProps {
  bets: Bet[];
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
}: PlayerBetTicketsProps) {
  if (bets.length === 0) {
    return (
      <p className="player-bets__empty">
        No betting tickets
      </p>
    );
  }

  return (
    <div
      className="player-bets"
      aria-label="Player betting tickets"
    >
      {bets.map((bet, index) => (
        <div
          className={`player-bet-ticket player-bet-ticket--${bet.color}`}
          key={`${bet.color}-${bet.value}-${index}`}
          title={`${CAMEL_NAMES[bet.color]} ${bet.value} ticket`}
          aria-label={`${CAMEL_NAMES[bet.color]} ${bet.value} ticket`}
        >
          {bet.value}
        </div>
      ))}
    </div>
  );
}