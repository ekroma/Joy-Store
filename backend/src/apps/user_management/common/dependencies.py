from fastapi import Depends, HTTPException, status

from apps.user_management.auth.token import get_token_from_cookie, decode_token, get_token_from_cookie_or_none
from apps.user_management.user import UserService, User

async def get_current_user(
        token: str = Depends(get_token_from_cookie)
)-> User:
    payload = await decode_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="622992")
    user = await UserService.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="1202993")
    return user

async def get_current_user_or_none(
        token: str|None = Depends(get_token_from_cookie_or_none)
)-> User|None:
    if token is None:
        return None
    payload = await decode_token(token)
    email = payload.get("sub")
    if email is None:
        return None
    user = await UserService.get_user_by_email(email)
    if not user:
        return None
    return user