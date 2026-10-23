import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_admin_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tzshop.vn", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["role"] == "ADMIN"


def test_staff_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "staff@tzshop.vn", "password": "staff123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["user"]["role"] == "STAFF"


def test_list_categories():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 8


def test_mau_01_filter_active_categories():
    # Lọc danh mục đang hoạt động
    response = client.get("/api/v1/categories?is_active=true")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for cat in data["data"]["items"]:
        assert cat["is_active"] is True


def test_list_products():
    response = client.get("/api/v1/products?page=1&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] == 40
    assert len(data["data"]["items"]) == 20


def test_search_products_by_partial_name():
    # Tìm kiếm theo một phần tên sản phẩm (không phân biệt hoa thường)
    response = client.get("/api/v1/products?search=tai%20nghe")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] > 0
    for item in data["data"]["items"]:
        assert "tai nghe" in item["name"].lower()


def test_filter_products_by_category():
    # Lọc sản phẩm theo category_id
    response = client.get("/api/v1/products?category_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 5
    for item in data["data"]["items"]:
        assert item["category_id"] == 1


def test_search_and_filter_products_combined():
    # Kết hợp vừa tìm kiếm theo tên vừa lọc theo danh mục
    response = client.get("/api/v1/products?search=tai%20nghe&category_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for item in data["data"]["items"]:
        assert "tai nghe" in item["name"].lower()
        assert item["category_id"] == 1


def test_search_products_no_result():
    # Tìm kiếm với từ khóa không tồn tại
    response = client.get("/api/v1/products?search=san_pham_khong_he_ton_tai_123456")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 0
    assert len(data["data"]["items"]) == 0

