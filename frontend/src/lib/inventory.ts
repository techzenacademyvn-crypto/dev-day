/**
 * Domain logic và tiện ích xử lý tồn kho (Inventory Stock Management).
 * Tuân thủ quy tắc nghiệp vụ TASK-03:
 * - quantity > 0: Còn hàng (In Stock)
 * - quantity = 0: Hết hàng (Out of Stock)
 * - quantity < 0: Dữ liệu bất thường (Anomalous Data) - không âm thầm chuyển thành 0
 * - quantity null / undefined / NaN / không hợp lệ: Không xác định (Invalid Data) - không tự động coi là còn hàng
 */

export type StockStatusType = 'IN_STOCK' | 'OUT_OF_STOCK' | 'ANOMALOUS' | 'INVALID';

export interface StockInfo {
  /** Giá trị số lượng hợp lệ, hoặc null nếu dữ liệu không hợp lệ */
  quantity: number | null;
  /** Mã trạng thái chuẩn hoá */
  status: StockStatusType;
  /** Nhãn trạng thái tiếng Việt thân thiện */
  statusLabel: string;
  /** Chuỗi biểu diễn số lượng hiển thị trên giao diện */
  displayQuantity: string;
  /** Tên class CSS phục vụ hiển thị badge trực quan */
  badgeClass: string;
  /** Cờ báo dữ liệu số lượng có hợp lệ về mặt kỹ thuật hay không */
  isValid: boolean;
}

/**
 * Phân tích và chuẩn hoá thông tin tồn kho từ dữ liệu thô.
 * @param rawQuantity - Giá trị quantity/stock nhận từ API hoặc người dùng
 */
export function getStockInfo(rawQuantity: unknown): StockInfo {
  // 1. Kiểm tra trường hợp thiếu hoặc null/undefined
  if (rawQuantity === null || rawQuantity === undefined || rawQuantity === '') {
    return {
      quantity: null,
      status: 'INVALID',
      statusLabel: 'Không xác định',
      displayQuantity: '—',
      badgeClass: 'stock-invalid',
      isValid: false,
    };
  }

  // 2. Chặn các kiểu dữ liệu không phải number hoặc string (ví dụ object, array, boolean)
  if (typeof rawQuantity !== 'number' && typeof rawQuantity !== 'string') {
    return {
      quantity: null,
      status: 'INVALID',
      statusLabel: 'Dữ liệu không hợp lệ',
      displayQuantity: 'Lỗi',
      badgeClass: 'stock-invalid',
      isValid: false,
    };
  }

  // 3. Nếu là chuỗi, kiểm tra chuỗi rỗng sau khi trim
  if (typeof rawQuantity === 'string') {
    const trimmed = rawQuantity.trim();
    if (trimmed === '') {
      return {
        quantity: null,
        status: 'INVALID',
        statusLabel: 'Không xác định',
        displayQuantity: '—',
        badgeClass: 'stock-invalid',
        isValid: false,
      };
    }
  }

  // 4. Chuyển đổi và kiểm tra tính hợp lệ kiểu số
  const parsed = typeof rawQuantity === 'number' ? rawQuantity : Number(rawQuantity);

  if (Number.isNaN(parsed) || !Number.isFinite(parsed)) {
    return {
      quantity: null,
      status: 'INVALID',
      statusLabel: 'Dữ liệu không hợp lệ',
      displayQuantity: 'Lỗi',
      badgeClass: 'stock-invalid',
      isValid: false,
    };
  }

  // 5. Xử lý số âm - Dữ liệu bất thường (Anomalous)
  if (parsed < 0) {
    return {
      quantity: parsed,
      status: 'ANOMALOUS',
      statusLabel: 'Dữ liệu bất thường',
      displayQuantity: String(parsed),
      badgeClass: 'stock-anomalous',
      isValid: false,
    };
  }

  // 6. quantity = 0: Hết hàng (AC02)
  if (parsed === 0) {
    return {
      quantity: 0,
      status: 'OUT_OF_STOCK',
      statusLabel: 'Hết hàng',
      displayQuantity: '0',
      badgeClass: 'out-of-stock',
      isValid: true,
    };
  }

  // 7. quantity > 0: Còn hàng (AC01)
  return {
    quantity: parsed,
    status: 'IN_STOCK',
    statusLabel: 'Còn hàng',
    displayQuantity: String(parsed),
    badgeClass: 'in-stock',
    isValid: true,
  };
}

/**
 * Format chuỗi hiển thị tổng hợp cho người dùng (ví dụ: "10 (Còn hàng)" hoặc "0 (Hết hàng)").
 */
export function formatStockDisplay(rawQuantity: unknown): string {
  const info = getStockInfo(rawQuantity);
  if (!info.isValid) {
    return `${info.displayQuantity} (${info.statusLabel})`;
  }
  return `${info.displayQuantity} (${info.statusLabel})`;
}
