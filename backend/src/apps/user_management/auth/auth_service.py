from datetime import datetime, timedelta, timezone
from apps.user_management.common.exceptions import IncorrectCredentialsException, InvalidRefreshTokenException
from apps.user_management.auth.token import  get_created_tokens, verify_refresh_token
from config.settings import settings
from apps.user_management.auth.auth import authenticate_user
from apps.user_management.user import UserService, User
from apps.base.collection import BaseDAO
from fastapi import Response
from apps.market.model import Market

class AuthService(BaseDAO):
    collection = User

    @classmethod
    async def authenticate_and_create_tokens(cls,email: str, password: str, market:Market|None=None):
        if not market:
            user = await UserService.get_user_by_email(email=email, additional_fields={"is_staff":True})
        else:
            user = await UserService.get_user_by_email(email=email, market=market,additional_fields={"is_staff":False})
        user = await authenticate_user(user, password)
        if not user:
            raise IncorrectCredentialsException()
        access_token, refresh_token = get_created_tokens(data={"sub": user.email})
        await UserService.update_user(user.id, {"refresh_token":refresh_token})
        return access_token, refresh_token

    @staticmethod
    async def refresh_access_token(refresh_token: str, market:Market|None=None):
        email = verify_refresh_token(refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
        if email is None:
            raise InvalidRefreshTokenException()
        if not market:
            user = await UserService.get_user_by_email(email=email, additional_fields={"is_staff":True})
        else:
            user = await UserService.get_user_by_email(email=email, market=market)
        if not user or user.refresh_token != refresh_token:
            raise InvalidRefreshTokenException()
        new_access_token, new_refresh_token = get_created_tokens(data={"sub": email})
        await UserService.update_user(user.id, {"refresh_token":new_refresh_token})
        user = await UserService.get_user_by_email(email=email,market=market)
        return new_access_token, new_refresh_token

    @staticmethod
    def remove_token_cookies(response):
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response

    @staticmethod
    def set_token_cookies(response:Response, access_token, refresh_token:str):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="strict",#type:ignore
            expires=(datetime.now(timezone.utc) + access_token_expires) # type: ignore
        )
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="strict",#type:ignore
            expires=(datetime.now(timezone.utc) + refresh_token_expires) # type: ignore
        )
        return response
