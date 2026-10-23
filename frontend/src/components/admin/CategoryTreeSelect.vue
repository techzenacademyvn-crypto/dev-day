<template>
  <div class="category-tree-select" ref="containerRef">
    <!-- Trigger Button -->
    <button
      type="button"
      class="tree-select-trigger"
      :class="{ 'is-open': isOpen }"
      @click="toggleDropdown"
      aria-haspopup="listbox"
      :aria-expanded="isOpen"
    >
      <div class="trigger-label">
        <svg class="icon-folder" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
        </svg>
        <span class="selected-text">{{ selectedLabel }}</span>
      </div>
      <svg class="chevron-indicator" :class="{ rotated: isOpen }" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
        <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z" />
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <div v-if="isOpen" class="tree-select-dropdown">
      <div class="category-search-box">
        <input v-model="keyword" type="search" placeholder="Tìm danh mục" aria-label="Tìm danh mục" />
        <button v-if="keyword" type="button" @click="keyword = ''" aria-label="Xóa từ khóa">×</button>
      </div>
      <!-- Item: Tất cả danh mục -->
      <div
        class="tree-node-row"
        :class="{ 'is-selected': modelValue === null }"
        @click="selectCategory(null, 'Tất cả danh mục')"
      >
        <div class="tree-node-content">
          <span class="tree-arrow-placeholder"></span>
          <svg class="icon-folder" viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
            <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
          </svg>
          <span class="tree-node-title">Tất cả danh mục</span>
        </div>
        <svg v-if="modelValue === null" class="icon-check" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
        </svg>
      </div>

      <!-- Loading / Error states -->
      <div v-if="loadingCategories" class="tree-loading">
        Đang tải danh mục...
      </div>
      <div v-else-if="categoriesError" class="tree-error">
        {{ categoriesError }}
      </div>

      <!-- Danh sách cây danh mục -->
      <div v-else-if="treeData.length" class="tree-nodes-list">
        <div
          v-for="cat in treeData"
          :key="cat.id"
          class="tree-node-group"
        >
          <!-- Nút cấp 1 -->
          <div
            class="tree-node-row"
            :class="{ 'is-selected': modelValue === cat.id }"
            @click="selectCategory(cat.id, cat.name)"
          >
            <div class="tree-node-content">
              <!-- Mũi tên đóng/mở nhánh nếu có con thực tế (ngăn chặn nổi bọt sự kiện chọn) -->
              <span
                v-if="cat.children && cat.children.length > 0"
                class="tree-arrow"
                :class="{ expanded: expandedIds.has(cat.id) }"
                @click.stop="toggleExpand(cat.id)"
                title="Mở/thu gọn nhánh"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                  <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" />
                </svg>
              </span>
              <span v-else class="tree-arrow-placeholder"></span>

              <svg class="icon-folder" viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
                <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
              </svg>
              <span class="tree-node-title">{{ cat.name }}</span>
            </div>
            <svg v-if="modelValue === cat.id" class="icon-check" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
            </svg>
          </div>

          <!-- Nhánh con cấp 2 (nếu có trong dữ liệu thực) -->
          <div
            v-if="cat.children && cat.children.length > 0 && expandedIds.has(cat.id)"
            class="tree-children"
          >
            <div
              v-for="sub in cat.children"
              :key="sub.id"
              class="tree-node-row is-child"
              :class="{ 'is-selected': modelValue === sub.id }"
              @click="selectCategory(sub.id, sub.name)"
            >
              <div class="tree-node-content">
                <span class="tree-arrow-placeholder"></span>
                <svg class="icon-folder" viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                  <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
                </svg>
                <span class="tree-node-title">{{ sub.name }}</span>
              </div>
              <svg v-if="modelValue === sub.id" class="icon-check" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="tree-loading">Không tìm thấy danh mục phù hợp</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../../lib/api';

interface CategoryItem {
  id: number;
  name: string;
  slug: string;
  parent_id?: number | null;
  children?: CategoryItem[];
}

const props = defineProps<{
  modelValue: number | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void;
  (e: 'change', value: number | null): void;
}>();

const containerRef = ref<HTMLElement | null>(null);
const isOpen = ref(false);
const rawCategories = ref<CategoryItem[]>([]);
const loadingCategories = ref(false);
const categoriesError = ref('');
const expandedIds = ref<Set<number>>(new Set());
const keyword = ref('');

function normalize(value: string) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'd').toLowerCase().trim();
}

// Nhãn hiển thị trên trigger button
const selectedLabel = computed(() => {
  if (props.modelValue === null) return 'Tất cả danh mục';
  const found = rawCategories.value.find((c) => c.id === props.modelValue);
  return found ? found.name : 'Tất cả danh mục';
});

// Xây dựng cây danh mục từ dữ liệu thực tế
const treeData = computed<CategoryItem[]>(() => {
  const query = normalize(keyword.value);
  const items = query
    ? rawCategories.value.filter((item) => normalize(item.name).includes(query))
    : rawCategories.value;
  // Kiểm tra nếu có parent_id thực tế
  const hasParent = items.some((item) => item.parent_id !== undefined && item.parent_id !== null);
  if (!hasParent) {
    // Database chỉ có danh mục một cấp: hiển thị nguyên bản 1 cấp, không tạo cha giả
    return items;
  }

  // Nếu có phân cấp cha - con
  const map = new Map<number, CategoryItem>();
  items.forEach((item) => map.set(item.id, { ...item, children: [] }));
  const roots: CategoryItem[] = [];

  items.forEach((item) => {
    const node = map.get(item.id)!;
    if (item.parent_id && map.has(item.parent_id)) {
      map.get(item.parent_id)!.children!.push(node);
    } else {
      roots.push(node);
    }
  });

  return roots;
});

async function fetchCategories() {
  loadingCategories.value = true;
  categoriesError.value = '';
  try {
    const res = await api.get('/categories', {
      params: { is_active: true, page_size: 100 },
    });
    if (res.data.success) {
      rawCategories.value = res.data.data.items;
    }
  } catch (err: any) {
    categoriesError.value = 'Không thể tải danh mục';
    console.error(err);
  } finally {
    loadingCategories.value = false;
  }
}

function toggleDropdown() {
  isOpen.value = !isOpen.value;
  if (!isOpen.value) keyword.value = '';
}

function toggleExpand(id: number) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id);
  } else {
    expandedIds.value.add(id);
  }
}

function selectCategory(id: number | null, _name: string) {
  emit('update:modelValue', id);
  emit('change', id);
  isOpen.value = false;
  keyword.value = '';
}

// Đóng dropdown khi click ra ngoài
function handleClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
}

onMounted(() => {
  fetchCategories();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.category-tree-select {
  position: relative;
  min-width: 210px;
}

.tree-select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.55rem 0.85rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.tree-select-trigger:hover,
.tree-select-trigger.is-open {
  border-color: #0284c7;
  background: #24344d;
}

.trigger-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.icon-folder {
  color: #38bdf8;
  flex-shrink: 0;
}

.selected-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron-indicator {
  color: #94a3b8;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.chevron-indicator.rotated {
  transform: rotate(180deg);
}

.tree-select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  min-width: 250px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
  max-height: 320px;
  overflow-y: auto;
  z-index: 100;
  padding: 0.35rem 0;
}

.category-search-box {
  display: flex;
  gap: .35rem;
  padding: .4rem .5rem;
  border-bottom: 1px solid #334155;
}
.category-search-box input { min-width: 0; flex: 1; padding: .45rem .55rem; color: #f8fafc; background: #020617; border: 1px solid #475569; border-radius: .3rem; }
.category-search-box button { color: #94a3b8; background: transparent; border: 0; cursor: pointer; font-size: 1.1rem; }

.tree-node-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.tree-node-row:hover {
  background: #1e293b;
  color: #f8fafc;
}

.tree-node-row.is-selected {
  background: rgba(2, 132, 199, 0.2);
  color: #38bdf8;
  font-weight: 600;
}

.tree-node-row.is-child {
  padding-left: 2rem;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  overflow: hidden;
}

.tree-node-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: #94a3b8;
  border-radius: 3px;
  transition: transform 0.2s ease, background 0.15s ease;
}

.tree-arrow:hover {
  background: #334155;
  color: #f8fafc;
}

.tree-arrow.expanded {
  transform: rotate(90deg);
}

.tree-arrow-placeholder {
  display: inline-block;
  width: 18px;
}

.icon-check {
  color: #38bdf8;
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.tree-loading,
.tree-error {
  padding: 0.75rem;
  text-align: center;
  font-size: 0.825rem;
  color: #94a3b8;
}

.tree-error {
  color: #f87171;
}

/* Custom scrollbar cho dropdown */
.tree-select-dropdown::-webkit-scrollbar {
  width: 6px;
}
.tree-select-dropdown::-webkit-scrollbar-track {
  background: #0f172a;
}
.tree-select-dropdown::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 3px;
}
.tree-select-dropdown::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
</style>
