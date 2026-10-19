"""Script nạp dữ liệu mẫu cho hệ thống TZ Shop (Ship It With AI).
Đặc tả dữ liệu:
  - 2 Tài khoản nhân viên (Admin & Staff)
  - 8 Danh mục
  - 40 Sản phẩm (giá lẻ Decimal, có tồn kho = 0)
  - 25 Khách hàng (3 khách bị xoá mềm: bẫy Soft Delete)
  - 60 Đơn hàng (có đơn lúc 23:30 GMT+7: bẫy Múi giờ, có đơn của khách đã xoá)
Tính chất: Idempotent (chạy lại xóa sạch và nạp lại chính xác).
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

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models import (
    Base,
    User,
    UserRole,
    Category,
    Product,
)

VN_TZ = timezone(timedelta(hours=7))


def clean_database(db: Session):
    """Xóa sạch dữ liệu các bảng theo đúng thứ tự khóa ngoại."""
    print("[*] Đang làm sạch dữ liệu cũ...")
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(User).delete()
    db.commit()
    print("[✓] Đã làm sạch dữ liệu.")


def seed_data(force: bool = False):
    db: Session = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count > 0 and not force:
            print(f"[*] Database đã có sẵn dữ liệu ({user_count} tài khoản). Bỏ qua seed để bảo vệ dữ liệu hiện có.")
            return

        if force:
            clean_database(db)

        # ----------------------------------------------------------------------
        # 1. Nhân viên (Users)
        # ----------------------------------------------------------------------
        print("[*] 1/3. Nạp tài khoản nhân viên...")
        admin = User(
            email="admin@tzshop.vn",
            hashed_password=get_password_hash("admin123"),
            full_name="Quản Trị Viên",
            role=UserRole.ADMIN,
            is_active=True,
        )
        staff = User(
            email="staff@tzshop.vn",
            hashed_password=get_password_hash("staff123"),
            full_name="Nhân Viên Bán Hàng",
            role=UserRole.STAFF,
            is_active=True,
        )
        db.add_all([admin, staff])
        db.flush()

        # ----------------------------------------------------------------------
        # 2. Danh mục (8 Categories)
        # ----------------------------------------------------------------------
        print("[*] 2/3. Nạp 8 danh mục sản phẩm...")
        cat_data = [
            ("Điện tử & Công nghệ", "dien-tu-cong-nghe", "Thiết bị thông minh, phụ kiện công nghệ"),
            ("Điện gia dụng", "dien-gia-dung", "Thiết bị tiện ích cho gia đình"),
            ("Thời trang Nam", "thoi-trang-nam", "Quần áo, phụ kiện thời trang nam hiện đại"),
            ("Thời trang Nữ", "thoi-trang-nu", "Bộ sưu tập thời trang nữ thanh lịch"),
            ("Phụ kiện & Đồng hồ", "phu-kien-dong-ho", "Trang sức, đồng hồ, kính mắt"),
            ("Sách & Văn phòng phẩm", "sach-van-phong-pham", "Sách kinh tế, công nghệ và dụng cụ học tập"),
            ("Mỹ phẩm & Chăm sóc da", "my-pham-cham-soc-da", "Mỹ phẩm chính hãng, chăm sóc sắc đẹp"),
            ("Thể thao & Dã ngoại", "the-thao-da-ngoai", "Trang thiết bị thể thao, đồ phượt dã ngoại"),
        ]
        categories = []
        for name, slug, desc in cat_data:
            cat = Category(name=name, slug=slug, description=desc, is_active=True)
            categories.append(cat)
            db.add(cat)
        db.flush()

        # ----------------------------------------------------------------------
        # 3. Sản phẩm (40 Products - 5 sp/danh mục)
        # Bẫy Decimal: giá có phần lẻ (.99, .49, .95, .50)
        # Bẫy Tồn kho: có sản phẩm stock = 0
        # ----------------------------------------------------------------------
        print("[*] 3/3. Nạp 40 sản phẩm (gài bẫy Decimal & tồn kho 0)...")
        raw_products = [
            # Cat 1: Điện tử
            (0, "Tai nghe không dây Bluetooth True Wireless TZ-Pod", "PRD-001", "49.99", 50, True),
            (0, "Chuột công thái học Wireless Silent", "PRD-002", "24.50", 80, False),
            (0, "Bàn phím cơ cơ học RGB Blue Switch", "PRD-003", "89.95", 35, True),
            (0, "Củ sạc nhanh 65W GaN 3 cổng", "PRD-004", "29.99", 100, False),
            (0, "Pin sạc dự phòng 20000mAh PowerDelivery", "PRD-005", "39.49", 0, False),  # Bẫy hết hàng (stock=0)

            # Cat 2: Điện gia dụng
            (1, "Nồi chiên không dầu điện tử 6.5L", "PRD-006", "119.99", 25, True),
            (1, "Máy hút bụi cầm tay mini không dây", "PRD-007", "45.00", 40, False),
            (1, "Ấm siêu tốc giữ nhiệt Inox 304", "PRD-008", "19.99", 60, False),
            (1, "Máy xay sinh tố đa năng cầm tay", "PRD-009", "34.50", 15, False),
            (1, "Quạt bàn tích điện pin dung lượng cao", "PRD-010", "22.95", 30, False),

            # Cat 3: Thời trang Nam
            (2, "Áo Polo nam vải sợi tre kháng khuẩn", "PRD-011", "18.99", 120, True),
            (2, "Quần Tây âu co giãn 4 chiều Slimfit", "PRD-012", "32.50", 45, False),
            (2, "Áo khoác gió thể thao nam chống nước", "PRD-013", "42.99", 30, False),
            (2, "Áo thun Cotton trơn thoáng mát", "PRD-014", "9.99", 150, False),
            (2, "Quần Short Kaki dạo phố phong cách", "PRD-015", "16.49", 0, False),  # Bẫy hết hàng (stock=0)

            # Cat 4: Thời trang Nữ
            (3, "Đầm suông công sở phối ren cao cấp", "PRD-016", "45.99", 20, True),
            (3, "Áo sơ mi lụa tay bồng phong cách Hàn Quốc", "PRD-017", "28.50", 50, False),
            (3, "Chân váy chữ A xếp ly nhẹ nhàng", "PRD-018", "21.99", 40, False),
            (3, "Áo Blazer nữ form rộng sành điệu", "PRD-019", "65.00", 15, True),
            (3, "Set đồ bộ lụa mặc nhà thoáng khí", "PRD-020", "25.49", 35, False),

            # Cat 5: Phụ kiện & Đồng hồ
            (4, "Đồng hồ dây da phong cách tối giản Minimalist", "PRD-021", "85.99", 25, True),
            (4, "Kính râm chống tia UV400 Polarized", "PRD-022", "19.99", 70, False),
            (4, "Ví da nam da bò nguyên tấm", "PRD-023", "27.50", 40, False),
            (4, "Thắt lưng da khóa tự động kim loại cao cấp", "PRD-024", "15.99", 60, False),
            (4, "Balo laptop chống sốc chống trộm", "PRD-025", "38.50", 30, False),

            # Cat 6: Sách & Văn phòng phẩm
            (5, "Sách: Nghệ thuật đàm phán đỉnh cao", "PRD-026", "12.50", 90, False),
            (5, "Sách: Thiết kế hệ thống phân tán quy mô lớn", "PRD-027", "29.99", 50, True),
            (5, "Sổ tay bìa da cao cấp cỡ A5 kèm bút ký", "PRD-028", "14.99", 80, False),
            (5, "Bộ bút gel ký tên mực đen ngòi 0.5mm", "PRD-029", "6.49", 200, False),
            (5, "Kệ đỡ sách và máy tính bảng xoay 360", "PRD-030", "18.50", 45, False),

            # Cat 7: Mỹ phẩm & Chăm sóc da
            (6, "Serum cấp ẩm phục hồi Hyaluronic Acid B5", "PRD-031", "26.99", 40, True),
            (6, "Kem chống nắng phổ rộng quang phổ hẹp SPF50+", "PRD-032", "19.50", 85, True),
            (6, "Sữa rửa mặt dịu nhẹ độ pH 5.5 cân bằng", "PRD-033", "11.99", 110, False),
            (6, "Nước hoa hồng cân bằng da hoa cúc Toner", "PRD-034", "15.49", 65, False),
            (6, "Kem dưỡng khóa ẩm mỏng nhẹ ban đêm", "PRD-035", "23.00", 35, False),

            # Cat 8: Thể thao & Dã ngoại
            (7, "Bình giữ nhiệt thể thao Inox 1000ml", "PRD-036", "17.99", 55, False),
            (7, "Thảm tập Yoga định tuyến chống trượt 8mm", "PRD-037", "28.50", 30, True),
            (7, "Dây nhảy kháng lực tốc độ cao bạc đạn", "PRD-038", "8.99", 90, False),
            (7, "Đèn pin dã ngoại chống nước chiếu xa 500m", "PRD-039", "21.49", 40, False),
            (7, "Túi trống thể thao tập Gym đa ngăn đựng giày", "PRD-040", "24.99", 50, False),
        ]

        products = []
        for cat_idx, name, sku, price_str, stock, is_feat in raw_products:
            prod = Product(
                category_id=categories[cat_idx].id,
                name=name,
                sku=sku,
                price=Decimal(price_str),
                stock=stock,
                is_featured=is_feat,
                image_url=f"https://placehold.co/400x400?text={sku}",
                description=f"Mô tả chi tiết cho sản phẩm {name}.",
            )
            products.append(prod)
            db.add(prod)
        db.flush()

        db.commit()
        print("\n" + "=" * 60)
        print("[SUCCESS] ĐÃ NẠP THÀNH CÔNG BỘ DỮ LIỆU MẪU:")
        print(f"  - 2 Tài khoản nhân viên: admin@tzshop.vn / staff@tzshop.vn (pass: admin123 / staff123)")
        print(f"  - {len(categories)} Danh mục (hoạt động đầy đủ)")
        print(f"  - {len(products)} Sản phẩm (giá lẻ Decimal, có 2 sản phẩm tồn kho = 0)")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Lỗi nạp dữ liệu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    force_mode = "--force" in sys.argv
    seed_data(force=force_mode)
