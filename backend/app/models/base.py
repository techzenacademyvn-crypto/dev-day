from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class cho tất cả SQLAlchemy models trong TZ Shop."""
    pass


class TimestampMixin:
    """Mixin bổ sung thời gian tạo và cập nhật kèm múi giờ UTC."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin hỗ trợ xóa mềm (Soft Delete).
    Bản ghi đã xóa mềm có deleted_at khác NULL.
    Mặc định các truy vấn nghiệp vụ phải lọc bỏ bản ghi đã xóa.
    """
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
