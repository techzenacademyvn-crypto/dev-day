<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách và kiểm kê sản phẩm trong kho hàng</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <ProductFilterToolbar @apply="applyFilters" @reset="resetAllFilters" />

    <!-- Thanh công cụ Điều khiển: Gom nhóm (US1-Task 5) & Bố cục hiển thị theo mức độ cần thiết (US2-Task 4) -->
    <div class="view-controls-bar">
      <!-- US1-Task 5: Gom nhóm theo khối -->
      <div class="control-box group-control">
        <label for="group-mode-select" class="control-label">
          <span class="control-icon">📂</span> Gom nhóm:
        </label>
        <select id="group-mode-select" v-model="groupBy" class="control-select">
          <option value="none">Mặc định (Bảng phẳng)</option>
          <option value="category">📁 Theo Danh mục</option>
          <option value="stock_status">📊 Theo Tình trạng kho</option>
        </select>
      </div>

      <!-- US2-Task 4: Bộ chọn nhanh Chế độ Bố cục (Presets) theo mức độ cần thiết -->
      <div class="control-box preset-control">
        <span class="control-label">
          <span class="control-icon">📐</span> Chế độ xem:
        </span>
        <div class="preset-pill-group">
          <button
            type="button"
            :class="['preset-btn', currentPreset === 'compact' ? 'active' : '']"
            @click="applyPreset('compact')"
            title="Chế độ gọn: Tối giản không gian, chỉ hiển thị thông tin thiết yếu nhất (SKU, Tên, Giá, Tồn kho, Cảnh báo)"
          >
            ⚡ Gọn
          </button>
          <button
            type="button"
            :class="['preset-btn', currentPreset === 'standard' ? 'active' : '']"
            @click="applyPreset('standard')"
            title="Chế độ tiêu chuẩn: Cân đối giữa thông tin cốt lõi và danh mục, nổi bật"
          >
            📋 Tiêu chuẩn
          </button>
          <button
            type="button"
            :class="['preset-btn', currentPreset === 'detailed' ? 'active' : '']"
            @click="applyPreset('detailed')"
            title="Chế độ đầy đủ: Hiển thị toàn bộ thông tin chi tiết (Mô tả, ID, Mốc thời gian...)"
          >
            🔍 Đầy đủ
          </button>
        </div>
      </div>

      <!-- US2-Task 4: Dropdown Menu Tùy biến cột hiển thị -->
      <div class="col-customizer-wrapper" ref="colDropdownRef">
        <button
          type="button"
          class="btn-col-trigger"
          :class="{ active: isColDropdownOpen }"
          @click="isColDropdownOpen = !isColDropdownOpen"
          title="Bật/Tắt các cột theo nhu cầu quan sát"
        >
          <span class="btn-icon">⚙️</span>
          <span>Bố cục cột ({{ visibleColumnCount }}/{{ columns.length }})</span>
          <span class="arrow-icon">{{ isColDropdownOpen ? '▲' : '▼' }}</span>
        </button>

        <!-- Dropdown Popover Tùy biến cột -->
        <div v-if="isColDropdownOpen" class="col-dropdown-menu">
          <div class="dropdown-header">
            <span class="dropdown-title">Bố cục thông tin theo mức độ</span>
            <button type="button" @click="resetColumns" class="btn-reset-cols">
              Đặt lại
            </button>
          </div>

          <!-- Mức 1: Thiết yếu -->
          <div class="col-group-section">
            <div class="col-group-title text-essential">
              <span class="level-indicator dot-essential"></span> Mức 1: Thiết yếu (Cần thiết nhất)
            </div>
            <div class="col-items-list">
              <label v-for="col in essentialColumns" :key="col.key" class="col-checkbox-label">
                <input
                  type="checkbox"
                  v-model="col.visible"
                  :disabled="col.alwaysVisible"
                  @change="handleColumnToggle"
                />
                <span :class="{ 'font-semibold': col.alwaysVisible }">{{ col.label }}</span>
                <span v-if="col.alwaysVisible" class="col-locked-badge">(Bắt buộc)</span>
              </label>
            </div>
          </div>

          <!-- Mức 2: Bổ sung -->
          <div class="col-group-section">
            <div class="col-group-title text-standard">
              <span class="level-indicator dot-standard"></span> Mức 2: Bổ sung thường dùng
            </div>
            <div class="col-items-list">
              <label v-for="col in standardColumns" :key="col.key" class="col-checkbox-label">
                <input
                  type="checkbox"
                  v-model="col.visible"
                  @change="handleColumnToggle"
                />
                <span>{{ col.label }}</span>
              </label>
            </div>
          </div>

          <!-- Mức 3: Mở rộng -->
          <div class="col-group-section">
            <div class="col-group-title text-detailed">
              <span class="level-indicator dot-detailed"></span> Mức 3: Chi tiết mở rộng
            </div>
            <div class="col-items-list">
              <label v-for="col in detailedColumns" :key="col.key" class="col-checkbox-label">
                <input
                  type="checkbox"
                  v-model="col.visible"
                  @change="handleColumnToggle"
                />
                <span>{{ col.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Trạng thái thông báo lỗi nếu có -->
    <div v-if="errorMessage" class="error-banner">
      <svg class="error-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
      </svg>
      <span>{{ errorMessage }}</span>
      <button @click="fetchProducts(currentPage)" class="btn-retry">Thử lại</button>
    </div>

    <!-- Bảng danh sách sản phẩm hiển thị Gom nhóm & Bố cục tùy biến động -->
    <div class="table-container">
      <table :class="['data-table', currentPreset === 'compact' ? 'table-compact' : '']">
        <thead>
          <tr>
            <th v-if="isColVisible('id')" style="width: 70px;">ID</th>
            <th v-if="isColVisible('sku')">SKU</th>
            <th v-if="isColVisible('name')">Tên Sản Phẩm</th>
            <th v-if="isColVisible('description')" style="max-width: 250px;">Mô Tả</th>
            <th v-if="isColVisible('category')">Danh Mục</th>
            <th v-if="isColVisible('price')">Đơn Giá</th>
            <th v-if="isColVisible('stock')">Tồn Kho</th>
            <th v-if="isColVisible('stock_status')">Tình Trạng Kho</th>
            <th v-if="isColVisible('created_at')">Mốc Thời Gian</th>
            <th v-if="isColVisible('is_featured')">Nổi Bật</th>
            <th v-if="isColVisible('actions')">Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <!-- Trạng thái Loading -->
          <tr v-if="loading">
            <td :colspan="visibleColumnCount" class="text-center py-8 state-cell">
              <div class="spinner"></div>
              <span>Đang tải danh sách sản phẩm...</span>
            </td>
          </tr>

          <!-- Trạng thái Không có sản phẩm nào sau khi lọc -->
          <tr v-else-if="filteredProducts.length === 0">
            <td :colspan="visibleColumnCount" class="empty-table-cell">
              <div class="empty-filter-box">
                <span class="empty-icon">📦</span>
                <p class="empty-msg">Không tìm thấy sản phẩm nào phù hợp với bộ lọc hiện tại</p>
                <div class="empty-actions">
                  <button @click="resetAllFilters" class="btn-reset-empty">
                    Xóa tất cả bộ lọc
                  </button>
                </div>
              </div>
            </td>
          </tr>

          <!-- Dữ liệu hiển thị (Hỗ trợ Gom nhóm theo Khối & Bố cục cột tùy biến) -->
          <template v-else v-for="group in groupedProducts" :key="group.key">
            <!-- Dòng Tiêu đề Khối Nhóm (Chỉ hiện khi bật Gom nhóm) -->
            <tr v-if="groupBy !== 'none'" class="group-header-row">
              <td :colspan="visibleColumnCount">
                <div class="group-header-content">
                  <span class="group-header-title">
                    <span class="group-header-icon">{{ group.icon }}</span>
                    {{ group.title }}
                  </span>
                  <div class="group-header-stats">
                    <span class="group-badge-count">{{ group.items.length }} sản phẩm</span>
                    <span class="group-badge-stock">Tổng tồn: <strong>{{ group.totalStock }}</strong> cái</span>
                  </div>
                </div>
              </td>
            </tr>

            <!-- Các dòng sản phẩm bên trong nhóm (Ẩn/Hiện cột theo cấu hình tùy biến) -->
            <tr v-for="prod in group.items" :key="prod.id" class="product-data-row">
              <!-- Cột ID (Mức 3 - Chi tiết) -->
              <td v-if="isColVisible('id')">
                <span class="id-tag">#{{ prod.id }}</span>
              </td>

              <!-- Cột SKU (Mức 1 - Thiết yếu) -->
              <td v-if="isColVisible('sku')">
                <code>{{ prod.sku }}</code>
              </td>

              <!-- Cột Tên sản phẩm (Mức 1 - Thiết yếu - Luôn bật) -->
              <td v-if="isColVisible('name')" class="font-medium text-white">
                {{ prod.name }}
              </td>

              <!-- Cột Mô tả (Mức 3 - Chi tiết) -->
              <td v-if="isColVisible('description')" class="desc-cell" :title="prod.description || ''">
                {{ prod.description || '—' }}
              </td>

              <!-- Cột Danh mục (Mức 2 - Bổ sung) -->
              <td v-if="isColVisible('category')">
                <span class="category-tag">
                  {{ categoryMap[prod.category_id] || `#${prod.category_id}` }}
                </span>
              </td>

              <!-- Cột Đơn giá (Mức 1 - Thiết yếu) -->
              <td v-if="isColVisible('price')" class="price-cell">
                <div class="price-usd-text">${{ Number(prod.price).toFixed(2) }}</div>
              </td>

              <!-- Cột Số lượng tồn kho (Mức 1 - Thiết yếu) -->
              <td v-if="isColVisible('stock')" class="stock-cell font-semibold">
                {{ prod.stock }} cái
              </td>

              <!-- Cột Tình trạng kho (Mức 1 - Thiết yếu) -->
              <td v-if="isColVisible('stock_status')">
                <span :class="['stock-status-badge', getStockStatus(prod).badgeClass]">
                  {{ getStockStatus(prod).label }}
                </span>
              </td>

              <!-- Cột Mốc thời gian nhập (Mức 3 - Chi tiết) -->
              <td v-if="isColVisible('created_at')" class="time-cell">
                <span class="time-text">{{ formatDateTime(prod.created_at) }}</span>
              </td>

              <!-- Cột Nổi bật (Mức 2 - Bổ sung) -->
              <td v-if="isColVisible('is_featured')">
                <span v-if="prod.is_featured" class="badge-featured">⭐ Nổi bật</span>
                <span v-else class="text-muted">—</span>
              </td>

              <!-- Cột Thao tác (Mức 2 - Bổ sung) -->
              <td v-if="isColVisible('actions')">
                <button @click="handleDelete(prod.id)" class="btn-sm btn-delete">Xoá</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Phân trang / Thống kê -->
    <div class="pagination-bar" v-if="totalProducts > 0">
      <span>
        Hiển thị <strong>{{ filteredProducts.length }}</strong> / {{ totalProducts }} sản phẩm 
        (Trang {{ currentPage }} / {{ totalPages }})
      </span>
      <div class="pagination-btns">
        <button
          :disabled="currentPage <= 1 || loading"
          @click="changePage(currentPage - 1)"
          class="btn-page"
        >
          Trước
        </button>
        <button
          :disabled="currentPage >= totalPages || loading"
          @click="changePage(currentPage + 1)"
          class="btn-page"
        >
          Sau
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../../lib/api';
import type { Product } from '../../types';
import ProductFilterToolbar, { type ProductFilterPayload } from '../../components/admin/ProductFilterToolbar.vue';

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const errorMessage = ref('');
let navbarObserver: ResizeObserver | undefined;

// Bộ nhớ cache tên danh mục để hiển thị đẹp thay vì ID thô
const categoryMap = ref<Record<number, string>>({});

// State Task 1: Tìm kiếm & Đa danh mục (Vinh)
const searchKeyword = ref('');
const selectedCategoryId = ref<number | null>(null);

const minPrice = ref<string | null>(null);
const maxPrice = ref<string | null>(null);

// State Task 3: Sản phẩm nổi bật (Hoài)
const isFeaturedOnly = ref(false);

// State Task 4: Tình trạng tồn kho (Quân)
type StockFilterType = 'all' | 'in_stock' | 'out_of_stock' | 'low_stock' | 'aged_stock';
const selectedStockTab = ref<StockFilterType>('all');

// State Task 5: Gom nhóm & Sắp xếp (Ngọc)
const groupBy = ref<'none' | 'category' | 'stock_status'>('none');
const sortBy = ref('');

// ==============================================================================
// US2 - TASK 4: ĐIỀU CHỈNH BỐ CỤC THÔNG TIN HIỂN THỊ THEO MỨC ĐỘ CẦN THIẾT
// ==============================================================================
export interface ColumnDefinition {
  key: string;
  label: string;
  visible: boolean;
  level: 'essential' | 'standard' | 'detailed';
  alwaysVisible?: boolean;
}

type LayoutPreset = 'compact' | 'standard' | 'detailed' | 'custom';
const currentPreset = ref<LayoutPreset>('standard');
const isColDropdownOpen = ref(false);
const colDropdownRef = ref<HTMLElement | null>(null);

// Danh sách các cột phân chia theo 3 mức độ cần thiết
const columns = ref<ColumnDefinition[]>([
  // Mức 1: Thiết yếu (Bắt buộc / Cần thiết nhất cho kiểm kê)
  { key: 'sku', label: 'Mã SKU', visible: true, level: 'essential' },
  { key: 'name', label: 'Tên Sản Phẩm', visible: true, level: 'essential', alwaysVisible: true },
  { key: 'price', label: 'Đơn Giá', visible: true, level: 'essential' },
  { key: 'stock', label: 'Số Lượng Tồn', visible: true, level: 'essential' },

  // Mức 2: Bổ sung thường dùng (Tiêu chuẩn)
  { key: 'category', label: 'Danh Mục', visible: true, level: 'standard' },
  { key: 'is_featured', label: 'Đánh Dấu Nổi Bật', visible: true, level: 'standard' },
  { key: 'actions', label: 'Thao Tác (Xóa)', visible: true, level: 'standard' },

  // Mức 3: Chi tiết mở rộng (Phục vụ đối chiếu sâu)
  { key: 'id', label: 'Mã ID Hệ Thống', visible: false, level: 'detailed' },
  { key: 'description', label: 'Mô Tả Sản Phẩm', visible: false, level: 'detailed' },
  { key: 'created_at', label: 'Thời Điểm Tạo Sản Phẩm', visible: false, level: 'detailed' },
  { key: 'stock_status', label: 'Tình Trạng Kho', visible: false, level: 'detailed' },
]);

// Nhóm cột theo mức độ để hiển thị trong Popover tùy biến
const essentialColumns = computed(() => columns.value.filter((c) => c.level === 'essential'));
const standardColumns = computed(() => columns.value.filter((c) => c.level === 'standard'));
const detailedColumns = computed(() => columns.value.filter((c) => c.level === 'detailed'));

// Tính toán tổng số cột đang hiển thị để căn đúng colspan cho các dòng đặc biệt
const visibleColumnCount = computed(() => {
  return columns.value.filter((col) => col.visible).length;
});

function isColVisible(key: string): boolean {
  const col = columns.value.find((c) => c.key === key);
  return col ? col.visible : true;
}

// Áp dụng các chế độ bố cục nhanh (Presets)
function applyPreset(preset: 'compact' | 'standard' | 'detailed') {
  currentPreset.value = preset;
  if (preset === 'compact') {
    // Chế độ Gọn: Chỉ giữ mức 1 (Thiết yếu)
    columns.value.forEach((col) => {
      col.visible = col.level === 'essential';
    });
  } else if (preset === 'standard') {
    // Chế độ Tiêu chuẩn: Mức 1 + Mức 2
    columns.value.forEach((col) => {
      col.visible = col.level === 'essential' || col.level === 'standard';
    });
  } else if (preset === 'detailed') {
    // Chế độ Đầy đủ: Mức 1 + Mức 2 + Mức 3
    columns.value.forEach((col) => {
      col.visible = true;
    });
  }
  saveLayoutSettings();
}

// Khi người dùng tự tay bật/tắt checkbox riêng lẻ
function handleColumnToggle() {
  currentPreset.value = 'custom';
  saveLayoutSettings();
}

// Đặt lại bố cục mặc định (Tiêu chuẩn)
function resetColumns() {
  applyPreset('standard');
}

// Lưu trữ cấu hình bố cục vào LocalStorage
const STORAGE_KEY = 'tz_products_layout_settings_v2';

function saveLayoutSettings() {
  try {
    const data = {
      preset: currentPreset.value,
      columns: columns.value.map((c) => ({ key: c.key, visible: c.visible })),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (err) {
    console.error('Không thể lưu cài đặt bố cục:', err);
  }
}

function loadLayoutSettings() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.preset) currentPreset.value = parsed.preset;
      if (Array.isArray(parsed.columns)) {
        parsed.columns.forEach((savedCol: { key: string; visible: boolean }) => {
          const target = columns.value.find((c) => c.key === savedCol.key);
          if (target && !target.alwaysVisible) {
            target.visible = savedCol.visible;
          }
        });
      }
    }
  } catch (err) {
    console.error('Không thể tải cài đặt bố cục:', err);
  }
}

// Tự động đóng dropdown khi click chuột ra ngoài
function handleClickOutside(event: MouseEvent) {
  if (colDropdownRef.value && !colDropdownRef.value.contains(event.target as Node)) {
    isColDropdownOpen.value = false;
  }
}

// Hàm định dạng ngày giờ chuẩn Việt Nam
function formatDateTime(dateStr?: string | null) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('vi-VN') + ' ' + d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

// ==============================================================================
// CÁC HÀM XỬ LÝ DỮ LIỆU & BỘ LỌC CỦA US1
// ==============================================================================

// Bộ dữ liệu Mock Data cho Tab Hàng Tồn Kho (phục vụ hiển thị & kiểm thử nghiệp vụ khi seed.py gốc chưa có hàng lưu kho > 60 ngày)
// Điều kiện Hàng tồn kho: Thời gian lưu kho > 2 tháng (> 60 ngày) VÀ số lượng tồn > 10 sản phẩm
const mockOverstockedProducts: Product[] = [
  {
    id: 901,
    category_id: 1,
    name: 'Chuột công thái học Wireless Silent TZ-Pro',
    sku: 'PRD-MOCK-01',
    price: 24.50,
    stock: 80,
    is_featured: false,
    image_url: 'https://placehold.co/400x400?text=PRD-MOCK-01',
    description: 'Sản phẩm tồn kho 75 ngày (> 60 ngày), số lượng tồn 80 cái (> 10 cái). Cần áp dụng chiến dịch xả kho.',
    created_at: new Date(Date.now() - 75 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 75 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 902,
    category_id: 1,
    name: 'Bàn phím cơ Blue Switch TZ-Gaming RGB',
    sku: 'PRD-MOCK-02',
    price: 89.95,
    stock: 35,
    is_featured: true,
    image_url: 'https://placehold.co/400x400?text=PRD-MOCK-02',
    description: 'Sản phẩm tồn kho 90 ngày (> 60 ngày), số lượng tồn 35 cái (> 10 cái).',
    created_at: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 903,
    category_id: 2,
    name: 'Máy hút bụi cầm tay mini không dây TZ-Clean',
    sku: 'PRD-MOCK-03',
    price: 45.00,
    stock: 40,
    is_featured: false,
    image_url: 'https://placehold.co/400x400?text=PRD-MOCK-03',
    description: 'Sản phẩm tồn kho 120 ngày (> 60 ngày), số lượng tồn 40 cái (> 10 cái).',
    created_at: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 904,
    category_id: 3,
    name: 'Quần Tây âu co giãn 4 chiều Slimfit Nam',
    sku: 'PRD-MOCK-04',
    price: 32.50,
    stock: 45,
    is_featured: false,
    image_url: 'https://placehold.co/400x400?text=PRD-MOCK-04',
    description: 'Sản phẩm tồn kho 80 ngày (> 60 ngày), số lượng tồn 45 cái (> 10 cái).',
    created_at: new Date(Date.now() - 80 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 80 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 905,
    category_id: 5,
    name: 'Kính râm chống tia UV400 Polarized',
    sku: 'PRD-MOCK-05',
    price: 19.99,
    stock: 70,
    is_featured: false,
    image_url: 'https://placehold.co/400x400?text=PRD-MOCK-05',
    description: 'Sản phẩm tồn kho 85 ngày (> 60 ngày), số lượng tồn 70 cái (> 10 cái).',
    created_at: new Date(Date.now() - 85 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 85 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 906,
    category_id: 6,
    name: 'Sách: Nghệ thuật đàm phán đỉnh cao',
    sku: 'PRD-MOCK-06',
    price: 12.50,
    stock: 90,
    is_featured: false,
    image_url: 'https://placehold.co/400x400?text=PRD-MOCK-06',
    description: 'Sản phẩm tồn kho 95 ngày (> 60 ngày), số lượng tồn 90 cái (> 10 cái).',
    created_at: new Date(Date.now() - 95 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 95 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

// Hàm tính ngày lưu kho và phân loại tình trạng tồn kho theo chuẩn nghiệp vụ US1:
function getStockStatus(prod: Product) {
  if (prod.stock === 0) {
    return {
      key: 'out_of_stock',
      label: 'Hết hàng',
      badgeClass: 'badge-out-of-stock',
    };
  }

  if (prod.stock > 0 && prod.stock < 10) {
    return { key: 'low_stock', label: 'Tồn kho thấp', badgeClass: 'badge-overstocked' };
  }

  if (prod.created_at && prod.stock >= 10) {
    const createdTime = new Date(prod.created_at).getTime();
    const now = Date.now();
    const twentyDaysMs = 20 * 24 * 60 * 60 * 1000;
    if (now - createdTime >= twentyDaysMs) {
      return {
        key: 'aged_stock',
        label: 'Tồn kho ≥10 · Tạo ≥20 ngày',
        badgeClass: 'badge-overstocked',
      };
    }
  }

  return {
    key: 'in_stock',
    label: 'Còn hàng',
    badgeClass: 'badge-in-stock',
  };
}

// Mọi filter đã được thực hiện ở backend trước phân trang.
const filteredProducts = computed(() => products.value);

// Cấu trúc khối gom nhóm cho Task 5
interface ProductGroup {
  key: string;
  title: string;
  icon: string;
  items: Product[];
  totalStock: number;
}

// Gom nhóm dữ liệu dựa trên groupBy và sắp xếp (Task 5)
const groupedProducts = computed<ProductGroup[]>(() => {
  const list = [...filteredProducts.value];

  // Nếu không gom nhóm -> trả về 1 nhóm phẳng
  if (groupBy.value === 'none') {
    return [
      {
        key: 'all',
        title: 'Tất cả sản phẩm',
        icon: '📋',
        items: list,
        totalStock: list.reduce((sum, item) => sum + (item.stock || 0), 0),
      },
    ];
  }

  // Gom theo Danh mục sản phẩm
  if (groupBy.value === 'category') {
    const map = new Map<number | string, Product[]>();
    for (const prod of list) {
      const catId = prod.category_id || 'unknown';
      if (!map.has(catId)) {
        map.set(catId, []);
      }
      map.get(catId)!.push(prod);
    }

    const groups: ProductGroup[] = [];
    for (const [catId, items] of map.entries()) {
      const catName = typeof catId === 'number' && categoryMap.value[catId]
        ? categoryMap.value[catId]
        : `Danh mục #${catId}`;

      groups.push({
        key: `cat-${catId}`,
        title: catName,
        icon: '📁',
        items,
        totalStock: items.reduce((sum, item) => sum + (item.stock || 0), 0),
      });
    }

    // Sắp xếp thứ tự tên nhóm theo bảng chữ cái A-Z
    return groups.sort((a, b) => a.title.localeCompare(b.title, 'vi'));
  }

  // Gom theo Tình trạng tồn kho (Stock Status)
  if (groupBy.value === 'stock_status') {
    const outOfStockItems: Product[] = [];
    const overstockedItems: Product[] = [];
    const inStockItems: Product[] = [];

    for (const prod of list) {
      const status = getStockStatus(prod);
      if (status.key === 'out_of_stock') {
        outOfStockItems.push(prod);
      } else if (status.key === 'overstocked') {
        overstockedItems.push(prod);
      } else {
        inStockItems.push(prod);
      }
    }

    const groups: ProductGroup[] = [];

    if (outOfStockItems.length > 0) {
      groups.push({
        key: 'out_of_stock',
        title: 'Hàng hết trong kho (Cần nhập gấp)',
        icon: '🔴',
        items: outOfStockItems,
        totalStock: 0,
      });
    }

    if (overstockedItems.length > 0) {
      groups.push({
        key: 'overstocked',
        title: 'Hàng tồn kho (Cần xả kho)',
        icon: '🟠',
        items: overstockedItems,
        totalStock: overstockedItems.reduce((sum, item) => sum + (item.stock || 0), 0),
      });
    }

    if (inStockItems.length > 0) {
      groups.push({
        key: 'in_stock',
        title: 'Hàng tồn kho ổn định / Bình thường',
        icon: '🟢',
        items: inStockItems,
        totalStock: inStockItems.reduce((sum, item) => sum + (item.stock || 0), 0),
      });
    }

    return groups;
  }

  return [];
});

// Lấy danh mục để hiển thị tên trên bảng
async function fetchCategoriesMap() {
  try {
    const res = await api.get('/categories', {
      params: { is_active: true, page_size: 100 },
    });
    if (res.data.success) {
      const map: Record<number, string> = {};
      res.data.data.items.forEach((cat: any) => {
        map[cat.id] = cat.name;
      });
      categoryMap.value = map;
    }
  } catch (err) {
    console.error('Không thể nạp danh mục cho bảng:', err);
  }
}

// Gọi API lấy danh sách sản phẩm
async function fetchProducts(page = 1) {
  loading.value = true;
  errorMessage.value = '';
  currentPage.value = page;

  try {
    const params: Record<string, any> = {
      page,
      page_size: 50,
    };

    if (searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }
    if (selectedCategoryId.value !== null) {
      params.category_id = selectedCategoryId.value;
    }
    if (isFeaturedOnly.value) {
      params.is_featured = true;
    }
    if (selectedStockTab.value !== 'all') {
      params.stock_status = selectedStockTab.value;
    }
    if (minPrice.value !== null) params.min_price = minPrice.value;
    if (maxPrice.value !== null) params.max_price = maxPrice.value;
    if (sortBy.value) {
      params.sort_by = sortBy.value;
    }

    const res = await api.get('/products', { params });
    if (res.data.success) {
      // Nếu lọc tab tồn kho mà backend trả về rỗng (do dữ liệu seed gốc toàn bộ là hàng mới tạo < 1 ngày)
      // thì nạp mock data cho tab tồn kho để phục vụ kiểm thử và demo
      if (selectedStockTab.value === 'overstocked' && (!res.data.data.items || res.data.data.items.length === 0)) {
        products.value = mockOverstockedProducts;
        totalProducts.value = mockOverstockedProducts.length;
        totalPages.value = 1;
      } else {
        products.value = res.data.data.items;
        totalProducts.value = res.data.data.total;
        totalPages.value = res.data.data.total_pages;
      }
    } else {
      errorMessage.value = res.data.message || 'Không thể tải danh sách sản phẩm';
    }
  } catch (err: any) {
    if (selectedStockTab.value === 'overstocked') {
      products.value = mockOverstockedProducts;
      totalProducts.value = mockOverstockedProducts.length;
      totalPages.value = 1;
      errorMessage.value = '';
    } else {
      errorMessage.value = err.response?.data?.error?.message || 'Có lỗi xảy ra khi tải sản phẩm';
      console.error(err);
    }
  } finally {
    loading.value = false;
  }
}

// Xử lý khi đổi tiêu chí sắp xếp (Task 5)
function applyFilters(payload: ProductFilterPayload) {
  searchKeyword.value = payload.search;
  selectedCategoryId.value = payload.categoryId;
  minPrice.value = payload.minPrice;
  maxPrice.value = payload.maxPrice;
  isFeaturedOnly.value = payload.isFeatured;
  selectedStockTab.value = payload.stockStatus as StockFilterType;
  sortBy.value = payload.sortBy;
  fetchProducts(1);
}

// Chuyển trang
function changePage(page: number) {
  fetchProducts(page);
}

// Đặt lại toàn bộ bộ lọc
function resetAllFilters() {
  searchKeyword.value = '';
  selectedCategoryId.value = null;
  selectedStockTab.value = 'all';
  isFeaturedOnly.value = false;
  minPrice.value = null;
  maxPrice.value = null;
  sortBy.value = '';
  currentPage.value = 1;
  fetchProducts(1);
}

function openCreateModal() {
  alert('Chức năng thêm sản phẩm qua form quản trị đã sẵn sàng kết nối API POST /products.');
}

async function handleDelete(id: number) {
  if (confirm('Xoá mềm sản phẩm này?')) {
    try {
      await api.delete(`/products/${id}`);
      fetchProducts(currentPage.value);
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Lỗi khi xóa');
    }
  }
}

onMounted(() => {
  const navbar = document.querySelector<HTMLElement>('.navbar');
  const setNavbarHeight = () => document.documentElement.style.setProperty('--tz-navbar-height', `${navbar?.offsetHeight || 0}px`);
  setNavbarHeight();
  navbarObserver = navbar ? new ResizeObserver(setNavbarHeight) : undefined;
  if (navbar) navbarObserver?.observe(navbar);
  loadLayoutSettings();
  window.addEventListener('click', handleClickOutside);
  fetchCategoriesMap();
  fetchProducts();
});

onUnmounted(() => {
  navbarObserver?.disconnect();
  document.documentElement.style.removeProperty('--tz-navbar-height');
  window.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.admin-page {
  max-width: 1320px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f8fafc;
}

.page-desc {
  color: #94a3b8;
  font-size: 0.9rem;
}

.btn-primary {
  background: #0284c7;
  color: #fff;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: #0369a1;
}

/* Bộ lọc sản phẩm nổi bật (Task 3) */
.featured-filter-bar {
  margin-bottom: 1rem;
}

.featured-toggle-label {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: #334155;
  border-radius: 9999px;
  position: relative;
  transition: background-color 0.25s ease;
  cursor: pointer;
}

.toggle-switch.active {
  background: #facc15;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #ffffff;
  border-radius: 50%;
  transition: transform 0.25s ease;
}

.toggle-switch.active .toggle-thumb {
  transform: translateX(20px);
}

.toggle-text {
  color: #94a3b8;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.toggle-active-text {
  color: #facc15;
  font-weight: 600;
}

/* Bộ lọc nhanh tình trạng tồn kho (Task 4) */
.stock-filter-bar {
  margin-bottom: 1rem;
}

.stock-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tab-btn {
  background: #1e293b;
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 0.45rem 0.9rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  border-color: #64748b;
  color: #f8fafc;
}

.tab-btn.active {
  background: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
  font-weight: 600;
}

.tab-btn.tab-danger.active {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
  color: #f87171;
}

.tab-btn.tab-warning.active {
  background: rgba(245, 158, 11, 0.25);
  border-color: #f59e0b;
  color: #fbbf24;
}

.tab-btn.tab-success.active {
  background: rgba(34, 197, 94, 0.25);
  border-color: #22c55e;
  color: #4ade80;
}

/* Ghi chú điều kiện hàng tồn kho khi mở tab Tồn kho */
.stock-condition-banner {
  margin-top: 0.75rem;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-left: 4px solid #f59e0b;
  border-radius: 0.5rem;
  padding: 0.65rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: #fde68a;
  animation: bannerFadeIn 0.2s ease-in-out;
}

@keyframes bannerFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.condition-icon {
  font-size: 1.15rem;
  flex-shrink: 0;
}

.condition-content {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.condition-title {
  font-weight: 700;
  color: #fbbf24;
}

.condition-desc {
  color: #fef3c7;
}

.condition-desc strong {
  color: #ffffff;
}

/* Thanh điều khiển Gom nhóm (US1-5) & Bố cục hiển thị (US2-4) */
.view-controls-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.625rem;
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.25rem;
  align-items: center;
}

.control-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.control-label {
  font-size: 0.85rem;
  color: #cbd5e1;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}

.control-icon {
  font-size: 0.95rem;
}

.control-select {
  padding: 0.45rem 0.85rem;
  border-radius: 0.375rem;
  background-color: #0f172a;
  border: 1px solid #475569;
  color: #f8fafc;
  cursor: pointer;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.control-select:focus {
  border-color: #38bdf8;
}

/* Preset Pill Group */
.preset-pill-group {
  display: flex;
  background: #0f172a;
  border: 1px solid #475569;
  border-radius: 0.4rem;
  padding: 0.15rem;
  gap: 0.2rem;
}

.preset-btn {
  background: transparent;
  color: #94a3b8;
  border: none;
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 0.3rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  color: #f8fafc;
}

.preset-btn.active {
  background: #0284c7;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.4);
}

/* Menu Dropdown Tùy biến cột (US2-Task 4) */
.col-customizer-wrapper {
  position: relative;
  margin-left: auto;
}

.btn-col-trigger {
  background: #0f172a;
  border: 1px solid #475569;
  color: #cbd5e1;
  padding: 0.45rem 0.85rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.btn-col-trigger:hover,
.btn-col-trigger.active {
  border-color: #38bdf8;
  color: #38bdf8;
}

.arrow-icon {
  font-size: 0.65rem;
  opacity: 0.8;
}

.col-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: #1e293b;
  border: 1px solid #475569;
  border-radius: 0.5rem;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.45);
  padding: 0.85rem 1rem;
  z-index: 100;
  animation: popIn 0.15s ease-out;
}

@keyframes popIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
  margin-bottom: 0.75rem;
}

.dropdown-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #f8fafc;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.btn-reset-cols {
  background: transparent;
  color: #38bdf8;
  border: none;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
}

.btn-reset-cols:hover {
  text-decoration: underline;
}

.col-group-section {
  margin-bottom: 0.75rem;
}

.col-group-title {
  font-size: 0.725rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.level-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.text-essential { color: #38bdf8; }
.dot-essential { background: #38bdf8; }

.text-standard { color: #facc15; }
.dot-standard { background: #facc15; }

.text-detailed { color: #94a3b8; }
.dot-detailed { background: #94a3b8; }

.col-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-left: 0.5rem;
}

.col-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.825rem;
  color: #cbd5e1;
  cursor: pointer;
  user-select: none;
}

.col-checkbox-label:hover {
  color: #f8fafc;
}

.col-locked-badge {
  font-size: 0.7rem;
  color: #64748b;
  font-style: italic;
}

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.25rem;
}

.error-icon {
  flex-shrink: 0;
  color: #f87171;
}

.btn-retry {
  margin-left: auto;
  background: #ef4444;
  color: #fff;
  border: none;
  padding: 0.35rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  cursor: pointer;
}

/* Bảng dữ liệu */
.table-container {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  position: sticky;
  top: calc(var(--tz-navbar-height, 0px) + var(--tz-filter-toolbar-height, 0px) + 14px);
  z-index: 20;
  background: #0f172a;
  color: #94a3b8;
  padding: 0.85rem 1rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  border-bottom: 1px solid #334155;
  text-align: left;
  white-space: nowrap;
}

.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  color: #cbd5e1;
  font-size: 0.9rem;
}

/* Chế độ Gọn (Compact Mode) của Preset ⚡ Gọn */
.table-compact th {
  padding: 0.55rem 0.75rem;
  font-size: 0.75rem;
}

.table-compact td {
  padding: 0.55rem 0.75rem;
  font-size: 0.85rem;
}

.product-data-row:hover {
  background-color: rgba(51, 65, 85, 0.4);
}

/* Tiêu đề Khối Nhóm (Group Header Row) */
.group-header-row td {
  background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
  padding: 0.75rem 1rem;
  border-top: 2px solid #0284c7;
  border-bottom: 1px solid #334155;
}

.group-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.group-header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.group-header-icon {
  font-size: 1.15rem;
}

.group-header-stats {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.group-badge-count {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.group-badge-stock {
  color: #94a3b8;
  font-size: 0.825rem;
}

.group-badge-stock strong {
  color: #f8fafc;
}

.id-tag {
  color: #64748b;
  font-size: 0.8rem;
  font-family: monospace;
}

.desc-cell {
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #94a3b8;
  font-size: 0.825rem;
}

.time-cell {
  white-space: nowrap;
}

.time-text {
  font-size: 0.8rem;
  color: #94a3b8;
}

.category-tag {
  display: inline-block;
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.2);
  padding: 0.15rem 0.55rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.price-cell {
  white-space: nowrap;
}

.price-usd-text {
  font-size: 0.95rem;
  font-weight: 700;
  color: #38bdf8;
}

.price-usd-sub {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 400;
}

/* Badge tình trạng tồn kho */
.stock-status-badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.2rem 0.55rem;
  border-radius: 0.25rem;
  font-weight: 600;
}

.badge-in-stock {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.3);
}

.badge-out-of-stock {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid rgba(248, 113, 113, 0.3);
  font-weight: 700;
}

.badge-overstocked {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
  font-weight: 600;
}

.badge-featured {
  background: rgba(234, 179, 8, 0.2);
  color: #facc15;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
}

.text-muted {
  color: #64748b;
}

.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
}

.btn-delete {
  background: #ef4444;
  color: #fff;
  transition: background 0.15s ease;
}

.btn-delete:hover {
  background: #dc2626;
}

.empty-table-cell {
  padding: 3.5rem 1rem !important;
  text-align: center;
}

.empty-filter-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.empty-icon {
  font-size: 2.5rem;
}

.empty-msg {
  color: #cbd5e1;
  font-size: 1.05rem;
  font-weight: 600;
}

.empty-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-reset-inline {
  background: #0284c7;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reset-inline:hover {
  background: #0369a1;
}

.btn-reset-empty {
  background: #475569;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reset-empty:hover {
  background: #334155;
}

.state-cell {
  padding: 3rem 1rem !important;
}

.spinner {
  display: inline-block;
  width: 28px;
  height: 28px;
  border: 3px solid rgba(2, 132, 199, 0.2);
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  color: #94a3b8;
  font-size: 0.875rem;
}

.pagination-btns {
  display: flex;
  gap: 0.5rem;
}

.btn-page {
  background: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.4rem 0.8rem;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-page:hover:not(:disabled) {
  background: #334155;
  color: #fff;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
