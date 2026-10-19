from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryFilter
from app.core.exceptions import NotFoundException, BadRequestException


class CategoryService:
    @staticmethod
    def get_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[CategoryFilter] = None,
    ) -> Tuple[List[Category], int]:
        """Lấy danh sách danh mục có phân trang và bộ lọc (Đề mẫu MAU-01).
        Quy tắc sư phạm: Không bao giờ trả về danh mục đã xóa mềm (deleted_at IS NOT NULL).
        """
        query = db.query(Category).filter(Category.deleted_at.is_(None))

        # Áp dụng bộ lọc cờ đang hoạt động (Đề mẫu MAU-01)
        if filters and filters.is_active is not None:
            query = query.filter(Category.is_active == filters.is_active)
            
        if filters and filters.name is not None:
            query = query.filter(Category.name.ilike(f"%{filters.name}%"))

        total = query.count()
        items = query.order_by(Category.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category:
        category = (
            db.query(Category)
            .filter(Category.id == category_id, Category.deleted_at.is_(None))
            .first()
        )
        if not category:
            raise NotFoundException(f"Không tìm thấy danh mục có ID {category_id}")
        return category

    @staticmethod
    def create(db: Session, data: CategoryCreate) -> Category:
        existing = db.query(Category).filter(Category.slug == data.slug).first()
        if existing:
            raise BadRequestException(f"Đường dẫn slug '{data.slug}' đã tồn tại")

        category = Category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            is_active=data.is_active,
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category_id: int, data: CategoryUpdate) -> Category:
        category = CategoryService.get_by_id(db, category_id)

        if data.slug and data.slug != category.slug:
            existing = db.query(Category).filter(Category.slug == data.slug, Category.id != category_id).first()
            if existing:
                raise BadRequestException(f"Đường dẫn slug '{data.slug}' đã tồn tại")
            category.slug = data.slug

        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        if data.is_active is not None:
            category.is_active = data.is_active

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def soft_delete(db: Session, category_id: int) -> None:
        category = CategoryService.get_by_id(db, category_id)
        category.deleted_at = datetime.now(timezone.utc)
        category.is_active = False
        db.commit()
