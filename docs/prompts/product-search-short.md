Dùng skill implement-user-story để triển khai:

**User story:** Là người quản lý kho, tôi muốn dễ dàng xem và tìm kiếm để quản lý sản phẩm.

**Tiêu chí chấp nhận:**
- Có thể tìm kiếm theo tên và danh mục, trên cả API danh sách sản phẩm và trang quản lý sản phẩm.
- Ô chọn danh mục cho phép gõ để tìm danh mục theo tên (cùng quy tắc tìm kiếm như sản phẩm, áp dụng cả ở API danh mục), vẫn dùng được khi có hàng trăm danh mục (không chỉ tìm trong những danh mục đã tải về).

**Nên có:** Cột danh mục trên trang quản lý hiển thị tên thay cho mã số.

**File liên quan:** `backend/app/modules/products/`, `backend/app/modules/categories/` (API đã có tìm theo tên nhưng chưa đủ quy tắc), `frontend/src/views/admin/ProductsView.vue`.

**Ngoài phạm vi:** Lọc tồn kho thấp, lọc nổi bật, sắp xếp, trang cửa hàng `StoreCatalogView`, tìm kiếm bỏ dấu tiếng Việt.
