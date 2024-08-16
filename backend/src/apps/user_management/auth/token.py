import jwt
from jwt import PyJWTError, decode as jwt_decode
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from config.settings import settings


def create_token(data: dict, expires_delta: timedelta|None, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_created_tokens(data: dict):
    access_token = create_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access")
    refresh_token = create_token(data, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")
    return access_token, refresh_token


async def decode_token(token: str) -> dict:
    try:
        return jwt_decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="622992",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_refresh_token(token: str, secret_key: str, algorithm: str) -> str:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="3001"
        )

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="130")
    elif not token:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="3002")
    return token

def get_token_from_cookie_or_none(request: Request) -> str|None:
    return request.cookies.get("access_token")