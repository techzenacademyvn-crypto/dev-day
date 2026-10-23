<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách sản phẩm đang bán</p>
      </div>
      <div class="header-actions">
        <button @click="sortByFeatured" :class="['btn-featured', isFeaturedSorted ? 'active' : '']">
          Sản phẩm nổi bật
        </button>
        <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
      </div>
    </div>


    <!-- Bộ lọc tìm kiếm theo khoảng giá -->
    <div class="filter-card">
      <div class="filter-header">
        <span class="filter-title">🔍 Lọc sản phẩm theo khoảng giá</span>
      </div>

      <div class="filter-controls">
        <div class="price-input-wrapper">
          <label class="input-label" for="min-price">Giá tối thiểu ($)</label>
          <div class="input-with-prefix">
            <span class="currency-symbol">$</span>
            <input
              id="min-price"
              v-model="minPriceInput"
              type="text"
              inputmode="decimal"
              placeholder="0.00"
              class="form-control price-input"
              @keydown="handlePriceKeydown"
              @input="sanitizePriceInput('min')"
              @paste="handlePricePaste($event, 'min')"
              @keyup.enter="handleFilter"
            />
          </div>
        </div>

        <span class="range-divider">—</span>

        <div class="price-input-wrapper">
          <label class="input-label" for="max-price">Giá tối đa ($)</label>
          <div class="input-with-prefix">
            <span class="currency-symbol">$</span>
            <input
              id="max-price"
              v-model="maxPriceInput"
              type="text"
              inputmode="decimal"
              placeholder="Tối đa..."
              class="form-control price-input"
              @keydown="handlePriceKeydown"
              @input="sanitizePriceInput('max')"
              @paste="handlePricePaste($event, 'max')"
              @keyup.enter="handleFilter"
            />
          </div>
        </div>

        <div class="sort-wrapper">
          <label class="input-label" for="select-sort">Sắp xếp theo</label>
          <select
            id="select-sort"
            v-model="sortBy"
            @change="handleSortChange"
            class="form-control select-sort"
          >
            <option value="">Mặc định (ID)</option>
            <option value="name_asc">🔤 Tên: A → Z (Alphabet)</option>
            <option value="name_desc">🔤 Tên: Z → A (Alphabet)</option>
            <option value="price_asc">📈 Giá: Thấp đến Cao</option>
            <option value="price_desc">📉 Giá: Cao đến Thấp</option>
            <option value="stock_asc">📦 Tồn kho: Ít đến Nhiều</option>
            <option value="stock_desc">📦 Tồn kho: Nhiều đến Ít</option>
          </select>
        </div>

        <div class="filter-btn-group">
          <button @click="handleFilter" class="btn-primary btn-search" id="btn-search-price">
            Lọc
          </button>
          <button
            v-if="isFilterActive || minPriceInput || maxPriceInput || sortBy"
            @click="handleReset"
            class="btn-reset"
            id="btn-reset-price"
          >
            Đặt lại
          </button>
        </div>
      </div>

      <!-- Thông báo khi min > max hoặc lỗi nhập liệu -->
      <div v-if="validationWarning" class="filter-warning">
        ⚠️ {{ validationWarning }}
      </div>

      <!-- Badge hiển thị khoảng giá và sắp xếp đang áp dụng -->
      <div v-if="isFilterActive && !validationWarning" class="active-filter-badge">
        <span>Đang áp dụng: <strong>{{ activeFilterText }}</strong></span>
        <button @click="handleReset" class="btn-clear-tag" title="Xóa bộ lọc và sắp xếp">✕</button>
      </div>
    </div>

    <!-- Bảng danh sách sản phẩm -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>SKU</th>
            <th class="th-sortable" @click="toggleSort('name')" title="Nhấp để sắp xếp theo Tên sản phẩm (A-Z / Z-A)">
              <div class="th-content">
                <span>Tên Sản Phẩm</span>
                <span :class="['sort-badge', sortBy.startsWith('name_') ? 'sort-active' : '']">
                  {{ sortBy === 'name_asc' ? '▲ A-Z' : (sortBy === 'name_desc' ? '▼ Z-A' : '⇅') }}
                </span>
              </div>
            </th>
            <th>Danh Mục</th>
            <th class="th-sortable" @click="toggleSort('price')" title="Nhấp để sắp xếp theo Giá tăng/giảm">
              <div class="th-content">
                <span>Đơn Giá</span>
                <span :class="['sort-badge', sortBy.startsWith('price_') ? 'sort-active' : '']">
                  {{ sortBy === 'price_asc' ? '▲ Tăng dần' : (sortBy === 'price_desc' ? '▼ Giảm dần' : '⇅') }}
                </span>
              </div>
            </th>
            <th class="th-sortable" @click="toggleSort('stock')" title="Nhấp để sắp xếp theo Số lượng tồn kho">
              <div class="th-content">
                <span>Tồn Kho</span>
                <span :class="['sort-badge', sortBy.startsWith('stock_') ? 'sort-active' : '']">
                  {{ sortBy === 'stock_asc' ? '▲ Ít nhất' : (sortBy === 'stock_desc' ? '▼ Nhiều nhất' : '⇅') }}
                </span>
              </div>
            </th>
            <th>Nổi Bật</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center py-4">Đang tải sản phẩm...</td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td colspan="7" class="empty-state">
              <div class="empty-state-content">
                <div class="empty-icon">🔍</div>
                <h3 class="empty-title">Không tìm thấy sản phẩm nào</h3>
                <p v-if="isFilterActive" class="empty-desc">
                  Không có sản phẩm nào thuộc khoảng giá <strong>{{ activeFilterText }}</strong>.
                  <br />Bạn có thể thử nhập khoảng giá khác hoặc bấm đặt lại bộ lọc.
                </p>
                <p v-else class="empty-desc">Danh sách sản phẩm hiện đang trống.</p>
                <button v-if="isFilterActive" @click="handleReset" class="btn-primary btn-sm btn-empty-reset">
                  Xoá bộ lọc và xem tất cả
                </button>
              </div>
            </td>
          </tr>
          <tr v-for="prod in products" :key="prod.id" v-else>
            <td><code>{{ prod.sku }}</code></td>
            <td class="font-medium">{{ prod.name }}</td>
            <td>#{{ prod.category_id }}</td>
            <td class="price-tag">${{ Number(prod.price).toFixed(2) }}</td>
            <td>
              <span :class="['stock-badge', prod.stock === 0 ? 'out-of-stock' : 'in-stock']">
                {{ prod.stock }} {{ prod.stock === 0 ? '(Hết hàng)' : 'cái' }}
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
        </tbody>
      </table>
    </div>

    <!-- Phân trang -->
    <div class="pagination-bar">
      <span>Trang {{ currentPage }} / {{ totalPages }} (Tổng cộng {{ totalProducts }} sản phẩm)</span>
      <div class="pagination-btns">
        <button
          :disabled="currentPage <= 1"
          @click="changePage(currentPage - 1)"
          class="btn-page"
        >
          Trước
        </button>
        <button
          :disabled="currentPage >= totalPages"
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

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const isFeaturedSorted = ref(false);

// Filter states
const minPriceInput = ref<string>('');
const maxPriceInput = ref<string>('');
const appliedMinPrice = ref<string>('');
const appliedMaxPrice = ref<string>('');
const sortBy = ref<string>('');
const validationWarning = ref<string>('');

const isFilterActive = computed(() => {
  return appliedMinPrice.value !== '' || appliedMaxPrice.value !== '' || sortBy.value !== '';
});

const activeFilterText = computed(() => {
  const parts: string[] = [];
  if (appliedMinPrice.value !== '' && appliedMaxPrice.value !== '') {
    parts.push(`từ $${Number(appliedMinPrice.value).toFixed(2)} đến $${Number(appliedMaxPrice.value).toFixed(2)}`);
  } else if (appliedMinPrice.value !== '') {
    parts.push(`từ $${Number(appliedMinPrice.value).toFixed(2)} trở lên`);
  } else if (appliedMaxPrice.value !== '') {
    parts.push(`dưới hoặc bằng $${Number(appliedMaxPrice.value).toFixed(2)}`);
  }

  if (sortBy.value === 'name_asc') {
    parts.push('tên A → Z 🔤');
  } else if (sortBy.value === 'name_desc') {
    parts.push('tên Z → A 🔤');
  } else if (sortBy.value === 'price_asc') {
    parts.push('giá tăng dần 📈');
  } else if (sortBy.value === 'price_desc') {
    parts.push('giá giảm dần 📉');
  } else if (sortBy.value === 'stock_asc') {
    parts.push('tồn kho ít → nhiều 📦');
  } else if (sortBy.value === 'stock_desc') {
    parts.push('tồn kho nhiều → ít 📦');
  }

  return parts.join(' • ');
});

function handlePriceKeydown(event: KeyboardEvent) {
  // Cho phép các phím điều khiển hệ thống
  const allowedControlKeys = [
    'Backspace',
    'Tab',
    'Delete',
    'ArrowLeft',
    'ArrowRight',
    'ArrowUp',
    'ArrowDown',
    'Home',
    'End',
    'Enter',
  ];

  if (allowedControlKeys.includes(event.key)) {
    return;
  }

  // Cho phép các tổ hợp phím tắt Ctrl/Cmd + A, C, V, X, Z
  if (event.ctrlKey || event.metaKey) {
    return;
  }

  // Chặn phím 'e', 'E', '+', '-'
  if (['e', 'E', '+', '-'].includes(event.key)) {
    event.preventDefault();
    return;
  }

  // Cho phép 1 dấu chấm '.' phân tách thập phân
  if (event.key === '.') {
    const input = event.target as HTMLInputElement;
    if (input && input.value.includes('.')) {
      event.preventDefault();
    }
    return;
  }

  // Chặn tất cả các ký tự không phải số (0-9)
  if (!/^[0-9]$/.test(event.key)) {
    event.preventDefault();
  }
}

function sanitizePriceInput(field: 'min' | 'max') {
  const current = field === 'min' ? minPriceInput.value : maxPriceInput.value;
  if (!current) return;

  // Lọc bỏ toàn bộ chữ và ký tự đặc biệt, chỉ giữ lại số và dấu chấm
  let sanitized = current.replace(/[^0-9.]/g, '');
  const parts = sanitized.split('.');
  if (parts.length > 2) {
    sanitized = parts[0] + '.' + parts.slice(1).join('');
  }

  if (field === 'min') {
    minPriceInput.value = sanitized;
  } else {
    maxPriceInput.value = sanitized;
  }
}

function handlePricePaste(event: ClipboardEvent, targetField: 'min' | 'max') {
  event.preventDefault();
  const text = event.clipboardData?.getData('text') || '';
  let sanitized = text.replace(/[^0-9.]/g, '');
  const parts = sanitized.split('.');
  if (parts.length > 2) {
    sanitized = parts[0] + '.' + parts.slice(1).join('');
  }
  if (targetField === 'min') {
    minPriceInput.value = sanitized;
  } else {
    maxPriceInput.value = sanitized;
  }
}

function handleFilter() {
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
    validationWarning.value = `Giá tối thiểu ($${min}) đang lớn hơn giá tối đa ($${max}). Không có sản phẩm nào thuộc khoảng giá này.`;
  }

  appliedMinPrice.value = minPriceInput.value;
  appliedMaxPrice.value = maxPriceInput.value;
  fetchProducts(1);
}

function handleReset() {
  minPriceInput.value = '';
  maxPriceInput.value = '';
  appliedMinPrice.value = '';
  appliedMaxPrice.value = '';
  sortBy.value = '';
  validationWarning.value = '';
  fetchProducts(1);
}

function handleSortChange() {
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

async function fetchProducts(page = 1) {
  loading.value = true;
  currentPage.value = page;
  try {
    const params: Record<string, any> = {
      page,
      page_size: 20,
    };
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
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function changePage(page: number) {
  fetchProducts(page);
}

function sortByFeatured() {
  if (!isFeaturedSorted.value) {
    // Đẩy các sản phẩm nổi bật lên đầu
    products.value = [...products.value].sort((a, b) => {
      if (a.is_featured !== b.is_featured) {
        return (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0);
      }
      return a.id - b.id;
    });
    isFeaturedSorted.value = true;
  } else {
    // Bấm lại lần nữa: Rã sản phẩm ra trở về thứ tự ban đầu
    products.value = [...products.value].sort((a, b) => a.id - b.id);
    isFeaturedSorted.value = false;
  }
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
  padding: 0.6rem 1.2rem;
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
}
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
.price-tag {
  color: #38bdf8;
  font-weight: 600;
}
.stock-badge {
  font-size: 0.8rem;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
}
.in-stock {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}
.out-of-stock {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  font-weight: 700;
}
.badge-featured {
  background: rgba(234, 179, 8, 0.2);
  color: #facc15;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
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
}
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
.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Filter Card Styles */
.filter-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
}
.filter-header {
  margin-bottom: 0.85rem;
}
.filter-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f8fafc;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.filter-controls {
  display: flex;
  align-items: flex-end;
  gap: 0.85rem;
  flex-wrap: wrap;
}
.price-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.input-label {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}
.input-with-prefix {
  position: relative;
  display: flex;
  align-items: center;
}
.currency-symbol {
  position: absolute;
  left: 0.75rem;
  color: #64748b;
  font-weight: 600;
  pointer-events: none;
  font-size: 0.9rem;
}
.price-input {
  width: 150px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  font-size: 0.9rem;
  padding: 0.55rem 0.75rem 0.55rem 1.65rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  -moz-appearance: textfield;
  appearance: textfield;
}
.price-input::-webkit-outer-spin-button,
.price-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.price-input:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
}
.range-divider {
  color: #64748b;
  padding: 0 0.25rem;
  font-weight: 700;
  margin-bottom: 0.6rem;
}
.filter-btn-group {
  display: flex;
  gap: 0.5rem;
}
.btn-search {
  padding: 0.55rem 1.25rem;
  font-size: 0.875rem;
  height: 38px;
  cursor: pointer;
}
.btn-reset {
  background: #334155;
  color: #cbd5e1;
  border: 1px solid #475569;
  padding: 0.55rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  height: 38px;
  transition: all 0.2s;
}
.btn-reset:hover {
  background: #475569;
  color: #f8fafc;
}
.filter-warning {
  margin-top: 0.85rem;
  padding: 0.65rem 0.85rem;
  background: rgba(234, 179, 8, 0.12);
  border: 1px solid rgba(234, 179, 8, 0.35);
  color: #facc15;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.active-filter-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.85rem;
  background: rgba(2, 132, 199, 0.15);
  border: 1px solid rgba(2, 132, 199, 0.35);
  color: #38bdf8;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.825rem;
}
.btn-clear-tag {
  background: none;
  border: none;
  color: #38bdf8;
  cursor: pointer;
  font-weight: 700;
  padding: 0 0.15rem;
  font-size: 0.85rem;
  line-height: 1;
}
.btn-clear-tag:hover {
  color: #fff;
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

/* Sorting Styles */
.sort-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.select-sort {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  font-size: 0.875rem;
  padding: 0.55rem 0.85rem;
  outline: none;
  height: 38px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.select-sort:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
}
.th-sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}
.th-sortable:hover {
  background-color: #1e293b !important;
}
.th-content {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.sort-badge {
  font-size: 0.725rem;
  color: #64748b;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  background: rgba(51, 65, 85, 0.4);
  transition: all 0.2s;
}
.sort-badge.sort-active {
  background: rgba(2, 132, 199, 0.25);
  color: #38bdf8;
  font-weight: 700;
  border: 1px solid rgba(2, 132, 199, 0.4);
}
</style>
