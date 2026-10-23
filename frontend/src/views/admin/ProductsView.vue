<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách và kiểm tra tình trạng tồn kho sản phẩm</p>
      </div>
      <div class="header-actions">
        <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
      </div>
    </div>

    <!-- Bảng danh sách sản phẩm tích hợp Sticky Filter Bar -->
    <div class="table-card" :style="{ '--filter-bar-h': filterBarHeight + 'px' }">
      <!-- Sticky Filter Bar gắn liền đỉnh bảng -->
      <div ref="stickyFilterBarRef" class="sticky-filter-bar">
        <div class="filter-controls">
          <!-- Ô tìm kiếm tên sản phẩm theo thời gian thực -->
          <div class="filter-item search-item">
            <label class="control-label" for="product-search-input">Tìm kiếm</label>
            <div class="input-with-icon">
              <span class="search-icon">🔍</span>
              <input
                id="product-search-input"
                type="text"
                v-model="searchQuery"
                @input="handleRealtimeSearch"
                placeholder="Nhập tên sản phẩm..."
                class="form-control search-input"
              />
            </div>
          </div>

          <!-- Chọn danh mục -->
          <div class="filter-item category-item">
            <label class="control-label" for="category-select">Danh mục</label>
            <select
              id="category-select"
              v-model="selectedCategoryId"
              @change="handleCategoryChange"
              class="form-control select-control"
            >
              <option value="">-- Tất cả danh mục --</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <!-- Khoảng giá tối thiểu & tối đa (áp dụng tự động) -->
          <div class="filter-item price-group-item">
            <label class="control-label">Khoảng giá ($)</label>
            <div class="price-inputs-row">
              <div class="input-with-prefix">
                <span class="currency-symbol">$</span>
                <input
                  id="min-price"
                  v-model="minPriceInput"
                  type="text"
                  inputmode="decimal"
                  placeholder="Min"
                  class="form-control price-input"
                  @keydown="handlePriceKeydown"
                  @input="handlePriceInput('min')"
                  @paste="handlePricePaste($event, 'min')"
                />
              </div>
              <span class="range-divider">—</span>
              <div class="input-with-prefix">
                <span class="currency-symbol">$</span>
                <input
                  id="max-price"
                  v-model="maxPriceInput"
                  type="text"
                  inputmode="decimal"
                  placeholder="Max"
                  class="form-control price-input"
                  @keydown="handlePriceKeydown"
                  @input="handlePriceInput('max')"
                  @paste="handlePricePaste($event, 'max')"
                />
              </div>
            </div>
          </div>

          <!-- Nút Sản phẩm nổi bật được đưa vào trong Sticky Bar -->
          <div class="filter-item featured-item">
            <label class="control-label">Nổi bật</label>
            <button
              type="button"
              @click="sortByFeatured"
              :class="['btn-featured-toggle', isFeaturedSorted ? 'active' : '']"
              title="Đẩy các sản phẩm nổi bật lên đầu"
            >
              <span class="star-icon">⭐</span>
              <span>Nổi bật</span>
            </button>
          </div>

          <!-- Nhóm nút bấm: Đặt lại (đã bỏ nút Lọc) -->
          <div class="filter-actions">
            <button
              v-if="isFilterActive"
              @click="handleReset"
              class="btn-reset"
              id="btn-reset-price"
            >
              Đặt lại
            </button>
          </div>
        </div>

        <!-- Thông báo lỗi khi min > max -->
        <div v-if="validationWarning" class="filter-warning">
          ⚠️ {{ validationWarning }}
        </div>

        <!-- Badge hiển thị bộ lọc đang áp dụng -->
        <div v-if="isFilterActive && !validationWarning" class="active-filter-badge-row">
          <div class="active-filter-badge">
            <span>Đang áp dụng: <strong>{{ activeFilterText }}</strong></span>
            <button @click="handleReset" class="btn-clear-tag" title="Xóa toàn bộ bộ lọc">✕</button>
          </div>
        </div>
      </div>

      <table class="data-table">
        <colgroup>
          <col style="width: 5%" />
          <col style="width: 27%" />
          <col style="width: 14%" />
          <col style="width: 11%" />
          <col style="width: 15%" />
          <col style="width: 17%" />
          <col style="width: 11%" />
        </colgroup>
        <thead>
          <tr>
            <th class="text-center col-featured-th" title="Sản phẩm nổi bật">⭐</th>
            <th class="th-sortable" @click="toggleSort('name')" title="Sắp xếp theo Tên (A-Z / Z-A)">
              <div class="th-header-inner">
                <span>Tên Sản Phẩm</span>
                <span :class="['sort-badge', sortBy.startsWith('name_') ? 'sort-active' : '']">
                  {{ sortBy === 'name_asc' ? '▲' : (sortBy === 'name_desc' ? '▼' : '⇅') }}
                </span>
              </div>
            </th>
            <th>Danh Mục</th>
            <th class="th-sortable" @click="toggleSort('price')" title="Sắp xếp theo Giá (Tăng / Giảm)">
              <div class="th-header-inner">
                <span>Đơn Giá</span>
                <span :class="['sort-badge', sortBy.startsWith('price_') ? 'sort-active' : '']">
                  {{ sortBy === 'price_asc' ? '▲' : (sortBy === 'price_desc' ? '▼' : '⇅') }}
                </span>
              </div>
            </th>
            <th class="th-sortable" @click="toggleSort('stock')" title="Sắp xếp theo Số lượng hàng (Tăng / Giảm)">
              <div class="th-header-inner">
                <span>Số Lượng Hàng</span>
                <span :class="['sort-badge', sortBy.startsWith('stock_') ? 'sort-active' : '']">
                  {{ sortBy === 'stock_asc' ? '▲' : (sortBy === 'stock_desc' ? '▼' : '⇅') }}
                </span>
              </div>
            </th>
            <th title="Thời điểm nhập hàng hoặc hết hàng gần nhất">Cập Nhật Kho</th>
            <th class="text-right">Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center py-6 text-muted">Đang tải sản phẩm...</td>
          </tr>
          <tr v-else-if="errorMessage">
            <td colspan="7" class="text-center py-6 error-cell">
              <span>{{ errorMessage }}</span>
              <button @click="fetchProducts(currentPage)" class="btn-sm btn-retry">Thử lại</button>
            </td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td colspan="7" class="empty-state">
              <div class="empty-state-content">
                <div class="empty-icon">🔍</div>
                <h3 class="empty-title">Không tìm thấy sản phẩm nào</h3>
                <p v-if="isFilterActive" class="empty-desc">
                  Không có sản phẩm nào phù hợp với bộ lọc đang chọn: <strong>{{ activeFilterText }}</strong>.
                  <br />Bạn có thể thử tìm từ khóa khác hoặc bấm đặt lại bộ lọc.
                </p>
                <p v-else class="empty-desc">Danh sách sản phẩm hiện đang trống.</p>
                <button v-if="isFilterActive" @click="handleReset" class="btn-primary btn-sm btn-empty-reset">
                  Xoá bộ lọc và xem tất cả
                </button>
              </div>
            </td>
          </tr>
          <tr v-for="prod in products" :key="prod.id" v-else>
            <td class="text-center">
              <span v-if="prod.is_featured" class="star-icon-featured" title="Sản phẩm nổi bật">⭐</span>
              <span v-else class="text-muted text-dim-dash">—</span>
            </td>
            <td class="font-medium prod-name-cell" :title="prod.name">{{ prod.name }}</td>
            <td>
              <span class="category-pill" :title="'ID: #' + prod.category_id">
                {{ getCategoryName(prod.category_id) }}
              </span>
            </td>
            <td class="price-tag">${{ Number(prod.price).toFixed(2) }}</td>
            <td>
              <StockBadge :stock="prod.stock" />
            </td>
            <td>
              <div class="stock-time-col">
                <!-- Dòng 1: Thời điểm ngày giờ -->
                <div
                  v-if="prod.stock === 0 && prod.out_of_stock_at"
                  class="stock-time-date text-out"
                  :title="'Hết hàng lúc: ' + formatFullDateTime(prod.out_of_stock_at)"
                >
                  {{ formatShortDateTime(prod.out_of_stock_at) }}
                </div>
                <div
                  v-else-if="prod.stock > 0 && prod.restocked_at"
                  class="stock-time-date text-restock"
                  :title="'Nhập hàng lúc: ' + formatFullDateTime(prod.restocked_at)"
                >
                  {{ formatShortDateTime(prod.restocked_at) }}
                </div>
                <div
                  v-else-if="prod.updated_at"
                  class="stock-time-date"
                  :title="'Cập nhật lúc: ' + formatFullDateTime(prod.updated_at)"
                >
                  {{ formatShortDateTime(prod.updated_at) }}
                </div>
                <div v-else class="text-muted text-dim-dash">—</div>

                <!-- Dòng 2: Thời gian tương đối kèm trạng thái (Thêm hàng / Đã bán / Hết hàng) -->
                <div
                  class="stock-update-line"
                  :title="'Thời gian cập nhật gần nhất: ' + formatFullDateTime(prod.updated_at)"
                >
                  <span :class="['stock-action-text', getStockActionInfo(prod).cls]">
                    {{ getStockActionInfo(prod).label }}
                  </span>
                  <span class="stock-action-sep">•</span>
                  <span class="stock-update-text">
                    {{ formatRelativeTime(prod.updated_at) }}
                  </span>
                </div>
              </div>
            </td>
            <td class="text-right">
              <div class="action-buttons justify-end">
                <button
                  @click="openStockModal(prod)"
                  class="btn-sm btn-stock"
                  title="Cập nhật số lượng tồn kho"
                >
                  Sửa kho
                </button>
                <button @click="handleDelete(prod.id)" class="btn-sm btn-delete">Xoá</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Phân trang -->
    <div v-if="totalProducts > 0" class="pagination-bar">
      <span>Trang {{ currentPage }} / {{ totalPages }} (Tổng cộng {{ totalProducts }} sản phẩm)</span>
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

    <!-- Modal Cập nhật Tồn Kho -->
    <div v-if="showStockModal && selectedProduct" class="modal-backdrop" @click.self="closeStockModal">
      <div class="modal-box">
        <div class="modal-header">
          <h3>Cập Nhật Tồn Kho</h3>
          <button @click="closeStockModal" class="btn-close">&times;</button>
        </div>
        <form @submit.prevent="handleStockSubmit" class="modal-body">
          <div class="product-info-box">
            <div class="info-row">
              <span class="info-label">Mã SKU:</span>
              <code>{{ selectedProduct.sku }}</code>
            </div>
            <div class="info-row">
              <span class="info-label">Sản phẩm:</span>
              <strong>{{ selectedProduct.name }}</strong>
            </div>
            <div class="info-row">
              <span class="info-label">Số lượng hiện tại:</span>
              <StockBadge :stock="selectedProduct.stock" />
            </div>
            <div class="info-row">
              <span class="info-label">Cập nhật gần nhất:</span>
              <span class="info-value-time" :title="formatFullDateTime(selectedProduct.updated_at)">
                🕒 {{ formatRelativeTime(selectedProduct.updated_at) }} ({{ formatFullDateTime(selectedProduct.updated_at) }})
              </span>
            </div>
            <div v-if="selectedProduct.restocked_at" class="info-row">
              <span class="info-label">Lần nhập gần nhất:</span>
              <span class="info-value-time" :title="formatFullDateTime(selectedProduct.restocked_at)">
                📦 {{ formatRelativeTime(selectedProduct.restocked_at) }} ({{ formatFullDateTime(selectedProduct.restocked_at) }})
              </span>
            </div>
            <div v-if="selectedProduct.out_of_stock_at" class="info-row">
              <span class="info-label">Lần hết gần nhất:</span>
              <span class="info-value-time" :title="formatFullDateTime(selectedProduct.out_of_stock_at)">
                ⏳ {{ formatRelativeTime(selectedProduct.out_of_stock_at) }} ({{ formatFullDateTime(selectedProduct.out_of_stock_at) }})
              </span>
            </div>
          </div>

          <div class="form-group">
            <label for="stockInput">Số Lượng Hàng Mới *</label>
            <input
              id="stockInput"
              type="number"
              v-model.number="stockFormValue"
              min="0"
              step="1"
              required
              class="form-control"
              placeholder="Nhập số lượng tồn kho (>= 0)"
            />
            <small v-if="stockFormError" class="field-error">{{ stockFormError }}</small>
            <small v-else class="field-hint">Nhập số nguyên không âm (0 = Hết hàng, > 0 = Còn hàng).</small>
          </div>

          <div v-if="modalError" class="alert-error">
            {{ modalError }}
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeStockModal" class="btn-cancel" :disabled="updatingStock">
              Hủy
            </button>
            <button type="submit" class="btn-primary" :disabled="updatingStock">
              {{ updatingStock ? 'Đang lưu...' : 'Lưu Thay Đổi' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../../lib/api';
import type { Product, Category } from '../../types';
import StockBadge from '../../components/StockBadge.vue';

const stickyFilterBarRef = ref<HTMLElement | null>(null);
const filterBarHeight = ref(68);
let filterBarResizeObserver: ResizeObserver | null = null;

const products = ref<Product[]>([]);
const categories = ref<Category[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const errorMessage = ref<string | null>(null);

// Modal tồn kho
const showStockModal = ref(false);
const selectedProduct = ref<Product | null>(null);
const stockFormValue = ref<number>(0);
const stockFormError = ref<string | null>(null);
const updatingStock = ref(false);
const modalError = ref<string | null>(null);

const isFeaturedSorted = ref(false);

// Tìm kiếm & Danh mục
const searchQuery = ref('');
const selectedCategoryId = ref<number | ''>('');

// Bộ lọc giá & Sắp xếp
const minPriceInput = ref<string>('');
const maxPriceInput = ref<string>('');
const appliedMinPrice = ref<string>('');
const appliedMaxPrice = ref<string>('');
const sortBy = ref<string>('');
const validationWarning = ref<string>('');

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;
let priceDebounceTimer: ReturnType<typeof setTimeout> | null = null;

const isFilterActive = computed(() => {
  return (
    searchQuery.value.trim() !== '' ||
    selectedCategoryId.value !== '' ||
    appliedMinPrice.value !== '' ||
    appliedMaxPrice.value !== '' ||
    sortBy.value !== ''
  );
});

const activeFilterText = computed(() => {
  const parts: string[] = [];

  if (searchQuery.value.trim() !== '') {
    parts.push(`Tìm kiếm: "${searchQuery.value.trim()}"`);
  }

  if (selectedCategoryId.value !== '') {
    parts.push(`Danh mục: ${getCategoryName(Number(selectedCategoryId.value))}`);
  }

  if (appliedMinPrice.value !== '' && appliedMaxPrice.value !== '') {
    parts.push(`giá $${Number(appliedMinPrice.value).toFixed(2)} - $${Number(appliedMaxPrice.value).toFixed(2)}`);
  } else if (appliedMinPrice.value !== '') {
    parts.push(`giá từ $${Number(appliedMinPrice.value).toFixed(2)} trở lên`);
  } else if (appliedMaxPrice.value !== '') {
    parts.push(`giá ≤ $${Number(appliedMaxPrice.value).toFixed(2)}`);
  }

  if (sortBy.value === 'name_asc') parts.push('tên A → Z');
  else if (sortBy.value === 'name_desc') parts.push('tên Z → A');
  else if (sortBy.value === 'price_asc') parts.push('giá tăng dần');
  else if (sortBy.value === 'price_desc') parts.push('giá giảm dần');
  else if (sortBy.value === 'stock_asc') parts.push('số lượng hàng ít → nhiều');
  else if (sortBy.value === 'stock_desc') parts.push('số lượng hàng nhiều → ít');

  return parts.join(' • ');
});

function handleRealtimeSearch() {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    fetchProducts(1);
  }, 250);
}

function handleCategoryChange() {
  fetchProducts(1);
}

function handlePriceKeydown(event: KeyboardEvent) {
  const allowed = [
    'Backspace', 'Tab', 'Delete',
    'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
    'Home', 'End', 'Enter',
  ];
  if (allowed.includes(event.key) || event.ctrlKey || event.metaKey) return;
  if (['e', 'E', '+', '-'].includes(event.key)) {
    event.preventDefault();
    return;
  }
  if (event.key === '.') {
    const input = event.target as HTMLInputElement;
    if (input && input.value.includes('.')) event.preventDefault();
    return;
  }
  if (!/^[0-9]$/.test(event.key)) event.preventDefault();
}

function sanitizePriceInput(field: 'min' | 'max') {
  const current = field === 'min' ? minPriceInput.value : maxPriceInput.value;
  if (!current) return;
  let sanitized = current.replace(/[^0-9.]/g, '');
  const parts = sanitized.split('.');
  if (parts.length > 2) sanitized = parts[0] + '.' + parts.slice(1).join('');
  if (field === 'min') minPriceInput.value = sanitized;
  else maxPriceInput.value = sanitized;
}

function handlePriceInput(field: 'min' | 'max') {
  sanitizePriceInput(field);
  if (priceDebounceTimer) clearTimeout(priceDebounceTimer);
  priceDebounceTimer = setTimeout(() => {
    applyPriceFilter();
  }, 350);
}

function handlePricePaste(event: ClipboardEvent, targetField: 'min' | 'max') {
  event.preventDefault();
  const text = event.clipboardData?.getData('text') || '';
  let sanitized = text.replace(/[^0-9.]/g, '');
  const parts = sanitized.split('.');
  if (parts.length > 2) sanitized = parts[0] + '.' + parts.slice(1).join('');
  if (targetField === 'min') minPriceInput.value = sanitized;
  else maxPriceInput.value = sanitized;
  handlePriceInput(targetField);
}

function applyPriceFilter() {
  validationWarning.value = '';

  const min = minPriceInput.value !== '' ? Number(minPriceInput.value) : null;
  const max = maxPriceInput.value !== '' ? Number(maxPriceInput.value) : null;

  if (min !== null && min < 0) {
    validationWarning.value = 'Giá tối thiểu không được là số âm.';
    return;
  }
  if (max !== null && max < 0) {
    validationWarning.value = 'Giá tối đa không được là số âm.';
    return;
  }
  if (min !== null && max !== null && min > max) {
    validationWarning.value = `Giá tối thiểu ($${min}) đang lớn hơn giá tối đa ($${max}).`;
  }

  appliedMinPrice.value = minPriceInput.value;
  appliedMaxPrice.value = maxPriceInput.value;
  fetchProducts(1);
}

function toggleSort(field: 'name' | 'price' | 'stock') {
  if (sortBy.value === `${field}_asc`) {
    sortBy.value = `${field}_desc`;
  } else if (sortBy.value === `${field}_desc`) {
    sortBy.value = '';
  } else {
    sortBy.value = `${field}_asc`;
  }
  fetchProducts(1);
}

function handleReset() {
  searchQuery.value = '';
  selectedCategoryId.value = '';
  minPriceInput.value = '';
  maxPriceInput.value = '';
  appliedMinPrice.value = '';
  appliedMaxPrice.value = '';
  sortBy.value = '';
  validationWarning.value = '';
  fetchProducts(1);
}

async function fetchCategories() {
  try {
    const res = await api.get('/categories', { params: { page: 1, page_size: 100 } });
    if (res.data.success) {
      categories.value = res.data.data.items;
    }
  } catch (err) {
    console.error('Lỗi tải danh mục:', err);
  }
}

function getCategoryName(categoryId: number): string {
  const cat = categories.value.find((c) => c.id === categoryId);
  return cat ? cat.name : `#${categoryId}`;
}

function formatShortDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '';
  const pad = (n: number) => (n < 10 ? '0' + n : String(n));
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  const day = pad(d.getDate());
  const month = pad(d.getMonth() + 1);
  const year = d.getFullYear();
  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

function formatFullDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '';
  const pad = (n: number) => (n < 10 ? '0' + n : String(n));
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  const seconds = pad(d.getSeconds());
  const day = pad(d.getDate());
  const month = pad(d.getMonth() + 1);
  const year = d.getFullYear();
  return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}

function formatRelativeTime(dateStr: string | null | undefined): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '';
  const now = new Date();
  const diffSec = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diffSec < 60) return 'Vừa xong';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin} phút trước`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours} giờ trước`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays} ngày trước`;

  const pad = (n: number) => (n < 10 ? '0' + n : String(n));
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

function getStockActionInfo(prod: Product): { label: string; cls: string } {
  if (prod.stock === 0 || prod.last_stock_action === 'OUT_OF_STOCK') {
    return { label: 'Hết hàng', cls: 'status-out' };
  }
  if (prod.last_stock_action === 'SOLD') {
    return { label: 'Đã bán', cls: 'status-sold' };
  }
  return { label: 'Thêm hàng', cls: 'status-restock' };
}

async function fetchProducts(page = 1) {
  loading.value = true;
  errorMessage.value = null;
  currentPage.value = page;
  try {
    const params: Record<string, any> = {
      page,
      page_size: 20,
    };
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim();
    }
    if (selectedCategoryId.value !== '') {
      params.category_id = Number(selectedCategoryId.value);
    }
    if (appliedMinPrice.value !== '') {
      params.min_price = appliedMinPrice.value;
    }
    if (appliedMaxPrice.value !== '') {
      params.max_price = appliedMaxPrice.value;
    }
    if (sortBy.value !== '') {
      params.sort_by = sortBy.value;
    }

    const res = await api.get('/products', { params });
    if (res.data.success) {
      products.value = res.data.data.items;
      totalProducts.value = res.data.data.total;
      totalPages.value = res.data.data.total_pages;
      isFeaturedSorted.value = false;
    } else {
      errorMessage.value = res.data.message || 'Không thể lấy dữ liệu sản phẩm.';
    }
  } catch (err: any) {
    console.error('Lỗi tải danh sách sản phẩm:', err);
    errorMessage.value =
      err.response?.data?.error?.message ||
      'Không thể kết nối đến máy chủ Backend. Vui lòng kiểm tra lại dịch vụ.';
  } finally {
    loading.value = false;
  }
}

function changePage(page: number) {
  fetchProducts(page);
}

function sortByFeatured() {
  if (!isFeaturedSorted.value) {
    products.value = [...products.value].sort((a, b) => {
      if (a.is_featured !== b.is_featured) {
        return (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0);
      }
      return a.id - b.id;
    });
    isFeaturedSorted.value = true;
  } else {
    products.value = [...products.value].sort((a, b) => a.id - b.id);
    isFeaturedSorted.value = false;
  }
}

function openCreateModal() {
  alert('Chức năng thêm sản phẩm qua form quản trị đã sẵn sàng kết nối API POST /products.');
}

function openStockModal(prod: Product) {
  selectedProduct.value = prod;
  stockFormValue.value = Number.isInteger(prod.stock) && prod.stock >= 0 ? prod.stock : 0;
  stockFormError.value = null;
  modalError.value = null;
  showStockModal.value = true;
}

function closeStockModal() {
  showStockModal.value = false;
  selectedProduct.value = null;
  stockFormError.value = null;
  modalError.value = null;
}

async function handleStockSubmit() {
  if (!selectedProduct.value) return;

  if (stockFormValue.value === null || stockFormValue.value === undefined || isNaN(stockFormValue.value)) {
    stockFormError.value = 'Vui lòng nhập số lượng hợp lệ.';
    return;
  }
  if (stockFormValue.value < 0) {
    stockFormError.value = 'Số lượng tồn kho không được là số âm (>= 0).';
    return;
  }
  if (!Number.isInteger(stockFormValue.value)) {
    stockFormError.value = 'Số lượng tồn kho phải là số nguyên.';
    return;
  }

  updatingStock.value = true;
  modalError.value = null;

  try {
    const res = await api.put(`/products/${selectedProduct.value.id}`, {
      stock: stockFormValue.value,
    });
    if (res.data.success) {
      closeStockModal();
      await fetchProducts(currentPage.value);
    } else {
      modalError.value = res.data.message || 'Cập nhật thất bại.';
    }
  } catch (err: any) {
    console.error('Lỗi cập nhật tồn kho:', err);
    modalError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail?.[0]?.msg ||
      'Có lỗi xảy ra khi lưu số lượng tồn kho.';
  } finally {
    updatingStock.value = false;
  }
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
  fetchCategories();
  fetchProducts();

  if (stickyFilterBarRef.value) {
    const updateHeight = () => {
      if (stickyFilterBarRef.value) {
        filterBarHeight.value = stickyFilterBarRef.value.offsetHeight;
      }
    };
    updateHeight();
    filterBarResizeObserver = new ResizeObserver(updateHeight);
    filterBarResizeObserver.observe(stickyFilterBarRef.value);
  }
});

onUnmounted(() => {
  if (filterBarResizeObserver) {
    filterBarResizeObserver.disconnect();
  }
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
  if (priceDebounceTimer) clearTimeout(priceDebounceTimer);
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
.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.btn-featured {
  background: rgba(234, 179, 8, 0.15);
  color: #facc15;
  border: 1px solid rgba(234, 179, 8, 0.4);
  padding: 0.6rem 1.2rem;
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-featured:hover {
  background: rgba(234, 179, 8, 0.25);
}
.btn-featured.active {
  background: #eab308;
  color: #0f172a;
  border-color: #eab308;
}
.btn-primary {
  background: #0284c7;
  color: #fff;
  border: none;
  padding: 0.55rem 1.15rem;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) {
  background: #0369a1;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table Card & Sticky Filter Bar */
.table-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.625rem;
  box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.3);
  position: relative;
}

.sticky-filter-bar {
  position: sticky;
  top: 58px;
  z-index: 20;
  background: #162032;
  border-bottom: 1px solid #334155;
  border-top-left-radius: 0.625rem;
  border-top-right-radius: 0.625rem;
  padding: 0.75rem 1rem;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.filter-controls {
  display: flex;
  align-items: flex-end;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.control-label {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-control {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  font-size: 0.825rem;
  padding: 0.4rem 0.65rem;
  outline: none;
  height: 35px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
}

.search-item {
  flex: 1;
  min-width: 180px;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.65rem;
  font-size: 0.75rem;
  opacity: 0.6;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 1.85rem;
}

.category-item .select-control {
  cursor: pointer;
  min-width: 155px;
}

.sort-item .select-control {
  cursor: pointer;
  min-width: 165px;
}

.price-inputs-row {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.input-with-prefix {
  position: relative;
  display: flex;
  align-items: center;
  width: 95px;
}

.currency-symbol {
  position: absolute;
  left: 0.55rem;
  color: #64748b;
  font-weight: 600;
  pointer-events: none;
  font-size: 0.8rem;
}

.price-input {
  width: 100%;
  padding-left: 1.35rem;
  -moz-appearance: textfield;
  appearance: textfield;
}

.price-input::-webkit-outer-spin-button,
.price-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.range-divider {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 700;
}

/* Nút Sản phẩm nổi bật trong Sticky Bar */
.featured-item {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.btn-featured-toggle {
  height: 35px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0 0.8rem;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(234, 179, 8, 0.1);
  color: #facc15;
  border: 1px solid rgba(234, 179, 8, 0.35);
  white-space: nowrap;
}

.btn-featured-toggle:hover {
  background: rgba(234, 179, 8, 0.2);
  border-color: rgba(234, 179, 8, 0.5);
}

.btn-featured-toggle.active {
  background: #eab308;
  color: #0f172a;
  border-color: #eab308;
  box-shadow: 0 0 10px rgba(234, 179, 8, 0.35);
}

.star-icon {
  font-size: 0.85rem;
  line-height: 1;
}

.filter-actions {
  display: flex;
  gap: 0.4rem;
}

.btn-search {
  padding: 0 0.95rem;
  font-size: 0.825rem;
  height: 35px;
}

.btn-reset {
  background: #334155;
  color: #cbd5e1;
  border: 1px solid #475569;
  padding: 0 0.8rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.825rem;
  cursor: pointer;
  height: 35px;
  transition: all 0.2s;
}

.btn-reset:hover {
  background: #475569;
  color: #f8fafc;
}

.filter-warning {
  margin-top: 0.6rem;
  padding: 0.5rem 0.75rem;
  background: rgba(234, 179, 8, 0.12);
  border: 1px solid rgba(234, 179, 8, 0.35);
  color: #facc15;
  border-radius: 0.375rem;
  font-size: 0.8rem;
}

.active-filter-badge-row {
  margin-top: 0.55rem;
}

.active-filter-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(2, 132, 199, 0.15);
  border: 1px solid rgba(2, 132, 199, 0.35);
  color: #38bdf8;
  padding: 0.25rem 0.7rem;
  border-radius: 9999px;
  font-size: 0.775rem;
}

.btn-clear-tag {
  background: none;
  border: none;
  color: #38bdf8;
  cursor: pointer;
  font-weight: 700;
  padding: 0 0.15rem;
  font-size: 0.75rem;
  line-height: 1;
}

.btn-clear-tag:hover {
  color: #fff;
}

/* Data Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.data-table th {
  position: sticky;
  top: calc(58px + var(--filter-bar-h, 68px));
  z-index: 15;
  background: #0f172a;
  color: #94a3b8;
  padding: 0.75rem 1rem;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #334155;
  text-align: left;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #334155;
  color: #cbd5e1;
  font-size: 0.875rem;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.015);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.prod-name-cell {
  font-weight: 600;
  color: #f8fafc;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.th-sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.th-sortable:hover {
  background-color: #1a2538 !important;
}

.th-content,
.th-header-inner {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.sort-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  font-size: 0.68rem;
  color: #64748b;
  border-radius: 0.25rem;
  background: rgba(51, 65, 85, 0.4);
  flex-shrink: 0;
  transition: all 0.2s ease;
  line-height: 1;
}

.sort-badge.sort-active {
  background: rgba(2, 132, 199, 0.25);
  color: #38bdf8;
  font-weight: 700;
  border: 1px solid rgba(2, 132, 199, 0.4);
}

.category-pill {
  display: inline-block;
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  padding: 0.18rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.price-tag {
  color: #38bdf8;
  font-weight: 600;
}

.col-featured-th {
  font-size: 0.9rem !important;
  user-select: none;
}

.star-icon-featured {
  font-size: 1.05rem;
  line-height: 1;
  display: inline-block;
  filter: drop-shadow(0 0 4px rgba(250, 204, 21, 0.45));
}

.text-dim-dash {
  color: #475569;
  font-size: 0.9rem;
}

.text-right {
  text-align: right;
}

.justify-end {
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  gap: 0.35rem;
}

.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-stock {
  background: #0284c7;
  color: #fff;
}

.btn-stock:hover {
  background: #0369a1;
}

.btn-delete {
  background: #ef4444;
  color: #fff;
}

.btn-delete:hover {
  background: #dc2626;
}
.btn-retry {
  background: #eab308;
  color: #0f172a;
  margin-left: 0.75rem;
  font-weight: 600;
}
.error-cell {
  color: #f87171;
}
.empty-state {
  padding: 3.5rem 1.5rem !important;
  text-align: center;
}
.empty-state-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.6rem;
  opacity: 0.85;
}
.empty-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 0.4rem 0;
}
.empty-desc {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0;
  max-width: 480px;
  line-height: 1.5;
}
.btn-empty-reset {
  margin-top: 1rem;
}

/* Pagination */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  color: #94a3b8;
  font-size: 0.85rem;
}
.pagination-btns {
  display: flex;
  gap: 0.5rem;
}
.btn-page {
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  padding: 0.4rem 0.8rem;
  border-radius: 0.375rem;
  cursor: pointer;
}
.btn-page:hover:not(:disabled) {
  border-color: #38bdf8;
  color: #38bdf8;
}
.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Modal styles */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.modal-box {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 480px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: #0f172a;
  border-bottom: 1px solid #334155;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.15rem;
  color: #f8fafc;
}
.btn-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
}
.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.product-info-box {
  background: #0f172a;
  padding: 0.85rem;
  border-radius: 0.375rem;
  border: 1px solid #334155;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.info-label {
  color: #94a3b8;
  min-width: 90px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #cbd5e1;
}
.field-hint {
  color: #94a3b8;
  font-size: 0.75rem;
}
.field-error {
  color: #f87171;
  font-size: 0.75rem;
}
.alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
  padding: 0.6rem 0.85rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #334155;
}
.btn-cancel {
  background: #334155;
  color: #cbd5e1;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}
.btn-cancel:hover {
  background: #475569;
}

/* Stock time column styling */
.stock-time-col {
  display: flex;
  flex-direction: column;
  gap: 3px;
  line-height: 1.25;
}

.stock-time-date {
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  color: #e2e8f0;
}

.stock-update-line {
  font-size: 0.72rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  cursor: help;
}

.stock-action-text {
  font-weight: 600;
  font-size: 0.72rem;
}

.status-restock {
  color: #4ade80;
}

.status-sold {
  color: #38bdf8;
}

.status-out {
  color: #f87171;
}

.stock-action-sep {
  opacity: 0.45;
  color: #64748b;
  font-size: 0.65rem;
}

.stock-update-text {
  color: #94a3b8;
}

.text-restock {
  color: #86efac;
}

.text-out {
  color: #fca5a5 !important;
}

.info-value-time {
  font-size: 0.82rem;
  color: #cbd5e1;
}
</style>
