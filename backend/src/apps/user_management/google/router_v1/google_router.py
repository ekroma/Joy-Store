import httpx
import jwt
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone

import logging

from apps.user_management.auth.token import get_created_tokens 
from apps.user_management.user import UserService
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Аутентификация & Авторизация через Google"]
)

# Настройки для Google OAuth
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

async def get_google_provider_cfg():
    async with httpx.AsyncClient() as client:
        response = await client.get(GOOGLE_DISCOVERY_URL)
        return response.json()

@router.get("/login_via_google")
async def login_via_google():
    """
    ВХОДИТЬ ЧЕРЕЗ БРАЗУЕР ПО ССЫЛКЕ локал http://localhost:8000/api/login_via_google\n
    ВХОДИТЬ ЧЕРЕЗ БРАЗУЕР ПО ССЫЛКЕ деплой https://aress2245.store/api/login_via_google
    """
    google_provider_cfg = await get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = authorization_endpoint + "?" + urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BASE_URL}/api/login/callback_from_google",
        "scope": "openid email profile",
        "response_type": "code",
        "state": "SOME_RANDOM_STRING",
    })


    return RedirectResponse(url=request_uri)

@router.get("/login/callback_from_google")
async def callback_from_google(code: str, response: Response):
    google_provider_cfg = await get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_endpoint, data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"{settings.BASE_URL}/api/login/callback_from_google",
            "grant_type": "authorization_code"
        })

        if token_response.status_code != 200:
            raise HTTPException(status_code=token_response.status_code, detail="Error retrieving Google OAuth token")

        tokens = token_response.json()
        id_token = tokens.get("id_token")

        if id_token is None:
            raise HTTPException(status_code=400, detail="id_token not found in Google's response")

        claims = jwt.decode(id_token, algorithms=["RS256"], options={"verify_signature": False})
        user_email = claims.get("email")
        user_first_name = claims.get("given_name", "")

        user = await UserService.get_user_by_email(email=user_email)
        if not user:
            user_data = {"email": user_email,
                "first_name": user_first_name,
                "display_name": user_first_name,
                "is_active": True,}
            user = await UserService.create(user_data)

        access_token, refresh_token = get_created_tokens(data={"sub": user['email']})
         
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        response = RedirectResponse(url=f"{settings.BASE_URL}")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="none",
            # domain="aress2245.store",  # Или опустите, чтобы использовать текущий домен
            # path="/",  # Доступно для всего сайта
            expires=(datetime.now(timezone.utc) + access_token_expires),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            # domain="aress2245.store",  # Или опустите, чтобы использовать текущий домен
            # path="/",  # Доступно для всего сайта
            expires=(datetime.now(timezone.utc) + refresh_token_expires),
        )

        # return response