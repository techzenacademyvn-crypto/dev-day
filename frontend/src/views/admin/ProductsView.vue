<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách sản phẩm đang bán</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <!-- Thanh lọc theo danh mục và tìm kiếm theo tên -->
    <div class="filter-bar">
      <div class="filter-controls">
        <!-- List box chọn danh mục -->
        <div class="filter-group">
          <label for="category-select" class="filter-label">Danh Mục:</label>
          <select
            id="category-select"
            v-model="selectedCategoryId"
            @change="handleCategoryChange"
            class="form-control select-category"
          >
            <option value="">-- Tất cả danh mục --</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Ô nhập tìm kiếm sản phẩm theo tên -->
        <div class="search-box">
          <input
            id="product-search-input"
            type="text"
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            placeholder="Tìm theo tên sản phẩm..."
            class="form-control search-input"
          />
          <button @click="handleSearch" class="btn-primary" type="button">Tìm</button>
          <button
            v-if="searchQuery.trim() || selectedCategoryId !== ''"
            @click="resetFilters"
            class="btn-secondary"
            type="button"
          >
            Đặt lại
          </button>
        </div>
      </div>
    </div>

    <!-- Bảng danh sách sản phẩm -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Tên Sản Phẩm</th>
            <th>Danh Mục</th>
            <th>Đơn Giá</th>
            <th>Tồn Kho</th>
            <th>Nổi Bật</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center py-4">Đang tải sản phẩm...</td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td colspan="7" class="text-center py-8 empty-row">
              <div class="empty-state">
                <span class="empty-icon">🔍</span>
                <p class="empty-text">Không tìm thấy sản phẩm nào phù hợp.</p>
                <button
                  v-if="searchQuery.trim() || selectedCategoryId !== ''"
                  @click="resetFilters"
                  class="btn-sm btn-reset-inline"
                  type="button"
                >
                  Xóa bộ lọc
                </button>
              </div>
            </td>
          </tr>
          <tr v-else v-for="prod in products" :key="prod.id">
            <td><code>{{ prod.sku }}</code></td>
            <td class="font-medium">{{ prod.name }}</td>
            <td>
              <span class="category-pill" :title="'ID: #' + prod.category_id">
                {{ getCategoryName(prod.category_id) }}
              </span>
            </td>
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
    <div v-if="totalProducts > 0" class="pagination-bar">
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
import { ref, onMounted } from 'vue';
import api from '../../lib/api';
import type { Product, Category } from '../../types';

const products = ref<Product[]>([]);
const categories = ref<Category[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);

const searchQuery = ref('');
const selectedCategoryId = ref<number | ''>('');

async function fetchCategories() {
  try {
    const res = await api.get('/categories', {
      params: { page: 1, page_size: 100 },
    });
    if (res.data.success) {
      categories.value = res.data.data.items;
    }
  } catch (err) {
    console.error('Lỗi khi tải danh mục:', err);
  }
}

function getCategoryName(categoryId: number): string {
  const cat = categories.value.find((c) => c.id === categoryId);
  return cat ? cat.name : `#${categoryId}`;
}

async function fetchProducts(page = 1) {
  loading.value = true;
  currentPage.value = page;
  try {
    const params: any = { page, page_size: 20 };
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim();
    }
    if (selectedCategoryId.value !== '') {
      params.category_id = Number(selectedCategoryId.value);
    }

    const res = await api.get('/products', { params });
    if (res.data.success) {
      products.value = res.data.data.items;
      totalProducts.value = res.data.data.total;
      totalPages.value = res.data.data.total_pages;
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  fetchProducts(1);
}

function handleCategoryChange() {
  fetchProducts(1);
}

function resetFilters() {
  searchQuery.value = '';
  selectedCategoryId.value = '';
  fetchProducts(1);
}

function changePage(page: number) {
  fetchProducts(page);
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
  fetchCategories();
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
  transition: background-color 0.2s;
}
.btn-primary:hover {
  background: #0369a1;
}
.btn-secondary {
  background: #475569;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}
.btn-secondary:hover {
  background: #334155;
}

/* Filter Bar */
.filter-bar {
  margin-bottom: 1.5rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1rem;
}
.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  align-items: center;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #94a3b8;
  white-space: nowrap;
}
.form-control {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}
.form-control:focus {
  border-color: #38bdf8;
}
.select-category {
  min-width: 220px;
  cursor: pointer;
}
.search-box {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex: 1;
  max-width: 450px;
}
.search-input {
  flex: 1;
  min-width: 200px;
}

/* Table */
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
.category-pill {
  display: inline-block;
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 500;
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
.btn-delete:hover {
  background: #dc2626;
}

/* Empty State inside Table */
.empty-row {
  background: #1e293b;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem 1rem;
}
.empty-icon {
  font-size: 2rem;
  opacity: 0.6;
}
.empty-text {
  color: #94a3b8;
  font-size: 0.95rem;
  margin: 0;
}
.btn-reset-inline {
  background: #0284c7;
  color: #fff;
  padding: 0.35rem 0.75rem;
  margin-top: 0.25rem;
  border-radius: 0.25rem;
}
.btn-reset-inline:hover {
  background: #0369a1;
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
</style>
