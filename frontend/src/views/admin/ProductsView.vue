<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách sản phẩm đang bán</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
    </div>

    <!-- Bộ lọc khoảng giá (Task US1-FE02: Dual-thumb Slider & Quick Price Chips) -->
    <PriceFilter
      ref="priceFilterRef"
      v-model="priceRange"
      :min="0"
      :max="2000000"
      :step="10000"
    />

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
          <!-- Thông báo khi không có sản phẩm nào trong khoảng giá -->
          <tr v-else-if="filteredProducts.length === 0">
            <td colspan="7" class="empty-table-cell">
              <div class="empty-filter-box">
                <span class="empty-icon">🏷️</span>
                <p class="empty-msg">Không tìm thấy sản phẩm nào trong khoảng giá này</p>
                <button @click="resetPriceFilter" class="btn-reset-inline">
                  🔄 Đặt lại tất cả mức giá
                </button>
              </div>
            </td>
          </tr>
          <tr v-for="prod in filteredProducts" :key="prod.id">
            <td><code>{{ prod.sku }}</code></td>
            <td class="font-medium">{{ prod.name }}</td>
            <td>#{{ prod.category_id }}</td>
            <td class="price-tag">
              <div class="price-vnd-text">{{ formatVND(getProductPriceVND(prod.price)) }}</div>
              <div class="price-usd-sub">${{ Number(prod.price).toFixed(2) }}</div>
            </td>
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

    <!-- Phân trang / Thống kê -->
    <div class="pagination-bar">
      <span>
        Hiển thị <strong>{{ filteredProducts.length }}</strong> / {{ totalProducts }} sản phẩm (Trang {{ currentPage }} / {{ totalPages }})
      </span>
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
import PriceFilter from '../../components/PriceFilter.vue';
import { getProductPriceVND, formatVND } from '../../utils/format';

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);

const priceFilterRef = ref<InstanceType<typeof PriceFilter> | null>(null);
const priceRange = ref<[number, number]>([0, 2000000]);

// Lọc sản phẩm hiển thị theo khoảng giá đã chọn
const filteredProducts = computed(() => {
  const [minPrice, maxPrice] = priceRange.value;
  return products.value.filter((prod) => {
    const vndPrice = getProductPriceVND(prod.price);
    return vndPrice >= minPrice && vndPrice <= maxPrice;
  });
});

function resetPriceFilter() {
  if (priceFilterRef.value) {
    priceFilterRef.value.reset();
  } else {
    priceRange.value = [0, 2000000];
  }
}

async function fetchProducts(page = 1) {
  loading.value = true;
  currentPage.value = page;
  try {
    const res = await api.get('/products', {
      params: { page, page_size: 50 },
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
.price-vnd-text {
  font-size: 1rem;
  font-weight: 700;
  color: #38bdf8;
}
.price-usd-sub {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 400;
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
  color: #f87171;
  font-size: 1.15rem;
  font-weight: 700;
}
.btn-reset-inline {
  background: #0284c7;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-reset-inline:hover {
  background: #0369a1;
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