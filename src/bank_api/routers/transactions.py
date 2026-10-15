from fastapi import APIRouter, Query
from sqlalchemy import select

from bank_api.dependencies import CurrentUser, Session
from bank_api.models import Transaction
from bank_api.schemas import AccountOut, MoneyIn, TransactionOut, TransferIn
from bank_api.services import deposit, transfer, withdraw

router = APIRouter(prefix="/transactions", tags=["Transações"])


@router.post("/deposit", response_model=AccountOut)
async def make_deposit(data: MoneyIn, user: CurrentUser, session: Session) -> AccountOut:
    return AccountOut.model_validate(await deposit(session, user.account, data.amount))


@router.post("/withdraw", response_model=AccountOut)
async def make_withdrawal(data: MoneyIn, user: CurrentUser, session: Session) -> AccountOut:
    return AccountOut.model_validate(await withdraw(session, user.account, data.amount))


@router.post("/transfer", response_model=AccountOut)
async def make_transfer(data: TransferIn, user: CurrentUser, session: Session) -> AccountOut:
    account = await transfer(session, user.account, data.destination_account, data.amount)
    return AccountOut.model_validate(account)


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    user: CurrentUser,
    session: Session,
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Transaction]:
    result = await session.execute(
        select(Transaction)
        .where(Transaction.account_id == user.account.id)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .limit(limit)
    )
    return list(result.scalars())

