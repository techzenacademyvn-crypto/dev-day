from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["1. Xác thực (Authentication)"])


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="Đăng nhập nhân viên",
    description="Nhân viên/Admin đăng nhập bằng email và mật khẩu để nhận Bearer Token.",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )

    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": role_val},
        expires_delta=access_token_expires,
    )

    token_data = TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
    return ApiResponse(data=token_data, message="Đăng nhập thành công")


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Thông tin tài khoản hiện tại",
)
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        data=UserResponse.model_validate(current_user),
        message="Lấy thông tin thành công",
    )
