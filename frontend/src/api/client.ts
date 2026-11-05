import type {
    AdviceResponse,
    CamelColor,
    GameState,
  } from "../types/game";
  
  const API_URL =
    import.meta.env.VITE_API_URL ??
    (import.meta.env.DEV ? "http://127.0.0.1:8000/api" : "/api");
  
  async function request<T>(
    path: string,
    options: RequestInit = {},
  ): Promise<T> {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  
    if (!response.ok) {
      let message = `Request failed with status ${response.status}`;
  
      try {
        const body = (await response.json()) as {
          detail?: string;
        };
  
        if (body.detail) {
          message = body.detail;
        }
      } catch {
        // Keep the default error message when the response is not JSON.
      }
  
      throw new Error(message);
    }
  
    return response.json() as Promise<T>;
  }
  
  export function createGame(players: string[]): Promise<GameState> {
    return request<GameState>("/games", {
      method: "POST",
      body: JSON.stringify({ players }),
    });
  }
  
  export function getGame(gameId: string): Promise<GameState> {
    return request<GameState>(`/games/${gameId}`);
  }
  
  export function rollDie(gameId: string): Promise<GameState> {
    return request<GameState>(`/games/${gameId}/roll`, {
      method: "POST",
    });
  }
  
  export function placeBet(
    gameId: string,
    color: CamelColor,
  ): Promise<GameState> {
    return request<GameState>(`/games/${gameId}/bet`, {
      method: "POST",
      body: JSON.stringify({ color }),
    });
  }
  
  export function getAdvice(
    gameId: string,
  ): Promise<AdviceResponse> {
    return request<AdviceResponse>(`/games/${gameId}/advice`);
  }
  
  export function startNextLeg(gameId: string): Promise<GameState> {
    return request<GameState>(`/games/${gameId}/next-leg`, {
      method: "POST",
    });
  }
