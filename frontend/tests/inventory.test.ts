import test from 'node:test';
import assert from 'node:assert/strict';
import { getStockInfo, formatStockDisplay } from '../src/lib/inventory.ts';

test('TASK-03 Inventory Unit Tests', async (t) => {
  await t.test('Scenario 1: quantity = 0 (AC02 - Hết hàng / Out of Stock)', () => {
    const info = getStockInfo(0);
    assert.equal(info.quantity, 0);
    assert.equal(info.status, 'OUT_OF_STOCK');
    assert.equal(info.statusLabel, 'Hết hàng');
    assert.equal(info.displayQuantity, '0');
    assert.equal(info.badgeClass, 'out-of-stock');
    assert.equal(info.isValid, true);
    assert.equal(formatStockDisplay(0), '0 (Hết hàng)');
  });

  await t.test('Scenario 2: quantity = 1 (AC01 - Còn hàng / In Stock)', () => {
    const info = getStockInfo(1);
    assert.equal(info.quantity, 1);
    assert.equal(info.status, 'IN_STOCK');
    assert.equal(info.statusLabel, 'Còn hàng');
    assert.equal(info.displayQuantity, '1');
    assert.equal(info.badgeClass, 'in-stock');
    assert.equal(info.isValid, true);
    assert.equal(formatStockDisplay(1), '1 (Còn hàng)');
  });

  await t.test('Scenario 3: quantity > 1 (AC01 - Còn hàng / In Stock)', () => {
    const testCases = [2, 10, 50, 9999];
    for (const qty of testCases) {
      const info = getStockInfo(qty);
      assert.equal(info.quantity, qty);
      assert.equal(info.status, 'IN_STOCK');
      assert.equal(info.statusLabel, 'Còn hàng');
      assert.equal(info.displayQuantity, String(qty));
      assert.equal(info.badgeClass, 'in-stock');
      assert.equal(info.isValid, true);
      assert.equal(formatStockDisplay(qty), `${qty} (Còn hàng)`);
    }
  });

  await t.test('Scenario 4: quantity is null, undefined, or empty (Invalid/Unavailable)', () => {
    const invalidInputs = [null, undefined, ''];
    for (const input of invalidInputs) {
      const info = getStockInfo(input);
      assert.equal(info.quantity, null);
      assert.equal(info.status, 'INVALID');
      assert.equal(info.statusLabel, 'Không xác định');
      assert.equal(info.displayQuantity, '—');
      assert.equal(info.badgeClass, 'stock-invalid');
      assert.equal(info.isValid, false);
      // Ensure it is NEVER classified as in stock
      assert.notEqual(info.status, 'IN_STOCK');
      assert.notEqual(info.badgeClass, 'in-stock');
    }
  });

  await t.test('Scenario 5: quantity < 0 (Anomalous Data - not silently converted to 0)', () => {
    const negativeCases = [-1, -5, -100];
    for (const neg of negativeCases) {
      const info = getStockInfo(neg);
      assert.equal(info.quantity, neg);
      assert.equal(info.status, 'ANOMALOUS');
      assert.equal(info.statusLabel, 'Dữ liệu bất thường');
      assert.equal(info.displayQuantity, String(neg));
      assert.equal(info.badgeClass, 'stock-anomalous');
      assert.equal(info.isValid, false);
      // Ensure it is not converted to 0 or treated as out-of-stock / in-stock
      assert.notEqual(info.quantity, 0);
      assert.notEqual(info.status, 'IN_STOCK');
      assert.notEqual(info.status, 'OUT_OF_STOCK');
    }
  });

  await t.test('Scenario 6: quantity is non-numeric or NaN (Invalid Data Handling)', () => {
    const malformedCases = [NaN, 'abc', {}, []];
    for (const val of malformedCases) {
      const info = getStockInfo(val);
      assert.equal(info.quantity, null);
      assert.equal(info.status, 'INVALID');
      assert.equal(info.isValid, false);
      assert.notEqual(info.status, 'IN_STOCK');
    }
  });

  await t.test('Scenario 7: numeric strings from API/Forms are parsed correctly', () => {
    const parsedZero = getStockInfo('0');
    assert.equal(parsedZero.quantity, 0);
    assert.equal(parsedZero.status, 'OUT_OF_STOCK');
    assert.equal(parsedZero.statusLabel, 'Hết hàng');

    const parsedTen = getStockInfo('10');
    assert.equal(parsedTen.quantity, 10);
    assert.equal(parsedTen.status, 'IN_STOCK');
    assert.equal(parsedTen.statusLabel, 'Còn hàng');
  });
});
