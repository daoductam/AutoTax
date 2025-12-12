from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

# Import Model và các hàm hỗ trợ mapping cũ
from app.models import Declaration01GTGT
from app.services.mapping_service import load_mapping, get_value_by_path

# Xác định thư mục chứa file HTML template
BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "app" / "templates" / "html"


def format_vnd(value: Any) -> str:
    """Format số nguyên thành tiền tệ Việt Nam"""
    if not value and value != 0:
        return ""
    try:
        val_int = int(value)
        return "{:,.0f}".format(val_int).replace(",", ".")
    except:
        return str(value)


def build_flat_context(declaration: Declaration01GTGT) -> Dict[str, Any]:
    """
    Hàm này biến đổi dữ liệu Object lồng nhau thành dictionary phẳng (F_...)
    để khớp với file HTML cũ của bạn.
    """
    # 1. Load file cấu hình mapping (file json cũ)
    mapping = load_mapping("01_GTGT_2021_docx")

    # 2. Chuyển đổi Object Pydantic sang Dict
    decl_dict = declaration.model_dump()

    context: Dict[str, Any] = {}

    # 3. Duyệt qua file mapping để lấy dữ liệu
    for placeholder, cfg in mapping.items():
        # Lấy giá trị theo đường dẫn (ví dụ: taxpayer.name)
        raw_val = get_value_by_path(decl_dict, cfg["path"])

        # Xử lý format đặc biệt (ví dụ ngày tháng)
        fmt = cfg.get("format")
        if fmt == "month_year" and raw_val:
            context[placeholder] = f"Tháng {raw_val['month']} năm {raw_val['year']}"
        else:
            # Nếu giá trị là số, format tiền tệ luôn (để hiển thị đẹp trên HTML)
            if isinstance(raw_val, (int, float)) and raw_val > 0:
                # Lưu ý: file HTML của bạn không dùng filter | format_vnd nên ta format ngay tại đây
                context[placeholder] = "{:,.0f}".format(raw_val).replace(",", ".")
            elif raw_val == 0:
                context[placeholder] = "0"
            else:
                context[placeholder] = raw_val if raw_val is not None else ""

    return context


def generate_01gtgt_pdf_from_html(
        declaration: Declaration01GTGT,
        output_pdf_path: Path
) -> None:
    # 1. Khởi tạo môi trường Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    # 2. Load template HTML (File cũ của bạn)
    try:
        template = env.get_template("01_GTGT_2021_template_v4.html")
    except Exception as e:
        print(f"Lỗi không tìm thấy template tại: {TEMPLATE_DIR}")
        raise e

    # 3. Chuẩn bị dữ liệu: Dùng hàm build_flat_context để tạo các biến F_...
    flat_data = build_flat_context(declaration)

    # Thêm biến ngày tháng hiện tại (nếu trong HTML có dùng)
    now = datetime.now()
    flat_data['today_day'] = now.day
    flat_data['today_month'] = now.month
    flat_data['today_year'] = now.year

    # 4. Render HTML
    html_content = template.render(**flat_data)

    # 5. Tạo thư mục output và xuất PDF
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    print("Đang tạo PDF bằng WeasyPrint...")
    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(str(output_pdf_path))
    print(f"Đã xuất file thành công: {output_pdf_path}")