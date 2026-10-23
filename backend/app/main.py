from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
)

# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.categories.router import router as categories_router
from app.modules.products.router import router as products_router, admin_router as admin_products_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Dev Day - TZ Shop bản rút gọn: sản phẩm và danh mục, chạy local",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cấu hình CORS cho Frontend Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hỗ trợ mọi port dev của frontend (5173, 3000,...)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Exception Handlers chuẩn hóa
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Gắn các Routers vào tiền tố /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(admin_products_router, prefix="/api/v1")


@app.get("/", tags=["Health Check"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "environment": settings.ENV,
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy"}
