import type { CamelColor } from "../../types/game";

import "./BettingPanel.css";

interface BettingPanelProps {
  tickets: Record<CamelColor, number[]>;
  disabled?: boolean;
  onBet: (color: CamelColor) => void;
}

const CAMEL_NAMES: Record<CamelColor, string> = {
  r: "Red",
  b: "Blue",
  g: "Green",
  y: "Yellow",
  p: "Purple",
};

const CAMEL_COLORS: CamelColor[] = [
  "r",
  "b",
  "g",
  "y",
  "p",
];

export function BettingPanel({
  tickets,
  disabled = false,
  onBet,
}: BettingPanelProps) {
  return (
    <section
      className="betting-panel"
      aria-labelledby="betting-panel-title"
    >
      <div className="betting-panel__header">
        <div>
          <p className="eyebrow">Leg betting</p>

          <h2 id="betting-panel-title">
            Available tickets
          </h2>
        </div>

        <p className="betting-panel__instruction">
          Choose one ticket instead of rolling.
        </p>
      </div>

      <div className="betting-panel__tickets">
        {CAMEL_COLORS.map((color) => {
          const availableTickets = tickets[color] ?? [];
          const topValue = availableTickets[0];
          const isSoldOut = availableTickets.length === 0;

          return (
            <button
              className={[
                "bet-ticket",
                `bet-ticket--${color}`,
                isSoldOut ? "bet-ticket--sold-out" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              type="button"
              key={color}
              disabled={disabled || isSoldOut}
              onClick={() => onBet(color)}
              aria-label={
                isSoldOut
                  ? `${CAMEL_NAMES[color]} tickets sold out`
                  : `Take the ${CAMEL_NAMES[color]} ${topValue} coin ticket`
              }
            >
              <span className="bet-ticket__camel">
                {CAMEL_NAMES[color]}
              </span>

              <span className="bet-ticket__value">
                {isSoldOut ? "—" : topValue}
              </span>

              <span className="bet-ticket__footer">
                {isSoldOut
                  ? "Sold out"
                  : `${availableTickets.length} remaining`}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}