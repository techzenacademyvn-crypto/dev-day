/**
 * Chuyển đổi giá sản phẩm từ DB sang VNĐ.
 * Dữ liệu mẫu ban đầu lưu dạng 49.99 (tương đương 49.99 x 10.000đ = 499.900đ),
 * hoặc giá đã nhập sẵn VNĐ (>= 1.000).
 */
export function getProductPriceVND(price: number | string): number {
  const num = Number(price);
  if (isNaN(num)) return 0;
  if (num < 1000) {
    return Math.round(num * 10000);
  }
  return Math.round(num);
}

/**
 * Định dạng tiền tệ VNĐ hiển thị to, rõ ràng (ví dụ: 100.000đ).
 */
export function formatVND(value: number): string {
  return new Intl.NumberFormat('vi-VN').format(value) + 'đ';
}
