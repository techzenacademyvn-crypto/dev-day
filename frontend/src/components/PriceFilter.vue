<template>
  <div class="price-filter-card">
    <div class="filter-header">
      <div class="filter-title-group">
        <span class="filter-icon">🏷️</span>
        <h3 class="filter-title">Bộ Lọc Theo Giá</h3>
      </div>
      <div class="price-range-badge">
        <span class="badge-label">Khoảng giá đã chọn:</span>
        <span class="badge-value">{{ formatVND(currentMin) }} — {{ formatVND(currentMax) }}</span>
      </div>
    </div>

    <!-- Thanh trượt kép chuẩn Pointer-Capture (kéo tới / vuốt lùi mượt mà 100%) -->
    <div class="slider-section">
      <div
        ref="trackContainerRef"
        class="slider-container"
        @pointerdown="onTrackPointerDown"
        title="Nhấn hoặc kéo bất kỳ đâu trên thanh để chọn giá"
      >
        <div class="slider-track-bg"></div>
        <div
          class="slider-track-highlight"
          :style="{
            left: `${minPercent}%`,
            width: `${Math.max(0, maxPercent - minPercent)}%`,
          }"
        ></div>

        <!-- Con trượt Min (Giá tối thiểu) -->
        <div
          class="slider-thumb thumb-min"
          :class="{ active: activeThumb === 'min' }"
          :style="{
            left: `${minPercent}%`,
            zIndex: activeThumb === 'min' ? 12 : 6,
          }"
          tabindex="0"
          role="slider"
          :aria-valuenow="currentMin"
          :aria-valuemin="min"
          :aria-valuemax="currentMax"
          aria-label="Con trượt giá tối thiểu"
          title="Kéo sang trái hoặc phải để đổi giá tối thiểu"
          @pointerdown.stop="startDrag($event, 'min')"
          @keydown="onKeyDown($event, 'min')"
        >
          <div class="thumb-core"></div>
        </div>

        <!-- Con trượt Max (Giá tối đa) -->
        <div
          class="slider-thumb thumb-max"
          :class="{ active: activeThumb === 'max' }"
          :style="{
            left: `${maxPercent}%`,
            zIndex: activeThumb === 'max' ? 12 : 7,
          }"
          tabindex="0"
          role="slider"
          :aria-valuenow="currentMax"
          :aria-valuemin="currentMin"
          :aria-valuemax="max"
          aria-label="Con trượt giá tối đa"
          title="Kéo sang trái hoặc phải để đổi giá tối đa"
          @pointerdown.stop="startDrag($event, 'max')"
          @keydown="onKeyDown($event, 'max')"
        >
          <div class="thumb-core"></div>
        </div>
      </div>

      <!-- Thước đo mốc giá bên dưới thanh trượt -->
      <div class="slider-ticks">
        <span class="tick-label">{{ formatVND(min) }}</span>
        <span class="tick-label">500.000đ</span>
        <span class="tick-label">1.000.000đ</span>
        <span class="tick-label">1.500.000đ</span>
        <span class="tick-label">{{ formatVND(max) }}</span>
      </div>
    </div>

    <!-- Danh sách các Nút gợi ý mức giá chọn nhanh (Quick Price Chips) -->
    <div class="chips-section">
      <span class="chips-label">Gợi ý chọn nhanh (bấm để xem ngay):</span>
      <div class="chips-list">
        <button
          v-for="chip in quickChips"
          :key="chip.id"
          type="button"
          :class="['chip-btn', selectedChipId === chip.id ? 'active' : '']"
          @click="applyChip(chip)"
        >
          <span class="chip-check" v-if="selectedChipId === chip.id">✓</span>
          {{ chip.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

export interface PriceRange {
  min: number;
  max: number;
}

const props = withDefaults(
  defineProps<{
    min?: number;
    max?: number;
    step?: number;
    modelValue?: [number, number];
  }>(),
  {
    min: 0,
    max: 2000000,
    step: 10000,
    modelValue: () => [0, 2000000],
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: [number, number]): void;
  (e: 'change', value: PriceRange): void;
}>();

const trackContainerRef = ref<HTMLElement | null>(null);
const currentMin = ref(props.modelValue ? props.modelValue[0] : props.min);
const currentMax = ref(props.modelValue ? props.modelValue[1] : props.max);
const activeThumb = ref<'min' | 'max' | null>(null);

// Đồng bộ nếu modelValue từ ngoài thay đổi
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      currentMin.value = newVal[0];
      currentMax.value = newVal[1];
    }
  },
  { deep: true }
);

// Tính phần trăm vị trí thanh trượt
const minPercent = computed(() => {
  const range = props.max - props.min;
  if (range <= 0) return 0;
  return Math.min(100, Math.max(0, ((currentMin.value - props.min) / range) * 100));
});

const maxPercent = computed(() => {
  const range = props.max - props.min;
  if (range <= 0) return 100;
  return Math.min(100, Math.max(0, ((currentMax.value - props.min) / range) * 100));
});

// Định dạng tiền tệ VNĐ rõ ràng cho người lớn tuổi
function formatVND(value: number): string {
  return new Intl.NumberFormat('vi-VN').format(value) + 'đ';
}

function emitChange() {
  const result: [number, number] = [currentMin.value, currentMax.value];
  emit('update:modelValue', result);
  emit('change', { min: currentMin.value, max: currentMax.value });
}

/**
 * Tính toán giá trị từ tọa độ X của chuột / ngón tay (chuẩn xác theo step 10.000đ)
 */
function getValueFromClientX(clientX: number): number {
  if (!trackContainerRef.value) return props.min;
  const rect = trackContainerRef.value.getBoundingClientRect();
  const width = rect.width;
  if (width <= 0) return props.min;

  let ratio = (clientX - rect.left) / width;
  ratio = Math.max(0, Math.min(1, ratio));

  const totalRange = props.max - props.min;
  const rawValue = props.min + ratio * totalRange;

  const steps = Math.round((rawValue - props.min) / props.step);
  let steppedValue = props.min + steps * props.step;
  steppedValue = Math.max(props.min, Math.min(props.max, steppedValue));

  return steppedValue;
}

/**
 * Kéo rê trực tiếp trên con trượt (Min hoặc Max)
 * Sử dụng Pointer Capture để không bao giờ bị mất trỏ chuột khi vuốt nhanh hoặc vuốt ngược
 */
function startDrag(e: PointerEvent, thumb: 'min' | 'max') {
  e.preventDefault();
  activeThumb.value = thumb;
  const target = e.currentTarget as HTMLElement;
  target.setPointerCapture(e.pointerId);

  const onPointerMove = (moveEvent: PointerEvent) => {
    const val = getValueFromClientX(moveEvent.clientX);
    if (thumb === 'min') {
      currentMin.value = Math.min(val, currentMax.value);
    } else {
      currentMax.value = Math.max(val, currentMin.value);
    }
    emitChange();
  };

  const onPointerUp = (upEvent: PointerEvent) => {
    try {
      target.releasePointerCapture(upEvent.pointerId);
    } catch {
      // Bỏ qua nếu pointer capture đã giải phóng
    }
    target.removeEventListener('pointermove', onPointerMove);
    target.removeEventListener('pointerup', onPointerUp);
    target.removeEventListener('pointercancel', onPointerUp);
    activeThumb.value = null;
  };

  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerup', onPointerUp);
  target.addEventListener('pointercancel', onPointerUp);
}

/**
 * Nhấn chuột hoặc chạm bất kỳ đâu trên thanh trượt
 * Tự động chọn con trượt gần nhất và cho phép tiếp tục vuốt lùi/tới ngay lập tức
 */
function onTrackPointerDown(e: PointerEvent) {
  if (!trackContainerRef.value) return;
  const val = getValueFromClientX(e.clientX);

  let chosenThumb: 'min' | 'max';
  if (currentMin.value === currentMax.value) {
    chosenThumb = val <= currentMin.value ? 'min' : 'max';
  } else {
    const distToMin = Math.abs(val - currentMin.value);
    const distToMax = Math.abs(val - currentMax.value);
    chosenThumb = distToMin <= distToMax ? 'min' : 'max';
  }

  activeThumb.value = chosenThumb;
  if (chosenThumb === 'min') {
    currentMin.value = Math.min(val, currentMax.value);
  } else {
    currentMax.value = Math.max(val, currentMin.value);
  }
  emitChange();

  const target = e.currentTarget as HTMLElement;
  target.setPointerCapture(e.pointerId);

  const onPointerMove = (moveEvent: PointerEvent) => {
    const moveVal = getValueFromClientX(moveEvent.clientX);
    if (chosenThumb === 'min') {
      currentMin.value = Math.min(moveVal, currentMax.value);
    } else {
      currentMax.value = Math.max(moveVal, currentMin.value);
    }
    emitChange();
  };

  const onPointerUp = (upEvent: PointerEvent) => {
    try {
      target.releasePointerCapture(upEvent.pointerId);
    } catch {
      // ignore
    }
    target.removeEventListener('pointermove', onPointerMove);
    target.removeEventListener('pointerup', onPointerUp);
    target.removeEventListener('pointercancel', onPointerUp);
    activeThumb.value = null;
  };

  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerup', onPointerUp);
  target.addEventListener('pointercancel', onPointerUp);
}

/**
 * Hỗ trợ phím mũi tên bàn phím (Trái/Phải)
 */
function onKeyDown(e: KeyboardEvent, thumb: 'min' | 'max') {
  let delta = 0;
  if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
    delta = -props.step;
  } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
    delta = props.step;
  } else if (e.key === 'PageDown') {
    delta = -props.step * 10;
  } else if (e.key === 'PageUp') {
    delta = props.step * 10;
  } else if (e.key === 'Home') {
    delta = -props.max;
  } else if (e.key === 'End') {
    delta = props.max;
  } else {
    return;
  }

  e.preventDefault();
  if (thumb === 'min') {
    currentMin.value = Math.max(props.min, Math.min(currentMin.value + delta, currentMax.value));
  } else {
    currentMax.value = Math.max(currentMin.value, Math.min(currentMax.value + delta, props.max));
  }
  emitChange();
}

// Cấu hình các nút gợi ý mức giá chọn nhanh (Quick Price Chips)
interface QuickChip {
  id: string;
  label: string;
  min: number;
  max: number;
}

const quickChips: QuickChip[] = [
  { id: 'under100', label: 'Dưới 100.000đ', min: 0, max: 100000 },
  { id: '100to300', label: '100.000đ - 300.000đ', min: 100000, max: 300000 },
  { id: '300to500', label: '300.000đ - 500.000đ', min: 300000, max: 500000 },
  { id: 'above500', label: 'Trên 500.000đ', min: 500000, max: 2000000 },
  { id: 'all', label: 'Tất cả mức giá (Đặt lại)', min: 0, max: 2000000 },
];

const selectedChipId = computed(() => {
  if (currentMin.value === 0 && currentMax.value === 2000000) return 'all';
  if (currentMin.value === 0 && currentMax.value === 100000) return 'under100';
  if (currentMin.value === 100000 && currentMax.value === 300000) return '100to300';
  if (currentMin.value === 300000 && currentMax.value === 500000) return '300to500';
  if (currentMin.value === 500000 && currentMax.value === 2000000) return 'above500';
  return null;
});

function applyChip(chip: QuickChip) {
  currentMin.value = chip.min;
  currentMax.value = chip.max;
  emitChange();
}

function reset() {
  currentMin.value = props.min;
  currentMax.value = props.max;
  emitChange();
}

defineExpose({
  reset,
  currentMin,
  currentMax,
  formatVND,
});
</script>

<style scoped>
.price-filter-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #334155;
}

.filter-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-icon {
  font-size: 1.5rem;
}

.filter-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.price-range-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #0f172a;
  border: 1px solid #0284c7;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
}

.badge-label {
  color: #94a3b8;
  font-size: 0.95rem;
}

.badge-value {
  color: #38bdf8;
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.01em;
}

/* Khu vực thanh trượt kép */
.slider-section {
  padding: 0.5rem 1rem 1rem 1rem;
}

.slider-container {
  position: relative;
  height: 48px;
  display: flex;
  align-items: center;
  cursor: pointer;
  touch-action: none; /* Tránh xung đột cuộn màn hình khi vuốt slider */
  user-select: none;
}

.slider-track-bg {
  position: absolute;
  width: 100%;
  height: 10px;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 9999px;
}

.slider-track-highlight {
  position: absolute;
  height: 10px;
  background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%);
  border-radius: 9999px;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
  pointer-events: none;
}

.slider-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #38bdf8;
  border: 4px solid #0f172a;
  box-shadow: 0 0 0 2px #38bdf8, 0 4px 8px rgba(0, 0, 0, 0.5);
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: none;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease;
  outline: none;
  user-select: none;
}

.slider-thumb:hover {
  transform: translate(-50%, -50%) scale(1.15);
  background: #7dd3fc;
  box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.5), 0 6px 12px rgba(0, 0, 0, 0.6);
}

.slider-thumb:active,
.slider-thumb.active {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.25);
  background: #ffffff;
  box-shadow: 0 0 0 5px rgba(56, 189, 248, 0.6), 0 8px 16px rgba(0, 0, 0, 0.7);
}

.thumb-core {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #0284c7;
  pointer-events: none;
}

.slider-ticks {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
  user-select: none;
}

/* Danh sách các nút chọn nhanh (Quick Price Chips) */
.chips-section {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px dashed #334155;
}

.chips-label {
  display: block;
  font-size: 0.95rem;
  font-weight: 600;
  color: #cbd5e1;
  margin-bottom: 0.75rem;
}

.chips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.chip-btn {
  background: #0f172a;
  color: #cbd5e1;
  border: 1.5px solid #334155;
  padding: 0.75rem 1.25rem;
  border-radius: 9999px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 46px; /* Chuẩn kích thước dễ chạm cho người lớn tuổi */
  transition: all 0.2s ease;
  user-select: none;
}

.chip-btn:hover {
  border-color: #38bdf8;
  color: #f8fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.chip-btn.active {
  background: #0284c7;
  color: #ffffff;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.4), 0 4px 10px rgba(2, 132, 199, 0.4);
  font-weight: 700;
}

.chip-check {
  font-weight: 900;
  color: #ffffff;
}

@media (max-width: 640px) {
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .price-range-badge {
    width: 100%;
    justify-content: space-between;
  }
  .chip-btn {
    flex: 1 1 calc(50% - 0.5rem);
    justify-content: center;
    font-size: 0.9rem;
    padding: 0.6rem 0.8rem;
  }
}
</style>