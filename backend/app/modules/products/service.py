from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.core.exceptions import NotFoundException, BadRequestException, AppException
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
            # Lọc theo danh mục đã chọn (kết hợp bằng AND)
            if filters.category_id is not None:
                query = query.filter(Product.category_id == filters.category_id)

            # Lọc sản phẩm nổi bật
            if filters.is_featured is not None:
                query = query.filter(Product.is_featured == filters.is_featured)

            # Lọc tồn kho thấp
            if filters.low_stock_threshold is not None:
                query = query.filter(Product.stock <= filters.low_stock_threshold)

            # Tìm kiếm thông minh (Smart Search)
            if filters.search and filters.search.strip():
                search_filter, ranking_score = build_search_expressions(db, filters.search)
                if search_filter is not None:
                    query = query.filter(search_filter)

        total = query.count()

        # Sắp xếp: ưu tiên theo sort_by nếu có, tiếp theo là ranking_score, cuối cùng là id
        if filters and filters.sort_by == "price_asc":
            query = query.order_by(Product.price.asc(), Product.id.asc())
        elif filters and filters.sort_by == "price_desc":
            query = query.order_by(Product.price.desc(), Product.id.asc())
        elif filters and filters.sort_by == "stock_asc":
            query = query.order_by(Product.stock.asc(), Product.id.asc())
        elif filters and filters.sort_by == "stock_desc":
            query = query.order_by(Product.stock.desc(), Product.id.asc())
        elif ranking_score is not None:
            query = query.order_by(ranking_score.desc(), Product.id.asc())
        else:
            query = query.order_by(Product.id.asc())

        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def get_featured_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        is_featured: Optional[bool] = None,
    ) -> Tuple[List[Product], int]:
        """Lấy danh sách sản phẩm theo sản phẩm nổi bật với phân trang."""
        try:
            query = db.query(Product).filter(Product.deleted_at.is_(None))

            if is_featured is not None:
                query = query.filter(Product.is_featured == is_featured)

            total = query.count()
            items = (
                query.order_by(Product.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return items, total
        except AppException:
            raise
        except SQLAlchemyError as exc:
            raise AppException(
                message="Lỗi truy vấn cơ sở dữ liệu khi lấy danh sách sản phẩm nổi bật",
                status_code=500,
                details=str(exc),
            )
        except Exception as exc:
            raise AppException(
                message="Đã xảy ra lỗi không xác định khi lấy danh sách sản phẩm nổi bật",
                status_code=500,
                details=str(exc),
            )

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
