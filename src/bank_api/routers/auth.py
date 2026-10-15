from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bank_api.dependencies import Session
from bank_api.models import User
from bank_api.schemas import TokenOut, UserCreate, UserOut
from bank_api.security import create_access_token, verify_password
from bank_api.services import register_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: Session) -> User:
    return await register_user(session, data)


@router.post("/token", response_model=TokenOut)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session,
) -> TokenOut:
    result = await session.execute(
        select(User).options(selectinload(User.account)).where(User.email == form.username.lower())
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    return TokenOut(access_token=create_access_token(user.id))

