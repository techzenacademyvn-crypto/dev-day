from decimal import Decimal
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, Integer, Boolean, Text, ForeignKey
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

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")

    @property
    def days_in_stock(self) -> int:
        """Số ngày sản phẩm đã lưu trong kho theo chuẩn UTC."""
        if not self.created_at:
            return 0
        now = datetime.now(timezone.utc)
        created = self.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return max(0, (now - created).days)

    @property
    def stock_status(self) -> str:
        """Phân loại tình trạng tồn kho:
        - out_of_stock: Hết hàng (stock == 0)
        - overstocked: Tồn kho (> 2 tháng tức 60 ngày VÀ có nhiều hơn 10 sản phẩm)
        - normal: Tồn kho bình thường
        """
        if self.stock == 0:
            return "out_of_stock"

        now = datetime.now(timezone.utc)
        created = self.created_at
        if created:
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            # Tiêu chí: ở trong kho > 2 tháng (60 ngày) VÀ nhiều hơn 10 sản phẩm
            if (now - created) > timedelta(days=60) and self.stock > 10:
                return "overstocked"

        return "normal"
