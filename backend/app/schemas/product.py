from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    category_id: int = Field(..., description="ID danh mục cha")
    name: str = Field(..., min_length=1, max_length=200, description="Tên sản phẩm")
    sku: str = Field(..., min_length=1, max_length=50, description="Mã SKU duy nhất")
    price: Decimal = Field(..., ge=0, description="Đơn giá, 2 số lẻ")
    stock: int = Field(default=0, ge=0, description="Số lượng tồn kho (sửa tay)")
    is_featured: bool = Field(default=False, description="Đánh dấu sản phẩm nổi bật")
    image_url: Optional[str] = None
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    is_featured: Optional[bool] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    restocked_at: Optional[datetime] = None
    out_of_stock_at: Optional[datetime] = None
    last_stock_action: Optional[str] = None


class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    search: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    low_stock_threshold: Optional[int] = None
    is_featured: Optional[bool] = None
    sort_by: Optional[str] = None  # "name_asc", "name_desc", "price_asc", "price_desc", "stock_asc", "stock_desc"
