from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bank_api.models import Account, Transaction, TransactionKind, User
from bank_api.schemas import UserCreate
from bank_api.security import hash_password

MONEY_STEP = Decimal("0.01")


def as_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_STEP)


async def register_user(session: AsyncSession, data: UserCreate) -> User:
    user = User(
        name=data.name.strip(),
        email=data.email,
        cpf=data.cpf,
        password_hash=hash_password(data.password),
    )
    session.add(user)
    try:
        await session.flush()
        user.account = Account(number=f"{user.id:08d}", balance=Decimal("0.00"))
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail ou CPF já cadastrado",
        ) from error

    result = await session.execute(
        select(User).options(selectinload(User.account)).where(User.id == user.id)
    )
    return result.scalar_one()


async def deposit(session: AsyncSession, account: Account, amount: Decimal) -> Account:
    amount = as_money(amount)
    account.balance = as_money(account.balance + amount)
    session.add(Transaction(kind=TransactionKind.DEPOSIT, amount=amount, account=account))
    await session.commit()
    await session.refresh(account)
    return account


async def withdraw(session: AsyncSession, account: Account, amount: Decimal) -> Account:
    amount = as_money(amount)
    if account.balance < amount:
        raise HTTPException(status_code=422, detail="Saldo insuficiente")

    account.balance = as_money(account.balance - amount)
    session.add(Transaction(kind=TransactionKind.WITHDRAWAL, amount=amount, account=account))
    await session.commit()
    await session.refresh(account)
    return account


async def transfer(
    session: AsyncSession,
    source: Account,
    destination_number: str,
    amount: Decimal,
) -> Account:
    amount = as_money(amount)
    if source.number == destination_number:
        raise HTTPException(status_code=422, detail="A conta de destino deve ser diferente")
    if source.balance < amount:
        raise HTTPException(status_code=422, detail="Saldo insuficiente")

    result = await session.execute(select(Account).where(Account.number == destination_number))
    destination = result.scalar_one_or_none()
    if destination is None:
        raise HTTPException(status_code=404, detail="Conta de destino não encontrada")

    source.balance = as_money(source.balance - amount)
    destination.balance = as_money(destination.balance + amount)
    session.add_all(
        [
            Transaction(
                kind=TransactionKind.TRANSFER_OUT,
                amount=amount,
                account=source,
                counterparty_account=destination.number,
            ),
            Transaction(
                kind=TransactionKind.TRANSFER_IN,
                amount=amount,
                account=destination,
                counterparty_account=source.number,
            ),
        ]
    )
    await session.commit()
    await session.refresh(source)
    return source

