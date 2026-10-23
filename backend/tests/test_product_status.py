import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_product_status_default_and_filter():
    # 1. Test GET default (show_hidden=False)
    res = client.get("/api/v1/products?page=1&page_size=20")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    initial_active_total = data["data"]["total"]
    for item in data["data"]["items"]:
        assert item["status"] == "active"

    # Lấy sản phẩm đầu tiên để test toggle
    first_prod_id = data["data"]["items"][0]["id"]

    # 2. Test PATCH /api/v1/admin/products/{id}/toggle-status
    res_patch = client.patch(f"/api/v1/admin/products/{first_prod_id}/toggle-status")
    assert res_patch.status_code == 200
    patched_data = res_patch.json()["data"]
    assert patched_data["status"] == "hidden"

    # 3. Test GET default (show_hidden=False) -> sản phẩm vừa ẩn không còn xuất hiện
    res_after_hide = client.get("/api/v1/products?page=1&page_size=20")
    assert res_after_hide.status_code == 200
    after_data = res_after_hide.json()["data"]
    assert after_data["total"] == initial_active_total - 1
    active_ids = [p["id"] for p in after_data["items"]]
    assert first_prod_id not in active_ids

    # 4. Test GET show_hidden=true -> chỉ trả về sản phẩm bị ẩn và cấu trúc phân trang chuẩn
    res_hidden = client.get("/api/v1/products?show_hidden=true")
    assert res_hidden.status_code == 200
    hidden_data = res_hidden.json()["data"]
    assert hidden_data["total"] >= 1
    assert "items" in hidden_data
    assert "page" in hidden_data
    assert "page_size" in hidden_data
    assert "total_pages" in hidden_data
    hidden_items = hidden_data["items"]
    for p in hidden_items:
        assert p["status"] == "hidden"
    assert any(p["id"] == first_prod_id for p in hidden_items)

    # 5. Toggle lại về active
    res_patch_back = client.patch(f"/api/v1/admin/products/{first_prod_id}/toggle-status")
    assert res_patch_back.status_code == 200
    assert res_patch_back.json()["data"]["status"] == "active"

    # 6. Kiểm tra lại GET default -> sản phẩm đã quay lại danh sách active
    res_final = client.get("/api/v1/products?page=1&page_size=20")
    assert res_final.status_code == 200
    final_data = res_final.json()["data"]
    assert final_data["total"] == initial_active_total
    final_ids = [p["id"] for p in final_data["items"]]
    assert first_prod_id in final_ids


def test_toggle_status_alternate_route():
    # Kiểm tra cả route /api/v1/products/{id}/toggle-status
    res = client.get("/api/v1/products?page=1&page_size=1")
    prod_id = res.json()["data"]["items"][0]["id"]
    
    # Toggle to hidden
    res1 = client.patch(f"/api/v1/products/{prod_id}/toggle-status")
    assert res1.status_code == 200
    assert res1.json()["data"]["status"] == "hidden"
    
    # Toggle back to active
    res2 = client.patch(f"/api/v1/products/{prod_id}/toggle-status")
    assert res2.status_code == 200
    assert res2.json()["data"]["status"] == "active"


def test_create_product_default_status():
    import uuid
    # Đăng nhập lấy admin token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tzshop.vn", "password": "admin123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    
    unique_sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
    new_product_payload = {
        "category_id": 1,
        "name": "Sản phẩm test trạng thái",
        "sku": unique_sku,
        "price": 150000.0,
        "stock": 5,
        "is_featured": False,
        "description": "Mô tả sản phẩm test",
    }
    create_res = client.post(
        "/api/v1/products",
        json=new_product_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    created_product = create_res.json()["data"]
    assert created_product["status"] == "active"
