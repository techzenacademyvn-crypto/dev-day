from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductFilter
from app.schemas.common import ApiResponse, PageResponse
from app.modules.products.service import ProductService

router = APIRouter(prefix="/products", tags=["3. Sản phẩm (Products)"])


@router.get(
    "",
    response_model=ApiResponse[PageResponse[ProductResponse]],
    summary="Danh sách sản phẩm (Phân trang cố định 20 sp/trang)",
)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, description="Tìm theo tên sản phẩm"),
    min_price: Optional[Decimal] = Query(default=None, ge=0, description="Giá tối thiểu"),
    max_price: Optional[Decimal] = Query(default=None, ge=0, description="Giá tối đa"),
    category_id: Optional[int] = Query(default=None, description="Lọc theo danh mục"),
    low_stock_threshold: Optional[int] = Query(default=None, description="Lọc sắp hết hàng"),
    is_featured: Optional[bool] = Query(default=None, description="Lọc sản phẩm nổi bật"),
    sort_by: Optional[str] = Query(default=None, description="Sắp xếp theo giá/tồn"),
    db: Session = Depends(get_db),
):
    filters = ProductFilter(
        search=search,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        low_stock_threshold=low_stock_threshold,
        is_featured=is_featured,
        sort_by=sort_by,
    )
    items, total = ProductService.get_list(db, page=page, page_size=page_size, filters=filters)
    page_data = PageResponse.create(
        items=[ProductResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=page_data, message="Lấy danh sách sản phẩm thành công")


@router.get(
    "/{product_id}",
    response_model=ApiResponse[ProductResponse],
    summary="Chi tiết sản phẩm",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    item = ProductService.get_by_id(db, product_id)
    return ApiResponse(data=ProductResponse.model_validate(item))


@router.post(
    "",
    response_model=ApiResponse[ProductResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm sản phẩm mới",
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = ProductService.create(db, data)
    return ApiResponse(
        data=ProductResponse.model_validate(item),
        message="Thêm sản phẩm thành công",
    )


@router.put(
    "/{product_id}",
    response_model=ApiResponse[ProductResponse],
    summary="Cập nhật sản phẩm",
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = ProductService.update(db, product_id, data)
    return ApiResponse(
        data=ProductResponse.model_validate(item),
        message="Cập nhật sản phẩm thành công",
    )


@router.delete(
    "/{product_id}",
    response_model=ApiResponse[None],
    summary="Xoá mềm sản phẩm",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ProductService.soft_delete(db, product_id)
    return ApiResponse(message="Đã xoá sản phẩm thành công")
