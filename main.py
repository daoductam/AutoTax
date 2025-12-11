# import json
# import time  # <--- 1. Thêm thư viện time
# from pathlib import Path
#
# # Import hàm tạo PDF từ service DOCX
# from app.services import generate_01gtgt_2021_pdf_from_json
#
# def main():
#     # Bắt đầu bấm giờ
#     start_time = time.time()  # <--- 2. Lấy thời gian bắt đầu
#
#     # 1. Xác định thư mục chứa file hiện tại
#     base_dir = Path(__file__).resolve().parent
#
#     # 2. Định nghĩa đường dẫn file dữ liệu mẫu đầu vào (JSON)
#     sample_json_path = base_dir / "tests" / "sample_input_01gtgt_2021.json"
#
#     # 3. Định nghĩa đường dẫn file PDF đầu ra
#     # Mẹo: Thêm timestamp vào tên file để tránh lỗi "Permission denied" nếu file cũ đang mở
#     output_pdf_path = base_dir / "app" / "output" / f"01_GTGT_2021_sample_docx_{int(start_time)}.pdf"
#
#     # 4. Đọc dữ liệu từ file JSON mẫu
#     with sample_json_path.open(encoding="utf-8") as f:
#         data = json.load(f)
#
#     # 5. Gọi hàm service để thực hiện quy trình sinh file
#     print("Đang xử lý...")
#     generate_01gtgt_2021_pdf_from_json(data, output_pdf_path)
#
#     # Kết thúc bấm giờ
#     end_time = time.time()  # <--- 3. Lấy thời gian kết thúc
#     duration = end_time - start_time  # <--- 4. Tính thời gian chạy
#
#     # 6. Thông báo thành công và thời gian
#     print("-" * 50)
#     print(f"✅ Đã sinh PDF thành công: {output_pdf_path}")
#     print(f"⏱️ Tổng thời gian chạy: {duration:.2f} giây")
#     print("-" * 50)
#
# if __name__ == "__main__":
#     main()

import json
import time  # <--- 1. Import thư viện time
from pathlib import Path
from app.models import Declaration01GTGT
from app.services.html_pdf_service import generate_01gtgt_pdf_from_html


def main():
    # Bắt đầu bấm giờ
    start_time = time.time()  # <--- 2. Lấy thời gian bắt đầu

    base_dir = Path(__file__).resolve().parent

    # File input/output
    sample_json_path = base_dir / "tests" / "sample_input_01gtgt_2021.json"

    # Đổi tên file output để tránh lỗi Permission denied nếu file cũ đang mở
    output_pdf_path = base_dir / "app" / "output" / f"01_GTGT_HTML_Version_{int(start_time)}.pdf"

    # Đọc dữ liệu
    with sample_json_path.open(encoding="utf-8") as f:
        data_dict = json.load(f)

    # Validate dữ liệu
    declaration = Declaration01GTGT(**data_dict)

    # Gọi hàm sinh PDF
    generate_01gtgt_pdf_from_html(declaration, output_pdf_path)

    # Kết thúc bấm giờ
    end_time = time.time()  # <--- 3. Lấy thời gian kết thúc
    duration = end_time - start_time  # <--- 4. Tính khoảng thời gian

    print(f"--------------------------------------------------")
    print(f"✅ Hoàn thành trong: {duration:.4f} giây")
    print(f"📁 File PDF: {output_pdf_path}")
    print(f"--------------------------------------------------")


if __name__ == "__main__":
    main()