<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách và kiểm kê sản phẩm trong kho hàng</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <!-- Task 1 (Vinh): Thanh tìm kiếm thông minh & bộ lọc danh mục Tree Select -->
    <ProductSearchFilters
      :initial-search="searchKeyword"
      :initial-category="selectedCategoryId"
      @filter="handleFilterChange"
    />

    <!-- Task 2 (Công): Bộ lọc khoảng giá (Dual-thumb Slider & Quick Price Chips) -->
    <PriceFilter
      ref="priceFilterRef"
      v-model="priceRange"
      :min="0"
      :max="2000000"
      :step="10000"
    />

    <!-- Task 3 (Hoài): Bộ lọc sản phẩm nổi bật -->
    <div class="featured-filter-bar">
      <label class="featured-toggle-label" for="toggle-featured">
        <div
          id="toggle-featured"
          class="toggle-switch"
          :class="{ active: isFeaturedOnly }"
          role="switch"
          :aria-checked="isFeaturedOnly"
          tabindex="0"
          @click="toggleFeatured"
          @keydown.enter="toggleFeatured"
          @keydown.space.prevent="toggleFeatured"
        >
          <div class="toggle-thumb"></div>
        </div>
        <span class="toggle-text">
          <span v-if="isFeaturedOnly" class="toggle-active-text">⭐ Chỉ sản phẩm nổi bật</span>
          <span v-else>Chỉ hiển thị sản phẩm nổi bật</span>
        </span>
      </label>
    </div>

    <!-- Task 4 (Quân): Bộ lọc nhanh tình trạng tồn kho -->
    <div class="stock-filter-bar">
      <div class="stock-tabs">
        <button
          :class="['tab-btn', selectedStockTab === 'all' ? 'active' : '']"
          @click="changeStockTab('all')"
        >
          Tất cả ({{ stockCounts.all }})
        </button>
        <button
          :class="['tab-btn tab-danger', selectedStockTab === 'out_of_stock' ? 'active' : '']"
          @click="changeStockTab('out_of_stock')"
        >
          🔴 Hết hàng ({{ stockCounts.out_of_stock }})
        </button>
        <button
          :class="['tab-btn tab-warning', selectedStockTab === 'overstocked' ? 'active' : '']"
          @click="changeStockTab('overstocked')"
        >
          🟡 Tồn kho > 2 tháng ({{ stockCounts.overstocked }})
        </button>
        <button
          :class="['tab-btn tab-success', selectedStockTab === 'normal' ? 'active' : '']"
          @click="changeStockTab('normal')"
        >
          🟢 Bình thường ({{ stockCounts.normal }})
        </button>
      </div>
    </div>

    <!-- Task 5 (Ngọc): Thanh công cụ Gom nhóm & Sắp xếp kiểm kê -->
    <div class="view-controls-bar">
      <div class="control-box group-control">
        <label for="group-mode-select" class="control-label">
          <span class="control-icon">📂</span> Chế độ gom nhóm:
        </label>
        <select id="group-mode-select" v-model="groupBy" class="control-select">
          <option value="none">Mặc định (Bảng phẳng không gom nhóm)</option>
          <option value="category">📁 Gom theo Danh mục sản phẩm</option>
          <option value="stock_status">📊 Gom theo Tình trạng kho (Tồn > 2 tháng & > 10sp / Hết hàng)</option>
        </select>
      </div>

      <div class="control-box sort-control">
        <label for="sort-select" class="control-label">
          <span class="control-icon">⇅</span> Sắp xếp thứ tự:
        </label>
        <select id="sort-select" v-model="sortBy" @change="handleSortChange" class="control-select">
          <option value="">Mặc định (Theo mã sản phẩm)</option>
          <option value="price_asc">Giá: Thấp đến Cao</option>
          <option value="price_desc">Giá: Cao đến Thấp</option>
          <option value="stock_asc">Tồn kho: Ít nhất (Ưu tiên kiểm tra)</option>
          <option value="stock_desc">Tồn kho: Nhiều nhất</option>
          <option value="category">Theo Danh mục</option>
        </select>
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

    <!-- Bảng danh sách sản phẩm hiển thị Gom nhóm & Sắp xếp -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Tên Sản Phẩm</th>
            <th>Danh Mục</th>
            <th>Đơn Giá</th>
            <th>Tồn Kho</th>
            <th>Tình Trạng Kho</th>
            <th>Nổi Bật</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <!-- Trạng thái Loading -->
          <tr v-if="loading">
            <td colspan="8" class="text-center py-8 state-cell">
              <div class="spinner"></div>
              <span>Đang tải danh sách sản phẩm...</span>
            </td>
          </tr>

          <!-- Trạng thái Không có sản phẩm nào sau khi lọc -->
          <tr v-else-if="filteredProducts.length === 0">
            <td colspan="8" class="empty-table-cell">
              <div class="empty-filter-box">
                <span class="empty-icon">📦</span>
                <p class="empty-msg">Không tìm thấy sản phẩm nào phù hợp với bộ lọc hiện tại</p>
                <div class="empty-actions">
                  <button @click="resetPriceFilter" class="btn-reset-inline">
                    🔄 Đặt lại giá
                  </button>
                  <button @click="resetAllFilters" class="btn-reset-empty">
                    Xóa tất cả bộ lọc
                  </button>
                </div>
              </div>
            </td>
          </tr>

          <!-- Dữ liệu hiển thị (Hỗ trợ Gom nhóm theo Khối hoặc Bảng phẳng) -->
          <template v-else v-for="group in groupedProducts" :key="group.key">
            <!-- Dòng Tiêu đề Khối Nhóm (Chỉ hiện khi bật Gom nhóm) -->
            <tr v-if="groupBy !== 'none'" class="group-header-row">
              <td colspan="8">
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

            <!-- Các dòng sản phẩm bên trong nhóm -->
            <tr v-for="prod in group.items" :key="prod.id" class="product-data-row">
              <td><code>{{ prod.sku }}</code></td>
              <td class="font-medium text-white">{{ prod.name }}</td>
              <td>
                <span class="category-tag">
                  {{ categoryMap[prod.category_id] || `#${prod.category_id}` }}
                </span>
              </td>
              <td class="price-cell">
                <div class="price-vnd-text">{{ formatVND(getProductPriceVND(prod.price)) }}</div>
                <div class="price-usd-sub">${{ Number(prod.price).toFixed(2) }}</div>
              </td>
              <td class="stock-cell font-semibold">
                {{ prod.stock }} cái
              </td>
              <td>
                <span :class="['stock-status-badge', getStockStatus(prod).badgeClass]">
                  {{ getStockStatus(prod).label }}
                </span>
              </td>
              <td>
                <span v-if="prod.is_featured" class="badge-featured">⭐ Nổi bật</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
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
import { ref, computed, onMounted } from 'vue';
import api from '../../lib/api';
import type { Product } from '../../types';
import PriceFilter from '../../components/PriceFilter.vue';
import ProductSearchFilters from '../../components/admin/ProductSearchFilters.vue';
import { getProductPriceVND, formatVND } from '../../utils/format';

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const errorMessage = ref('');

// Bộ nhớ cache tên danh mục để hiển thị đẹp thay vì ID thô
const categoryMap = ref<Record<number, string>>({});

// State Task 1: Tìm kiếm & Đa danh mục (Vinh)
const searchKeyword = ref('');
const selectedCategoryId = ref<number | null>(null);

// State Task 2: Khoảng giá (Công)
const priceFilterRef = ref<InstanceType<typeof PriceFilter> | null>(null);
const priceRange = ref<[number, number]>([0, 2000000]);

// State Task 3: Sản phẩm nổi bật (Hoài)
const isFeaturedOnly = ref(false);

// State Task 4: Tình trạng tồn kho (Quân)
type StockFilterType = 'all' | 'out_of_stock' | 'overstocked' | 'normal';
const selectedStockTab = ref<StockFilterType>('all');

// State Task 5: Gom nhóm & Sắp xếp (Ngọc)
const groupBy = ref<'none' | 'category' | 'stock_status'>('none');
const sortBy = ref('');

// Hàm tính ngày lưu kho và phân loại tình trạng tồn kho theo chuẩn nghiệp vụ US1:
function getStockStatus(prod: Product) {
  if (prod.stock === 0) {
    return {
      key: 'out_of_stock',
      label: 'Hết hàng',
      badgeClass: 'badge-out-of-stock',
    };
  }

  if (prod.created_at && prod.stock > 10) {
    const createdTime = new Date(prod.created_at).getTime();
    const now = Date.now();
    const sixtyDaysMs = 60 * 24 * 60 * 60 * 1000;
    if (now - createdTime >= sixtyDaysMs) {
      return {
        key: 'overstocked',
        label: 'Tồn kho > 2 tháng',
        badgeClass: 'badge-overstocked',
      };
    }
  }

  return {
    key: 'normal',
    label: 'Còn hàng',
    badgeClass: 'badge-in-stock',
  };
}

// Đếm số lượng sản phẩm theo từng tab tồn kho (Task 4)
const stockCounts = computed(() => {
  const counts = { all: 0, out_of_stock: 0, overstocked: 0, normal: 0 };
  for (const prod of products.value) {
    counts.all++;
    const status = getStockStatus(prod).key as StockFilterType;
    if (status in counts) {
      counts[status]++;
    }
  }
  return counts;
});

// Lọc sản phẩm hiển thị theo khoảng giá đã chọn (Task 2)
const filteredProducts = computed(() => {
  const [minPrice, maxPrice] = priceRange.value;
  return products.value.filter((prod) => {
    // 1. Lọc theo giá (Task 2)
    const vndPrice = getProductPriceVND(prod.price);
    if (vndPrice < minPrice || vndPrice > maxPrice) {
      return false;
    }
    // 2. Lọc theo tab tồn kho nếu đã chọn tab cụ thể (Task 4)
    if (selectedStockTab.value !== 'all') {
      if (getStockStatus(prod).key !== selectedStockTab.value) {
        return false;
      }
    }
    return true;
  });
});

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
        title: 'Hàng tồn đọng lâu ngày (> 2 tháng & > 10 cái - Cần xả kho)',
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
    if (sortBy.value) {
      params.sort_by = sortBy.value;
    }

    const res = await api.get('/products', { params });
    if (res.data.success) {
      products.value = res.data.data.items;
      totalProducts.value = res.data.data.total;
      totalPages.value = res.data.data.total_pages;
    } else {
      errorMessage.value = res.data.message || 'Không thể tải danh sách sản phẩm';
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Có lỗi xảy ra khi tải sản phẩm';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

// Xử lý đổi tiêu chí sắp xếp (Task 5)
function handleSortChange() {
  fetchProducts(1);
}

// Xử lý đổi bộ lọc Task 1 (Search / Category)
function handleFilterChange(payload: { search: string; categoryId: number | null }) {
  searchKeyword.value = payload.search;
  selectedCategoryId.value = payload.categoryId;
  currentPage.value = 1;
  fetchProducts(1);
}

// Xử lý bật/tắt nổi bật (Task 3)
function toggleFeatured() {
  isFeaturedOnly.value = !isFeaturedOnly.value;
  currentPage.value = 1;
  fetchProducts(1);
}

// Xử lý đổi tab tồn kho (Task 4)
function changeStockTab(tab: StockFilterType) {
  selectedStockTab.value = tab;
  currentPage.value = 1;
  fetchProducts(1);
}

// Chuyển trang
function changePage(page: number) {
  fetchProducts(page);
}

// Đặt lại khoảng giá (Task 2)
function resetPriceFilter() {
  if (priceFilterRef.value) {
    priceFilterRef.value.reset();
  } else {
    priceRange.value = [0, 2000000];
  }
}

// Đặt lại toàn bộ bộ lọc
function resetAllFilters() {
  searchKeyword.value = '';
  selectedCategoryId.value = null;
  selectedStockTab.value = 'all';
  isFeaturedOnly.value = false;
  resetPriceFilter();
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
  fetchCategoriesMap();
  fetchProducts();
});
</script>

<style scoped>
.admin-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
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

/* Thanh điều khiển Gom nhóm & Sắp xếp (Task 5) */
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
  font-size: 0.875rem;
  color: #cbd5e1;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.control-icon {
  font-size: 1rem;
}

.control-select {
  padding: 0.45rem 0.85rem;
  border-radius: 0.375rem;
  background-color: #0f172a;
  border: 1px solid #475569;
  color: #f8fafc;
  cursor: pointer;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.control-select:focus {
  border-color: #38bdf8;
}

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
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #0f172a;
  color: #94a3b8;
  padding: 0.85rem 1rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  border-bottom: 1px solid #334155;
  text-align: left;
}

.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  color: #cbd5e1;
  font-size: 0.9rem;
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

.price-vnd-text {
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

.pagination-bar strong {
  color: #38bdf8;
  font-size: 1rem;
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
