from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bank_api.database import get_session
from bank_api.models import User
from bank_api.security import decode_access_token, oauth2_scheme

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(session: Session, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token)
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_error from None

    result = await session.execute(
        select(User).options(selectinload(User.account)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

