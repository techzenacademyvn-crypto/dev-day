<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Sản Phẩm</h1>
        <p class="page-desc">Danh sách và kiểm tra tình trạng tồn kho sản phẩm</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Sản Phẩm</button>
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
          <tr v-else-if="errorMessage">
            <td colspan="7" class="text-center py-4 error-cell">
              <span>{{ errorMessage }}</span>
              <button @click="fetchProducts(currentPage)" class="btn-sm btn-retry">Thử lại</button>
            </td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td colspan="7" class="text-center py-4 text-muted">Không có sản phẩm nào.</td>
          </tr>
          <tr v-for="prod in products" :key="prod.id">
            <td><code>{{ prod.sku }}</code></td>
            <td class="font-medium">{{ prod.name }}</td>
            <td>#{{ prod.category_id }}</td>
            <td class="price-tag">${{ Number(prod.price).toFixed(2) }}</td>
            <td>
              <!-- TASK-03: Hiển thị số lượng và trạng thái tồn kho chuẩn hóa -->
              <StockBadge :stock="prod.stock" />
            </td>
            <td>
              <span v-if="prod.is_featured" class="badge-featured">⭐ Nổi bật</span>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <div class="action-buttons">
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
    <div class="pagination-bar">
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

    <!-- Modal Cập nhật Tồn Kho (Hỗ trợ AC03 - Cập nhật và làm mới tồn kho) -->
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
              <span class="info-label">Tồn hiện tại:</span>
              <StockBadge :stock="selectedProduct.stock" />
            </div>
          </div>

          <div class="form-group">
            <label for="stockInput">Số Lượng Tồn Kho Mới *</label>
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
import { ref, onMounted } from 'vue';
import api from '../../lib/api';
import type { Product } from '../../types';
import StockBadge from '../../components/StockBadge.vue';

const products = ref<Product[]>([]);
const totalProducts = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const errorMessage = ref<string | null>(null);

// Trạng thái modal cập nhật tồn kho (AC03)
const showStockModal = ref(false);
const selectedProduct = ref<Product | null>(null);
const stockFormValue = ref<number>(0);
const stockFormError = ref<string | null>(null);
const updatingStock = ref(false);
const modalError = ref<string | null>(null);

async function fetchProducts(page = 1) {
  loading.value = true;
  errorMessage.value = null;
  currentPage.value = page;
  try {
    const res = await api.get('/products', {
      params: { page, page_size: 20 },
    });
    if (res.data.success) {
      products.value = res.data.data.items;
      totalProducts.value = res.data.data.total;
      totalPages.value = res.data.data.total_pages;
    } else {
      errorMessage.value = res.data.message || 'Không thể lấy dữ liệu sản phẩm.';
    }
  } catch (err: any) {
    console.error('Lỗi khi tải danh sách sản phẩm:', err);
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

  // Validation chặt chẽ theo Business Rules
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
      // AC03: Tải lại dữ liệu ngay sau khi cập nhật thành công
      await fetchProducts(currentPage.value);
    } else {
      modalError.value = res.data.message || 'Cập nhật thất bại.';
    }
  } catch (err: any) {
    console.error('Lỗi khi cập nhật tồn kho:', err);
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
  transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) {
  background: #0369a1;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
.badge-featured {
  background: rgba(234, 179, 8, 0.2);
  color: #facc15;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
}
.action-buttons {
  display: flex;
  gap: 0.4rem;
}
.btn-sm {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
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
.text-muted {
  color: #64748b;
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
  line-height: 1;
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
.form-control {
  background: #0f172a;
  border: 1px solid #334155;
  color: #f8fafc;
  padding: 0.6rem 0.85rem;
  border-radius: 0.375rem;
  font-size: 0.95rem;
}
.form-control:focus {
  outline: none;
  border-color: #0284c7;
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
</style>
