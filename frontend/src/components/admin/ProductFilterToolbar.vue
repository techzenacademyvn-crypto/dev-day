<template>
  <section ref="toolbarRef" class="product-filter-toolbar" aria-label="Bộ lọc sản phẩm">
    <div class="filter-row">
      <CategoryTreeSelect v-model="draft.categoryId" />
      <label class="search-field">
        <span class="sr-only">Tên hoặc mã sản phẩm</span>
        <input v-model="draft.search" type="search" placeholder="Nhập tên / mã sản phẩm" @keyup.enter="apply" />
      </label>
      <label class="number-field">
        <span>Min ($)</span>
        <input v-model="draft.minPrice" inputmode="decimal" placeholder="0.00" @input="validatePrices" />
        <small v-if="minPriceError">{{ minPriceError }}</small>
      </label>
      <label class="number-field">
        <span>Max ($)</span>
        <input v-model="draft.maxPrice" inputmode="decimal" placeholder="0.00" @input="validatePrices" />
        <small v-if="maxPriceError">{{ maxPriceError }}</small>
      </label>
      <button type="button" class="featured-button" :class="{ active: draft.isFeatured }" @click="draft.isFeatured = !draft.isFeatured">
        {{ draft.isFeatured ? '★ Nổi bật' : '☆ Nổi bật' }}
      </button>
      <button type="button" class="apply-button" @click="apply">Lọc</button>
    </div>
    <div class="filter-row filter-row-secondary">
      <label class="select-field">
        <span>Tình trạng tồn kho</span>
        <select v-model="draft.stockStatus">
          <option value="all">Tất cả tồn kho</option>
          <option value="in_stock">Còn hàng</option>
          <option value="out_of_stock">Hết hàng</option>
          <option value="low_stock">Tồn kho thấp</option>
          <option value="aged_stock">Tồn kho ≥10 · Tạo ≥20 ngày</option>
        </select>
      </label>
      <button type="button" class="stock-order-button" @click="toggleStockOrder">
        {{ draft.sortBy === 'stock_asc' ? '↑ Ít → nhiều' : '↓ Nhiều → ít' }}
      </button>
      <label class="select-field sort-field">
        <span>Sắp xếp</span>
        <select v-model="draft.sortBy">
          <option value="">Mặc định hệ thống</option>
          <option value="created_desc">Mới tạo nhất</option>
          <option value="created_asc">Cũ nhất</option>
          <option value="name_asc">Tên A → Z</option>
          <option value="name_desc">Tên Z → A</option>
          <option value="price_desc">Giá cao → thấp</option>
          <option value="price_asc">Giá thấp → cao</option>
          <option value="sku_asc">SKU A → Z</option>
          <option value="sku_desc">SKU Z → A</option>
          <option value="category">Theo danh mục</option>
          <option value="featured_first">Sản phẩm nổi bật trước</option>
        </select>
      </label>
      <button type="button" class="reset-button" @click="reset">Đặt lại</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import CategoryTreeSelect from './CategoryTreeSelect.vue';

export interface ProductFilterPayload {
  search: string;
  categoryId: number | null;
  minPrice: string | null;
  maxPrice: string | null;
  isFeatured: boolean;
  stockStatus: string;
  sortBy: string;
}

const emit = defineEmits<{ (e: 'apply', value: ProductFilterPayload): void; (e: 'reset'): void }>();
const toolbarRef = ref<HTMLElement | null>(null);
let resizeObserver: ResizeObserver | undefined;
const draft = reactive({ search: '', categoryId: null as number | null, minPrice: '', maxPrice: '', isFeatured: false, stockStatus: 'all', sortBy: '' });
const minPriceError = ref('');
const maxPriceError = ref('');
const moneyPattern = /^\d+(?:\.\d{1,2})?$/;

function validatePrices() {
  minPriceError.value = '';
  maxPriceError.value = '';
  const min = draft.minPrice.trim();
  const max = draft.maxPrice.trim();
  if (min && !moneyPattern.test(min)) minPriceError.value = 'Nhập số không âm, tối đa 2 số lẻ';
  if (max && !moneyPattern.test(max)) maxPriceError.value = 'Nhập số không âm, tối đa 2 số lẻ';
  if (!minPriceError.value && !maxPriceError.value && min && max && Number(min) > Number(max)) {
    maxPriceError.value = 'Max phải lớn hơn hoặc bằng Min';
  }
  return !minPriceError.value && !maxPriceError.value;
}

function apply() {
  if (!validatePrices()) return;
  emit('apply', {
    search: draft.search.trim(), categoryId: draft.categoryId, minPrice: draft.minPrice.trim() || null,
    maxPrice: draft.maxPrice.trim() || null, isFeatured: draft.isFeatured, stockStatus: draft.stockStatus, sortBy: draft.sortBy,
  });
}

function toggleStockOrder() {
  draft.sortBy = draft.sortBy === 'stock_desc' ? 'stock_asc' : 'stock_desc';
}

function reset() {
  Object.assign(draft, { search: '', categoryId: null, minPrice: '', maxPrice: '', isFeatured: false, stockStatus: 'all', sortBy: '' });
  minPriceError.value = '';
  maxPriceError.value = '';
  emit('reset');
}

onMounted(() => {
  const updateHeight = () => document.documentElement.style.setProperty('--tz-filter-toolbar-height', `${toolbarRef.value?.offsetHeight || 0}px`);
  updateHeight();
  resizeObserver = new ResizeObserver(updateHeight);
  if (toolbarRef.value) resizeObserver.observe(toolbarRef.value);
});
onUnmounted(() => { resizeObserver?.disconnect(); document.documentElement.style.removeProperty('--tz-filter-toolbar-height'); });
</script>

<style scoped>
.product-filter-toolbar { position: sticky; top: var(--tz-navbar-height, 0px); z-index: 60; margin-bottom: 14px; padding: .7rem; background: #142b4a; border: 1px solid #365676; border-radius: .55rem; box-shadow: 0 4px 12px rgba(0,0,0,.18); }
.filter-row { display: flex; align-items: flex-start; gap: .55rem; flex-wrap: wrap; }
.filter-row + .filter-row { margin-top: .55rem; }
.search-field { flex: 1 1 240px; min-width: 190px; }
.search-field input, .number-field input, .select-field select { box-sizing: border-box; width: 100%; height: 42px; padding: 0 .75rem; color: #f8fafc; background: #0f172a; border: 1px solid #475569; border-radius: .375rem; font: inherit; }
.number-field { width: 118px; position: relative; }
.number-field > span, .select-field > span { display: block; margin: 0 0 .2rem .1rem; color: #cbd5e1; font-size: .72rem; font-weight: 600; }
.number-field small { display: block; color: #fca5a5; font-size: .68rem; line-height: 1.1; }
.select-field { min-width: 205px; }
.sort-field { min-width: 185px; }
button { height: 42px; padding: 0 .85rem; border-radius: .375rem; border: 1px solid #475569; cursor: pointer; font-weight: 600; white-space: nowrap; }
.featured-button, .stock-order-button, .reset-button { color: #cbd5e1; background: #0f172a; }
.featured-button.active { color: #facc15; border-color: #facc15; background: rgba(250,204,21,.12); }
.apply-button { color: #fff; background: #0284c7; border-color: #0284c7; }
.reset-button { color: #fca5a5; }
.sr-only { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0,0,0,0); }
@media (max-width: 768px) { .product-filter-toolbar { padding: .6rem; } .filter-row { align-items: stretch; } .search-field, .number-field, .select-field { flex: 1 1 100%; width: 100%; } button { flex: 1 1 auto; } }
</style>
