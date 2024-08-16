from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
    new_confirm_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
