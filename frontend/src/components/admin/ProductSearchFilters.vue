<template>
  <div class="product-search-filters">
    <!-- Hàng điều khiển tìm kiếm & lọc -->
    <div class="filters-row">
      <!-- Bộ lọc Danh mục dạng cây (Tree Select) -->
      <div class="filter-item category-filter">
        <CategoryTreeSelect
          v-model="selectedCategory"
          @change="handleCategoryChange"
        />
      </div>

      <!-- Ô nhập tìm kiếm từ khóa -->
      <div class="filter-item search-input-wrapper">
        <!-- Biểu tượng kính lúp -->
        <svg class="icon-search" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
        </svg>

        <!-- Input không auto-fetch khi gõ phím khác rỗng -->
        <input
          type="text"
          v-model="keyword"
          class="search-input"
          placeholder="Tìm sản phẩm (tên, không dấu, danh mục...)"
          @keyup.enter="handleSearchSubmit"
        />

        <!-- Nút × xóa từ khóa nhanh -->
        <button
          v-if="keyword"
          type="button"
          class="btn-clear-keyword"
          @click="clearKeyword"
          title="Xóa từ khóa tìm kiếm"
          aria-label="Xóa từ khóa"
        >
          &times;
        </button>
      </div>

      <!-- Nút Tìm kiếm -->
      <button
        type="button"
        class="btn-search"
        @click="handleSearchSubmit"
      >
        Tìm kiếm
      </button>

      <!-- Nút Xóa bộ lọc (reset all) -->
      <button
        v-if="hasActiveFilter"
        type="button"
        class="btn-reset-filters"
        @click="resetAllFilters"
        title="Đặt lại toàn bộ bộ lọc về mặc định"
      >
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
        </svg>
        Xóa bộ lọc
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import CategoryTreeSelect from './CategoryTreeSelect.vue';

const props = defineProps<{
  initialSearch?: string;
  initialCategory?: number | null;
}>();

const emit = defineEmits<{
  (e: 'filter', payload: { search: string; categoryId: number | null }): void;
}>();

const keyword = ref(props.initialSearch || '');
// submittedKeyword lưu lại từ khóa đã được áp dụng vào bộ lọc hiện tại
const submittedKeyword = ref(props.initialSearch || '');
const selectedCategory = ref<number | null>(props.initialCategory ?? null);

// Đồng bộ khi prop từ ngoài thay đổi
watch(() => props.initialSearch, (val) => {
  keyword.value = val || '';
  submittedKeyword.value = val || '';
});
watch(() => props.initialCategory, (val) => {
  selectedCategory.value = val ?? null;
});

// Kiểm tra xem hiện có bộ lọc nào đang được áp dụng hay không
const hasActiveFilter = computed(() => {
  return keyword.value.trim().length > 0 || submittedKeyword.value.length > 0 || selectedCategory.value !== null;
});

// Theo dõi khi ô tìm kiếm trở thành rỗng do Backspace, Delete hoặc clear
watch(keyword, (newVal) => {
  const trimmed = newVal.trim();
  // Khi ô tìm kiếm trở thành rỗng VÀ trước đó đã có từ khóa đang áp dụng, tự động tải lại
  if (trimmed === '' && submittedKeyword.value !== '') {
    submittedKeyword.value = '';
    emit('filter', {
      search: '',
      categoryId: selectedCategory.value,
    });
  }
});

// Chỉ phát sự kiện tìm kiếm khi nhấn Enter hoặc bấm nút Tìm kiếm
function handleSearchSubmit() {
  submittedKeyword.value = keyword.value.trim();
  emit('filter', {
    search: submittedKeyword.value,
    categoryId: selectedCategory.value,
  });
}

// Khi thay đổi danh mục: áp dụng ngay và giữ nguyên từ khóa đã submit (nếu có)
function handleCategoryChange(newCatId: number | null) {
  selectedCategory.value = newCatId;
  emit('filter', {
    search: submittedKeyword.value,
    categoryId: newCatId,
  });
}

// Khi bấm nút ×: làm rỗng từ khóa và tự động tải lại ngay
function clearKeyword() {
  keyword.value = '';
  submittedKeyword.value = '';
  emit('filter', {
    search: '',
    categoryId: selectedCategory.value,
  });
}

// Khi bấm nút Xóa bộ lọc: reset tất cả về mặc định
function resetAllFilters() {
  keyword.value = '';
  submittedKeyword.value = '';
  selectedCategory.value = null;
  emit('filter', {
    search: '',
    categoryId: null,
  });
}
</script>

<style scoped>
.product-search-filters {
  margin-bottom: 1.25rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 0.85rem 1rem;
}

.filters-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-item {
  display: flex;
  align-items: center;
}

.category-filter {
  flex-shrink: 0;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.icon-search {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  background: #0f172a;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.55rem 2.2rem 0.55rem 2.25rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25);
}

.search-input::placeholder {
  color: #64748b;
}

.btn-clear-keyword {
  position: absolute;
  right: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.btn-clear-keyword:hover {
  color: #f8fafc;
  background: #334155;
}

.btn-search {
  background: #0284c7;
  color: #ffffff;
  border: none;
  padding: 0.55rem 1.2rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  white-space: nowrap;
}

.btn-search:hover {
  background: #0369a1;
}

.btn-reset-filters {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: transparent;
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 0.5rem 0.85rem;
  border-radius: 0.375rem;
  font-size: 0.825rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-reset-filters:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: #ef4444;
}

@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input-wrapper {
    min-width: 100%;
  }
  .btn-search,
  .btn-reset-filters {
    width: 100%;
    justify-content: center;
  }
}
</style>
