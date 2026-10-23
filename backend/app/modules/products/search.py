import re
from typing import List, Tuple, Optional, Set
from sqlalchemy import func, or_, and_, case
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.category import Category
from app.models.product import Product

# Mapping toàn diện bảng ký tự tiếng Việt (hoa/thường) và bảng chữ cái A-Z
# sang chữ thường không dấu ASCII. Giúp độc lập hoàn toàn với collation của DB.
VN_CHAR_MAP = {
    "a": "aáàảãạăắằẳẵặâấầẩẫậAÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ",
    "e": "eéèẻẽẹêếềểễệEÉÈẺẼẸÊẾỀỂỄỆ",
    "i": "iíìỉĩịIÍÌỈĨỊ",
    "o": "oóòỏõọôốồổỗộơớờởỡợOÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ",
    "u": "uúùủũụưứừửữựUÚÙỦŨỤƯỨỪỬỮỰ",
    "y": "yýỳỷỹỵYÝỲỶỸỴ",
    "d": "dđDĐ",
    "b": "bB", "c": "cC", "f": "fF", "g": "gG", "h": "hH", "j": "jJ", "k": "kK",
    "l": "lL", "m": "mM", "n": "nN", "p": "pP", "q": "qQ", "r": "rR", "s": "sS",
    "t": "tT", "v": "vV", "w": "wW", "x": "xX", "z": "zZ"
}

FROM_CHARS = "".join(group for group in VN_CHAR_MAP.values())
TO_CHARS = "".join(target * len(group) for target, group in VN_CHAR_MAP.items())

# Từ điển đồng nghĩa có kiểm soát (chỉ ánh xạ 1:1 ngữ cảnh công nghệ / sản phẩm rõ ràng)
# Không mặc định bluetooth và không dây luôn tương đương
SYNONYM_PAIRS = [
    ("keyboard", "ban phim"),
    ("mouse", "chuot"),
    ("headphone", "tai nghe"),
    ("earphone", "tai nghe"),
    ("wireless", "khong day"),
]


def normalize_text(text: Optional[str]) -> str:
    """Chuẩn hóa chuỗi tiếng Việt: bỏ dấu, chuyển chữ thường, dọn dẹp khoảng trắng."""
    if not text:
        return ""
    res = text
    for target, group in VN_CHAR_MAP.items():
        for ch in group:
            if ch in res:
                res = res.replace(ch, target)
    res = re.sub(r"\s+", " ", res).strip()
    return res


def sql_normalized_col(column):
    """Tạo biểu thức PostgreSQL TRANSLATE để chuẩn hóa cột DB mà không phụ thuộc collation."""
    return func.translate(column, FROM_CHARS, TO_CHARS)


def sql_spaceless_col(column):
    """Tạo biểu thức cột DB không dấu và loại bỏ toàn bộ khoảng trắng, dấu gạch nối."""
    return func.replace(func.replace(sql_normalized_col(column), " ", ""), "-", "")


def get_product_vocab(db: Session) -> Set[str]:
    """Lấy danh sách các từ/âm tiết có nghĩa từ tên các sản phẩm thực tế trong DB."""
    prods = db.query(Product.name).filter(Product.deleted_at.is_(None)).all()
    vocab: Set[str] = set()
    for p in prods:
        norm = normalize_text(p[0])
        for w in re.findall(r"[a-z0-9]+", norm):
            if len(w) >= 2:
                vocab.add(w)
    return vocab


def segment_compound_word(word: str, vocab: Set[str]) -> List[str]:
    """Tách từ ghép viết liền thành các từ đơn dựa trên vốn từ vựng sản phẩm (ví dụ: tainghebluetooth -> tai, nghe, bluetooth)."""
    n = len(word)
    dp = {0: []}
    for i in range(1, n + 1):
        for j in range(max(0, i - 15), i):
            sub = word[j:i]
            if j in dp and (sub in vocab or len(sub) == 1):
                dp[i] = dp[j] + [sub]
                break
    return dp.get(n, [word])


def find_matching_categories(db: Session, query_norm: str) -> List[int]:
    """
    Nhận diện từ khóa nhóm ngành hàng dựa trên danh mục THỰC TẾ trong database.
    Không hardcode ID, không tự suy đoán quan hệ cha-con.
    Sử dụng ranh giới từ (word boundary) để tránh overexpansion (ví dụ 'ao' không được khớp 'da ngoai').
    """
    if not query_norm or len(query_norm) < 2:
        return []

    active_categories = (
        db.query(Category.id, Category.name, Category.slug)
        .filter(Category.deleted_at.is_(None), Category.is_active == True)
        .all()
    )

    matched_ids: List[int] = []
    pattern = rf"\b{re.escape(query_norm)}\b"

    for cat in active_categories:
        cat_name_norm = normalize_text(cat.name).replace("&", " ").replace("-", " ")
        cat_name_norm = re.sub(r"\s+", " ", cat_name_norm).strip()
        cat_slug_norm = normalize_text(cat.slug).replace("-", " ").strip()

        if re.search(pattern, cat_name_norm) or re.search(pattern, cat_slug_norm):
            matched_ids.append(cat.id)

    return matched_ids


def get_synonym_variants(query_norm: str) -> List[str]:
    """
    Tạo các biến thể truy vấn từ từ điển đồng nghĩa có kiểm soát.
    Đảm bảo giữ toàn bộ điều kiện có nghĩa của truy vấn.
    """
    variants: Set[str] = set()

    for term1, term2 in SYNONYM_PAIRS:
        pattern1 = rf"\b{re.escape(term1)}\b"
        if re.search(pattern1, query_norm):
            variant = re.sub(pattern1, term2, query_norm)
            variant = re.sub(r"\s+", " ", variant).strip()
            if variant != query_norm:
                variants.add(variant)

        pattern2 = rf"\b{re.escape(term2)}\b"
        if re.search(pattern2, query_norm):
            variant = re.sub(pattern2, term1, query_norm)
            variant = re.sub(r"\s+", " ", variant).strip()
            if variant != query_norm:
                variants.add(variant)

    return list(variants)


def _token_match_expr(col_norm, token: str):
    """
    Tạo biểu thức khớp từ có kiểm soát ranh giới từ:
    - Nếu từ ngắn (<= 2 ký tự như 'ao', 'ví'): bắt buộc khớp ranh giới cả 2 đầu \\y{token}\\y
      để tránh trường hợp 'ao' bị khớp vào 'cao', 'giao', 'dạo'.
    - Nếu từ dài hơn 2 ký tự: khớp tiền tố từ \\y{token} hoặc nguyên từ.
    """
    escaped = re.escape(token)
    if len(token) <= 2:
        return col_norm.op("~*")(rf"\y{escaped}\y")
    return or_(
        col_norm.op("~*")(rf"\y{escaped}\y"),
        col_norm.op("~*")(rf"\y{escaped}")
    )


def build_search_expressions(
    db: Session,
    search_str: str,
) -> Tuple[Optional[ColumnElement[bool]], Optional[ColumnElement[int]]]:
    """
    Xây dựng điều kiện lọc (filter clause) và biểu thức tính điểm xếp hạng (ranking score)
    hoàn toàn tại database.

    Thứ tự xếp hạng ưu tiên (Score):
    - 100: Khớp tên chính xác (Exact match)
    - 80:  Khớp cụm từ nguyên vẹn có ranh giới từ (Phrase match)
    - 50:  Khớp tất cả các từ riêng lẻ với ranh giới từ (All words match)
    - 30:  Khớp biến thể từ đồng nghĩa (Synonym match - giữ toàn bộ ngữ cảnh truy vấn)
    - 25:  Khớp chuỗi viết liền không khoảng trắng (Spaceless match, ví dụ: tainghe, tainghebluetooth)
    - 10:  Khớp nhóm ngành / danh mục thực tế (Category match)
    """
    query_norm = normalize_text(search_str)
    if not query_norm:
        return None, None

    col_norm = sql_normalized_col(Product.name)
    col_spaceless = sql_spaceless_col(Product.name)
    tokens = [t for t in query_norm.split(" ") if t]
    query_spaceless = query_norm.replace(" ", "").replace("-", "")

    # 1. Điều kiện khớp tên chính xác
    exact_cond = col_norm == query_norm

    # 2. Điều kiện khớp cụm từ (có ranh giới từ)
    phrase_escaped = re.escape(query_norm)
    phrase_boundary_cond = col_norm.op("~*")(rf"\y{phrase_escaped}\y")

    # 3. Điều kiện khớp tất cả các từ riêng lẻ (không cần đúng thứ tự)
    token_boundary_conds = [_token_match_expr(col_norm, t) for t in tokens]
    all_tokens_boundary_cond = and_(*token_boundary_conds) if token_boundary_conds else False

    # 4. Điều kiện từ đồng nghĩa có kiểm soát
    synonym_variants = get_synonym_variants(query_norm)
    synonym_conds = []
    for var in synonym_variants:
        var_tokens = [t for t in var.split(" ") if t]
        if var_tokens:
            var_token_conds = [_token_match_expr(col_norm, t) for t in var_tokens]
            synonym_conds.append(and_(*var_token_conds))
    synonym_cond = or_(*synonym_conds) if synonym_conds else False

    # 5. Điều kiện khớp chuỗi viết liền không khoảng trắng (Spaceless matching)
    # Chỉ áp dụng khi độ dài query_spaceless >= 4 để bảo đảm an toàn,
    # tuyệt đối không làm mất cơ chế chống overexpansion của các từ ngắn như 'ao'
    spaceless_sub_conds = []
    if len(query_spaceless) >= 4:
        # So khớp trực tiếp chuỗi viết liền trong cột spaceless
        spaceless_sub_conds.append(col_spaceless.like(f"%{query_spaceless}%"))

        # Phân tách từ ghép thành các âm tiết từ vựng sản phẩm (ví dụ tainghebluetooth -> tai, nghe, bluetooth)
        vocab = get_product_vocab(db)
        segmented_tokens = segment_compound_word(query_spaceless, vocab)
        if len(segmented_tokens) > 1:
            # Tất cả các từ đã tách phải xuất hiện trong tên sản phẩm
            seg_match_conds = [_token_match_expr(col_norm, st) for st in segmented_tokens]
            spaceless_sub_conds.append(and_(*seg_match_conds))
            # Hoặc khớp theo thứ tự xuất hiện trong cột spaceless
            seq_pattern = ".*".join(re.escape(st) for st in segmented_tokens)
            spaceless_sub_conds.append(col_spaceless.op("~*")(seq_pattern))

    spaceless_cond = or_(*spaceless_sub_conds) if spaceless_sub_conds else False

    # 6. Điều kiện nhận diện danh mục thực tế
    matched_cat_ids = find_matching_categories(db, query_norm)
    category_cond = Product.category_id.in_(matched_cat_ids) if matched_cat_ids else False

    # Tổng hợp bộ lọc: sản phẩm được chọn nếu thỏa mãn bất kỳ cấp độ nào ở trên
    master_filter = or_(
        exact_cond,
        phrase_boundary_cond,
        all_tokens_boundary_cond,
        synonym_cond,
        spaceless_cond,
        category_cond,
    )

    # Biểu thức tính điểm xếp hạng
    ranking_score = case(
        (exact_cond, 100),
        (phrase_boundary_cond, 80),
        (all_tokens_boundary_cond, 50),
        (synonym_cond, 30),
        (spaceless_cond, 25),
        (category_cond, 10),
        else_=0
    )

    return master_filter, ranking_score
