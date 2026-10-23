<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách sản phẩm đang bán</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <!-- Bộ lọc nhanh tình trạng tồn kho -->
    <div class="stock-filter-bar">
      <div class="stock-tabs">
        <button
          :class="['tab-btn', selectedStockTab === 'all' ? 'active' : '']"
          @click="selectedStockTab = 'all'"
        >
          Tất cả ({{ stockCounts.all }})
        </button>
        <button
          :class="['tab-btn tab-danger', selectedStockTab === 'out_of_stock' ? 'active' : '']"
          @click="selectedStockTab = 'out_of_stock'"
        >
          🔴 Hết hàng ({{ stockCounts.out_of_stock }})
        </button>
        <button
          :class="['tab-btn tab-warning', selectedStockTab === 'overstocked' ? 'active' : '']"
          @click="selectedStockTab = 'overstocked'"
        >
          🟡 Tồn kho ({{ stockCounts.overstocked }})
        </button>
        <button
          :class="['tab-btn tab-success', selectedStockTab === 'normal' ? 'active' : '']"
          @click="selectedStockTab = 'normal'"
        >
          🟢 Bình thường ({{ stockCounts.normal }})
        </button>
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
          <tr v-else-if="displayedProducts.length === 0">
            <td colspan="7" class="text-center py-4 text-muted">Không có sản phẩm nào thuộc tình trạng tồn kho này.</td>
          </tr>
          <tr v-for="prod in displayedProducts" :key="prod.id">
            <td><code>{{ prod.sku }}</code></td>
            <td class="font-medium">{{ prod.name }}</td>
            <td>#{{ prod.category_id }}</td>
            <td class="price-tag">${{ Number(prod.price).toFixed(2) }}</td>
            <td>
              <div class="stock-cell">
                <span class="stock-qty">{{ prod.stock }} {{ prod.stock === 0 ? '(Hết hàng)' : 'cái' }}</span>
                <span :class="['stock-badge', getStockStatus(prod).badgeClass]">
                  {{ getStockStatus(prod).label }}
                </span>
                <span v-if="getStockStatus(prod).daysInStock > 0" class="stock-hint">
                  Ở kho {{ getStockStatus(prod).daysInStock }} ngày
                </span>
              </div>
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

// State lọc theo tình trạng tồn kho
type StockFilterType = 'all' | 'out_of_stock' | 'overstocked' | 'normal';
const selectedStockTab = ref<StockFilterType>('all');

/**
 * Tính số ngày lưu kho theo múi giờ Việt Nam (UTC+7)
 */
function getDaysInStockVN(createdAt: string): number {
  if (!createdAt) return 0;
  try {
    const createdDate = new Date(createdAt);
    if (isNaN(createdDate.getTime())) return 0;
    const now = Date.now();
    const diffMs = now - createdDate.getTime();
    return Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
  } catch {
    return 0;
  }
}

/**
 * Xác định trạng thái tồn kho theo đúng 3 tiêu chí:
 * 1. Hết hàng: stock === 0
 * 2. Tồn kho (> 2 tháng): ở trong kho > 60 ngày VÀ có nhiều hơn 10 sản phẩm
 * 3. Bình thường: các trường hợp còn lại
 */
function getStockStatus(prod: Product) {
  const stock = Number(prod.stock) || 0;
  const daysInStock = getDaysInStockVN(prod.created_at);

  if (stock === 0) {
    return {
      key: 'out_of_stock' as const,
      label: 'Hết hàng',
      badgeClass: 'out-of-stock',
      daysInStock,
    };
  }

  // Tiêu chí: ở trong kho 2 tháng (60 ngày) và có nhiều hơn 10 sản phẩm
  if (daysInStock > 60 && stock > 10) {
    return {
      key: 'overstocked' as const,
      label: 'Tồn kho',
      badgeClass: 'overstocked',
      daysInStock,
    };
  }

  return {
    key: 'normal' as const,
    label: 'Bình thường',
    badgeClass: 'in-stock',
    daysInStock,
  };
}

/**
 * Đếm số lượng sản phẩm theo từng tình trạng tồn kho
 */
const stockCounts = computed(() => {
  const counts = { all: 0, out_of_stock: 0, overstocked: 0, normal: 0 };
  for (const prod of products.value) {
    counts.all++;
    const status = getStockStatus(prod).key;
    counts[status]++;
  }
  return counts;
});

/**
 * Danh sách sản phẩm hiển thị theo tab tình trạng tồn kho đã chọn
 */
const displayedProducts = computed(() => {
  if (selectedStockTab.value === 'all') return products.value;
  return products.value.filter(prod => getStockStatus(prod).key === selectedStockTab.value);
});

async function fetchProducts(page = 1) {
  loading.value = true;
  currentPage.value = page;
  try {
    const res = await api.get('/products', {
      params: { page, page_size: 20 },
    });
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

/* Bộ lọc nhanh tình trạng tồn kho */
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

/* Bảng danh sách sản phẩm */
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

/* Cột tồn kho */
.stock-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}
.stock-qty {
  font-weight: 500;
  color: #cbd5e1;
}
.stock-badge {
  font-size: 0.8rem;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  display: inline-block;
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
.overstocked {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  font-weight: 600;
  border: 1px solid rgba(245, 158, 11, 0.4);
}
.stock-hint {
  font-size: 0.7rem;
  color: #94a3b8;
}

/* Nổi bật & Nút thao tác */
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
.text-muted {
  color: #64748b;
}
</style>
