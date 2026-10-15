from conftest import register_and_login
from fastapi.testclient import TestClient


def test_deposit_withdraw_and_statement(client: TestClient) -> None:
    _, headers = register_and_login(client)
    deposit = client.post("/transactions/deposit", json={"amount": "150.50"}, headers=headers)
    assert deposit.status_code == 200
    assert deposit.json()["balance"] == "150.50"

    withdrawal = client.post(
        "/transactions/withdraw", json={"amount": "50.25"}, headers=headers
    )
    assert withdrawal.status_code == 200
    assert withdrawal.json()["balance"] == "100.25"

    statement = client.get("/transactions", headers=headers)
    assert [item["kind"] for item in statement.json()] == ["withdrawal", "deposit"]


def test_rejects_invalid_transactions(client: TestClient) -> None:
    user, headers = register_and_login(client)
    invalid_deposit = client.post(
        "/transactions/deposit", json={"amount": 0}, headers=headers
    )
    assert invalid_deposit.status_code == 422
    insufficient = client.post(
        "/transactions/withdraw", json={"amount": "1.00"}, headers=headers
    )
    assert insufficient.status_code == 422
    same_account = client.post(
        "/transactions/transfer",
        json={"amount": "1.00", "destination_account": user["account"]["number"]},
        headers=headers,
    )
    assert same_account.status_code == 422


def test_transfer_is_reflected_in_both_accounts(client: TestClient) -> None:
    _, first_headers = register_and_login(client)
    second_user, second_headers = register_and_login(
        client,
        name="Maria Silva",
        email="maria@example.com",
        cpf="98765432100",
    )
    client.post("/transactions/deposit", json={"amount": "200.00"}, headers=first_headers)

    transfer = client.post(
        "/transactions/transfer",
        json={"amount": "75.00", "destination_account": second_user["account"]["number"]},
        headers=first_headers,
    )
    assert transfer.status_code == 200
    assert transfer.json()["balance"] == "125.00"

    destination = client.get("/accounts/balance", headers=second_headers)
    assert destination.json()["balance"] == "75.00"
    destination_statement = client.get("/transactions", headers=second_headers).json()
    assert destination_statement[0]["kind"] == "transfer_in"
    assert destination_statement[0]["counterparty_account"] == "00000001"


def test_transfer_to_unknown_account_is_rejected(client: TestClient) -> None:
    _, headers = register_and_login(client)
    client.post("/transactions/deposit", json={"amount": "20.00"}, headers=headers)
    response = client.post(
        "/transactions/transfer",
        json={"amount": "10.00", "destination_account": "99999999"},
        headers=headers,
    )
    assert response.status_code == 404
