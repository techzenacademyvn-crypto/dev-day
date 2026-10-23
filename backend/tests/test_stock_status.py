"""Test logic xác định tình trạng tồn kho theo đúng tiêu chí nghiệp vụ US1.
- Hết hàng: stock == 0
- Tồn kho (> 2 tháng): lưu kho > 60 ngày VÀ stock > 10
- Bình thường: các trường hợp còn lại
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.models.product import Product
from app.schemas.product import ProductFilter, ProductResponse


def test_stock_status_out_of_stock():
    prod = Product(
        name="Pin sạc",
        sku="PRD-TEST-01",
        price=Decimal("10.00"),
        stock=0,
        category_id=1,
        created_at=datetime.now(timezone.utc) - timedelta(days=90),
    )
    assert prod.stock_status == "out_of_stock"


def test_stock_status_overstocked():
    # Ở trong kho > 2 tháng (khoảng 60 ngày) và có nhiều hơn 10 sản phẩm
    prod = Product(
        name="Bàn phím cơ",
        sku="PRD-TEST-02",
        price=Decimal("50.00"),
        stock=15,  # > 10 sản phẩm
        category_id=1,
        created_at=datetime.now(timezone.utc) - timedelta(days=65),  # > 60 ngày
    )
    assert prod.stock_status == "overstocked"
    assert prod.days_in_stock >= 65


def test_stock_status_normal_when_recent_created():
    # Tồn kho nhiều nhưng mới nhập (< 60 ngày) -> Bình thường
    prod = Product(
        name="Chuột gaming",
        sku="PRD-TEST-03",
        price=Decimal("25.00"),
        stock=50,
        category_id=1,
        created_at=datetime.now(timezone.utc) - timedelta(days=15),
    )
    assert prod.stock_status == "normal"


def test_stock_status_normal_when_exact_ten_or_less():
    # Ở kho > 2 tháng nhưng stock <= 10 -> Không thuộc nhóm tồn kho lâu ngày
    prod = Product(
        name="Tai nghe",
        sku="PRD-TEST-04",
        price=Decimal("30.00"),
        stock=10,  # <= 10 sản phẩm
        category_id=1,
        created_at=datetime.now(timezone.utc) - timedelta(days=70),
    )
    assert prod.stock_status == "normal"


def test_product_filter_schema_accepts_stock_status():
    f = ProductFilter(stock_status="overstocked")
    assert f.stock_status == "overstocked"

    f2 = ProductFilter()
    assert f2.stock_status is None
