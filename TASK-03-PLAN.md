# TASK-03 PLAN: HIỂN THỊ TÌNH TRẠNG TỒN KHO (INVENTORY STOCK STATUS)

## 1. Project & Branch Identification
- **Workspace Root**: `C:\CODE\dev-day`
- **Current Git Branch**: `task/kiem-tra-ton-kho` (Verified via `git branch --show-current`)
- **Task Identification**: 
  - Repository Task File: No dedicated markdown task file exists in the workspace. All tracked and untracked files as well as git commit history were inspected.
  - Authoritative Requirement Source: Direct User Specification for **TASK-03 — HIỂN THỊ TÌNH TRẠNG TỒN KHO** (User Story, Business Rules, and Acceptance Criteria AC01, AC02, AC03).

---

## 2. Findings from Existing Implementation
1. **Backend**:
   - `Product` model (`backend/app/models/product.py`): Contains `stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)`.
   - `ProductResponse` schema (`backend/app/schemas/product.py`): Contains `stock: int = Field(default=0, ge=0)`.
   - `ProductService` & `ProductRouter`: Endpoints `GET /api/v1/products`, `GET /api/v1/products/{id}`, `PUT /api/v1/products/{id}` already support reading and updating `stock`.
   - Validation: Pydantic rejects negative stock (`ge=0`) on create/update with HTTP 422.
   
2. **Frontend**:
   - Types (`frontend/src/types/index.ts`): `Product` has `stock: number;`.
   - Admin view (`frontend/src/views/admin/ProductsView.vue`):
     - Displays `prod.stock` with a naive condition: `prod.stock === 0 ? '(Hết hàng)' : 'cái'`.
     - Defect 1: When `stock > 0`, it only says `X cái`, failing AC01 which mandates displaying both quantity and the explicit status `"Còn hàng"`.
     - Defect 2: When `stock < 0` (anomalous data), it treats it as in stock (`-5 cái`, badge `in-stock`), violating the rule: *"quantity < 0: Xem là dữ liệu bất thường, không âm thầm chuyển thành 0"*.
     - Defect 3: When `stock` is `null`, `undefined`, or `NaN`, it defaults to in-stock badge.
     - Defect 4: Error handling on API failure only logs to console, leaving no visible feedback or retry action for the user.
     - Defect 5: No stock update interaction in `ProductsView.vue` to satisfy AC03 directly in the UI.
   - Store view (`frontend/src/views/store/StoreCatalogView.vue`):
     - Contains duplicated, naive stock logic: `prod.stock === 0 ? 'Hết hàng' : 'Còn ' + prod.stock`.
     - Violates DRY principle and consistency requirements.

---

## 3. Root Cause & Implementation Gap
- Absence of a centralized, domain-driven inventory utility in the frontend to classify stock quantity and format status badges consistently.
- Incomplete business rule handling for edge cases (negative, null, missing, NaN, non-numeric).
- Lack of explicit `"Còn hàng"` label for positive inventory.
- Missing inventory update modal/action on `ProductsView.vue` to allow warehouse staff to update stock and verify dynamic status refresh (AC03).

---

## 4. Proposed Implementation Approach

### A. Centralized Inventory Module (`frontend/src/lib/inventory.ts`)
Create a pure, thoroughly testable TypeScript module implementing the business rules:
- **Status Types**:
  - `IN_STOCK`: quantity > 0 -> Label: `"Còn hàng"`, badge class: `in-stock`
  - `OUT_OF_STOCK`: quantity === 0 -> Label: `"Hết hàng"`, badge class: `out-of-stock`
  - `ANOMALOUS`: quantity < 0 -> Label: `"Dữ liệu bất thường"`, badge class: `stock-anomalous`
  - `INVALID`: null, undefined, NaN, or non-numeric -> Label: `"Không xác định"`, badge class: `stock-invalid`
- **Helper Functions**:
  - `getStockInfo(quantity: unknown): StockInfo`
  - `formatStockDisplay(quantity: unknown): string`

### B. Reusable Stock Badge Component (`frontend/src/components/StockBadge.vue`)
- Renders quantity and status badge with clean, accessible styling.
- Distinct visual badges:
  - Green for `Còn hàng`
  - Red for `Hết hàng`
  - Orange/Amber for `Dữ liệu bất thường`
  - Gray/Muted for `Không xác định` / invalid

### C. Update Admin Product View (`frontend/src/views/admin/ProductsView.vue`)
- Replace ad-hoc badge with `StockBadge.vue`.
- Display quantity and status accurately according to AC01 and AC02.
- Add an "Sửa tồn kho" (Quick Stock Update) action and modal to enable warehouse managers to edit stock via `PUT /api/v1/products/{id}`.
- Trigger `fetchProducts()` upon successful save to satisfy AC03 with immediate visual refresh.
- Enhance API error handling: show alert / banner if fetch fails.

### D. Update Store Catalog View (`frontend/src/views/store/StoreCatalogView.vue`)
- Reuse `getStockInfo()` to guarantee DRY and cross-component consistency.

### E. Backend Tests (`backend/tests/test_inventory.py`)
- Add automated pytest cases covering:
  - Fetching products and verifying stock fields.
  - Updating stock to 0, 1, and > 1.
  - Validating that negative stock (`stock < 0`) is rejected with HTTP 422.
  - Ensuring soft-deleted items are excluded.

### F. Frontend Automated Unit Tests (`frontend/tests/inventory.test.ts`)
- Automated tests using Node.js test runner covering:
  1. `quantity = 0` -> Out of stock (`Hết hàng`)
  2. `quantity = 1` -> In stock (`Còn hàng`)
  3. `quantity > 1` (e.g. 15, 100) -> In stock (`Còn hàng`)
  4. `quantity = null` / `undefined` -> Invalid (`Không xác định`)
  5. `quantity < 0` (e.g. -1, -50) -> Anomalous (`Dữ liệu bất thường`)
  6. `quantity = NaN` / non-numeric string -> Invalid
  7. Formatted display string verification.

---

## 5. Files Expected to Change
| File | Action | Reason |
|---|---|---|
| `frontend/src/lib/inventory.ts` | Create | Centralized stock business logic & formatting (DRY) |
| `frontend/src/components/StockBadge.vue` | Create | Reusable UI badge component for stock status |
| `frontend/src/views/admin/ProductsView.vue` | Update | Apply `StockBadge`, add stock update modal (AC01, AC02, AC03), improve error states |
| `frontend/src/views/store/StoreCatalogView.vue` | Update | Reuse centralized stock logic for consistency |
| `frontend/tests/inventory.test.ts` | Create | Frontend unit tests for all stock edge cases |
| `backend/tests/test_inventory.py` | Create | Backend integration tests for inventory API & validation |

---

## 6. Risks and Compatibility Considerations
- **Data Contract Compatibility**: No breaking changes to existing database schema or API response models. Schema remains 100% backward compatible.
- **Performance**: Computation is O(1) in frontend rendering; no extra database queries required.
- **Regression Prevention**: Existing product listing, deletion, pagination, and store catalog are preserved.
