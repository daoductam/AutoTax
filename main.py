import json  # Thư viện đọc JSON
from pathlib import Path  # Thư viện đường dẫn

# Import hàm tạo PDF từ service chúng ta đã viết
from app.services import generate_01gtgt_2021_pdf_from_json


def main():
    # 1. Xác định thư mục chứa file hiện tại
    base_dir = Path(__file__).resolve().parent

    # 2. Định nghĩa đường dẫn file dữ liệu mẫu đầu vào (JSON)
    sample_json_path = base_dir / "tests" / "sample_input_01gtgt_2021.json"

    # 3. Định nghĩa đường dẫn file PDF đầu ra
    output_pdf_path = base_dir / "app" / "output" / "01_GTGT_2021_sample_docx.pdf"

    # 4. Đọc dữ liệu từ file JSON mẫu
    with sample_json_path.open(encoding="utf-8") as f:
        data = json.load(f)  # Chuyển nội dung file thành Dict Python

    # 5. Gọi hàm service để thực hiện quy trình sinh file
    # Hàm này sẽ làm hết: Validate -> Fill Word -> Convert PDF
    generate_01gtgt_2021_pdf_from_json(data, output_pdf_path)

    # 6. Thông báo thành công
    print(f"Đã sinh PDF: {output_pdf_path}")


# Kiểm tra xem file có đang được chạy trực tiếp không (hay là được import)
if __name__ == "__main__":
    main()