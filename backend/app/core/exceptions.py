from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """Lớp ngoại lệ cơ sở cho ứng dụng TZ Shop."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Tài nguyên không tồn tại", details: Optional[Any] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class BadRequestException(AppException):
    def __init__(self, message: str = "Dữ liệu yêu cầu không hợp lệ", details: Optional[Any] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Không có quyền thực hiện hành động này", details: Optional[Any] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        errors.append({"field": loc, "message": err.get("msg")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "message": "Dữ liệu gửi lên không đúng định dạng",
                "details": errors,
            },
        },
    )
