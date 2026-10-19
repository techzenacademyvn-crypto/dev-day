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
    # Test đề mẫu MAU-01
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
