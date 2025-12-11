from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

# Import Model của bạn
from app.models import Declaration01GTGT

# Xác định thư mục chứa file HTML template
BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "app" / "templates" / "html"


def format_vnd(value: int) -> str:
    """
    Format số nguyên thành tiền tệ Việt Nam:
    1000000 -> 1.000.000
    0 -> 0
    None -> ""
    """
    if value is None:
        return ""
    if value == 0:
        return "0"
    # Format dấu phẩy kiểu Mỹ (1,000,000) sau đó đổi dấu phẩy thành dấu chấm
    return "{:,.0f}".format(value).replace(",", ".")


def translate_period(type_code: str) -> str:
    """Dịch loại kỳ tính thuế"""
    if type_code == "month":
        return "Tháng"
    elif type_code == "quarter":
        return "Quý"
    return type_code


def generate_01gtgt_pdf_from_html(
        declaration: Declaration01GTGT,
        output_pdf_path: Path
) -> None:
    """
    Hàm chính: Nhận object tờ khai -> Điền vào HTML -> Xuất ra PDF
    """
    # 1. Khởi tạo môi trường Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    # 2. Đăng ký các hàm format (filter) để dùng trong file HTML
    env.filters['format_vnd'] = format_vnd
    env.filters['translate_period'] = translate_period

    # 3. Load template
    try:
        template = env.get_template("01_GTGT_2021.html")
    except Exception as e:
        print(f"Lỗi không tìm thấy template tại: {TEMPLATE_DIR}")
        raise e

    # 4. Chuẩn bị dữ liệu context
    # Chuyển Pydantic model thành dict
    data = declaration.model_dump()
    # Thêm ngày hiện tại để in ngày ký
    data['today'] = datetime.now()

    # 5. Render HTML thành chuỗi string
    html_content = template.render(**data)

    # 6. Tạo thư mục output nếu chưa có
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # 7. Gọi WeasyPrint để xuất PDF
    # base_url=str(TEMPLATE_DIR) giúp load ảnh/css nếu bạn để file rời
    print("Đang tạo PDF bằng WeasyPrint...")
    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(str(output_pdf_path))
    print(f"Đã xuất file thành công: {output_pdf_path}")