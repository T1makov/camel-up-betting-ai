import type { CamelColor } from "../../types/game";
import { CamelPiece } from "../icons/CamelPiece";
import type { CSSProperties } from "react";

import "./RaceBoard.css";

interface RaceBoardProps {
  track: CamelColor[][];
}

export function RaceBoard({ track }: RaceBoardProps) {
  return (
    <section className="race-board" aria-label="Camel race track">
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
        {track.map((stack, position) => (
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
          </div>
        ))}
      </div>
    </section>
  );
}