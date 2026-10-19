import { createRouter, createWebHistory } from 'vue-router';
import StoreCatalogView from '../views/store/StoreCatalogView.vue';
import LoginView from '../views/admin/LoginView.vue';
import CategoriesView from '../views/admin/CategoriesView.vue';
import ProductsView from '../views/admin/ProductsView.vue';

const routes = [
  // Tuyến đường Cửa hàng
  { path: '/', name: 'StoreCatalog', component: StoreCatalogView },

  // Tuyến đường Quản trị (Admin)
  { path: '/admin/login', name: 'AdminLogin', component: LoginView },
  {
    path: '/admin/categories',
    name: 'AdminCategories',
    component: CategoriesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/products',
    name: 'AdminProducts',
    component: ProductsView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard bảo vệ các trang quản trị
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token');
  if (to.meta.requiresAuth && !token) {
    next({ path: '/admin/login' });
  } else {
    next();
  }
});

export default router;
