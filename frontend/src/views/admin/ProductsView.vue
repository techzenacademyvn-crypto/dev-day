<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách sản phẩm đang bán tại cửa hàng</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <!-- Thanh tìm kiếm thông minh & bộ lọc danh mục Tree Select -->
    <ProductSearchFilters
      :initial-search="searchKeyword"
      :initial-category="selectedCategoryId"
      @filter="handleFilterChange"
    />

    <!-- Trạng thái lỗi nếu có -->
    <div v-if="errorMessage" class="error-banner">
      <svg class="error-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
      </svg>
      <span>{{ errorMessage }}</span>
      <button @click="fetchProducts(currentPage)" class="btn-retry">Thử lại</button>
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
          <!-- Loading State -->
          <tr v-if="loading">
            <td colspan="7" class="text-center py-8 state-cell">
              <div class="spinner"></div>
              <span>Đang tải danh sách sản phẩm...</span>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-else-if="products.length === 0">
            <td colspan="7" class="text-center py-8 state-cell">
              <div class="empty-state">
                <svg class="empty-icon" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                </svg>
                <p class="empty-title">Không tìm thấy sản phẩm phù hợp</p>
                <p class="empty-desc">Thử thay đổi từ khóa tìm kiếm hoặc chọn danh mục khác.</p>
                <button
                  v-if="searchKeyword || selectedCategoryId !== null"
                  @click="resetFilters"
                  class="btn-reset-empty"
                >
                  Xóa bộ lọc
                </button>
              </div>
            </td>
          </tr>

          <!-- Data Rows -->
          <tr v-for="prod in products" :key="prod.id">
            <td><code>{{ prod.sku }}</code></td>
            <td class="font-medium text-white">{{ prod.name }}</td>
            <td>
              <span class="category-tag">
                {{ categoryMap[prod.category_id] || `#${prod.category_id}` }}
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

    <!-- Phân trang (giữ nguyên bộ lọc khi chuyển trang) -->
    <div class="pagination-bar" v-if="totalProducts > 0">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../lib/api';
import type { Product } from '../../types';
import ProductSearchFilters from '../../components/admin/ProductSearchFilters.vue';

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const errorMessage = ref('');

// Bộ nhớ cache tên danh mục để hiển thị đẹp thay vì ID thô
const categoryMap = ref<Record<number, string>>({});

// State bộ lọc hiện tại
const searchKeyword = ref('');
const selectedCategoryId = ref<number | null>(null);

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

async function fetchProducts(page = 1) {
  loading.value = true;
  errorMessage.value = '';
  currentPage.value = page;

  try {
    const params: Record<string, any> = {
      page,
      page_size: 20,
    };

    if (searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }
    if (selectedCategoryId.value !== null) {
      params.category_id = selectedCategoryId.value;
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

// Xử lý khi bộ lọc thay đổi: reset về trang 1
function handleFilterChange(payload: { search: string; categoryId: number | null }) {
  searchKeyword.value = payload.search;
  selectedCategoryId.value = payload.categoryId;
  currentPage.value = 1;
  fetchProducts(1);
}

// Chuyển trang (giữ nguyên bộ lọc)
function changePage(page: number) {
  fetchProducts(page);
}

// Xóa tất cả bộ lọc từ empty state
function resetFilters() {
  searchKeyword.value = '';
  selectedCategoryId.value = null;
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
  transition: background 0.15s ease;
}

.btn-delete:hover {
  background: #dc2626;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  color: #64748b;
  margin-bottom: 0.75rem;
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 0.25rem;
}

.empty-desc {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 1rem;
}

.btn-reset-empty {
  background: #1e293b;
  color: #38bdf8;
  border: 1px solid #334155;
  padding: 0.45rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reset-empty:hover {
  background: #334155;
  border-color: #38bdf8;
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
  transition: all 0.15s ease;
}

.btn-page:hover:not(:disabled) {
  border-color: #0284c7;
  color: #38bdf8;
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
