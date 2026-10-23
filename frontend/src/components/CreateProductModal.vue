<template>
  <div class="modal-backdrop" @click.self="handleClose">
    <div class="modal-box create-modal-box">
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>Thêm Sản Phẩm Mới</h3>
        <button type="button" @click="handleClose" class="btn-close" title="Đóng">&times;</button>
      </div>

      <!-- Modal Body / Form -->
      <form @submit.prevent="handleSubmit" class="modal-body" novalidate>
        <!-- Banner lỗi chung từ server nếu có -->
        <div v-if="serverError" class="alert-error">
          <span class="error-icon">⚠️</span>
          <span>{{ serverError }}</span>
        </div>

        <div class="form-grid">
          <!-- Tên sản phẩm -->
          <div class="form-group col-span-2">
            <label for="create-name">
              Tên Sản Phẩm <span class="required-star">*</span>
            </label>
            <input
              id="create-name"
              v-model="form.name"
              type="text"
              maxlength="200"
              class="form-control"
              :class="{ 'has-error': fieldErrors.name }"
              placeholder="VD: Bàn phím cơ không dây Bluetooth RGB..."
              @input="clearFieldError('name')"
            />
            <small v-if="fieldErrors.name" class="field-error">{{ fieldErrors.name }}</small>
            <small v-else class="field-hint">Tối đa 200 ký tự.</small>
          </div>

          <!-- Mã SKU duy nhất -->
          <div class="form-group">
            <label for="create-sku">
              Mã SKU <span class="required-star">*</span>
            </label>
            <input
              id="create-sku"
              v-model="form.sku"
              type="text"
              maxlength="50"
              class="form-control font-mono"
              :class="{ 'has-error': fieldErrors.sku }"
              placeholder="VD: KB-MECH-01"
              @input="handleSkuInput"
            />
            <small v-if="fieldErrors.sku" class="field-error">{{ fieldErrors.sku }}</small>
            <small v-else class="field-hint">Mã định danh duy nhất (VD: SP-001).</small>
          </div>

          <!-- Danh mục với Tìm kiếm gõ chữ -->
          <div class="form-group custom-select-group" ref="categoryDropdownRef">
            <label>
              Danh Mục <span class="required-star">*</span>
            </label>
            <div
              class="custom-select-trigger"
              :class="{
                'has-error': fieldErrors.category_id,
                'is-open': isCategoryDropdownOpen,
                'has-value': !!selectedCategoryName
              }"
              @click="toggleCategoryDropdown"
              tabindex="0"
              @keydown.enter.prevent="toggleCategoryDropdown"
              @keydown.space.prevent="toggleCategoryDropdown"
              role="button"
              aria-haspopup="listbox"
              :aria-expanded="isCategoryDropdownOpen"
            >
              <span v-if="selectedCategoryName" class="selected-text">{{ selectedCategoryName }}</span>
              <span v-else class="placeholder-text">-- Chọn hoặc gõ tìm danh mục --</span>
              <span class="dropdown-chevron">{{ isCategoryDropdownOpen ? '▲' : '▼' }}</span>
            </div>

            <!-- Dropdown Menu Tìm kiếm & Chọn -->
            <div v-if="isCategoryDropdownOpen" class="custom-dropdown-menu">
              <div class="dropdown-search-box">
                <span class="search-box-icon">🔍</span>
                <input
                  ref="categorySearchInputRef"
                  v-model="categorySearchText"
                  type="text"
                  class="dropdown-search-input"
                  placeholder="Gõ để tìm danh mục..."
                  @click.stop
                  @keydown.stop
                />
                <button
                  v-if="categorySearchText"
                  type="button"
                  class="btn-clear-search"
                  @click.stop="categorySearchText = ''"
                  title="Xoá tìm kiếm"
                >
                  ✕
                </button>
              </div>

              <ul class="dropdown-list" role="listbox">
                <li
                  v-for="cat in filteredCategories"
                  :key="cat.id"
                  :class="['dropdown-item', { active: form.category_id === cat.id }]"
                  @click="selectCategory(cat)"
                  role="option"
                  :aria-selected="form.category_id === cat.id"
                >
                  <span class="cat-name">{{ cat.name }}</span>
                  <span v-if="form.category_id === cat.id" class="check-icon">✓</span>
                </li>
                <li v-if="filteredCategories.length === 0" class="dropdown-empty">
                  Không tìm thấy danh mục "{{ categorySearchText }}"
                </li>
              </ul>
            </div>

            <small v-if="fieldErrors.category_id" class="field-error">{{ fieldErrors.category_id }}</small>
            <small v-else class="field-hint">Nhấp để mở và gõ tìm kiếm danh mục nhanh.</small>
          </div>

          <!-- Đơn giá ($) -->
          <div class="form-group">
            <label for="create-price">
              Đơn Giá ($) <span class="required-star">*</span>
            </label>
            <div class="input-with-prefix">
              <span class="currency-prefix">$</span>
              <input
                id="create-price"
                v-model.number="form.price"
                type="number"
                step="0.01"
                min="0"
                class="form-control with-prefix-padding"
                :class="{ 'has-error': fieldErrors.price }"
                placeholder="0.00"
                @input="clearFieldError('price')"
              />
            </div>
            <small v-if="fieldErrors.price" class="field-error">{{ fieldErrors.price }}</small>
            <small v-else class="field-hint">Đơn giá bán, không âm (>= 0).</small>
          </div>

          <!-- Tồn kho ban đầu -->
          <div class="form-group">
            <label for="create-stock">
              Số Lượng Tồn Kho <span class="required-star">*</span>
            </label>
            <input
              id="create-stock"
              v-model.number="form.stock"
              type="number"
              step="1"
              min="0"
              class="form-control"
              :class="{ 'has-error': fieldErrors.stock }"
              placeholder="0"
              @input="clearFieldError('stock')"
            />
            <small v-if="fieldErrors.stock" class="field-error">{{ fieldErrors.stock }}</small>
            <small v-else class="field-hint">Số nguyên không âm (0 = hết hàng).</small>
          </div>

          <!-- URL hình ảnh đại diện -->
          <div class="form-group col-span-2">
            <label for="create-image">Link Ảnh Đại Diện (Tùy chọn)</label>
            <input
              id="create-image"
              v-model="form.image_url"
              type="url"
              class="form-control"
              placeholder="https://example.com/images/product.jpg"
            />
            <small class="field-hint">Đường dẫn ảnh định dạng HTTP/HTTPS hợp lệ.</small>
          </div>

          <!-- Checkbox Sản phẩm nổi bật -->
          <div class="form-group col-span-2 featured-toggle-group">
            <label class="checkbox-container">
              <input
                type="checkbox"
                v-model="form.is_featured"
                class="checkbox-input"
              />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">
                <span class="star-icon">⭐</span> Đánh dấu là <strong>Sản phẩm nổi bật</strong>
              </span>
            </label>
            <small class="field-hint pl-6">Sản phẩm nổi bật sẽ được ưu tiên hiển thị trên trang chủ và danh mục.</small>
          </div>

          <!-- Mô tả sản phẩm -->
          <div class="form-group col-span-2">
            <label for="create-description">Mô Tả Sản Phẩm (Tùy chọn)</label>
            <textarea
              id="create-description"
              v-model="form.description"
              rows="3"
              class="form-control textarea-control"
              placeholder="Nhập thông tin chi tiết, đặc điểm nổi bật hoặc thông số kỹ thuật..."
            ></textarea>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="modal-footer">
          <button
            type="button"
            @click="handleClose"
            class="btn-cancel"
            :disabled="isSubmitting"
          >
            Hủy Bỏ
          </button>
          <button
            type="submit"
            class="btn-primary btn-submit"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner"></span>
            <span>{{ isSubmitting ? 'Đang tạo sản phẩm...' : '+ Tạo Sản Phẩm' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import api from '../lib/api';
import type { Category } from '../types';

interface ProductCreatePayload {
  name: string;
  sku: string;
  category_id: number;
  price: number;
  stock: number;
  is_featured: boolean;
  image_url: string | null;
  description: string | null;
}

const props = defineProps<{
  categories: Category[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'created'): void;
}>();

const isSubmitting = ref(false);
const serverError = ref<string | null>(null);

// Tìm kiếm trong danh mục
const isCategoryDropdownOpen = ref(false);
const categorySearchText = ref('');
const categoryDropdownRef = ref<HTMLElement | null>(null);
const categorySearchInputRef = ref<HTMLInputElement | null>(null);

function removeAccents(str: string): string {
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
}

const filteredCategories = computed(() => {
  const query = categorySearchText.value.trim();
  if (!query) return props.categories;
  const normalizedQuery = removeAccents(query);
  return props.categories.filter((cat) =>
    removeAccents(cat.name).includes(normalizedQuery)
  );
});

const selectedCategoryName = computed(() => {
  if (!form.category_id) return '';
  const found = props.categories.find((c) => c.id === Number(form.category_id));
  return found ? found.name : '';
});

function toggleCategoryDropdown() {
  isCategoryDropdownOpen.value = !isCategoryDropdownOpen.value;
  if (isCategoryDropdownOpen.value) {
    categorySearchText.value = '';
    nextTick(() => {
      categorySearchInputRef.value?.focus();
    });
  }
}

function selectCategory(cat: Category) {
  form.category_id = cat.id;
  clearFieldError('category_id');
  isCategoryDropdownOpen.value = false;
  categorySearchText.value = '';
}

function handleClickOutside(event: MouseEvent) {
  if (
    categoryDropdownRef.value &&
    !categoryDropdownRef.value.contains(event.target as Node)
  ) {
    isCategoryDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const form = reactive({
  name: '',
  sku: '',
  category_id: '' as unknown as number,
  price: 0,
  stock: 0,
  is_featured: false,
  image_url: '',
  description: '',
});

const fieldErrors = reactive<Record<string, string>>({
  name: '',
  sku: '',
  category_id: '',
  price: '',
  stock: '',
});

function clearFieldError(field: string) {
  if (fieldErrors[field]) {
    fieldErrors[field] = '';
  }
  if (serverError.value) {
    serverError.value = null;
  }
}

function handleSkuInput(event: Event) {
  const target = event.target as HTMLInputElement;
  form.sku = target.value.toUpperCase();
  clearFieldError('sku');
}

function validateForm(): boolean {
  let isValid = true;

  // 1. Tên sản phẩm
  if (!form.name || !form.name.trim()) {
    fieldErrors.name = 'Vui lòng nhập tên sản phẩm.';
    isValid = false;
  } else if (form.name.trim().length > 200) {
    fieldErrors.name = 'Tên sản phẩm không được vượt quá 200 ký tự.';
    isValid = false;
  } else {
    fieldErrors.name = '';
  }

  // 2. Mã SKU
  if (!form.sku || !form.sku.trim()) {
    fieldErrors.sku = 'Vui lòng nhập mã SKU duy nhất.';
    isValid = false;
  } else if (form.sku.trim().length > 50) {
    fieldErrors.sku = 'Mã SKU không được vượt quá 50 ký tự.';
    isValid = false;
  } else {
    fieldErrors.sku = '';
  }

  // 3. Danh mục
  if (!form.category_id || Number(form.category_id) <= 0) {
    fieldErrors.category_id = 'Vui lòng chọn một danh mục cho sản phẩm.';
    isValid = false;
  } else {
    fieldErrors.category_id = '';
  }

  // 4. Đơn giá
  if (form.price === null || form.price === undefined || isNaN(form.price)) {
    fieldErrors.price = 'Vui lòng nhập đơn giá hợp lệ.';
    isValid = false;
  } else if (Number(form.price) < 0) {
    fieldErrors.price = 'Đơn giá không được là số âm (>= 0).';
    isValid = false;
  } else {
    fieldErrors.price = '';
  }

  // 5. Số lượng tồn kho
  if (form.stock === null || form.stock === undefined || isNaN(form.stock)) {
    fieldErrors.stock = 'Vui lòng nhập số lượng tồn kho.';
    isValid = false;
  } else if (Number(form.stock) < 0) {
    fieldErrors.stock = 'Số lượng tồn kho không được âm (>= 0).';
    isValid = false;
  } else if (!Number.isInteger(Number(form.stock))) {
    fieldErrors.stock = 'Số lượng tồn kho phải là số nguyên.';
    isValid = false;
  } else {
    fieldErrors.stock = '';
  }

  return isValid;
}

async function handleSubmit() {
  serverError.value = null;

  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;

  const payload: ProductCreatePayload = {
    name: form.name.trim(),
    sku: form.sku.trim(),
    category_id: Number(form.category_id),
    price: Number(form.price),
    stock: Math.floor(Number(form.stock)),
    is_featured: Boolean(form.is_featured),
    image_url: form.image_url.trim() ? form.image_url.trim() : null,
    description: form.description.trim() ? form.description.trim() : null,
  };

  try {
    const res = await api.post('/products', payload);
    if (res.data.success) {
      emit('created');
    } else {
      serverError.value = res.data.message || 'Không thể tạo sản phẩm.';
    }
  } catch (err: any) {
    console.error('Lỗi khi tạo sản phẩm:', err);
    const apiErrorMsg =
      err.response?.data?.error?.message ||
      err.response?.data?.message ||
      err.response?.data?.detail?.[0]?.msg ||
      'Đã xảy ra lỗi khi tạo sản phẩm. Vui lòng kiểm tra lại thông tin.';

    if (apiErrorMsg.toLowerCase().includes('sku')) {
      fieldErrors.sku = apiErrorMsg;
    }
    serverError.value = apiErrorMsg;
  } finally {
    isSubmitting.value = false;
  }
}

function handleClose() {
  if (isSubmitting.value) return;
  emit('close');
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  backdrop-filter: blur(4px);
}

.create-modal-box {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
  animation: modalFadeIn 0.2s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
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
  font-weight: 700;
  color: #f8fafc;
}

.btn-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  transition: color 0.15s, background-color 0.15s;
}

.btn-close:hover {
  color: #f8fafc;
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox: ẩn thanh kéo */
  -ms-overflow-style: none; /* IE and Edge: ẩn thanh kéo */
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

/* Ẩn hoàn toàn thanh kéo (scrollbar) trên Chrome, Safari, Opera */
.modal-body::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.col-span-2 {
  grid-column: span 2 / span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.825rem;
  font-weight: 600;
  color: #cbd5e1;
}

.required-star {
  color: #f87171;
  font-weight: bold;
}

.form-control {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  height: 38px;
  box-sizing: border-box;
}

.form-control:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25);
}

.form-control.has-error {
  border-color: #f87171;
  background: rgba(239, 68, 68, 0.05);
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  letter-spacing: 0.05em;
}

.select-control {
  appearance: auto;
  cursor: pointer;
}

.input-with-prefix {
  position: relative;
  display: flex;
  align-items: center;
}

.currency-prefix {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
  pointer-events: none;
}

.with-prefix-padding {
  padding-left: 1.75rem;
}

.textarea-control {
  height: auto;
  min-height: 75px;
  resize: none;
}

.field-hint {
  color: #94a3b8;
  font-size: 0.75rem;
}

.field-error {
  color: #f87171;
  font-size: 0.75rem;
  font-weight: 500;
}

.pl-6 {
  padding-left: 1.5rem;
}

/* Checkbox Styling */
.featured-toggle-group {
  background: rgba(15, 23, 42, 0.5);
  padding: 0.65rem 0.85rem;
  border-radius: 0.375rem;
  border: 1px dashed #334155;
}

.checkbox-container {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  gap: 0.5rem;
  user-select: none;
}

.checkbox-input {
  width: 1.1rem;
  height: 1.1rem;
  accent-color: #0284c7;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.85rem;
  color: #e2e8f0;
}

.star-icon {
  color: #facc15;
}

.alert-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 0.65rem 0.9rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
}

.error-icon {
  font-size: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #334155;
}

.btn-cancel {
  background: #334155;
  color: #cbd5e1;
  border: none;
  padding: 0.55rem 1.15rem;
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover:not(:disabled) {
  background: #475569;
}

.btn-primary {
  background: #0284c7;
  color: #fff;
  border: none;
  padding: 0.55rem 1.15rem;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-primary:hover:not(:disabled) {
  background: #0369a1;
}

.btn-primary:disabled,
.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .col-span-2 {
    grid-column: span 1;
  }
}

/* Custom Searchable Category Select */
.custom-select-group {
  position: relative;
}

.custom-select-trigger {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.custom-select-trigger:focus,
.custom-select-trigger.is-open {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25);
  outline: none;
}

.custom-select-trigger.has-error {
  border-color: #f87171;
  background: rgba(239, 68, 68, 0.05);
}

.placeholder-text {
  color: #64748b;
}

.selected-text {
  color: #f8fafc;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-chevron {
  color: #94a3b8;
  font-size: 0.65rem;
  margin-left: 0.5rem;
}

.custom-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.6);
  z-index: 1050;
  overflow: hidden;
  animation: dropdownFade 0.15s ease-out;
}

@keyframes dropdownFade {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-search-box {
  display: flex;
  align-items: center;
  padding: 0.45rem 0.65rem;
  border-bottom: 1px solid #334155;
  background: #162032;
  gap: 0.45rem;
}

.search-box-icon {
  font-size: 0.8rem;
  color: #94a3b8;
}

.dropdown-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f8fafc;
  font-size: 0.825rem;
  padding: 0;
}

.dropdown-search-input::placeholder {
  color: #64748b;
}

.btn-clear-search {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0 0.25rem;
  line-height: 1;
}

.btn-clear-search:hover {
  color: #f8fafc;
}

.dropdown-list {
  list-style: none;
  margin: 0;
  padding: 0.25rem 0;
  max-height: 180px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #334155 transparent;
}

.dropdown-list::-webkit-scrollbar {
  width: 5px;
}

.dropdown-list::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: #cbd5e1;
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}

.dropdown-item:hover {
  background: #1e293b;
  color: #f8fafc;
}

.dropdown-item.active {
  background: rgba(2, 132, 199, 0.15);
  color: #38bdf8;
  font-weight: 600;
}

.check-icon {
  color: #38bdf8;
  font-weight: bold;
}

.dropdown-empty {
  padding: 0.85rem 0.75rem;
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: center;
  font-style: italic;
}
</style>
