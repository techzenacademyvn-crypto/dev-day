from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.order import OrderItem


class Product(Base, TimestampMixin, SoftDeleteMixin):
    """Bảng sản phẩm.
    price là Numeric(12, 2), có 2 số lẻ (vd: 19.99). stock là số lượng tồn, sửa tay.
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    restocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    out_of_stock_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    last_stock_action: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")
