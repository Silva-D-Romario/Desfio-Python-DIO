from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bank_api.database import create_tables
from bank_api.routers import accounts, auth, transactions


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await create_tables()
    yield


app = FastAPI(
    title="Desafio Python DIO - API Bancária",
    version="1.0.0",
    description="API assíncrona para operações bancárias com autenticação JWT.",
    lifespan=lifespan,
)
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/health", tags=["Monitoramento"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
