from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from web.service import GameService
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Camel Up API",
    version="0.1.0",
    description="Web API for the Camel Up betting simulator.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = GameService()


class CreateGameRequest(BaseModel):
    players: list[str] = Field(
        min_length=2,
        max_length=6,
    )


class PlaceBetRequest(BaseModel):
    color: str = Field(
        min_length=1,
        max_length=1,
    )


@app.get("/api/health")
def health_check() -> dict[str, bool]:
    return {"ok": True}


@app.post(
    "/api/games",
    status_code=status.HTTP_201_CREATED,
)
def create_game(request: CreateGameRequest) -> dict:
    try:
        return service.create_game(request.players)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@app.get("/api/games/{game_id}")
def get_game(game_id: str) -> dict:
    try:
        return service.get_state(game_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@app.post("/api/games/{game_id}/roll")
def roll(game_id: str) -> dict:
    try:
        return service.roll(game_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.post("/api/games/{game_id}/bet")
def place_bet(
    game_id: str,
    request: PlaceBetRequest,
) -> dict:
    try:
        return service.place_bet(
            game_id,
            request.color.lower(),
        )
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.get("/api/games/{game_id}/advice")
def get_advice(game_id: str) -> dict:
    try:
        return service.get_advice(game_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.post("/api/games/{game_id}/next-leg")
def start_next_leg(game_id: str) -> dict:
    try:
        return service.start_next_leg(game_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error