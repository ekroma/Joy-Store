import logging
from fastapi import APIRouter, Depends, Response, Request, status, Body
from fastapi_versioning import version
from apps.user_management.auth.auth_service import AuthService
from apps.base import FeatureAccessException, NotFoundException, SuccessResponse
from apps.market.model import Market
from apps.market.dependencies import get_market
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.user import UserCreate, UserProfile, User,UserService, UserSettings
from apps.user_management.auth.schemas import LoginSchema, PasswordChangeRequest
from apps.user_management.common.exceptions import InvalidRefreshTokenException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация & Авторизация"]
)


@router.post("/pre-register-user", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def pre_register_user(email: str,market:Market=Depends(get_market)):
    if market:
        if not market.features.user_auth:
            raise FeatureAccessException()
    await UserService.pre_register_user(email, market=market)
    return SuccessResponse


@router.post("/register-user", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def register_user(user: UserCreate,market:Market=Depends(get_market)):
    if not market:
        raise NotFoundException(1)
    if not market.features.user_auth:
        raise FeatureAccessException()
    await UserService.register_user(user.model_dump(), market=market)
    return SuccessResponse


@router.post("/login-user", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def login_user(response: Response, request: LoginSchema,market:Market=Depends(get_market)):
    access_token, refresh_token = await AuthService.authenticate_and_create_tokens(request.email, request.password, market=market)
    AuthService.set_token_cookies(response, access_token, refresh_token)
    return SuccessResponse


@router.post("/refresh-token", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def refresh_token(request: Request, response: Response, market:Market=Depends(get_market)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise InvalidRefreshTokenException()
    new_access_token, new_refresh_token = await AuthService.refresh_access_token(refresh_token, market=market)
    AuthService.set_token_cookies(response, new_access_token, new_refresh_token)
    return SuccessResponse


@router.post("/logout", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def logout(response: Response):
    AuthService.remove_token_cookies(response)
    return SuccessResponse


@router.post("/change-password", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def change_password(
        password_change_request: PasswordChangeRequest,
        current_user: User = Depends(get_current_user),
        market:Market=Depends(get_market)
):
    await UserService.change_password(current_user, password_change_request.old_password,
                                    password_change_request.new_password, password_change_request.new_confirm_password,
                                    market=market)
    return SuccessResponse


@router.get("/get-user-profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
@version(1)
async def get_user_profile(
        current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/pre-restore-password", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def pre_restore_password(
        email:str = Body(...),
        current_user: User = Depends(get_current_user),
        market:Market=Depends(get_market)
):
    await UserService.pre_restore_password(email, market=market)
    return SuccessResponse


@router.post("/restore-password", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def restore_password(
        email:str = Body(...),
        password:str = Body(...),
        password_confirm: str = Body(...),
        code:str = Body(...),
        current_user: User = Depends(get_current_user),
        market:Market=Depends(get_market)
):
    await UserService.restore_password(email, password, password_confirm, code, market=market)
    return SuccessResponse


@router.post("/login-token", status_code=status.HTTP_200_OK)
async def login_token(request: LoginSchema,market:Market=Depends(get_market)):
    access_token, refresh_token = await AuthService.authenticate_and_create_tokens(request.email, request.password,market=market)
    bearer_access_token = f"{access_token}"
    return {"access_token": bearer_access_token, "refresh_token": refresh_token}


@router.patch("/user-settings", response_model=UserProfile, status_code=status.HTTP_200_OK)
@version(1)
async def update_user_settings(
    settings:UserSettings = Body(...),
    current_user: User = Depends(get_current_user),
):
    return await UserService.update_user(current_user.id, update_data={"user_settings":settings.model_dump(exclude_none=True, exclude_unset=True)})