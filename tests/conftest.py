import asyncio
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path("/tmp/desfio-python-dio-test.db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB}"
os.environ["JWT_SECRET"] = "test-secret"

from bank_api.database import Base, engine  # noqa: E402
from bank_api.main import app  # noqa: E402


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def clean_database() -> Iterator[None]:
    asyncio.run(reset_database())
    yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(
    client: TestClient,
    *,
    name: str = "Romario Silva",
    email: str = "romario@example.com",
    cpf: str = "12345678901",
) -> tuple[dict, dict[str, str]]:
    response = client.post(
        "/auth/register",
        json={"name": name, "email": email, "cpf": cpf, "password": "senha123"},
    )
    assert response.status_code == 201
    token_response = client.post(
        "/auth/token",
        data={"username": email, "password": "senha123"},
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    return response.json(), {"Authorization": f"Bearer {token}"}

