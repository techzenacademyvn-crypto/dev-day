# Dev Day — TZ Shop bản rút gọn

Dự án TZ Shop rút gọn dùng cho Dev Day, chạy trên máy: **danh mục và sản phẩm**, có backend và frontend.
Không có CI, Docker, khách hàng, đơn hàng, giỏ hàng.

| Phần | Công nghệ | Có gì |
|---|---|---|
| `backend/` | FastAPI · PostgreSQL | Đăng nhập nhân viên, API danh mục, API sản phẩm |
| `frontend/` | Vue 3 · Vite | Trang cửa hàng (chỉ xem), đăng nhập, quản lý danh mục, quản lý sản phẩm |

## Cần cài sẵn

- Python 3.12
- Node.js 22 trở lên
- PostgreSQL, biết mật khẩu user `postgres`

## 1. Chạy backend

PowerShell, thư mục `backend`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

Mở `.env`, sửa 2 dòng:

- `DATABASE_URL`: thay `MAT_KHAU_POSTGRES` bằng mật khẩu PostgreSQL của máy.
- `SECRET_KEY`: thay bằng chuỗi ngẫu nhiên dài ít nhất 32 ký tự.

```powershell
.\.venv\Scripts\python.exe scripts\init_db.py
.\.venv\Scripts\python.exe scripts\seed.py
.\.venv\Scripts\pytest.exe
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

- `init_db` tự tạo database `dev_day` và các bảng.
- `seed` nạp 2 tài khoản, 8 danh mục, 40 sản phẩm.
- `pytest` phải ra **6 passed**.
- Backend chạy ở http://localhost:8000, tài liệu API ở http://localhost:8000/docs

## 2. Chạy frontend

PowerShell thứ hai, thư mục `frontend`:

```powershell
npm install
npm run dev
```

Mở http://localhost:5173

## Tài khoản mẫu

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Quản trị | admin@tzshop.vn | admin123 |
| Nhân viên | staff@tzshop.vn | staff123 |

Xem danh sách không cần đăng nhập. Thêm, sửa, xoá phải đăng nhập.

## Nạp lại dữ liệu mẫu

```powershell
.\.venv\Scripts\python.exe scripts\seed.py --force
```

Lệnh này xoá hết dữ liệu hiện có rồi nạp lại từ đầu.

## Gặp lỗi

| Lỗi | Cách xử lý |
|---|---|
| `DATABASE_URL Field required` | Chưa có file `.env` trong `backend` |
| `password authentication failed` | Sai mật khẩu PostgreSQL trong `.env` |
| `no pq wrapper available` / `DLL load failed` | Gõ `$env:PATH = "C:\Program Files\PostgreSQL\18\bin;$env:PATH"` rồi chạy lại. Mỗi terminal mới phải gõ lại |
| Trang web không có sản phẩm | Backend chưa chạy, hoặc không chạy ở cổng 8000 |

## Cấu trúc thư mục

```
backend/
  app/
    core/        cấu hình, kết nối database, đăng nhập (JWT), lỗi chuẩn
    models/      User, Category, Product
    schemas/     dữ liệu vào/ra của API
    modules/     auth, categories, products (router + service)
    main.py      khởi tạo app, gắn router
  scripts/       init_db.py, seed.py
  tests/         test đăng nhập, danh mục, sản phẩm
  .env.example   mẫu cấu hình
frontend/
  src/
    views/store/   trang cửa hàng
    views/admin/   đăng nhập, danh mục, sản phẩm
    components/    thanh menu
    stores/        trạng thái đăng nhập
    router/        đường dẫn các trang
    lib/api.ts     gọi API (mặc định http://localhost:8000/api/v1)
```
