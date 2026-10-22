from sqlalchemy import inspect

from app.models import Base, OrderStatus


def test_reporting_source_tables_are_registered():
    assert {"orders", "order_items"}.issubset(Base.metadata.tables)


def test_order_items_contain_required_reporting_columns():
    columns = {column.name for column in inspect(Base.metadata.tables["order_items"]).columns}
    assert {"order_id", "product_id", "quantity", "unit_price"}.issubset(columns)


def test_order_status_supports_completed_and_cancelled_filters():
    assert OrderStatus.COMPLETED.value == "COMPLETED"
    assert OrderStatus.CANCELLED.value == "CANCELLED"
