// ==============================================================================
// VÙNG DÙNG CHUNG (VÙNG CẤM) - frontend/src/types/index.ts
// Chứa toàn bộ định nghĩa kiểu dữ liệu thống nhất giữa Backend và Frontend.
// Bắt buộc qua PR có xét duyệt của Mentor / Tech Lead.
// ==============================================================================

export type UserRole = 'ADMIN' | 'STAFF';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
}

export interface Product {
  id: number;
  category_id: number;
  name: string;
  sku: string;
  price: number; // Trong JS số thập phân là number
  stock: number;
  is_featured: boolean;
  image_url?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  restocked_at?: string | null;
  out_of_stock_at?: string | null;
  last_stock_action?: string | null;
}

export interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    message: string;
    details?: any;
  };
}

