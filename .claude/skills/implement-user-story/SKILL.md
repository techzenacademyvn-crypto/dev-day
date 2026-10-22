---
name: implement-user-story
description: Triển khai một user story có tiêu chí chấp nhận (AC) trên repo TZ Shop (FastAPI + Vue 3). Dùng khi được giao user story, AC hoặc yêu cầu tính năng cần sửa backend, frontend và viết test.
---

# Triển khai user story trên TZ Shop

Bạn là kỹ sư full-stack senior. Ưu tiên thay đổi nhỏ, đúng phạm vi, có test chứng minh.

## Bối cảnh repo
- Backend: FastAPI + SQLAlchemy + PostgreSQL, thư mục `backend/`.
  - Mỗi module trong `app/modules/<tên>/` gồm `router.py` (khai báo endpoint) và `service.py` (logic, class dùng `@staticmethod`).
  - Response luôn bọc trong `ApiResponse`; danh sách dùng `PageResponse` (`items`, `total`, `page`, `page_size`, `total_pages`).
  - Xoá mềm qua cột `deleted_at`.
- Frontend: Vue 3 + TypeScript + Vite, thư mục `frontend/`. View dùng `<script setup lang="ts">`, CSS scoped tông tối (nền `#1e293b`, viền `#334155`).
- Dữ liệu mẫu: `backend/scripts/seed.py`. Test: `backend/tests/`.

## Luật bắt buộc
- KHÔNG sửa vùng cấm: `frontend/src/lib/api.ts`, `frontend/src/types/index.ts`.
- KHÔNG đổi chữ ký API, schema DB, migration, format `ApiResponse`/`PageResponse` trừ khi user story yêu cầu rõ.
- KHÔNG cài thêm thư viện.
- Giữ style code của file đang sửa.
- Toàn bộ test hiện có phải vẫn pass.

## Quy ước mặc định (áp dụng khi AC không nói khác)
Cho API danh sách / tìm kiếm / lọc:
- Tìm theo text: khớp một phần, không phân biệt hoa/thường (ILIKE), bỏ khoảng trắng đầu/cuối, chuỗi rỗng = không lọc, escape `%` và `_`.
- Nhiều bộ lọc cùng lúc kết hợp AND.
- `total`/`total_pages` tính sau khi lọc.
- Không có kết quả hoặc ID lọc không tồn tại → HTTP 200 với danh sách rỗng, không trả 404.
- Bản ghi đã xoá mềm không bao giờ xuất hiện.

Cho màn hình danh sách ở frontend:
- Ô tìm kiếm gọi API có debounce ~300ms (tự viết bằng `setTimeout`).
- Dropdown lọc có lựa chọn "Tất cả".
- Đổi bộ lọc → về trang 1; chuyển trang giữ nguyên bộ lọc.
- Có trạng thái rỗng ("Không tìm thấy ... phù hợp") và nút "Xoá bộ lọc".
- Hiển thị tên thay cho ID khoá ngoại khi có API để tra.

## Quy trình
1. Đọc code liên quan, xác nhận hiện trạng. Nếu khác mô tả trong yêu cầu, nêu rõ.
2. Chạy test hiện có để lấy kết quả gốc: `.\.venv\Scripts\pytest.exe` trong `backend/`.
3. Từ user story, viết ra danh sách AC chi tiết (đánh số AC1, AC2...) = AC được giao + quy ước mặc định liên quan. Nêu kế hoạch ≤ 6 gạch đầu dòng.
4. Sửa backend → viết test → chạy pytest.
5. Sửa frontend → chạy `npm run build` trong `frontend/`.
6. Điểm mơ hồ không có trong yêu cầu và quy ước: chọn phương án đơn giản nhất phù hợp AC, ghi vào "Giả định".

## Yêu cầu test
- Thêm file mới trong `backend/tests/`, mỗi AC backend ít nhất 1 test.
- Giá trị mong đợi lấy từ dữ liệu thật trong `seed.py`, không đoán. ID sinh tự động thì tra qua API (ví dụ tìm danh mục theo `slug`).
- Có test cho trường hợp biên: rỗng, không tồn tại, ký tự đặc biệt.

## Định dạng báo cáo
1. Danh sách file đã sửa/thêm, mỗi file 1 dòng mô tả.
2. Bảng đối chiếu từng AC: Đạt / Chưa đạt + bằng chứng (tên test hoặc bước kiểm tra tay). Ghi rõ AC nào chỉ được kiểm qua build, chưa kiểm tay.
3. Output rút gọn của `pytest` (trước và sau) và `npm run build`.
4. Hướng dẫn kiểm tra tay trên UI (3–5 bước, ví dụ lấy từ seed).
5. Giả định đã đưa ra và rủi ro còn lại.
