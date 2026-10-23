import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_sort_by_stock_asc():
    """Kiểm tra sắp xếp tồn kho ít nhất: 2 sản phẩm tồn kho = 0 (PRD-005, PRD-015) phải đứng đầu."""
    response = client.get("/api/v1/products?sort_by=stock_asc&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    items = data["data"]["items"]
    assert len(items) == 20
    assert items[0]["stock"] == 0
    assert items[1]["stock"] == 0
    assert {items[0]["sku"], items[1]["sku"]} == {"PRD-005", "PRD-015"}


def test_sort_by_stock_desc():
    """Kiểm tra sắp xếp tồn kho nhiều nhất trước."""
    response = client.get("/api/v1/products?sort_by=stock_desc&page_size=20")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    stocks = [item["stock"] for item in items]
    assert stocks == sorted(stocks, reverse=True)


def test_sort_by_price_asc():
    """Kiểm tra sắp xếp giá thấp đến cao."""
    response = client.get("/api/v1/products?sort_by=price_asc&page_size=20")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    prices = [float(item["price"]) for item in items]
    assert prices == sorted(prices)


def test_sort_by_price_desc():
    """Kiểm tra sắp xếp giá cao đến thấp."""
    response = client.get("/api/v1/products?sort_by=price_desc&page_size=20")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    prices = [float(item["price"]) for item in items]
    assert prices == sorted(prices, reverse=True)


def test_sort_by_category():
    """Kiểm tra gom nhóm theo danh mục."""
    response = client.get("/api/v1/products?sort_by=category&page_size=20")
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    cat_ids = [item["category_id"] for item in items]
    assert cat_ids == sorted(cat_ids)
