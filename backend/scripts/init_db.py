"""Script khởi tạo Database tz_shop trên PostgreSQL cục bộ (Không cần Docker).
Tự động kiểm tra và tạo database 'tz_shop' nếu chưa tồn tại, sau đó tạo bảng.
"""
import sys
from pathlib import Path

# Đảm bảo in ký tự tiếng Việt an toàn trên Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Thêm thư mục gốc dự án vào sys.path để import app.*
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models import Base


def init_database():
    parsed = urlparse(settings.DATABASE_URL)
    print(f"[*] Database: {parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
    db_name = parsed.path.lstrip("/")
    
    # URL kết nối vào database mặc định 'postgres' để kiểm tra / tạo database tz_shop
    # urlparse scheme: postgresql+psycopg -> postgresql+psycopg
    postgres_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
    
    try:
        # 1. Kết nối postgres default DB
        admin_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            ).scalar()
            if not result:
                print(f"[+] Cơ sở dữ liệu '{db_name}' chưa tồn tại. Đang tiến hành tạo mới...")
                conn.execute(text(f"CREATE DATABASE {db_name} WITH ENCODING 'UTF8'"))
                print(f"[✓] Đã tạo thành công cơ sở dữ liệu '{db_name}'!")
            else:
                print(f"[✓] Cơ sở dữ liệu '{db_name}' đã tồn tại sẵn.")
        admin_engine.dispose()
    except Exception as e:
        print(f"[!] Lỗi khi kiểm tra/tạo database từ postgres admin engine: {e}")
        print("[!] Đang thử kết nối trực tiếp vào database đích...")

    # 2. Kết nối vào tz_shop và tạo bảng
    try:
        app_engine = create_engine(settings.DATABASE_URL)
        print(f"[*] Đang đồng bộ cấu trúc bảng (Schema) vào database '{db_name}'...")
        Base.metadata.create_all(bind=app_engine)
        print(f"[✓] Đồng bộ bảng thành công cho các mô hình:")
        for table in Base.metadata.tables.keys():
            print(f"    - {table}")
        app_engine.dispose()
        print("\n[SUCCESS] Cơ sở dữ liệu đã sẵn sàng để sử dụng!")
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo bảng: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
