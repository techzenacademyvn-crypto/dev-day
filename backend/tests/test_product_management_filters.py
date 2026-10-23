from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.base import Base
from app.models.product import Product
from app.modules.products.search import escape_like_pattern
from app.modules.products.service import ProductService
from app.schemas.product import ProductFilter


client = TestClient(app)


def items_for(params: dict):
    response = client.get("/api/v1/products", params={"page_size": 100, **params})
    assert response.status_code == 200
    return response.json()["data"]["items"]


def test_search_by_sku_is_supported():
    items = items_for({"search": "PRD-001"})
    assert any(item["sku"] == "PRD-001" for item in items)


def test_sku_like_special_characters_are_escaped():
    assert escape_like_pattern(r"SKU_100%\\") == r"SKU\_100\%\\"


def test_usd_price_range_filters_before_response():
    items = items_for({"min_price": "20.00", "max_price": "50.00"})
    assert items
    assert all(Decimal("20.00") <= Decimal(str(item["price"])) <= Decimal("50.00") for item in items)


def test_invalid_price_range_is_rejected():
    response = client.get("/api/v1/products", params={"min_price": "50.00", "max_price": "20.00"})
    assert response.status_code == 422


def test_new_stock_statuses_follow_the_documented_rules():
    for status in ("in_stock", "out_of_stock", "low_stock", "aged_stock"):
        for item in items_for({"stock_status": status}):
            if status == "in_stock":
                assert item["stock"] > 0
            elif status == "out_of_stock":
                assert item["stock"] == 0
            elif status == "low_stock":
                assert 1 <= item["stock"] < 10
            else:
                assert item["stock"] >= 10


@pytest.fixture
def isolated_product_db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_aged_stock_requires_stock_and_timezone_aware_age(isolated_product_db):
    now = datetime.now(timezone.utc)
    products = [
        Product(name="Đạt tuổi", sku="AGED-OK", price=Decimal("10.00"), stock=10, category_id=1, created_at=now - timedelta(days=21)),
        Product(name="Thiếu tồn", sku="AGED-LOW", price=Decimal("10.00"), stock=9, category_id=1, created_at=now - timedelta(days=21)),
        Product(name="Còn mới", sku="AGED-RECENT", price=Decimal("10.00"), stock=10, category_id=1, created_at=now - timedelta(days=19)),
        Product(name="Đúng biên", sku="AGED-BOUNDARY", price=Decimal("10.00"), stock=10, category_id=1, created_at=now - timedelta(days=20)),
    ]
    isolated_product_db.add_all(products)
    isolated_product_db.commit()

    items, total = ProductService.get_list(
        isolated_product_db,
        page_size=20,
        filters=ProductFilter(stock_status="aged_stock"),
    )

    assert total == 2
    assert {item.sku for item in items} == {"AGED-OK", "AGED-BOUNDARY"}


def test_new_sorts_are_stable_by_id_when_primary_values_match():
    items = items_for({"sort_by": "created_desc"})
    values = [(item["created_at"], item["id"]) for item in items]
    assert values == sorted(values, key=lambda value: (value[0], -value[1]), reverse=True)

    items = items_for({"sort_by": "featured_first"})
    featured = [item["is_featured"] for item in items]
    assert featured == sorted(featured, reverse=True)
