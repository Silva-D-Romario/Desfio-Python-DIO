from fastapi import APIRouter

from bank_api.dependencies import CurrentUser
from bank_api.schemas import AccountOut, UserOut

router = APIRouter(prefix="/accounts", tags=["Contas"])


@router.get("/me", response_model=UserOut)
async def get_my_account(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.get("/balance", response_model=AccountOut)
async def get_balance(user: CurrentUser) -> AccountOut:
    return AccountOut.model_validate(user.account)

