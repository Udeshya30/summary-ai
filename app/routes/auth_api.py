from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Header

from app.services.auth_service import (
    create_password_reset,
    create_session,
    create_user,
    current_user,
    extract_bearer_token,
    public_user,
    reset_password,
    authenticate_user,
    revoke_session,
)

router = APIRouter()


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=160)
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=5, max_length=160)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=8, max_length=128)


@router.post("/signup")
def signup(req: SignupRequest):
    user = create_user(req.name, req.email, req.password)
    token, expires_at = create_session(user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": public_user(user),
    }


@router.post("/login")
def login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    token, expires_at = create_session(user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": public_user(user),
    }


@router.get("/me")
def me(user=Depends(current_user)):
    return {"user": user}


@router.post("/logout")
def logout(authorization: str = Header(default=""), user=Depends(current_user)):
    token = extract_bearer_token(authorization)
    if token:
        revoke_session(token)
    return {"message": "Signed out.", "user": user}


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    reset_token = create_password_reset(req.email)
    response = {
        "message": "If an account exists, password reset instructions have been prepared.",
    }
    if reset_token:
        response["reset_token"] = reset_token
        response["delivery"] = "development"
    return response


@router.post("/reset-password")
def reset_password_route(req: ResetPasswordRequest):
    reset_password(req.token, req.password)
    return {"message": "Password has been reset. Sign in with the new password."}
