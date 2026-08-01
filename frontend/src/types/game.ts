export type CamelColor = "r" | "b" | "g" | "y" | "p";

export interface Bet {
  color: CamelColor;
  value: number;
}

export interface Player {
  name: string;
  money: number;
  bets: Bet[];
}

export interface RolledDie {
  color: CamelColor;
  value: number;
}

export interface GameCapabilities {
  legBetting: boolean;
  aiAdvice: boolean;
  raceBetting: boolean;
  spectatorTiles: boolean;
  fullRace: boolean;
}

export interface GameState {
  gameId: string;
  status: "playing" | "leg_complete";
  currentPlayer: number;
  leg: number;
  track: CamelColor[][];
  rankings: CamelColor[];
  players: Player[];
  tickets: Record<CamelColor, number[]>;
  rolledDice: RolledDie[];
  remainingDice: CamelColor[];
  log: string[];
  capabilities: GameCapabilities;
}

export interface AdviceItem {
  color: CamelColor;
  colorName: string;
  value: number;
  probabilityFirst: number;
  probabilitySecond: number;
  expectedValue: number;
}

export interface AdviceResponse {
  advice: AdviceItem[];
}