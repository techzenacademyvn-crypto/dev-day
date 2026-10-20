<template>
  <header class="navbar">
    <div class="nav-container">
      <div class="brand">
        <router-link to="/" class="logo">
          <span class="logo-accent">TZ</span> Shop
        </router-link>
      </div>

      <nav class="nav-links">
        <!-- Menu Cửa Hàng -->
        <router-link to="/" class="nav-item">Cửa Hàng</router-link>

        <div class="divider"></div>

        <!-- Menu Quản Trị -->
        <template v-if="authStore.isAuthenticated">
          <router-link to="/admin/categories" class="nav-item">Danh Mục</router-link>
          <router-link to="/admin/products" class="nav-item">Sản Phẩm</router-link>

          <div class="user-info">
            <span class="user-role">{{ authStore.user?.full_name }} ({{ authStore.user?.role }})</span>
            <button @click="handleLogout" class="btn-logout">Đăng Xuất</button>
          </div>
        </template>
        <template v-else>
          <router-link to="/admin/login" class="nav-item btn-login">
            🔐 Nhân Viên Đăng Nhập
          </router-link>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  router.push('/admin/login');
}
</script>

<style scoped>
.navbar {
  background: #1e293b;
  color: #f8fafc;
  border-bottom: 1px solid #334155;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.logo {
  font-size: 1.35rem;
  font-weight: 800;
  text-decoration: none;
  color: #f8fafc;
  letter-spacing: -0.025em;
}
.logo-accent {
  color: #38bdf8;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.nav-item {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.4rem 0.75rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}
.nav-item:hover, .nav-item.router-link-active {
  color: #fff;
  background: #334155;
}
.divider {
  width: 1px;
  height: 1.5rem;
  background: #475569;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: 0.5rem;
}
.user-role {
  font-size: 0.8rem;
  color: #94a3b8;
}
.btn-logout {
  background: #475569;
  border: none;
  color: #f8fafc;
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-logout:hover {
  background: #dc2626;
}
.btn-login {
  background: #0284c7;
  color: #fff !important;
}
.btn-login:hover {
  background: #0369a1 !important;
}
</style>
