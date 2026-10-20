from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.core.exceptions import NotFoundException, BadRequestException


class ProductService:
    @staticmethod
    def get_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[ProductFilter] = None,
    ) -> Tuple[List[Product], int]:
        """Lấy danh sách sản phẩm, 20 sản phẩm mỗi trang."""
        query = db.query(Product).filter(Product.deleted_at.is_(None))

        total = query.count()
        items = query.order_by(Product.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product:
        product = (
            db.query(Product)
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .first()
        )
        if not product:
            raise NotFoundException(f"Không tìm thấy sản phẩm có ID {product_id}")
        return product

    @staticmethod
    def create(db: Session, data: ProductCreate) -> Product:
        existing = db.query(Product).filter(Product.sku == data.sku).first()
        if existing:
            raise BadRequestException(f"Mã SKU '{data.sku}' đã tồn tại trong hệ thống")

        product = Product(
            category_id=data.category_id,
            name=data.name,
            sku=data.sku,
            price=data.price,
            stock=data.stock,
            is_featured=data.is_featured,
            image_url=data.image_url,
            description=data.description,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update(db: Session, product_id: int, data: ProductUpdate) -> Product:
        product = ProductService.get_by_id(db, product_id)

        if data.sku and data.sku != product.sku:
            existing = db.query(Product).filter(Product.sku == data.sku, Product.id != product_id).first()
            if existing:
                raise BadRequestException(f"Mã SKU '{data.sku}' đã tồn tại trong hệ thống")
            product.sku = data.sku

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def soft_delete(db: Session, product_id: int) -> None:
        product = ProductService.get_by_id(db, product_id)
        product.deleted_at = datetime.now(timezone.utc)
        db.commit()
