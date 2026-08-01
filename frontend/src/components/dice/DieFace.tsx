import type { CamelColor } from "../../types/game";

interface DieFaceProps {
  color: CamelColor;
  value: number;
}

const PIP_POSITIONS: Record<number, readonly number[]> = {
  1: [4],
  2: [0, 8],
  3: [0, 4, 8],
};

export function DieFace({ color, value }: DieFaceProps) {
  const visiblePips = PIP_POSITIONS[value] ?? [];

  return (
    <span
      className={`die camel-${color}`}
      role="img"
      aria-label={`${color} die showing ${value}`}
    >
      {Array.from({ length: 9 }, (_, index) => (
        <span
          className={
            visiblePips.includes(index)
              ? "die__pip die__pip--visible"
              : "die__pip"
          }
          key={index}
        />
      ))}
    </span>
  );
}