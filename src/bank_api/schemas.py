from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from bank_api.models import TransactionKind


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    cpf: str = Field(pattern=r"^\d{11}$")
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class AccountOut(BaseModel):
    number: str
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    account: AccountOut

    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MoneyIn(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class TransferIn(MoneyIn):
    destination_account: str = Field(pattern=r"^\d{8}$")


class TransactionOut(BaseModel):
    id: int
    kind: TransactionKind
    amount: Decimal
    counterparty_account: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

