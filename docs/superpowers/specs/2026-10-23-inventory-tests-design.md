# Thiết kế kiểm thử tồn kho

## Mục đích

Kiểm tra quy tắc phân loại tồn kho ở backend và cách các màn hình hiển thị/lọc sản phẩm theo tồn kho, để phát hiện sai khác giữa API và Vue.

## Phạm vi và cách tiếp cận

Đã chọn kiểm thử hai lớp: `pytest` cho model/schema/service/API và Vue component tests cho màn hình. Backend-only không bao phủ màn hình. Kiểm thử trình duyệt cần khởi chạy cả hai ứng dụng và không phải unit/component test thuần.

## Mục tiêu

- Bảo vệ phân loại `out_of_stock`, `overstocked`, `normal` theo số lượng và số ngày lưu kho.
- Xác nhận lọc tồn kho ở API trả đúng các sản phẩm và metadata.
- Xác nhận các tab và badge tồn kho trên trang quản trị; trạng thái số lượng trên trang cửa hàng.
- Chạy backend tests bằng Conda environment `tzshop` (Python 3.12.15).
- Không gọi database PostgreSQL hoặc dịch vụ bên ngoài trong test mới; test API dùng SQLite trong bộ nhớ và UI dùng API mock.

## Ngoài phạm vi

- Không thay đổi quy tắc nghiệp vụ hoặc giao diện sản phẩm.
- Không viết kiểm thử E2E qua trình duyệt.
- Không chạy kiểm thử pentest qua Strix; Strix không chạy unit/component tests.

## Kịch bản backend

1. `stock = 0` được phân loại hết hàng, bất kể ngày tạo.
2. Sau 61 ngày: `stock = 10` bình thường; `stock = 11` tồn kho.
3. Tại đúng 60 ngày với `stock = 11`, kết quả mong muốn theo mô tả nghiệp vụ là bình thường; kiểm tra model, service filter và response API cùng nhất quán. Dùng đồng hồ cố định để tránh sai số thời gian.
4. Ngày tạo ở tương lai không tạo số ngày lưu kho âm; trạng thái vẫn là bình thường nếu `stock > 0`.
5. Schema tạo/cập nhật từ chối `stock < 0`, chấp nhận `0` và số dương.
6. Lọc API theo ba trạng thái chỉ trả đúng nhóm; phân trang giữ tổng số và nội dung trang đúng. Sản phẩm đã xoá mềm không xuất hiện.
7. Response API có trạng thái và số ngày phù hợp với cùng quy tắc phân loại.

## Kịch bản Vue component

1. Trang quản trị bắt đầu ở trạng thái đang tải, gọi API trang 1 với `page_size=20`, rồi hiển thị các hàng nhận được.
2. Các hàng hiển thị số lượng, badge trạng thái và số ngày; ranh giới 0, 10/11 và 60/61 ngày khớp quy tắc.
3. Các tab “Tất cả”, “Hết hàng”, “Tồn kho”, “Bình thường” lọc đúng các hàng đã tải; trạng thái rỗng hiển thị thông báo tương ứng.
4. Bộ đếm tab bằng số sản phẩm trong trang đang tải; chuyển trang gọi đúng API và cập nhật danh sách đang lọc.
5. Trang cửa hàng hiển thị “Hết hàng” khi số lượng bằng 0 và “Còn N” khi số lượng dương.

## Cách xử lý các điểm hiện tại

- `Product.stock_status` và UI dùng điều kiện tuổi kho `> 60 ngày`, trong khi `ProductService.get_list` coi `created_at <= now - 60 ngày` là tồn kho. Kịch bản 3 sẽ làm lộ sự không nhất quán; test dự kiến dùng quy tắc ghi trong docstring hiện tại (`> 60 ngày`) làm chuẩn.
- UI chỉ tải 20 sản phẩm mỗi trang và tính tab/bộ đếm trên lô đã tải. Kịch bản 4 ghi nhận đúng hành vi hiện tại, không khẳng định bộ đếm là tổng toàn kho.
- Frontend chưa có test runner. Đề xuất thêm Vitest và Vue Test Utils làm dev dependencies, không cài hay cập nhật dependency trước khi duyệt.

## Điều kiện hoàn tất

- Backend unit/API tests và Vue component tests bao phủ các kịch bản trên.
- Kết quả test được báo cáo riêng cho backend/frontend.
- Trước lần chạy test đầu tiên, gửi thông báo cho người dùng như đã yêu cầu.

## Chưa thực hiện

Thiết kế được người dùng duyệt. Chưa thêm test code, chưa cài dependency và chưa chạy test.
