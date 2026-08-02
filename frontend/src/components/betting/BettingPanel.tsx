import type { CamelColor } from "../../types/game";

import "./BettingPanel.css";

interface BettingPanelProps {
  tickets: Record<CamelColor, number[]>;
  disabled?: boolean;
  animatingColor?: CamelColor | null;
  onBet: (
    color: CamelColor,
    sourceRect: DOMRect,
  ) => void;
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
  animatingColor = null,
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
          Choose a ticket instead of rolling.
        </p>
      </div>

      <div className="betting-panel__tickets">
        {CAMEL_COLORS.map((color) => {
          const availableTickets = tickets[color] ?? [];
          const topValue = availableTickets[0];
          const isSoldOut =
            availableTickets.length === 0;
          const isInFlight =
            animatingColor === color;

          return (
            <button
              className={[
                "bet-ticket",
                `bet-ticket--${color}`,
                isSoldOut
                  ? "bet-ticket--sold-out"
                  : "",
                isInFlight
                  ? "bet-ticket--in-flight"
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
              type="button"
              key={color}
              disabled={disabled || isSoldOut}
              onClick={(event) =>
                onBet(
                  color,
                  event.currentTarget.getBoundingClientRect(),
                )
              }
              aria-label={
                isSoldOut
                  ? `${CAMEL_NAMES[color]} tickets sold out`
                  : `Take the ${CAMEL_NAMES[color]} ticket. Pays ${topValue} coins for first, 1 coin for second, and loses 1 coin otherwise.`
              }
            >
              <span className="bet-ticket__camel">
                {CAMEL_NAMES[color]}
              </span>

              {isSoldOut ? (
                <span className="bet-ticket__sold-out">
                  Sold out
                </span>
              ) : (
                <div className="bet-ticket__payouts">
                  <div className="bet-ticket__main-payout">
                    <span>1st</span>
                    <strong>+{topValue}</strong>
                  </div>

                  <div className="bet-ticket__secondary-payouts">
                    <span>
                      2nd <strong>+1</strong>
                    </span>

                    <span>
                      Other <strong>−1</strong>
                    </span>
                  </div>
                </div>
              )}

              {!isSoldOut && (
                <span className="bet-ticket__remaining">
                  {availableTickets.length} remaining
                </span>
              )}
            </button>
          );
        })}
      </div>
    </section>
  );
}