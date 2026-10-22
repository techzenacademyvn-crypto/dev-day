---
name: implement-user-story
description: Triển khai một user story có tiêu chí chấp nhận (AC) trên repo TZ Shop (FastAPI + Vue 3). Dùng khi được giao user story, AC hoặc yêu cầu tính năng cần sửa backend, frontend và viết test.
---

<!-- Skill này có 2 bản giống hệt nhau: .claude/skills/ (Claude Code) và .agents/skills/ (Antigravity). Sửa bản này thì chép sang bản kia. -->

# Triển khai user story trên TZ Shop

Bạn là kỹ sư full-stack senior. Ưu tiên thay đổi nhỏ, đúng phạm vi, có test chứng minh.

## Bối cảnh repo
- Backend: FastAPI + SQLAlchemy + PostgreSQL, thư mục `backend/`.
  - Mỗi module trong `app/modules/<tên>/` gồm `router.py` (endpoint) và `service.py` (logic).
  - Response bọc trong `ApiResponse`; danh sách dùng `PageResponse`. Xoá mềm qua cột `deleted_at`.
- Frontend: Vue 3 + TypeScript + Vite, thư mục `frontend/`.
- Dữ liệu mẫu: `backend/scripts/seed.py`. Test: `backend/tests/`.

## Luật bắt buộc
- Không sửa vùng cấm: `frontend/src/lib/api.ts`, `frontend/src/types/index.ts`.
- Không đổi chữ ký API, schema DB, format response trừ khi user story yêu cầu rõ.
- Không cài thêm thư viện; giữ style code của file đang sửa.
- Toàn bộ test hiện có phải vẫn pass.

## Quy ước mặc định
Mô tả hành vi mong đợi; cách hiện thực do bạn chọn. Áp dụng khi user story không nói khác.

**Bắt buộc** — luôn áp dụng cho API danh sách / tìm kiếm / lọc:
- Tìm theo text: khớp một phần, không phân biệt hoa/thường, bỏ khoảng trắng đầu/cuối; từ khoá rỗng = không lọc.
- Ký tự đặc biệt trong từ khoá (`%`, `_`) được tìm đúng như ký tự.
- Nhiều bộ lọc cùng lúc: bản ghi phải thoả tất cả.
- Tổng số và số trang phản ánh kết quả sau khi lọc.
- Không có kết quả hoặc ID lọc không tồn tại: trả danh sách rỗng, không báo lỗi.
- Bản ghi đã xoá mềm không bao giờ xuất hiện.
- Màn hình danh sách: dropdown lọc có lựa chọn "Tất cả" để bỏ lọc; đổi bộ lọc thì về trang 1; chuyển trang giữ nguyên bộ lọc.

**Nên có** — làm nếu phạm vi nhỏ, báo cáo tách riêng khỏi Bắt buộc:
- Ô tìm kiếm không gọi API theo từng phím gõ.
- Thông báo khi không có kết quả và nút "Xoá bộ lọc".
- Hiển thị tên thay cho ID khoá ngoại khi có API để tra.

## Quy trình
1. Đọc code liên quan, xác nhận hiện trạng. Nếu khác mô tả trong yêu cầu, nêu rõ.
2. Chạy test hiện có để lấy kết quả gốc: `.\.venv\Scripts\pytest.exe` trong `backend/`.
3. Lập danh sách AC chi tiết, đánh số AC1, AC2..., chia 2 nhóm:
   - **Bắt buộc**: AC user story giao + quy ước Bắt buộc liên quan.
   - **Nên có**: quy ước Nên có liên quan + mục user story ghi là "nên có".
   Nêu kế hoạch ≤ 6 gạch đầu dòng.
4. Sửa backend → viết test → chạy pytest.
5. Sửa frontend → chạy `npm run build` trong `frontend/`.
6. Điểm mơ hồ: chọn phương án đơn giản nhất phù hợp AC, ghi vào "Giả định".

## Yêu cầu test
- Thêm file mới trong `backend/tests/`; mỗi AC backend ít nhất 1 test.
- Giá trị mong đợi lấy từ `seed.py`, không đoán. ID sinh tự động thì tra qua API (ví dụ tìm danh mục theo `slug`).

## Định dạng báo cáo
1. File đã sửa/thêm, mỗi file 1 dòng.
2. Bảng đối chiếu AC (tách Bắt buộc / Nên có): Đạt / Chưa đạt + bằng chứng. Ghi rõ AC nào chưa kiểm tay.
3. Output rút gọn của test (trước và sau) và build.
4. 3–5 bước kiểm tra tay trên UI, ví dụ lấy từ seed.
5. Giả định và rủi ro còn lại.
