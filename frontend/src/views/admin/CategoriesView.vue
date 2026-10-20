<template>
  <div class="admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Quản Lý Danh Mục</h1>
        <p class="page-desc">Danh mục sản phẩm của cửa hàng</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">+ Thêm Danh Mục</button>
    </div>

    <!-- Bộ lọc theo trạng thái và tìm theo tên -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button
          @click="setStatusFilter(null)"
          :class="['tab-btn', activeTab === null ? 'active' : '']"
        >
          Tất cả ({{ totalCount }})
        </button>
        <button
          @click="setStatusFilter(true)"
          :class="['tab-btn', activeTab === true ? 'active' : '']"
        >
          Đang Hoạt Động
        </button>
        <button
          @click="setStatusFilter(false)"
          :class="['tab-btn', activeTab === false ? 'active' : '']"
        >
          Ngừng Hoạt Động
        </button>
      </div>
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="handleSearch"
          placeholder="Tìm kiếm danh mục..." 
          class="form-control search-input"
        />
        <button @click="handleSearch" class="btn-primary">Tìm</button>
      </div>
    </div>

    <!-- Bảng dữ liệu -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên Danh Mục</th>
            <th>Đường Dẫn (Slug)</th>
            <th>Mô Tả</th>
            <th>Trạng Thái</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="text-center py-4">Đang tải dữ liệu...</td>
          </tr>
          <tr v-else-if="categories.length === 0">
            <td colspan="6" class="text-center py-4">Không có danh mục nào.</td>
          </tr>
          <tr v-for="cat in categories" :key="cat.id">
            <td>#{{ cat.id }}</td>
            <td class="font-medium">{{ cat.name }}</td>
            <td><code>{{ cat.slug }}</code></td>
            <td class="text-muted">{{ cat.description || '—' }}</td>
            <td>
              <span :class="['badge', cat.is_active ? 'badge-success' : 'badge-danger']">
                {{ cat.is_active ? 'Hoạt động' : 'Tạm ngừng' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="openEditModal(cat)" class="btn-sm btn-edit">Sửa</button>
                <button @click="handleDelete(cat.id)" class="btn-sm btn-delete">Xóa</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Thêm/Sửa -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ editingId ? 'Sửa Danh Mục' : 'Thêm Danh Mục Mới' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-body">
          <div class="form-group">
            <label>Tên Danh Mục *</label>
            <input v-model="form.name" required class="form-control" />
          </div>
          <div class="form-group">
            <label>Đường Dẫn (Slug) *</label>
            <input v-model="form.slug" required class="form-control" />
          </div>
          <div class="form-group">
            <label>Mô Tả</label>
            <textarea v-model="form.description" rows="3" class="form-control"></textarea>
          </div>
          <div class="form-group checkbox-group">
            <label>
              <input type="checkbox" v-model="form.is_active" />
              Đang hoạt động (Hiển thị ngoài cửa hàng)
            </label>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn-secondary">Hủy</button>
            <button type="submit" class="btn-primary">Lưu</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../lib/api';
import type { Category } from '../../types';

const categories = ref<Category[]>([]);
const totalCount = ref(0);
const loading = ref(false);
const activeTab = ref<boolean | null>(null);
const searchQuery = ref('');

const showModal = ref(false);
const editingId = ref<number | null>(null);
const form = ref({
  name: '',
  slug: '',
  description: '',
  is_active: true,
});

async function fetchCategories() {
  loading.value = true;
  try {
    const params: any = { page: 1, page_size: 100 };
    if (activeTab.value !== null) {
      params.is_active = activeTab.value;
    }
    if (searchQuery.value) {
      params.name = searchQuery.value;
    }
    const res = await api.get('/categories', { params });
    if (res.data.success) {
      categories.value = res.data.data.items;
      if (activeTab.value === null) {
        totalCount.value = res.data.data.total;
      }
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  fetchCategories();
}

function setStatusFilter(val: boolean | null) {
  activeTab.value = val;
  fetchCategories();
}

function openCreateModal() {
  editingId.value = null;
  form.value = { name: '', slug: '', description: '', is_active: true };
  showModal.value = true;
}

function openEditModal(cat: Category) {
  editingId.value = cat.id;
  form.value = {
    name: cat.name,
    slug: cat.slug,
    description: cat.description || '',
    is_active: cat.is_active,
  };
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

async function handleSubmit() {
  try {
    if (editingId.value) {
      await api.put(`/categories/${editingId.value}`, form.value);
    } else {
      await api.post('/categories', form.value);
    }
    closeModal();
    fetchCategories();
  } catch (err: any) {
    alert(err.response?.data?.error?.message || 'Có lỗi xảy ra khi lưu');
  }
}

async function handleDelete(id: number) {
  if (confirm('Bạn có chắc chắn muốn xóa danh mục này không?')) {
    try {
      await api.delete(`/categories/${id}`);
      fetchCategories();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Có lỗi khi xóa');
    }
  }
}

onMounted(() => {
  fetchCategories();
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
  margin-top: 0.25rem;
}
.filter-bar {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-box {
  display: flex;
  gap: 0.5rem;
}
.search-input {
  width: 250px;
}
.filter-tabs {
  display: flex;
  gap: 0.5rem;
}
.tab-btn {
  background: #1e293b;
  color: #94a3b8;
  border: 1px solid #334155;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}
.tab-btn:hover, .tab-btn.active {
  background: #0284c7;
  color: #fff;
  border-color: #0284c7;
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
  text-align: left;
}
.data-table th {
  background: #0f172a;
  color: #94a3b8;
  padding: 0.85rem 1rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #334155;
}
.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  color: #cbd5e1;
  font-size: 0.9rem;
}
.badge {
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}
.badge-success {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}
.badge-danger {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}
.action-buttons {
  display: flex;
  gap: 0.5rem;
}
.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
}
.btn-edit {
  background: #0284c7;
  color: #fff;
}
.btn-delete {
  background: #ef4444;
  color: #fff;
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
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal-box {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 500px;
  overflow: hidden;
}
.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #f8fafc;
}
.btn-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
}
.modal-body {
  padding: 1.5rem;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  font-size: 0.85rem;
  color: #cbd5e1;
  margin-bottom: 0.4rem;
}
.form-control {
  width: 100%;
  padding: 0.6rem 0.8rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  outline: none;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
.btn-secondary {
  background: #475569;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
}
</style>
