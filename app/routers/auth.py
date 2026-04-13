from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import jwt
from sqlalchemy.orm import Session

from app.dependencies.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    create_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.dependencies.db import get_db
from app.models.tenant import RevokedToken, User
from app.routers._utils import audit_mutation, commit_or_409
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TwoFAVerifyRequest,
    TwoFAVerifyResponse,
)
from app.schemas.common import MessageResponse
from uuid import uuid4

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.deleted_at.is_(None)).first()
    if not user or not user.is_active or not verify_password(data.password.get_secret_value(), user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    requires_2fa = False
    if requires_2fa:
        temp_token = create_token(user, token_type="2fa", expires_delta=__import__("datetime").timedelta(minutes=5))
        return LoginResponse(access_token="", refresh_token=None, requires_2fa=True, temp_token=temp_token)

    return LoginResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        requires_2fa=False,
    )


@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
def verify_2fa(data: TwoFAVerifyRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.temp_token)
    if payload.get("type") != "2fa":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid 2FA token.")
    user = db.query(User).filter(User.id == __import__("uuid").UUID(payload["sub"]).bytes, User.deleted_at.is_(None)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
    return TwoFAVerifyResponse(access_token=create_access_token(user), refresh_token=create_refresh_token(user), user=user)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    user = db.query(User).filter(User.id == __import__("uuid").UUID(payload["sub"]).bytes, User.deleted_at.is_(None)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
    return RefreshTokenResponse(access_token=create_access_token(user))


@router.post("/logout", response_model=MessageResponse)
def logout(
    data: LogoutRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Refresh token has no jti.")
    if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        db.add(
            RevokedToken(
                id=uuid4().bytes,
                jti=jti,
                user_id=current_user.id,
                expires_at=datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc),
            )
        )
    audit_mutation(db, request, current_user, action="logout", table_name="revoked_tokens", record_id=current_user.id)
    commit_or_409(db)
    return MessageResponse(message="OK")
