# Inventory Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add isolated backend tests and Vue component tests for inventory classification, API filtering, and inventory display.

**Architecture:** Keep application behavior unchanged. Backend route tests use an in-memory SQLite database and override FastAPI's `get_db`; model/schema tests remain pure. Vue tests use Vitest, Vue Test Utils, jsdom, and a mocked API client.

**Tech Stack:** Python 3.12.15 in Conda environment `tzshop`, pytest, SQLAlchemy, FastAPI, httpx; Node.js 22, Vitest, Vue Test Utils, jsdom.

**Spec:** `docs/superpowers/specs/2026-10-23-inventory-tests-design.md`

## Global Constraints

- Do not change product behavior or UI; this task adds tests and frontend test configuration only.
- Run backend tests with `conda run -n tzshop python -m pytest` from `backend/`.
- New API tests use in-memory SQLite; do not connect to the PostgreSQL target in `backend/.env`.
- Frontend component tests mock `src/lib/api.ts`; do not start either app server.
- The inventory rule is: `stock == 0` is out of stock; otherwise overstocked requires `stock > 10` and age `> 60` days.
- UI tab counts and filtering apply to the currently loaded page of 20 products.
- Notify the user with the exact backend/frontend test commands before the first test run.
- The 60-day API filter consistency test is expected to expose a known mismatch in current production code; do not fix product code in this test-only task.
- Freeze model and service clocks to the same timezone-aware instant for backend 60/61-day cases; mock `Date.now()` for matching Vue boundary cases.

## Review Focus

1. Zero stock must override age — pin in `test_stock_status_zero_precedes_age` and the admin/store component tests.
2. Exactly 60 days must remain normal, while 61 days can be overstocked — pin in model, API-filter, and component tests; the API-filter test is expected to fail on current code.
3. Quantity 10 is normal and 11 is overstocked only after the age threshold — pin in backend boundary tests and the admin component test.
4. Naive and future timestamps must not produce invalid negative ages — pin in backend model tests and a future-date admin component case.
5. Counts and filters are page-scoped — pin in the admin component pagination test so later changes to API or pagination cannot silently alter this contract.

---

### Task 1: Backend inventory rules and API filters

**Files:**
- Modify: `backend/tests/test_stock_status.py`
- Create: `backend/tests/test_product_inventory_api.py`

**Interfaces:**
- Consumes: `Product.stock_status`, `Product.days_in_stock`, `ProductCreate`, `ProductUpdate`, `ProductService.update`, the products list route, and FastAPI dependency `get_db`.
- Produces: deterministic model/schema tests and API tests isolated from PostgreSQL.

- [ ] **Step 1: Extend pure stock status and schema tests**

Add assertions for stock zero at an old creation date, stock 10 versus 11 at 61 days, exactly 60 days, naive UTC timestamps, future timestamps clamped to zero days, and rejecting negative `stock` in both create and update schemas while accepting zero. Freeze `app.models.product.datetime.now` to a fixed UTC instant for deterministic age boundaries.

- [ ] **Step 2: Add an in-memory SQLite fixture and API cases**

Create an engine with `sqlite://`, `StaticPool`, and `check_same_thread=False`; create `Base.metadata`; override `get_db` to yield per-request sessions; clear the override and dispose the engine after each test. Seed a category and products with fixed `created_at` values. Freeze `app.modules.products.service.datetime.now` and `app.models.product.datetime.now` to the same UTC instant so SQL filtering and response properties use the same boundary.

Add tests that each status filter only returns rows of that serialized status, that the exact-60-day overstocked query does not return a normal-status row, that pagination reports the correct total and page items, and that soft-deleted products are excluded. Add a service-level stock update test that changes the quantity and observes the recalculated status.

- [ ] **Step 3: Notify the user, then run only the backend inventory tests**

From `backend/`, run: `conda run -n tzshop python -m pytest tests/test_stock_status.py tests/test_product_inventory_api.py -q`

Expected: model/schema and other API assertions pass; the exact-60-day consistency assertion exposes the existing service-filter mismatch. Keep that failure visible and report it; do not alter application code.

### Task 2: Vue component tests for inventory screens

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/views/admin/ProductsView.spec.ts`
- Create: `frontend/src/views/store/StoreCatalogView.spec.ts`

**Interfaces:**
- Consumes: the current ProductsView and StoreCatalogView component behavior and `src/lib/api.ts` module.
- Produces: `npm test` running component tests in jsdom with API calls mocked.

- [ ] **Step 1: Configure the Vue test runner**

Add a `test` script using `vitest run`; add Vitest, `@vue/test-utils`, and jsdom as dev dependencies; configure Vite's Vue plugin and Vitest's jsdom environment in `vite.config.ts`.

- [ ] **Step 2: Test admin inventory rendering and tab behavior**

Mock `api.get`. Assert the loading row while the request is pending, the initial request uses page 1 and page size 20, and returned products show correct quantities, badges, and days-in-stock. Mock `Date.now()` to a fixed instant; cover 0, 10/11, 60/61 days, and a future creation date. Click all four tabs and verify rows, page-scoped counts, and the empty-state message. Change pages and assert the request and filtered rows update.

- [ ] **Step 3: Test storefront stock labels**

Mock `api.get` and assert stock zero renders “Hết hàng” while positive stock renders “Còn N”. Assert loading resolves to the product cards.

- [ ] **Step 4: Notify the user, then run the frontend component tests**

From `frontend/`, run: `npm test -- --reporter=dot`

Expected: all component assertions pass without starting the backend or contacting a database.

## Scope Self-Review

- Backend status, timestamp, schema, update, filtering, pagination, and soft-delete cases map to Task 1.
- Admin tabs/counts/pagination and storefront stock display map to Task 2.
- No application source file is in either task; only the already identified API boundary test is expected to be red.
- Backend and frontend runs are separate so a missing frontend dependency or the known API mismatch is reported precisely.
