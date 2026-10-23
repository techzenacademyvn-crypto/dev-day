import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_admin_token() -> str:
    """Đăng nhập với quyền Admin để lấy JWT token."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tzshop.vn", "password": "admin123"},
    )
    assert res.status_code == 200
    return res.json()["data"]["access_token"]


def test_list_products_contains_valid_stock_fields():
    """Kiểm tra danh sách sản phẩm trả về có trường stock hợp lệ (số nguyên >= 0)."""
    res = client.get("/api/v1/products?page=1&page_size=20")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    items = data["data"]["items"]
    assert len(items) > 0

    for item in items:
        assert "stock" in item
        assert isinstance(item["stock"], int)
        assert item["stock"] >= 0


def test_update_product_stock_lifecycle():
    """Kiểm tra cập nhật tồn kho: 0 (Hết hàng), 1 (Còn hàng), > 1 (Còn hàng).
    AC01, AC02, AC03 lifecycle test.
    """
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Lấy sản phẩm đầu tiên
    list_res = client.get("/api/v1/products?page=1&page_size=1")
    assert list_res.status_code == 200
    prod = list_res.json()["data"]["items"][0]
    prod_id = prod["id"]
    original_stock = prod["stock"]

    try:
        # 2. Cập nhật stock = 0 (AC02 - Hết hàng)
        res_zero = client.put(
            f"/api/v1/products/{prod_id}",
            json={"stock": 0},
            headers=headers,
        )
        assert res_zero.status_code == 200
        data_zero = res_zero.json()
        assert data_zero["success"] is True
        assert data_zero["data"]["stock"] == 0

        # Kiểm tra qua GET lại sản phẩm đó
        get_zero = client.get(f"/api/v1/products/{prod_id}")
        assert get_zero.status_code == 200
        assert get_zero.json()["data"]["stock"] == 0

        # 3. Cập nhật stock = 1 (AC01 - Còn hàng với quantity = 1)
        res_one = client.put(
            f"/api/v1/products/{prod_id}",
            json={"stock": 1},
            headers=headers,
        )
        assert res_one.status_code == 200
        assert res_one.json()["data"]["stock"] == 1

        # 4. Cập nhật stock = 42 (AC01 - Còn hàng với quantity > 1)
        res_many = client.put(
            f"/api/v1/products/{prod_id}",
            json={"stock": 42},
            headers=headers,
        )
        assert res_many.status_code == 200
        assert res_many.json()["data"]["stock"] == 42

    finally:
        # Khôi phục tồn kho ban đầu để giữ toàn vẹn dữ liệu
        client.put(
            f"/api/v1/products/{prod_id}",
            json={"stock": original_stock},
            headers=headers,
        )


def test_reject_negative_stock_update():
    """Kiểm tra Backend từ chối cập nhật số lượng tồn kho âm (< 0).
    Tuân thủ quy tắc: 'quantity < 0: Xem là dữ liệu bất thường, không âm thầm chuyển thành 0'.
    """
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Lấy sản phẩm đầu tiên
    list_res = client.get("/api/v1/products?page=1&page_size=1")
    prod = list_res.json()["data"]["items"][0]
    prod_id = prod["id"]
    initial_stock = prod["stock"]

    # Thử gửi stock âm: -5
    res_neg = client.put(
        f"/api/v1/products/{prod_id}",
        json={"stock": -5},
        headers=headers,
    )
    # FastAPI / Pydantic validation (ge=0) phải trả về 422 Unprocessable Entity
    assert res_neg.status_code == 422

    # Đảm bảo dữ liệu tồn kho trong DB không bị thay đổi thành số âm
    check_res = client.get(f"/api/v1/products/{prod_id}")
    assert check_res.json()["data"]["stock"] == initial_stock


def test_reject_invalid_stock_type():
    """Kiểm tra Backend từ chối cập nhật dữ liệu tồn kho không hợp lệ (chuỗi không phải số)."""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    list_res = client.get("/api/v1/products?page=1&page_size=1")
    prod_id = list_res.json()["data"]["items"][0]["id"]

    res_invalid = client.put(
        f"/api/v1/products/{prod_id}",
        json={"stock": "khong_phai_so"},
        headers=headers,
    )
    assert res_invalid.status_code == 422
