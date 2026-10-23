<template>
  <span :class="['stock-badge', info.badgeClass]" :title="tooltipText">
    <span v-if="showQuantity" class="stock-qty">{{ info.displayQuantity }}</span>
    <span v-if="showQuantity" class="stock-separator">-</span>
    <span class="stock-status">{{ info.statusLabel }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { getStockInfo } from '../lib/inventory';

const props = withDefaults(
  defineProps<{
    stock: unknown;
    showQuantity?: boolean;
  }>(),
  {
    showQuantity: true,
  }
);

const info = computed(() => getStockInfo(props.stock));

const tooltipText = computed(() => {
  if (info.value.status === 'ANOMALOUS') {
    return 'Cảnh báo: Dữ liệu tồn kho bị âm, cần kiểm tra lại cơ sở dữ liệu!';
  }
  if (info.value.status === 'INVALID') {
    return 'Lỗi: Dữ liệu tồn kho không hợp lệ hoặc không có sẵn!';
  }
  return `Tồn kho: ${info.value.displayQuantity} (${info.value.statusLabel})`;
});
</script>

<style scoped>
.stock-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 0.375rem;
  white-space: nowrap;
  line-height: 1.25;
  border: 1px solid transparent;
}

.stock-qty {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stock-separator {
  opacity: 0.6;
}

.stock-status {
  font-weight: 500;
}

/* 1. Còn hàng (In Stock) */
.in-stock {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border-color: rgba(34, 197, 94, 0.3);
}

/* 2. Hết hàng (Out of Stock) */
.out-of-stock {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.35);
  font-weight: 600;
}

/* 3. Dữ liệu bất thường (Anomalous Data < 0) */
.stock-anomalous {
  background: rgba(249, 115, 22, 0.2);
  color: #fb923c;
  border-color: rgba(249, 115, 22, 0.4);
  font-weight: 600;
}

/* 4. Dữ liệu không xác định / Lỗi (Invalid Data) */
.stock-invalid {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  border-color: rgba(148, 163, 184, 0.3);
  font-style: italic;
}
</style>
