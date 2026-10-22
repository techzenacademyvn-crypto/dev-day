# VAI TRÒ
Bạn là kỹ sư full-stack senior trên repo TZ Shop (backend FastAPI + PostgreSQL, frontend Vue 3 + TypeScript). Ưu tiên thay đổi nhỏ, đúng phạm vi, có test chứng minh.

# YÊU CẦU
User story: "Là người quản lý kho, tôi muốn dễ dàng xem và tìm kiếm để quản lý sản phẩm."
Tiêu chí chấp nhận gốc: Có thể tìm kiếm theo tên và danh mục.

File liên quan (tự đọc để nắm hiện trạng, không giả định):
- Backend: `backend/app/modules/products/` (router, service), `backend/app/schemas/product.py`
- Backend danh mục: `backend/app/modules/categories/` (API danh sách đã có tìm theo tên nhưng chưa theo đủ quy tắc AC1, AC6)
- Frontend: `frontend/src/views/admin/ProductsView.vue`
- Dữ liệu mẫu: `backend/scripts/seed.py`

# TIÊU CHÍ CHẤP NHẬN CHI TIẾT

## Bắt buộc (từ tiêu chí gốc)
Khi gọi API danh sách sản phẩm:
- AC1. Tìm theo tên: khớp một phần, không phân biệt hoa/thường, bỏ qua khoảng trắng đầu/cuối; từ khoá rỗng = không lọc.
- AC2. Lọc theo danh mục: chỉ trả sản phẩm thuộc danh mục đã chọn.
- AC3. Dùng cả hai cùng lúc: sản phẩm phải thoả cả hai điều kiện.
- AC4. Tổng số sản phẩm và số trang phản ánh kết quả sau khi lọc.
- AC5. Không có kết quả, hoặc danh mục không tồn tại: trả danh sách rỗng, không báo lỗi.
- AC6. Ký tự đặc biệt trong từ khoá (`%`, `_`) được tìm đúng như ký tự, không làm sai kết quả.
- AC7. Sản phẩm đã xoá không bao giờ xuất hiện.

Trên trang quản lý sản phẩm:
- AC8. Có ô tìm kiếm theo tên và dropdown chọn danh mục (có lựa chọn "Tất cả danh mục").
- AC9. Đổi bộ lọc thì quay về trang 1; chuyển trang thì giữ nguyên bộ lọc.
- AC10. Ô chọn danh mục cho phép gõ để tìm danh mục theo tên, áp dụng cùng quy tắc tìm kiếm như AC1 và AC6 (cả ở API danh mục), vẫn dùng được khi có hàng trăm danh mục — không chỉ tìm trong những danh mục đã tải về. Không có danh mục khớp thì báo "Không tìm thấy danh mục".

## Nên có (cải thiện trải nghiệm, ngoài tiêu chí gốc)
- AC11. Cột danh mục hiển thị tên thay cho mã số.
- AC12. Gõ từ khoá (sản phẩm hoặc danh mục) không gọi API liên tục theo từng phím.
- AC13. Không có kết quả thì hiển thị thông báo "Không tìm thấy sản phẩm phù hợp".
- AC14. Có nút "Xoá bộ lọc".

# RÀNG BUỘC
- Không đổi chữ ký API, schema DB, format response.
- Không sửa vùng cấm: `frontend/src/lib/api.ts`, `frontend/src/types/index.ts`.
- Không cài thêm thư viện; giữ style code của file đang sửa.
- Toàn bộ test hiện có phải vẫn pass.

# NGOÀI PHẠM VI
Lọc tồn kho thấp, lọc nổi bật, sắp xếp, trang cửa hàng `StoreCatalogView`, tìm kiếm bỏ dấu tiếng Việt.

# CÁCH LÀM
1. Đọc code, chạy test hiện có để lấy kết quả gốc, nêu kế hoạch ngắn (≤ 6 gạch đầu dòng).
2. Backend → test → frontend → `npm run build`.
3. Mỗi AC backend có ít nhất 1 test tự động trong `backend/tests/`, giá trị mong đợi lấy từ `seed.py`.
4. Gặp điểm mơ hồ: chọn phương án đơn giản nhất phù hợp AC, ghi vào "Giả định".

# ĐỊNH DẠNG KẾT QUẢ
1. File đã sửa/thêm, mỗi file 1 dòng.
2. Bảng đối chiếu AC1–AC14 (tách Bắt buộc / Nên có): Đạt / Chưa đạt + bằng chứng. Ghi rõ AC nào chưa kiểm tay.
3. Output rút gọn của test (trước và sau) và build.
4. 3–5 bước kiểm tra tay trên UI, ví dụ lấy từ seed.
5. Giả định và rủi ro còn lại.
