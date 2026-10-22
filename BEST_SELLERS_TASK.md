# Bài tập: Top sản phẩm bán chạy

Repo cung cấp sẵn hai bảng dữ liệu nguồn, không cung cấp API báo cáo:

- `orders`: 60 đơn hàng mẫu với các trạng thái `PENDING`, `CONFIRMED`,
  `SHIPPING`, `COMPLETED`, `CANCELLED`.
- `order_items`: sản phẩm, số lượng và đơn giá được chốt tại thời điểm mua.

## Yêu cầu

Xây dựng API `GET /api/v1/reports/best-sellers?limit=10` trả về các sản
phẩm bán chạy nhất.

- Chỉ tính đơn hàng có trạng thái `COMPLETED`.
- Tổng số lượng bán là `SUM(order_items.quantity)` theo sản phẩm.
- Sắp xếp `sold_quantity` giảm dần, sau đó `product_id` tăng dần để xử lý
  đồng hạng ổn định.
- `limit` mặc định là 10 và chỉ chấp nhận giá trị từ 1 đến 100.
- Sản phẩm chưa bán không xuất hiện trong kết quả.
- Nếu trả về doanh thu, phải tính bằng `quantity * unit_price`, không dùng
  giá hiện tại trong bảng `products`.

Không cần xây dựng khách hàng hoặc giao diện quản lý đơn hàng cho bài tập này.
