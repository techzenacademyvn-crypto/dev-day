# VAI TRÒ
Bạn là kỹ sư full-stack senior, làm việc trên repo TZ Shop (backend FastAPI + SQLAlchemy + PostgreSQL, frontend Vue 3 + TypeScript + Vite). Bạn ưu tiên thay đổi nhỏ, đúng phạm vi, có test chứng minh.

# BỐI CẢNH
User story: "Là người quản lý kho, tôi muốn dễ dàng xem và tìm kiếm để quản lý sản phẩm."
Tiêu chí chấp nhận gốc: Có thể tìm kiếm theo tên và danh mục.

Hiện trạng (hãy tự đọc lại để xác nhận, không giả định):
- `backend/app/modules/products/router.py`: `GET /api/v1/products` đã nhận `search` và `category_id`, đóng gói vào `ProductFilter`.
- `backend/app/modules/products/service.py` → `ProductService.get_list`: đang BỎ QUA `filters`, luôn trả toàn bộ sản phẩm chưa xoá mềm.
- `frontend/src/views/admin/ProductsView.vue`: chỉ có bảng + phân trang, không có ô tìm kiếm/lọc; cột "Danh Mục" hiển thị `#category_id`.
- `GET /api/v1/categories` trả danh sách danh mục (có phân trang, `page_size` tối đa 100).
- Dữ liệu mẫu: `backend/scripts/seed.py` (8 danh mục, 40 sản phẩm). Test: `backend/tests/`.

# NHIỆM VỤ
1. Backend: làm cho `ProductService.get_list` áp dụng `search` và `category_id`.
2. Frontend: thêm thanh tìm kiếm theo tên + bộ lọc danh mục vào trang quản lý sản phẩm, và hiển thị tên danh mục thay cho `#id`.
3. Viết test tự động cho phần backend.

# TIÊU CHÍ CHẤP NHẬN CHI TIẾT (phải đạt toàn bộ)
Backend:
- AC1. `search` khớp một phần tên, không phân biệt hoa/thường (ILIKE `%từ khoá%`). Khoảng trắng đầu/cuối được bỏ qua; chuỗi rỗng = không lọc.
- AC2. `category_id` trả về đúng sản phẩm thuộc danh mục đó.
- AC3. Dùng cả hai cùng lúc → kết hợp AND.
- AC4. `total` và `total_pages` phản ánh kết quả SAU khi lọc (đếm sau filter, trước offset/limit).
- AC5. Không có kết quả hoặc `category_id` không tồn tại → HTTP 200, `items: []`, `total: 0` (không trả 404).
- AC6. Sản phẩm đã xoá mềm (`deleted_at` khác null) không bao giờ xuất hiện.
- AC7. Ký tự `%` và `_` trong từ khoá được hiểu theo nghĩa đen (escape), không phải wildcard.

Frontend (`ProductsView.vue`):
- AC8. Có ô nhập "Tìm theo tên sản phẩm", gọi API có debounce ~300ms.
- AC9. Có dropdown danh mục, nạp từ `GET /categories`, có lựa chọn mặc định "Tất cả danh mục".
- AC10. Đổi từ khoá hoặc danh mục → quay về trang 1; chuyển trang giữ nguyên bộ lọc.
- AC11. Không có kết quả → hiển thị "Không tìm thấy sản phẩm phù hợp" trong bảng.
- AC12. Có nút "Xoá bộ lọc" đưa về trạng thái ban đầu.
- AC13. Cột "Danh Mục" hiển thị tên danh mục (map từ danh sách đã nạp), fallback `#id` nếu không tìm thấy.

# RÀNG BUỘC / NGOÀI PHẠM VI
- KHÔNG đổi chữ ký API, schema DB, migration, hay response format `ApiResponse`/`PageResponse`.
- KHÔNG cài thêm thư viện (debounce tự viết bằng `setTimeout`).
- KHÔNG xử lý `low_stock_threshold`, `is_featured`, `sort_by`, trang cửa hàng `StoreCatalogView`; không làm tìm kiếm bỏ dấu tiếng Việt.
- Giữ nguyên style code hiện có (staticmethod trong service, `<script setup lang="ts">`, CSS scoped cùng tông màu).
- 6 test hiện có phải vẫn pass.

# CÁCH LÀM
1. Đọc các file liên quan ở mục Bối cảnh, xác nhận hiện trạng. Nếu khác mô tả, nêu rõ và điều chỉnh kế hoạch.
2. Nêu kế hoạch ngắn (≤ 6 gạch đầu dòng) rồi mới sửa code.
3. Sửa backend → viết test → chạy `.\.venv\Scripts\pytest.exe` trong `backend/`.
4. Sửa frontend → chạy `npm run build` trong `frontend/` để kiểm tra lỗi type.
5. Nếu gặp điểm mơ hồ không có trong prompt: chọn phương án đơn giản nhất phù hợp AC và ghi vào mục "Giả định".

# YÊU CẦU TEST (thêm vào `backend/tests/`, dựa trên dữ liệu thật trong `seed.py`, không đoán)
- Tìm theo một phần tên, viết khác hoa/thường → đúng sản phẩm.
- Lọc theo `category_id` → mọi item có đúng `category_id`, `total` đúng số lượng seed.
- Kết hợp `search` + `category_id`.
- Từ khoá không tồn tại → `total == 0`, `items == []`.
- `category_id` không tồn tại → 200, rỗng.

# ĐỊNH DẠNG KẾT QUẢ TRẢ VỀ
1. Danh sách file đã sửa/thêm, mỗi file 1 dòng mô tả.
2. Bảng đối chiếu AC1–AC13: Đạt / Chưa đạt + bằng chứng (tên test hoặc bước kiểm tra tay).
3. Output rút gọn của `pytest` và `npm run build`.
4. Hướng dẫn kiểm tra tay trên UI (3–5 bước, có ví dụ từ khoá lấy từ seed).
5. Giả định đã đưa ra và rủi ro còn lại (nếu có).
