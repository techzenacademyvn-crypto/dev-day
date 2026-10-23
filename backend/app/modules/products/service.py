from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.core.exceptions import NotFoundException, BadRequestException
from app.modules.products.search import build_search_expressions


class ProductService:
    @staticmethod
    def get_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[ProductFilter] = None,
    ) -> Tuple[List[Product], int]:
        """Lấy danh sách sản phẩm có bộ lọc và tìm kiếm thông minh."""
        query = db.query(Product).filter(Product.deleted_at.is_(None))
        ranking_score = None

        if filters:
            if filters.category_id is not None:
                query = query.filter(Product.category_id == filters.category_id)
            if filters.search and filters.search.strip():
                search_filter, ranking_score = build_search_expressions(db, filters.search)
                if search_filter is not None:
                    query = query.filter(search_filter)
            if filters.is_featured is not None:
                query = query.filter(Product.is_featured == filters.is_featured)
            if filters.low_stock_threshold is not None:
                query = query.filter(Product.stock <= filters.low_stock_threshold)

            # Lọc theo tình trạng tồn kho:
            # - out_of_stock: stock == 0
            # - overstocked: lưu kho > 2 tháng (60 ngày) VÀ stock > 10
            # - normal: các trường hợp còn lại
            if filters.stock_status:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
                if filters.stock_status == "out_of_stock":
                    query = query.filter(Product.stock == 0)
                elif filters.stock_status == "overstocked":
                    query = query.filter(
                        and_(
                            Product.created_at <= cutoff_date,
                            Product.stock > 10,
                        )
                    )
                elif filters.stock_status == "normal":
                    query = query.filter(
                        and_(
                            Product.stock > 0,
                            or_(
                                Product.created_at > cutoff_date,
                                Product.stock <= 10,
                            ),
                        )
                    )

            if filters.sort_by == "price_asc":
                query = query.order_by(Product.price.asc(), Product.id.asc())
            elif filters.sort_by == "price_desc":
                query = query.order_by(Product.price.desc(), Product.id.asc())
            elif filters.sort_by == "stock_asc":
                query = query.order_by(Product.stock.asc(), Product.id.asc())
            elif filters.sort_by == "stock_desc":
                query = query.order_by(Product.stock.desc(), Product.id.asc())
            elif ranking_score is not None:
                query = query.order_by(ranking_score.desc(), Product.id.asc())
            else:
                query = query.order_by(Product.id.asc())
        else:
            query = query.order_by(Product.id.asc())

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
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
