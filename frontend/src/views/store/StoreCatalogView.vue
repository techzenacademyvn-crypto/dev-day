<template>
  <div class="store-page">
    <div class="hero-banner">
      <div class="hero-content">
        <h1>Cửa Hàng Trực Tuyến TZ Shop</h1>
        <p>Đồ công nghệ, gia dụng, thời trang và nhiều hơn nữa</p>
      </div>
    </div>

    <div class="container">
      <div class="catalog-header">
        <h2>Danh Sách Sản Phẩm Mẫu</h2>
        <span class="product-count">Hiển thị {{ products.length }} sản phẩm</span>
      </div>

      <div v-if="loading" class="text-center py-8">
        Đang tải sản phẩm cửa hàng...
      </div>

      <div v-else class="product-grid">
        <div v-for="prod in products" :key="prod.id" class="product-card">
          <div class="card-media">
            <span class="sku-tag">{{ prod.sku }}</span>
            <span v-if="prod.is_featured" class="featured-badge">Hot</span>
            <div class="placeholder-img">
              🛍️ {{ prod.name.slice(0, 15) }}...
            </div>
          </div>

          <div class="card-body">
            <h3 class="product-title">{{ prod.name }}</h3>
            <p class="product-desc">{{ prod.description || 'Sản phẩm chất lượng cao của TZ Shop.' }}</p>

            <div class="card-footer">
              <div class="price-box">
                <span class="price">${{ Number(prod.price).toFixed(2) }}</span>
                <span :class="['stock-text', prod.stock === 0 ? 'text-danger' : '']">
                  {{ prod.stock === 0 ? 'Hết hàng' : 'Còn ' + prod.stock }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../lib/api';
import type { Product } from '../../types';

const products = ref<Product[]>([]);
const loading = ref(false);

async function fetchProducts() {
  loading.value = true;
  try {
    const res = await api.get('/products', {
      params: { page: 1, page_size: 40 },
    });
    if (res.data.success) {
      products.value = res.data.data.items;
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchProducts();
});
</script>

<style scoped>
.store-page {
  min-height: 100vh;
}
.hero-banner {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border-bottom: 1px solid #334155;
  padding: 3rem 1.5rem;
  text-align: center;
}
.hero-content h1 {
  font-size: 2.25rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.025em;
}
.hero-content p {
  color: #94a3b8;
  margin-top: 0.5rem;
  font-size: 1.1rem;
}
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}
.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.catalog-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f8fafc;
}
.product-count {
  color: #94a3b8;
  font-size: 0.875rem;
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.product-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.3);
}
.card-media {
  position: relative;
  background: #0f172a;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #334155;
}
.sku-tag {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid #334155;
  color: #38bdf8;
  font-size: 0.75rem;
  font-family: monospace;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
}
.featured-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: #eab308;
  color: #0f172a;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}
.placeholder-img {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 600;
}
.card-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.product-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}
.product-desc {
  color: #94a3b8;
  font-size: 0.825rem;
  flex: 1;
  margin-bottom: 1rem;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid #334155;
}
.price-box {
  display: flex;
  flex-direction: column;
}
.price {
  font-size: 1.2rem;
  font-weight: 700;
  color: #38bdf8;
}
.stock-text {
  font-size: 0.75rem;
  color: #94a3b8;
}
.text-danger {
  color: #f87171 !important;
  font-weight: 700;
}
</style>
