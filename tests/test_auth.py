from conftest import register_and_login
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_and_read_account(client: TestClient) -> None:
    user, headers = register_and_login(client)
    assert user["account"]["number"] == "00000001"
    assert user["account"]["balance"] == "0.00"

    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "romario@example.com"


def test_rejects_duplicate_user_and_invalid_login(client: TestClient) -> None:
    register_and_login(client)
    duplicate = client.post(
        "/auth/register",
        json={
            "name": "Outro Usuario",
            "email": "romario@example.com",
            "cpf": "98765432100",
            "password": "senha123",
        },
    )
    assert duplicate.status_code == 409

    login = client.post(
        "/auth/token",
        data={"username": "romario@example.com", "password": "incorreta"},
    )
    assert login.status_code == 401


def test_requires_valid_token(client: TestClient) -> None:
    assert client.get("/accounts/me").status_code == 401
    response = client.get(
        "/accounts/me", headers={"Authorization": "Bearer token-invalido"}
    )
    assert response.status_code == 401
