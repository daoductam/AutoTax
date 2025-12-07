from pathlib import Path  # Thư viện để xử lý đường dẫn file (đa nền tảng)
from typing import Dict, Any  # Thư viện để định nghĩa kiểu dữ liệu (Type Hinting)

from docxtpl import DocxTemplate  # Thư viện để điền dữ liệu vào file Word template (.docx)
from docx2pdf import convert  # Thư viện để convert từ Word sang PDF (yêu cầu Word cài sẵn hoặc Windows)

from app.models import Declaration01GTGT  # Import Model dữ liệu tờ khai đã định nghĩa
from app.services.mapping_service import load_mapping, get_value_by_path  # Import các hàm tiện ích hỗ trợ mapping

# Xác định thư mục gốc của dự án (tax_pdf_service) bằng cách lấy thư mục cha cấp 2 của file hiện tại
BASE_DIR = Path(__file__).resolve().parents[2]


def build_docx_context(
        declaration: Declaration01GTGT,  # Tham số đầu vào: Object chứa dữ liệu tờ khai
        mapping: Dict[str, Dict[str, Any]],  # Tham số đầu vào: Config ánh xạ (mapping json)
) -> Dict[str, Any]:
    """
    Hàm này chuyển đổi dữ liệu từ Object Declaration01GTGT thành dictionary phẳng (context)
    để thư viện docxtpl có thể điền vào file Word.
    Ví dụ: Object taxpayer.name -> Context key "F_04_ten_nguoi_nop_thue"
    """
    # 1. Chuyển đổi Object Pydantic sang Dictionary thuần của Python
    decl_dict = declaration.model_dump()

    # 2. Khởi tạo dict context rỗng để chứa kết quả
    context: Dict[str, Any] = {}

    # 3. Duyệt qua từng dòng trong file cấu hình mapping (file JSON)
    # placeholder: là tên biến trong file Word (ví dụ: F_04_ten_nguoi_nop_thue)
    # cfg: là cấu hình tương ứng (ví dụ: {"path": "taxpayer.name"})
    for placeholder, cfg in mapping.items():

        # 4. Lấy giá trị thực tế từ dữ liệu dựa trên đường dẫn (path) được cấu hình
        # Ví dụ: path là "taxpayer.name" thì hàm get_value_by_path sẽ tìm trong decl_dict
        raw_val = get_value_by_path(decl_dict, cfg["path"])

        # 5. Lấy định dạng dữ liệu (nếu có), ví dụ: "month_year"
        fmt = cfg.get("format")

        # 6. Xử lý logic định dạng đặc biệt
        # Nếu format là "month_year" và có giá trị raw_val (không bị null)
        if fmt == "month_year" and raw_val:
            # raw_val lúc này là dict dạng {"month": 12, "year": 2024}
            # Format lại thành chuỗi "Tháng 12 năm 2024"
            context[placeholder] = f"Tháng {raw_val['month']} năm {raw_val['year']}"
        else:
            # Nếu không có format đặc biệt, gán giá trị nguyên bản
            context[placeholder] = raw_val

    # 7. Trả về context đã chuẩn bị xong
    return context


def render_docx_from_template(
        template_path: Path,  # Đường dẫn file mẫu (.docx template)
        context: Dict[str, Any],  # Dữ liệu đã chuẩn bị để điền vào
        output_docx_path: Path,  # Đường dẫn file Word kết quả sau khi điền
) -> None:
    """
    Hàm này nhận file mẫu và dữ liệu, sau đó sinh ra file Word đã có dữ liệu.
    """
    # 1. Khởi tạo object DocxTemplate từ file mẫu
    tpl = DocxTemplate(str(template_path))

    # 2. Thực hiện render (điền dữ liệu từ context vào các placeholder {{...}} trong Word)
    tpl.render(context)

    # 3. Tạo thư mục chứa file output nếu chưa tồn tại (tránh lỗi file not found)
    output_docx_path.parent.mkdir(parents=True, exist_ok=True)

    # 4. Lưu file Word kết quả ra ổ cứng
    tpl.save(str(output_docx_path))


def convert_docx_to_pdf(input_docx_path: Path, output_pdf_path: Path) -> None:
    """
    Hàm này chuyển đổi file Word sang PDF.
    Lưu ý: Hàm này dùng 'docx2pdf', yêu cầu máy chạy phải cài Microsoft Word (trên Windows/macOS).
    """
    # 1. Tạo thư mục chứa file PDF output nếu chưa tồn tại
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. Gọi lệnh convert của thư viện docx2pdf
    convert(str(input_docx_path), str(output_pdf_path))


def generate_01gtgt_2021_pdf_from_json(
        declaration_data: Dict[str, Any],  # Dữ liệu đầu vào dạng JSON (dict)
        output_pdf_path: Path,  # Đường dẫn file PDF mong muốn đầu ra
) -> None:
    """
    Hàm chính (Public): Kết hợp toàn bộ quy trình từ JSON -> DOCX -> PDF.
    """
    # 1. Validate dữ liệu đầu vào bằng Pydantic Model (nếu sai cấu trúc sẽ báo lỗi ngay tại đây)
    declaration = Declaration01GTGT(**declaration_data)

    # 2. Load file cấu hình mapping (file 01_GTGT_2021_docx_mapping.json)
    mapping = load_mapping("01_GTGT_2021_docx")

    # 3. Chuẩn bị dữ liệu context cho file Word
    context = build_docx_context(declaration, mapping)

    # 4. Xác định đường dẫn đến file mẫu template (.docx)
    template_path = (
            BASE_DIR / "app" / "templates" / "docx" / "01_GTGT_2021_template.docx"
    )

    # 5. Tạo đường dẫn file Word tạm thời (cùng tên file PDF nhưng đuôi .docx)
    # Ví dụ: output/file.pdf -> output/file.docx
    tmp_docx_path = output_pdf_path.with_suffix(".docx")

    # 6. Sinh file Word tạm thời
    render_docx_from_template(template_path, context, tmp_docx_path)

    # 7. Convert file Word tạm thời sang PDF
    convert_docx_to_pdf(tmp_docx_path, output_pdf_path)