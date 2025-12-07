import json  # Thư viện để đọc/ghi file JSON
from pathlib import Path  # Thư viện xử lý đường dẫn
from typing import Any, Dict  # Thư viện định kiểu

# Xác định thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parents[2]


def load_mapping(form_code: str) -> Dict[str, Dict[str, Any]]:
    """
    Hàm đọc file cấu hình JSON mapping.
    form_code: Mã biểu mẫu, ví dụ '01_GTGT_2021_docx'
    """
    # 1. Xây dựng đường dẫn tuyệt đối đến file JSON trong thư mục config
    mapping_path = (
            BASE_DIR
            / "app"
            / "config"
            / "form_mappings"
            / f"{form_code}_mapping.json"
    )

    # 2. Kiểm tra xem file có tồn tại không
    if not mapping_path.exists():
        # Nếu không thấy file thì ném ra lỗi
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

    # 3. Mở file và đọc nội dung JSON trả về dạng Dictionary
    with mapping_path.open(encoding="utf-8") as f:
        return json.load(f)


def get_value_by_path(obj: Any, path: str) -> Any:
    """
    Hàm tiện ích giúp lấy giá trị từ dict lồng nhau bằng chuỗi ký tự.
    Ví dụ: obj = {"a": {"b": 10}}, path = "a.b" -> Trả về 10
    """
    # 1. Tách chuỗi path thành danh sách các key. VD: "taxpayer.name" -> ["taxpayer", "name"]
    parts = path.split(".")

    # 2. Biến tạm 'current' giữ vị trí hiện tại đang duyệt, bắt đầu từ gốc (obj)
    current = obj

    # 3. Duyệt qua từng phần của key
    for key in parts:
        # Nếu tại cấp hiện tại là None, dừng lại và trả về None (tránh lỗi crash)
        if current is None:
            return None

        # Nếu current là Dictionary, dùng .get(key)
        if isinstance(current, dict):
            current = current.get(key)
        else:
            # Nếu current là Object (class), dùng getattr
            current = getattr(current, key, None)

    # 4. Trả về giá trị cuối cùng tìm được
    return current