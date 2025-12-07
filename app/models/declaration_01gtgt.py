from pydantic import BaseModel  # Class cơ sở của Pydantic để validate dữ liệu
from typing import Optional, Dict, Any  # Các kiểu dữ liệu bổ trợ


# Class định nghĩa thông tin chung (meta)
class Meta(BaseModel):
    first_time: Optional[str] = None  # Có thể là string hoặc None (Optional)
    revision_number: Optional[str] = None


# Class định nghĩa kỳ tính thuế
class TaxPeriod(BaseModel):
    type: str  # Bắt buộc phải là string ("month" hoặc "quarter")
    month: Optional[int] = None  # Tháng (số nguyên), có thể null
    quarter: Optional[int] = None # Quý (số nguyên), có thể null
    year: int # Năm (số nguyên), bắt buộc


# Class định nghĩa người nộp thuế
class Taxpayer(BaseModel):
    name: str # Tên công ty/cá nhân (bắt buộc)
    tax_code: str # Mã số thuế (bắt buộc)
    address: str # Địa chỉ (bắt buộc)
    phone: Optional[str] = None # Số điện thoại (tùy chọn)


class Agency(BaseModel):
    name: Optional[str] = None
    tax_code: Optional[str] = None
    contract_number: Optional[str] = None
    contract_date: Optional[str] = None


class AddressDetail(BaseModel):
    ward: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None


class Branch(BaseModel):
    name: Optional[str] = None
    tax_code: Optional[str] = None
    address: Optional[AddressDetail] = None


class Business(BaseModel):
    activity_name: str
    scale: str
    method: str


# Class định nghĩa chi tiết thuế suất (dùng chung cho 5%, 10%)
class VatRateDetail(BaseModel):
    value: int = 0  # Giá trị hàng hóa (mặc định là 0 nếu không truyền)
    vat: int = 0    # Tiền thuế (mặc định là 0)


class InputPurchases(BaseModel):
    value: int = 0
    vat: int = 0
    imports: Optional[VatRateDetail] = None  # [23a], [24a]


class OutputSales(BaseModel):
    non_vat: int = 0  # [26]
    vat_0: int = 0  # [29]
    vat_5: VatRateDetail = VatRateDetail()  # [30], [31]
    vat_10: VatRateDetail = VatRateDetail()  # [32], [33]
    not_taxed: int = 0  # [32a]


class OutputTotal(BaseModel):
    value: int = 0
    vat: int = 0

# Class tổng hợp các chỉ tiêu tính thuế
class TaxCalc(BaseModel):
    no_activity: Optional[str] = None  # [21] (Giá trị "X" hoặc null)
    deductible_previous: int = 0  # [22]

    input_purchases: InputPurchases  # [23], [24], [23a], [24a]

    # [25] Thuế GTGT được khấu trừ kỳ này
    deductible_period: int = 0

    output_sales: OutputSales  # [26] -> [33], [32a]
    output_total: OutputTotal  # [27], [28], [34], [35]

    vat_period: int = 0  # [36] Thuế phát sinh trong kỳ

    adjustment_decrease: int = 0  # [37]
    adjustment_increase: int = 0  # [38]
    vat_received_deduction: int = 0  # [39a]

    vat_payable_period: int = 0  # [40a]
    vat_investment_offset: int = 0  # [40b]
    vat_payable_final: int = 0  # [40]

    vat_remaining_unpaid: int = 0  # [41]
    vat_refund_claim: int = 0  # [42]
    vat_transfer_next: int = 0  # [43]


# Class TỔNG HỢP TOÀN BỘ TỜ KHAI (Root Model)
class Declaration01GTGT(BaseModel):
    declaration_type: str  # Loại tờ khai (VD: "01_GTGT_2021")
    meta: Optional[Meta] = None
    tax_period: TaxPeriod  # Chứa thông tin kỳ thuế
    taxpayer: Taxpayer     # Chứa thông tin người nộp
    agency: Optional[Agency] = None # Đại lý thuế (tùy chọn)
    branch: Optional[Branch] = None # Chi nhánh (tùy chọn)
    business: Business     # Ngành nghề kinh doanh
    revenue: Optional[Dict[str, Any]] = {} # Dữ liệu doanh thu khác (nếu cần mở rộng)
    tax_calc: TaxCalc      # Chứa toàn bộ số liệu tính toán