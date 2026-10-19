from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryFilter
from app.schemas.common import ApiResponse, PageResponse
from app.modules.categories.service import CategoryService

router = APIRouter(prefix="/categories", tags=["2. Danh mục (Categories) - Mẫu chuẩn MAU-01"])


@router.get(
    "",
    response_model=ApiResponse[PageResponse[CategoryResponse]],
    summary="Danh sách danh mục (Hỗ trợ lọc đang hoạt động)",
)
def list_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: Optional[bool] = Query(default=None, description="Lọc danh mục đang hoạt động (Đề MAU-01)"),
    name: Optional[str] = Query(default=None, description="Tìm kiếm theo tên danh mục"),
    db: Session = Depends(get_db),
):
    filters = CategoryFilter(is_active=is_active, name=name)
    items, total = CategoryService.get_list(db, page=page, page_size=page_size, filters=filters)
    page_data = PageResponse.create(
        items=[CategoryResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=page_data, message="Lấy danh sách danh mục thành công")


@router.get(
    "/{category_id}",
    response_model=ApiResponse[CategoryResponse],
    summary="Chi tiết danh mục",
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    item = CategoryService.get_by_id(db, category_id)
    return ApiResponse(data=CategoryResponse.model_validate(item))


@router.post(
    "",
    response_model=ApiResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm danh mục mới",
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = CategoryService.create(db, data)
    return ApiResponse(
        data=CategoryResponse.model_validate(item),
        message="Thêm danh mục thành công",
    )


@router.put(
    "/{category_id}",
    response_model=ApiResponse[CategoryResponse],
    summary="Cập nhật danh mục",
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = CategoryService.update(db, category_id, data)
    return ApiResponse(
        data=CategoryResponse.model_validate(item),
        message="Cập nhật danh mục thành công",
    )


@router.delete(
    "/{category_id}",
    response_model=ApiResponse[None],
    summary="Xoá mềm danh mục",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CategoryService.soft_delete(db, category_id)
    return ApiResponse(message="Đã xoá danh mục thành công")
