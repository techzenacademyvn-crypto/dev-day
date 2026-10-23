<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách sản phẩm đang bán</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <!-- Thanh bộ lọc sản phẩm nổi bật -->
    <div class="filter-bar flex items-center justify-between mb-4 bg-slate-800/60 p-3 rounded-lg border border-slate-700">
      <label class="toggle-featured flex items-center gap-2.5 text-sm font-medium text-slate-200 cursor-pointer select-none">
        <input
          type="checkbox"
          v-model="isFeaturedOnly"
          @change="handleFilterChange"
          class="w-4 h-4 text-sky-600 bg-slate-700 border-slate-500 rounded focus:ring-sky-500 cursor-pointer accent-sky-500"
        />
        <span>⭐ Lọc sản phẩm nổi bật</span>
      </label>
      <span v-if="isFeaturedOnly" class="text-xs text-amber-400 font-semibold bg-amber-400/10 px-2 py-0.5 rounded-full border border-amber-400/20">
        Đang lọc nổi bật
      </span>
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
          <tr v-for="prod in products" :key="prod.id">
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
import { ref, onMounted } from 'vue';
import api from '../../lib/api';
import type { Product } from '../../types';

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const isFeaturedOnly = ref(false);

async function fetchProducts(page = 1) {
  loading.value = true;
  currentPage.value = page;
  try {
    const params: Record<string, any> = { page, page_size: 20 };
    if (isFeaturedOnly.value) {
      params.is_featured = true;
    }
    const res = await api.get('/products/featured', { params });
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

function handleFilterChange() {
  currentPage.value = 1;
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
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding: 0.75rem 1rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
}
.toggle-featured {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #e2e8f0;
  font-size: 0.9rem;
  cursor: pointer;
  user-select: none;
}
.toggle-featured input[type="checkbox"] {
  width: 1.15rem;
  height: 1.15rem;
  accent-color: #0284c7;
  cursor: pointer;
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
</style>
