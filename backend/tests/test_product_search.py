import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_accent_insensitive_search():
    """1. Tìm không phân biệt hoa/thường và dấu tiếng Việt (ao -> áo, chuot -> chuột, đ -> d)."""
    # Tìm 'ao' -> ra các sản phẩm áo
    res_ao = client.get("/api/v1/products?search=ao")
    assert res_ao.status_code == 200
    data_ao = res_ao.json()["data"]
    assert data_ao["total"] > 0
    names_ao = [p["name"] for p in data_ao["items"]]
    assert any("Áo Polo" in name for name in names_ao)
    assert any("Áo khoác" in name for name in names_ao)

    # Tìm chữ hoa 'ÁO' -> kết quả giống hệt 'ao'
    res_upper = client.get("/api/v1/products?search=%C3%81O")  # 'ÁO'
    assert res_upper.status_code == 200
    assert res_upper.json()["data"]["total"] == data_ao["total"]

    # Tìm 'chuot' -> ra chuột
    res_chuot = client.get("/api/v1/products?search=chuot")
    assert res_chuot.status_code == 200
    data_chuot = res_chuot.json()["data"]
    assert data_chuot["total"] >= 1
    assert any("Chuột" in p["name"] for p in data_chuot["items"])

    # Tìm 'dam' (d -> đ) -> ra Đầm suông
    res_dam = client.get("/api/v1/products?search=dam")
    assert res_dam.status_code == 200
    data_dam = res_dam.json()["data"]
    assert any("Đầm" in p["name"] for p in data_dam["items"])


def test_spaceless_compound_search():
    """1b. Tìm chuỗi viết liền không dấu / không khoảng trắng (tainghe, tainghebluetooth, TAINGHE)."""
    # 'tainghe' phải tìm được 'Tai nghe không dây Bluetooth True Wireless TZ-Pod'
    res_tn = client.get("/api/v1/products?search=tainghe")
    assert res_tn.status_code == 200
    names_tn = [p["name"] for p in res_tn.json()["data"]["items"]]
    assert any("Tai nghe" in name for name in names_tn)

    # 'TAINGHE' viết hoa viết liền
    res_tn_upper = client.get("/api/v1/products?search=TAINGHE")
    assert res_tn_upper.status_code == 200
    assert any("Tai nghe" in p["name"] for p in res_tn_upper.json()["data"]["items"])

    # 'tai nghe' có khoảng trắng
    res_tn_space = client.get("/api/v1/products?search=tai+nghe")
    assert res_tn_space.status_code == 200
    assert any("Tai nghe" in p["name"] for p in res_tn_space.json()["data"]["items"])

    # 'tainghebluetooth' viết liền hai cụm từ
    res_tn_bt = client.get("/api/v1/products?search=tainghebluetooth")
    assert res_tn_bt.status_code == 200
    names_bt = [p["name"] for p in res_tn_bt.json()["data"]["items"]]
    assert any("Tai nghe" in name and "Bluetooth" in name for name in names_bt)

    # Các từ ghép khác
    res_bp = client.get("/api/v1/products?search=banphim")
    assert res_bp.status_code == 200
    assert any("Bàn phím" in p["name"] for p in res_bp.json()["data"]["items"])

    res_ap = client.get("/api/v1/products?search=aopolo")
    assert res_ap.status_code == 200
    assert any("Áo Polo" in p["name"] for p in res_ap.json()["data"]["items"])


def test_multi_word_unordered_search():
    """2. Tìm một phần tên và nhiều từ không cần đúng thứ tự ('ao nam' == 'nam ao')."""
    res1 = client.get("/api/v1/products?search=ao+nam")
    assert res1.status_code == 200
    items1 = [p["id"] for p in res1.json()["data"]["items"]]

    res2 = client.get("/api/v1/products?search=nam+ao")
    assert res2.status_code == 200
    items2 = [p["id"] for p in res2.json()["data"]["items"]]

    assert len(items1) > 0
    # Cả hai thứ tự phải trả về tập sản phẩm giống nhau
    assert set(items1) == set(items2)
    # Phải chứa Áo Polo nam hoặc Áo khoác gió nam
    names = [p["name"] for p in res1.json()["data"]["items"]]
    assert any("Áo Polo nam" in n for n in names)


def test_synonym_search():
    """3. Tìm từ đồng nghĩa có kiểm soát (keyboard ↔ bàn phím, mouse ↔ chuột)."""
    # Tìm 'keyboard' phải ra Bàn phím cơ
    res_kb = client.get("/api/v1/products?search=keyboard")
    assert res_kb.status_code == 200
    names_kb = [p["name"] for p in res_kb.json()["data"]["items"]]
    assert any("Bàn phím" in n for n in names_kb)

    # Tìm 'mouse' phải ra Chuột công thái học
    res_m = client.get("/api/v1/products?search=mouse")
    assert res_m.status_code == 200
    names_m = [p["name"] for p in res_m.json()["data"]["items"]]
    assert any("Chuột" in n for n in names_m)

    # Tìm 'chuot khong day' phải ra Chuột Wireless và bảo toàn mọi điều kiện (AND logic)
    res_kd = client.get("/api/v1/products?search=chuot+khong+day")
    assert res_kd.status_code == 200
    data_kd = res_kd.json()["data"]
    assert data_kd["total"] >= 1
    assert any("Chuột" in p["name"] and "Wireless" in p["name"] for p in data_kd["items"])


def test_category_recognition():
    """4. Nhận diện từ khóa nhóm ngành hàng ('thoi trang', 'dien tu') dựa trên danh mục thật."""
    res_tt = client.get("/api/v1/products?search=thoi+trang")
    assert res_tt.status_code == 200
    data_tt = res_tt.json()["data"]
    assert data_tt["total"] > 0
    # Sản phẩm trả về phải thuộc danh mục thời trang (Thời trang Nam hoặc Nữ)
    cat_ids = {p["category_id"] for p in data_tt["items"]}
    assert cat_ids.issubset({3, 4})

    res_dt = client.get("/api/v1/products?search=dien+tu")
    assert res_dt.status_code == 200
    data_dt = res_dt.json()["data"]
    assert data_dt["total"] > 0
    cat_ids_dt = {p["category_id"] for p in data_dt["items"]}
    assert 1 in cat_ids_dt  # ID danh mục Điện tử & Công nghệ


def test_no_overexpansion():
    """5. Không mở rộng quá mức: tìm 'ao' không trả tất cả sản phẩm thời trang; tìm 'chuot' không trả tất cả điện tử."""
    # Tìm 'ao' chỉ trả sản phẩm áo, KHÔNG được chứa Quần Tây, Quần Short, Đầm, hay các từ chứa 'cao'
    res_ao = client.get("/api/v1/products?search=ao")
    assert res_ao.status_code == 200
    items_ao = res_ao.json()["data"]["items"]
    names_ao = [p["name"] for p in items_ao]
    assert not any("Quần Tây" in n for n in names_ao)
    assert not any("Quần Short" in n for n in names_ao)
    assert not any("Đầm suông" in n for n in names_ao)
    assert not any("đỉnh cao" in n for n in names_ao)
    assert not any("dã ngoại" in n for n in names_ao)

    # Tìm 'chuot' chỉ trả chuột, KHÔNG trả về Bàn phím hay Củ sạc hay Tai nghe
    res_chuot = client.get("/api/v1/products?search=chuot")
    assert res_chuot.status_code == 200
    names_chuot = [p["name"] for p in res_chuot.json()["data"]["items"]]
    assert all("Chuột" in n for n in names_chuot)
    assert not any("Bàn phím" in n for n in names_chuot)
    assert not any("Củ sạc" in n for n in names_chuot)


def test_ranking_priority():
    """6. Xếp hạng: Khớp tên chính xác -> Khớp cụm từ -> Khớp các từ -> Từ đồng nghĩa -> Viết liền -> Danh mục."""
    res = client.get("/api/v1/products?search=ban+phim")
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    assert len(items) > 0
    # Sản phẩm 'Bàn phím cơ cơ học RGB Blue Switch' phải đứng đầu
    assert "Bàn phím" in items[0]["name"]


def test_combined_with_category_id():
    """7. Kết hợp category_id bằng AND, không bỏ qua danh mục người dùng chọn."""
    # Tìm 'ao' trong danh mục Thời trang Nam (category_id = 3) -> có kết quả
    res1 = client.get("/api/v1/products?search=ao&category_id=3")
    assert res1.status_code == 200
    data1 = res1.json()["data"]
    assert data1["total"] > 0
    assert all(p["category_id"] == 3 for p in data1["items"])

    # Tìm 'ao' nhưng lọc vào danh mục Điện tử (category_id = 1) -> 0 kết quả
    res2 = client.get("/api/v1/products?search=ao&category_id=1")
    assert res2.status_code == 200
    data2 = res2.json()["data"]
    assert data2["total"] == 0
    assert len(data2["items"]) == 0


def test_empty_keyword_behavior():
    """Kiểm tra khi từ khóa rỗng: hiển thị lại toàn bộ sản phẩm hoặc danh mục đang chọn."""
    # Keyword rỗng + category_id = 3 -> trả đúng 5 sản phẩm của category 3
    res_cat = client.get("/api/v1/products?search=&category_id=3")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()["data"]
    assert data_cat["total"] == 5
    assert all(p["category_id"] == 3 for p in data_cat["items"])

    # Keyword rỗng + Tất cả danh mục -> trả về đầy đủ 40 sản phẩm
    res_all = client.get("/api/v1/products?search=")
    assert res_all.status_code == 200
    assert res_all.json()["data"]["total"] == 40


def test_pagination_and_total_accuracy():
    """8. Lọc và xếp hạng tại database trước khi phân trang; total phải chính xác."""
    res = client.get("/api/v1/products?search=ao&page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    assert data["total"] > 2
    assert data["total_pages"] >= 2


def test_safe_special_characters():
    """9. Chuẩn hóa khoảng trắng, xử lý an toàn %, _, \\, không crash SQL."""
    special_queries = ["%", "_", "'", "\\", "   ao   nam   ", "ao [nam]", "ao (polo)"]
    for q in special_queries:
        res = client.get(f"/api/v1/products?search={q}")
        assert res.status_code == 200
        assert res.json()["success"] is True
