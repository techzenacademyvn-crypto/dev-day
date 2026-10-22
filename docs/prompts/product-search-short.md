Dùng skill implement-user-story để triển khai:

**User story:** Là người quản lý kho, tôi muốn dễ dàng xem và tìm kiếm để quản lý sản phẩm.

**Tiêu chí chấp nhận:**
- Tìm kiếm sản phẩm theo tên.
- Lọc sản phẩm theo danh mục.
- Trang quản lý sản phẩm (`ProductsView.vue`) có ô tìm kiếm, dropdown danh mục; cột danh mục hiển thị tên thay cho `#id`.

**Gợi ý:** API `GET /products` đã nhận `search` và `category_id` nhưng `ProductService.get_list` đang bỏ qua.

**Ngoài phạm vi:** `low_stock_threshold`, `is_featured`, `sort_by`, trang cửa hàng `StoreCatalogView`, tìm kiếm bỏ dấu tiếng Việt.
