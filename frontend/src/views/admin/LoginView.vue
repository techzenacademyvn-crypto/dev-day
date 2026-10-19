<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <h2>Đăng Nhập Quản Trị</h2>
        <p>Hệ thống bán hàng nội bộ TZ Shop</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="errorMessage" class="alert-error">
          {{ errorMessage }}
        </div>

        <div class="form-group">
          <label>Email Nhân Viên</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="admin@tzshop.vn"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label>Mật Khẩu</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="form-control"
          />
        </div>

        <button type="submit" :disabled="loading" class="btn-submit">
          {{ loading ? 'Đang xác thực...' : 'Đăng Nhập' }}
        </button>

        <div class="credentials-hint">
          <p><strong>Tài khoản mẫu có sẵn:</strong></p>
          <code>admin@tzshop.vn / admin123</code> (Admin)<br />
          <code>staff@tzshop.vn / staff123</code> (Staff)
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../lib/api';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('admin@tzshop.vn');
const password = ref('admin123');
const loading = ref(false);
const errorMessage = ref('');

async function handleLogin() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const res = await api.post('/auth/login', {
      email: email.value,
      password: password.value,
    });
    if (res.data.success) {
      authStore.setAuth(res.data.data.access_token, res.data.data.user);
      router.push('/admin/categories');
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại.';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: calc(100vh - 70px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: #0f172a;
}
.login-card {
  width: 100%;
  max-width: 420px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}
.login-header {
  text-align: center;
  margin-bottom: 1.5rem;
}
.login-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f8fafc;
}
.login-header p {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
.form-group {
  margin-bottom: 1.25rem;
}
.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
  margin-bottom: 0.5rem;
}
.form-control {
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f8fafc;
  font-size: 0.9rem;
  outline: none;
}
.form-control:focus {
  border-color: #38bdf8;
}
.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background: #0284c7;
  color: #fff;
  border: none;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-submit:hover:not(:disabled) {
  background: #0369a1;
}
.alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
.credentials-hint {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #334155;
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: center;
}
.credentials-hint code {
  color: #38bdf8;
}
</style>
