"""Sổ nhập CLB — MỘT tệp Excel thay cho ba tệp nạp cũ.

Ban giám khảo nhận xét bước nhập quá rối: ba tệp riêng, tên cột tiếng Anh,
gõ tay mã CLB (gõ sai một ký tự là mất cả học sinh), và mẫu .xlsx chỉ có bản
một buổi. Sổ nhập gom tất cả về một tệp, hai sheet, tiêu đề tiếng Việt:

  `1. CLB`        Tên CLB · Buổi · Chỉ tiêu · Suất ưu tiên · Nhóm ưu tiên · Mã CLB
  `2. Học sinh`   Mã HS · Họ tên · Nhóm ưu tiên · NV1 · Điểm 1 · NV2 · Điểm 2 · …

Ô NV là danh sách thả xuống tên CLB. Ô Điểm đứng ngay cạnh NV cùng số:
có điểm (hoặc chữ `thi`) nghĩa là em đã dự thi CLB đó; trống là không thi.
Vì thế tệp "chọn CLB muốn thi" cũ biến mất — nó chỉ còn là các ô điểm.

Một danh sách NV chung cho mọi buổi: buổi của từng nguyện vọng suy ra từ cột
Buổi của CLB, và thuật toán luôn lọc nguyện vọng theo buổi trước khi dùng
(xem `import_preferences_csv`). Nhờ vậy mẫu KHÔNG phụ thuộc trường có mấy buổi.

Tệp này là NGUỒN DUY NHẤT mô tả sổ nhập. Bốn nơi dùng chung nó: phần mềm
(api_nhap.py — đọc sổ), mẫu (mau_csv/tao_so_nhap.py), xuất dữ liệu đầu vào
(api_xuat.py) và hai skill sinh/xử lí dữ liệu. Sửa định dạng thì chỉ sửa ở đây.

Không phụ thuộc gì ngoài openpyxl, i18n_errors và nhan_ws (nhan_ws không phụ thuộc gì) —
để skill đóng gói được. KHÔNG import cau_hinh_ws: cấu hình workspace (`cfg`) được truyền
vào dưới dạng dict thô — {"labels": {...}, "rules": {...}} — thiếu gì thì lấy mặc định
trường học, nên `cfg=None` cho ra đúng sổ như trước khi có workspace.
"""

from __future__ import annotations

import csv
import io
import math
import re
import unicodedata

from i18n_errors import err
from nhan_ws import dang_chu

# ---------------------------------------------------------------------------
# Tên sheet, tiêu đề cột
# ---------------------------------------------------------------------------
SHEET_CLB = "1. CLB"
SHEET_HS = "2. Học sinh"
SHEET_HD = "Hướng dẫn"

# Số cột NV mặc định của mẫu trống. Trần nguyện vọng của phần mềm là 10 MỖI
# BUỔI; 15 đủ cho trường một-hai buổi mà dòng vẫn vừa màn hình. Mẫu sinh từ
# dữ liệu có sẵn tự nới theo số buổi và số NV dài nhất.
SO_NV_MAC_DINH = 15
# Trần MỖI BUỔI của phần mềm (rbda_priority_pipeline.TRAN_NGUYEN_VONG_MOI_BUOI,
# TRAN_CLB_THI_MOI_BUOI). Chép lại ở đây vì tệp này phải chạy được một mình
# trong bản đóng gói của skill; tests/test_so_nhap.py canh hai bên bằng nhau.
TRAN_NV_MOI_BUOI = 10
TRAN_THI_MOI_BUOI = 5
SO_DONG_CLB_TRONG = 60
SO_DONG_HS_TRONG = 1500
TU_DANH_DAU_THI = "thi"

COT_CLB = ["Tên CLB", "Buổi", "Chỉ tiêu", "Suất ưu tiên", "Nhóm ưu tiên", "Mã CLB"]
COT_HS_DAU = ["Mã HS", "Họ tên", "Nhóm ưu tiên"]

# Nhãn buổi trong danh sách thả xuống -> mã buổi lưu trong CSDL.
NHAN_BUOI = [
    ("Thứ 2", "thu_2"), ("Thứ 3", "thu_3"), ("Thứ 4", "thu_4"),
    ("Thứ 5", "thu_5"), ("Thứ 6", "thu_6"), ("Thứ 7", "thu_7"),
    ("Chủ nhật", "chu_nhat"),
]


# ---------------------------------------------------------------------------
# Từ vựng của workspace (cfg) -> tên sheet, tiêu đề cột, trần
# ---------------------------------------------------------------------------
def _cfg(cfg) -> dict:
    """Rút `cfg` (dict thô, có thể thiếu/None) thành những thứ sổ nhập cần.

    Thiếu gì lấy mặc định trường học: nhãn mặc định, trần 10/5, điểm theo từng CLB.
    `max_tests` bằng None là KHÔNG GIỚI HẠN — khác với thiếu khoá (mặc định 5).
    """
    cfg = cfg if isinstance(cfg, dict) else {}
    nhan = cfg.get("labels") if isinstance(cfg.get("labels"), dict) else {}
    luat = cfg.get("rules") if isinstance(cfg.get("rules"), dict) else {}
    mc = luat.get("max_choices", TRAN_NV_MOI_BUOI)
    mt = luat["max_tests"] if "max_tests" in luat else TRAN_THI_MOI_BUOI
    return {
        "nhan": nhan,
        "max_choices": mc if isinstance(mc, int) and not isinstance(mc, bool) else TRAN_NV_MOI_BUOI,
        "max_tests": mt if (mt is None or (isinstance(mt, int) and not isinstance(mt, bool)))
        else TRAN_THI_MOI_BUOI,
        "per_person": luat.get("score_scope") == "per_person",
        # Điểm Wharton (mục A13): thêm cột "Điểm W k" sau "Điểm k". Chỉ có nghĩa khi điểm theo
        # từng CLB (cau_hinh_ws không cho bật cùng per_person); thiếu khoá = tắt.
        "wharton": luat.get("wharton") is True and luat.get("score_scope") != "per_person",
    }


def _ten_sheet(ten: str) -> str:
    """Tên sheet Excel hợp lệ: bỏ ký tự cấm `[ ] : * ? / \\`, tối đa 31 ký tự.

    Đọc lại cũng đi qua hàm này, nên nhãn dài hay có ký tự cấm vẫn khớp."""
    return "".join("-" if c in '[]:*?/\\' else c for c in ten).strip()[:31]


def ten_sheet_clb(cfg=None) -> str:
    """'1. CLB' với mặc định trường học; 1. <nhãn chỗ xếp> với workspace khác."""
    return _ten_sheet("1. " + dang_chu(_cfg(cfg)["nhan"], "slot", "s", "vi"))


def ten_sheet_hs(cfg=None) -> str:
    """'2. Học sinh' với mặc định trường học; 2. <nhãn người> với workspace khác."""
    return _ten_sheet("2. " + dang_chu(_cfg(cfg)["nhan"], "person", "", "vi"))


def nhan_nhom(cfg=None) -> str:
    """Tiêu đề cột nhóm ưu tiên: nhãn của danh từ 'group' ('Nhóm ưu tiên' mặc định)."""
    return dang_chu(_cfg(cfg)["nhan"], "group", "", "vi")


def nhan_diem(cfg=None) -> str:
    """Tiêu đề cột điểm: nhãn của danh từ 'score' ('Điểm' mặc định)."""
    return dang_chu(_cfg(cfg)["nhan"], "score", "", "vi")


def cot_clb(cfg=None) -> list:
    """Tiêu đề sheet CLB; cột nhóm đặt theo nhãn nhóm của workspace."""
    c = list(COT_CLB)
    c[c.index("Nhóm ưu tiên")] = nhan_nhom(cfg)
    return c


def cot_hs_dau(cfg=None) -> list:
    c = list(COT_HS_DAU)
    c[c.index("Nhóm ưu tiên")] = nhan_nhom(cfg)
    return c


def _bien_the(cfg, danh_tu: str) -> set:
    """Mọi cách gọi `danh_tu` đã bỏ dấu: nhãn vi, nhãn en, dạng viết tắt ('clb')."""
    nhan = _cfg(cfg)["nhan"]
    return {bo_dau(dang_chu(nhan, danh_tu, co, lang))
            for co in ("", "s") for lang in ("vi", "en")} - {""}


def bo_dau(chuoi) -> str:
    """'Mã HS *' -> 'ma hs'. Bỏ dấu, hạ chữ thường, gọn khoảng trắng.

    CHỈ dùng để so TIÊU ĐỀ CỘT (người dùng gõ lại tiêu đề không dấu, viết
    hoa cả cột…). Không dùng làm khoá tên CLB: nó bỏ cả phần trong ngoặc và
    mọi ký hiệu, nên "Bóng đá (nam)" với "Bóng đá (nữ)", hay "C++" với "C#",
    thành một — xem `khoa_ten`.
    """
    s = unicodedata.normalize("NFD", str(chuoi or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    s = re.sub(r"\(.*?\)", " ", s)          # "(bắt buộc)" và chú thích kiểu đó
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def khong_dau(chuoi) -> str:
    """'Bóng đá (Nữ)' -> 'bong da (nu)'. Chỉ bỏ dấu, hoa/thường, khoảng trắng
    thừa; GIỮ ngoặc và ký hiệu — khác `bo_dau`, vốn chỉ dành cho tiêu đề cột."""
    s = unicodedata.normalize("NFD", str(chuoi or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").casefold()
    return " ".join(s.split())


def khoa_long(chuoi) -> str:
    """Khoá so "gõ lỏng" cho ô NV: bỏ dấu, hoa/thường, và coi `_ - .` như
    khoảng trắng ("clb tin hoc", "CLB-Tin-Hoc" khớp mã `clb_tin_hoc`). GIỮ
    ngoặc và ký hiệu khác: "(nữ)" khác "(nam)", "C#" khác "C++"."""
    return " ".join(re.sub(r"[_.\-]+", " ", khong_dau(chuoi)).split())


def khoa_ten(ten) -> str:
    """Khoá so TÊN CLB: chỉ bỏ khác biệt hoa/thường và khoảng trắng thừa.

    Giữ dấu, ngoặc và ký hiệu: hai tên chỉ khác nhau ở đó là hai CLB khác
    nhau thật ("Bóng đá (nam)" / "Bóng đá (nữ)", "C++" / "C#", "Toán" / "Toan").
    """
    s = unicodedata.normalize("NFC", str(ten or "")).casefold()
    return " ".join(s.split())


def tao_ma_clb(ten: str) -> str:
    """'CLB Bóng đá (nữ)' -> 'clb_bong_da_nu'. Tất định: cùng tên, cùng mã.

    Giữ phần trong ngoặc; '+' -> 'plus', '#' -> 'sharp' để "C++" và "C#"
    ra hai mã khác nhau. Không tự thêm _2 khi trùng: số thêm vào phụ thuộc
    thứ tự dòng, sắp lại dòng là hai CLB đổi mã cho nhau. Trùng thì người
    dùng phải điền Mã CLB (lỗi `so_nhap_ma_tu_sinh_trung`).
    """
    s = unicodedata.normalize("NFD", str(ten or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    s = s.replace("+", " plus ").replace("#", " sharp ")
    s = "_".join(re.sub(r"[^a-z0-9]+", " ", s).split()) or "clb"
    return s if s.startswith("clb") else "clb_" + s


_THU = {"2": 2, "hai": 2, "3": 3, "ba": 3, "4": 4, "tu": 4, "5": 5, "nam": 5,
        "6": 6, "sau": 6, "7": 7, "bay": 7}


def ma_buoi(nhan) -> str:
    """'Thứ 2' / 'thu 2' / 'T2' / 'Chủ nhật' -> 'thu_2' / 'chu_nhat'.

    Trống -> '' (trường một buổi). Chỉ đổi khi CẢ nhãn là một thứ trong
    tuần: 'thu_3_tiet_9' là một buổi riêng của trường, gộp nó vào 'thu_3'
    là biến hai buổi khác giờ thành trùng giờ. Nhãn khác giữ nguyên, chuẩn
    hoá đúng như `chuan_hoa_buoi` của phần mềm.
    """
    tho = " ".join(str(nhan or "").split()).strip()
    if not tho:
        return ""
    # Dấu câu là dấu tách ("Thứ-2", "T.2", "Thứ 2." đều là thứ Hai), nhưng
    # CHỮ trong ngoặc được giữ: bo_dau bỏ cả phần trong ngoặc nên "Thứ 3
    # (sáng)" và "Thứ 3 (chiều)" từng thành một buổi — hai giờ khác nhau bị
    # coi là trùng giờ.
    c = re.sub(r"[^a-z0-9]+", "_", khong_dau(tho)).strip("_")
    if c in ("cn", "chu_nhat"):
        return "chu_nhat"
    # "thu" + số hoặc chữ (thu_2, thu_hai); "t" CHỈ đi với số (t2, t_2):
    # "tba" (to be announced) hay "thai" không phải thứ Ba, thứ Hai.
    m = re.fullmatch(r"thu_?([a-z0-9]+)|t_?([0-9])", c)
    con_lai = (m.group(1) or m.group(2)) if m else None
    if con_lai in _THU:
        return f"thu_{_THU[con_lai]}"
    return tho.lower().replace(" ", "_")


def nhan_buoi(ma) -> str:
    """'thu_2' -> 'Thứ 2'. Mã lạ giữ nguyên; trống giữ trống."""
    for nhan, m in NHAN_BUOI:
        if m == ma:
            return nhan
    return ma or ""


def doc_diem(chuoi):
    """Một ô điểm -> float, hoặc None nếu không phải số.

    Nhận dấu phẩy thập phân (Excel tiếng Việt lưu 8,5). Chỉ đổi khi có ĐÚNG
    một dấu phẩy và không có dấu chấm — "1,234.5" là cách viết nghìn.
    """
    chuoi = str(chuoi if chuoi is not None else "").strip()
    if not chuoi:
        return None
    if chuoi.count(",") == 1 and "." not in chuoi:
        chuoi = chuoi.replace(",", ".")
    try:
        so = float(chuoi)
    except (TypeError, ValueError):
        return None
    return so if so == so and so not in (float("inf"), float("-inf")) else None


def o_thanh_chu(gia_tri) -> str:
    """Ô Excel -> chuỗi. 20.0 -> '20' (int('20.0') ném lỗi)."""
    if gia_tri is None:
        return ""
    if isinstance(gia_tri, bool):
        return "1" if gia_tri else ""
    if isinstance(gia_tri, float) and gia_tri.is_integer():
        return str(int(gia_tri))
    return str(gia_tri).strip()


# ---------------------------------------------------------------------------
# Nhận ra cột
# ---------------------------------------------------------------------------
_TEN_COT_CLB = {
    "name": {"ten clb", "ten cau lac bo", "ten", "clb", "cau lac bo"},
    "buoi": {"buoi", "buoi sinh hoat", "ngay", "thu"},
    "capacity": {"chi tieu", "so cho", "so luong", "chi tieu tong"},
    "reserve_capacity": {"suat uu tien", "chi tieu uu tien", "cho uu tien",
                         "suat du tru"},
    "reserve_group": {"nhom uu tien", "nhom du tru", "doi tuong uu tien"},
    "club_id": {"ma clb", "ma", "ma cau lac bo"},
}
_TEN_COT_HS = {
    "student_id": {"ma hs", "ma hoc sinh", "ma", "ma so", "ma so hoc sinh"},
    "name": {"ho ten", "ho va ten", "ten", "ten hoc sinh"},
    "reserve_group": {"nhom uu tien", "nhom du tru", "doi tuong uu tien"},
}
_MAU_NV = re.compile(r"^(?:nv|nguyen vong)\s*(\d+)$")
_MAU_DIEM = re.compile(r"^diem(?: nv| thi)?\s*(\d+)$")


def _ten_cot_clb(cfg=None) -> dict:
    """`_TEN_COT_CLB` nới thêm bằng nhãn của workspace (đã bỏ dấu). Tiêu đề cũ của
    trường học VẪN được nhận: chỉ THÊM, không bao giờ bớt."""
    ra = {k: set(v) for k, v in _TEN_COT_CLB.items()}
    chi = _bien_the(cfg, "slot")
    ra["name"] |= chi | {"ten " + x for x in chi}
    ra["club_id"] |= {"ma " + x for x in chi}
    ra["reserve_group"] |= _bien_the(cfg, "group")
    return ra


def _ten_cot_hs(cfg=None) -> dict:
    ra = {k: set(v) for k, v in _TEN_COT_HS.items()}
    nguoi = _bien_the(cfg, "person")
    ra["student_id"] |= {"ma " + x for x in nguoi}
    ra["name"] |= {"ten " + x for x in nguoi}
    ra["reserve_group"] |= _bien_the(cfg, "group")
    return ra


def _mau_diem(cfg=None):
    """`_MAU_DIEM` nới thêm bằng nhãn điểm: 'Điểm 1', 'Score 1', '<nhãn> thi 1'…"""
    cac = sorted({"diem"} | _bien_the(cfg, "score"), key=len, reverse=True)
    return re.compile(r"^(?:%s)(?: nv| thi)?\s*(\d+)$" % "|".join(re.escape(x) for x in cac))


def _tim_sheet(ten_cac_sheet, ten_chuan, *ten_khac):
    """Tìm sheet theo tên đã bỏ dấu: '1. CLB', '1 clb', 'CLB' đều khớp.

    `ten_khac`: các tên thay thế cũng nhận (nhãn của workspace). Tên chuẩn cũ vẫn
    luôn được nhận — sổ của trường học cũ nạp vào workspace nào cũng được."""
    mau = []
    for ten in (ten_chuan, *ten_khac):
        muc = bo_dau(ten)
        mau.append((muc, re.sub(r"^\d+ ", "", muc)))
    for ten in ten_cac_sheet:
        b = bo_dau(ten)
        b_ngan = re.sub(r"^\d+ ", "", b)
        if any(b == muc or b_ngan == muc_ngan for muc, muc_ngan in mau):
            return ten
    return None


def _cac_ten_sheet_clb(cfg=None) -> tuple:
    return tuple(_ten_sheet("1. " + x) for x in sorted(_ten_dai_ngan(cfg, "slot")))


def _cac_ten_sheet_hs(cfg=None) -> tuple:
    return tuple(_ten_sheet("2. " + x) for x in sorted(_ten_dai_ngan(cfg, "person")))


def _ten_dai_ngan(cfg, danh_tu: str) -> set:
    """Nhãn (chưa bỏ dấu) mà một sheet có thể mang: vi, en, dạng viết tắt."""
    nhan = _cfg(cfg)["nhan"]
    return {dang_chu(nhan, danh_tu, co, lang)
            for co in ("", "s") for lang in ("vi", "en")}


def la_so_nhap(ten_cac_sheet, cfg=None) -> bool:
    """Tệp có đủ hai sheet của sổ nhập không."""
    return bool(_tim_sheet(ten_cac_sheet, SHEET_CLB, *_cac_ten_sheet_clb(cfg))
                and _tim_sheet(ten_cac_sheet, SHEET_HS, *_cac_ten_sheet_hs(cfg)))


def _khop_cot(tieu_de, bang_ten):
    """{khoá: chỉ số cột} theo bảng tên. Cột đầu khớp được giữ."""
    vi_tri = {}
    for i, t in enumerate(tieu_de):
        b = bo_dau(t)
        for khoa, cac_ten in bang_ten.items():
            if b in cac_ten and khoa not in vi_tri:
                vi_tri[khoa] = i
                break
    return vi_tri


def _cac_dong(ws):
    """(số dòng Excel, [ô đã thành chuỗi]) — bỏ dòng trống hoàn toàn."""
    for so_dong, hang in enumerate(ws.iter_rows(values_only=True), start=1):
        o = [o_thanh_chu(v) for v in hang]
        if any(o):
            yield so_dong, o


# ---------------------------------------------------------------------------
# ĐỌC sổ nhập
# ---------------------------------------------------------------------------
def doc_so_nhap(wb, clb_da_co=None, ma_da_co=None, clb_cu=None, cfg=None) -> dict:
    """Đọc sổ nhập (openpyxl Workbook) thành dữ liệu thuần, KHÔNG ghi gì.

    Trả về {"clubs": [...], "students": [...], "loi": [...]}.
    `loi` khác rỗng nghĩa là sổ có lỗi phải sửa — phần mềm KHÔNG nạp gì cả.
    Nạp một nửa sổ còn tệ hơn không nạp: người dùng tưởng đã xong.

    clubs:    {club_id, name, capacity, reserve_capacity, reserve_group, buoi, dong}
    students: {student_id, name, reserve_group, dong,
               nv: [{club_id, thi: bool, diem: str}]}

    clb_da_co: {khoa_ten(tên): club_id} của các CLB đã có trong phần mềm.
    Dòng CLB bỏ trống Mã CLB mà tên trùng một CLB đã có thì dùng mã của CLB
    đó — nạp lại sổ không đẻ ra CLB thứ hai.
    ma_da_co:  {club_id: tên} của mọi CLB đã có. Mã TỰ TẠO trùng (bỏ hoa/thường)
    mã một CLB đã có (mà tên khác) là lỗi: nạp vào sẽ đè lên CLB đó.
    clb_cu:    {club_id: {buoi, reserve_capacity, reserve_group}} của CLB đã có.
    Sheet CLB THIẾU HẲN cột Buổi / Suất ưu tiên / Nhóm ưu tiên thì CLB đã có
    giữ giá trị cũ (cột vắng mặt = "không biết"; cột có mà ô trống = "không có").

    cfg: cấu hình workspace (dict thô, xem `_cfg`). Có nó thì sổ có thể dùng tên sheet
    và tiêu đề cột theo nhãn của workspace — và vẫn nhận tiêu đề CŨ của trường học.
    Trần nguyện vọng / số CLB thi mỗi buổi lấy từ `rules`; `max_tests` None = không
    giới hạn. Điểm theo từng người (`score_scope = per_person`) thì đọc MỘT cột điểm
    chung và gán cho mọi nguyện vọng của người đó (xem `_doc_sheet_hs`).
    """
    loi: list = []
    ten_cac_sheet = list(wb.sheetnames)
    ten_clb = _tim_sheet(ten_cac_sheet, SHEET_CLB, *_cac_ten_sheet_clb(cfg))
    ten_hs = _tim_sheet(ten_cac_sheet, SHEET_HS, *_cac_ten_sheet_hs(cfg))
    # Báo lỗi bằng tên sheet CHUẨN của workspace (mặc định: "1. CLB" / "2. Học sinh").
    chuan_clb, chuan_hs = ten_sheet_clb(cfg), ten_sheet_hs(cfg)
    for ten, chuan in ((ten_clb, chuan_clb), (ten_hs, chuan_hs)):
        if not ten:
            loi.append(err("so_nhap_thieu_sheet", sheet=chuan))
    if loi:
        return {"clubs": [], "students": [], "loi": loi}

    clubs = _doc_sheet_clb(wb[ten_clb], loi, clb_da_co or {}, ma_da_co or {}, clb_cu or {},
                           cfg, chuan_clb)
    students = _doc_sheet_hs(wb[ten_hs], clubs, loi, cfg, chuan_hs)
    return {"clubs": [c for c in clubs if not c.get("hong")],
            "students": students, "loi": loi}


def _doc_sheet_clb(ws, loi, clb_da_co, ma_da_co, clb_cu, cfg=None, ten_sheet=SHEET_CLB) -> list:
    dong_iter = _cac_dong(ws)
    dau = next(dong_iter, None)
    if dau is None:
        loi.append(err("so_nhap_khong_co_clb", sheet=ten_sheet))
        return []
    _, tieu_de = dau
    cot = _khop_cot(tieu_de, _ten_cot_clb(cfg))
    for khoa, nhan in (("name", "Tên CLB"), ("capacity", "Chỉ tiêu")):
        if khoa not in cot:
            loi.append(err("so_nhap_thieu_cot", sheet=ten_sheet, cot=nhan))
    if loi:
        return []

    def lay(o, khoa):
        i = cot.get(khoa)
        return o[i].strip() if i is not None and i < len(o) else ""

    tho = []
    for so_dong, o in dong_iter:
        ten = lay(o, "name")
        if not ten and not lay(o, "club_id"):
            continue        # dòng chỉ có buổi/chỉ tiêu lạc: coi như trống
        tho.append((so_dong, o, ten))

    clubs, ten_da_gap, ma_da_gap = [], {}, {}
    for so_dong, o, ten in tho:
        if not ten:
            loi.append(err("so_nhap_clb_thieu_ten", sheet=ten_sheet, dong=so_dong))
            continue
        k_ten = khoa_ten(ten)
        if k_ten in ten_da_gap:
            loi.append(err("so_nhap_clb_trung_ten", sheet=ten_sheet, dong=so_dong,
                           dong_truoc=ten_da_gap[k_ten], ten=ten))
            continue
        ma = lay(o, "club_id")
        tu_sinh = False
        if not ma:
            # Mã lấy lại của CLB cùng tên đã có là mã THẬT trong phần mềm,
            # so như mã người dùng điền (phân biệt hoa/thường). Chỉ mã vừa
            # tạo từ tên mới là "tự sinh".
            ma = clb_da_co.get(k_ten)
            if ma is None:
                tu_sinh = True
                ma = tao_ma_clb(ten)
                # Mã tự tạo trùng mã một CLB KHÁC đã có trong phần mềm: nạp vào
                # là đổi tên, chỉ tiêu, buổi của CLB đó và chuyển cả nguyện vọng
                # của học sinh sang — không một cảnh báo nào. Bắt điền Mã CLB.
                # Gợi ý MÃ THẬT của CLB đó (CLB_TIN, không phải clb_tin vừa
                # tạo): mã phân biệt hoa/thường, điền clb_tin là tạo CLB mới.
                ma_cu = ma if ma in ma_da_co else next(
                    (k for k in ma_da_co if k.lower() == ma.lower()), None)
                if ma_cu is not None:
                    loi.append(err("so_nhap_ma_tu_sinh_trung_clb_da_co", sheet=ten_sheet,
                                   dong=so_dong, ten=ten, ma=ma, ma_cu=ma_cu,
                                   ten_cu=ma_da_co[ma_cu]))
                    continue
        # Phần mềm phân biệt hoa/thường ở mã (clb_a và CLB_A là hai CLB), nên
        # hai mã người dùng tự điền chỉ khác hoa/thường KHÔNG trùng — sổ xuất
        # từ một CSDL như thế phải nạp lại được. Mã TỰ TẠO thì so không phân
        # biệt hoa/thường: hàm nạp khớp mã lệch hoa/thường về mã đã có.
        trung = ma_da_gap.get(ma) or next(
            (v for k, v in ma_da_gap.items()
             if k.lower() == ma.lower() and (tu_sinh or v[1])), None)
        if trung:
            dong_truoc, truoc_tu_sinh = trung
            # Mã tự sinh đụng nhau: báo để người dùng điền Mã CLB, đừng tự
            # đánh số — số phụ thuộc thứ tự dòng.
            ma_loi = ("so_nhap_ma_tu_sinh_trung" if (tu_sinh or truoc_tu_sinh)
                      else "so_nhap_clb_trung_ma")
            loi.append(err(ma_loi, sheet=ten_sheet, dong=so_dong,
                           dong_truoc=dong_truoc, ma=ma, ten=ten))
            continue
        ten_da_gap[k_ten] = so_dong
        ma_da_gap[ma] = (so_dong, tu_sinh)

        cu = clb_cu.get(ma, {})

        def lay_hoac_cu(khoa, mac_dinh, o=o, cu=cu):
            # Cột VẮNG MẶT: giữ giá trị của CLB đã có (mới thì mặc định).
            # Không thế thì một sheet chỉ có Tên CLB + Chỉ tiêu xoá buổi và
            # suất ưu tiên của mọi CLB — trường nhiều buổi thành một buổi.
            return lay(o, khoa) if khoa in cot else cu.get(khoa, mac_dinh)

        chi_tieu = lay(o, "capacity")
        uu_tien = str(lay_hoac_cu("reserve_capacity", 0) or "0")
        try:
            f_chi_tieu, f_uu_tien = float(chi_tieu), float(uu_tien)
            # "inf", "1e999", "nan" đọc được thành float nhưng không thành
            # chỉ tiêu: int(inf) ném OverflowError, nan so sánh luôn sai.
            hop_le = (math.isfinite(f_chi_tieu) and math.isfinite(f_uu_tien)
                      and f_chi_tieu.is_integer() and f_uu_tien.is_integer())
            n_chi_tieu = int(f_chi_tieu) if hop_le else 0
            n_uu_tien = int(f_uu_tien) if hop_le else 0
            hop_le = hop_le and n_chi_tieu > 0 and 0 <= n_uu_tien <= n_chi_tieu
        except (ValueError, OverflowError):
            hop_le = False
        if not hop_le:
            loi.append(err("so_nhap_chi_tieu_sai", sheet=ten_sheet, dong=so_dong,
                           ten=ten, chi_tieu=chi_tieu or "0", uu_tien=uu_tien))
            # Vẫn giữ tên để tra NV: một lỗi chỉ tiêu không được kéo theo
            # một loạt lỗi "không có CLB" ở sheet học sinh.
            clubs.append({"club_id": ma, "name": ten, "hong": True})
            continue
        clubs.append({
            "club_id": ma, "name": ten, "capacity": n_chi_tieu,
            "reserve_capacity": n_uu_tien,
            "reserve_group": lay_hoac_cu("reserve_group", "") or "",
            "buoi": ma_buoi(lay(o, "buoi")) if "buoi" in cot else (cu.get("buoi") or ""),
            "dong": so_dong,
        })

    if not any(not c.get("hong") for c in clubs) and not loi:
        loi.append(err("so_nhap_khong_co_clb", sheet=ten_sheet))
    return clubs


def _mau_diem_w(cfg=None):
    """Tiêu đề cột điểm Wharton, đã bỏ dấu: 'Điểm W 1', 'diem w1', '<nhãn điểm> W 1'…

    Cố ý không khớp `_mau_diem`: sau "diem" mẫu kia chỉ nhận " nv" / " thi" rồi số, còn ở đây
    bắt buộc có chữ `w`. Nhận ở MỌI workspace — bật hay tắt Wharton là việc của bước nạp.
    """
    cac = sorted({"diem"} | _bien_the(cfg, "score"), key=len, reverse=True)
    return re.compile(r"^(?:%s)\s*w\s*(\d+)$" % "|".join(re.escape(x) for x in cac))


def _doc_sheet_hs(ws, clubs, loi, cfg=None, ten_sheet=SHEET_HS) -> list:
    dong_iter = _cac_dong(ws)
    dau = next(dong_iter, None)
    if dau is None:
        return []           # chưa có học sinh: nạp riêng danh sách CLB
    _, tieu_de = dau
    cot = _khop_cot(tieu_de, _ten_cot_hs(cfg))
    cau_hinh = _cfg(cfg)
    ca_nhan = cau_hinh["per_person"]
    mau_diem = _mau_diem(cfg)
    mau_diem_w = _mau_diem_w(cfg)
    nhan_diem_ca_nhan = {"diem"} | _bien_the(cfg, "score")
    cot_nv, cot_diem, cot_diem_cn = {}, {}, None
    cot_w: dict = {}                 # k -> chỉ số cột "Điểm W k" (điểm Wharton, mục A13)
    cot_sai_che_do: list = []
    for i, t in enumerate(tieu_de):
        b = bo_dau(t)
        m = _MAU_NV.match(b)
        if m:
            cot_nv.setdefault(int(m.group(1)), i)
            continue
        m = mau_diem_w.match(b)
        if m:
            if ca_nhan:
                cot_sai_che_do.append(i)    # điểm Wharton cần điểm theo từng CLB
            else:
                cot_w.setdefault(int(m.group(1)), i)
            continue
        # Điểm theo người: MỘT cột tên đúng nhãn điểm ("Điểm"), không kèm số.
        if ca_nhan and cot_diem_cn is None and b in nhan_diem_ca_nhan:
            cot_diem_cn = i
            continue
        m = mau_diem.match(b)
        if m and not ca_nhan:
            cot_diem.setdefault(int(m.group(1)), i)
        elif m or (not ca_nhan and b in nhan_diem_ca_nhan):
            # Cột điểm KHÔNG đúng kiểu chấm của workspace: "Điểm 1…" ở workspace chấm theo
            # người, hoặc một cột "Điểm" đơn ở workspace chấm theo CLB. Không dùng được; có dữ
            # liệu trong đó thì phải báo (xem vòng đọc dòng), không lặng lẽ bỏ.
            cot_sai_che_do.append(i)
    if "student_id" not in cot:
        loi.append(err("so_nhap_thieu_cot", sheet=ten_sheet, cot="Mã HS"))
    if not cot_nv:
        loi.append(err("so_nhap_thieu_cot", sheet=ten_sheet, cot="NV1"))
    if "student_id" not in cot or not cot_nv:
        return []

    # Ô NV nhận TÊN CLB (danh sách thả xuống) hoặc MÃ CLB. Khớp đúng tên
    # (bỏ hoa/thường) trước; gõ thiếu dấu thì chỉ nhận khi ra ĐÚNG MỘT CLB —
    # không bao giờ đoán giữa "Bóng đá (nam)" và "Bóng đá (nữ)".
    # Thứ tự: tên đúng TỪNG KÝ TỰ (danh sách thả xuống và sổ xuất ra đều ghi
    # tên), rồi mã đúng từng ký tự (clb_a và CLB_A là hai CLB khác nhau), rồi
    # mới bỏ hoa/thường. Khớp mã bỏ hoa/thường chỉ khi ra đúng một CLB.
    dung_ten = {c["name"]: c["club_id"] for c in clubs}
    dung_ma = {c["club_id"]: c["club_id"] for c in clubs}
    ma_bo_hoa: dict = {}
    for c in clubs:
        ma_bo_hoa.setdefault(khoa_ten(c["club_id"]), set()).add(c["club_id"])
    tra = {k: next(iter(v)) for k, v in ma_bo_hoa.items() if len(v) == 1}
    for c in clubs:
        tra[khoa_ten(c["name"])] = c["club_id"]
    # Khoá "gõ thiếu dấu" chỉ bỏ dấu, GIỮ ngoặc và ký hiệu: "Bóng đá (nữ)"
    # không được rơi vào "Bóng đá (nam)", "C#" không được rơi vào "C++".
    tra_long: dict = {}
    for c in clubs:
        for k in {khoa_long(c["name"]), khoa_long(c["club_id"])}:
            tra_long.setdefault(k, set()).add(c["club_id"])
    buoi_cua = {c["club_id"]: c.get("buoi", "") for c in clubs if not c.get("hong")}

    def tim_clb(gia_tri):
        ma = (dung_ten.get(gia_tri) or dung_ma.get(gia_tri)
              or tra.get(khoa_ten(gia_tri)))
        if ma is None:
            ung_vien = tra_long.get(khoa_long(gia_tri), set())
            ma = next(iter(ung_vien)) if len(ung_vien) == 1 else None
        return ma

    def lay(o, i):
        return o[i].strip() if i is not None and i < len(o) else ""

    students, ma_da_gap = [], {}
    for so_dong, o in dong_iter:
        sid = lay(o, cot["student_id"])
        if not sid:
            loi.append(err("so_nhap_thieu_ma_hs", sheet=ten_sheet, dong=so_dong))
            continue
        # Trùng ĐÚNG từng ký tự mới là trùng. "hs01" và "HS01" là hai học
        # sinh với phần mềm; hàm nạp vẫn cảnh báo cặp mã như thế.
        if sid in ma_da_gap:
            loi.append(err("so_nhap_hs_trung", sheet=ten_sheet, dong=so_dong,
                           dong_truoc=ma_da_gap[sid], student_id=sid))
            continue
        ma_da_gap[sid] = so_dong

        for i in cot_sai_che_do:
            if lay(o, i):
                loi.append(err("so_nhap_diem_sai_che_do", sheet=ten_sheet, dong=so_dong,
                               student_id=sid, cot=tieu_de[i]))
                break

        nv, da_chon = [], {}
        diem_w_mo_coi: list = []         # "Điểm W k" có chữ mà NV k trống
        # Điểm theo NGƯỜI: một ô cho cả dòng, kiểm một lần. Có điểm (hoặc chữ `thi`) =
        # người đó "đã thi" — và nó áp cho MỌI nguyện vọng của người đó.
        o_diem_ca_nhan, diem_ca_nhan_hong = "", False
        if cot_diem_cn is not None:
            o_diem_ca_nhan = lay(o, cot_diem_cn)
            if o_diem_ca_nhan and o_diem_ca_nhan.lower() != TU_DANH_DAU_THI:
                so = doc_diem(o_diem_ca_nhan)
                if so is None or so < 0:
                    loi.append(err("so_nhap_diem_ca_nhan_sai", sheet=ten_sheet, dong=so_dong,
                                   student_id=sid, gia_tri=o_diem_ca_nhan))
                    diem_ca_nhan_hong = True
        for k in sorted(set(cot_nv) | set(cot_diem) | set(cot_w)):
            o_nv = lay(o, cot_nv.get(k))
            o_diem = lay(o, cot_diem.get(k))
            o_w = lay(o, cot_w.get(k))
            if not o_nv:
                if o_diem:
                    loi.append(err("so_nhap_diem_khong_nv", sheet=ten_sheet,
                                   dong=so_dong, student_id=sid, k=k))
                elif o_w:
                    diem_w_mo_coi.append(str(tieu_de[cot_w[k]]).strip())
                continue
            ma = tim_clb(o_nv)
            if ma is None:
                loi.append(err("so_nhap_clb_khong_co", sheet=ten_sheet, dong=so_dong,
                               student_id=sid, k=k, gia_tri=o_nv))
                continue
            if ma in da_chon:
                loi.append(err("so_nhap_nv_trung", sheet=ten_sheet, dong=so_dong,
                               student_id=sid, k=k, k_truoc=da_chon[ma], gia_tri=o_nv))
                continue
            da_chon[ma] = k
            if cot_diem_cn is not None:
                # Điểm theo người KHÔNG thuộc nguyện vọng nào: nó nằm ở `diem_ca_nhan` của
                # người đó (ghi vào students.diem_ca_nhan, mở rộng ra các CLB lúc xếp).
                nv.append({"club_id": ma, "thi": False, "diem": ""})
                continue
            thi = bool(o_diem)
            if thi and o_diem.lower() != TU_DANH_DAU_THI:
                so = doc_diem(o_diem)
                if so is None or so < 0:
                    loi.append(err("so_nhap_diem_sai", sheet=ten_sheet, dong=so_dong,
                                   student_id=sid, k=k, gia_tri=o_diem))
                    continue
            diem = "" if (not thi or o_diem.lower() == TU_DANH_DAU_THI) else o_diem
            x = {"club_id": ma, "thi": thi, "diem": diem}
            if cot_w:
                # Điểm Wharton: chuỗi GỐC của ô, chưa kiểm. Ô không phải số nguyên >= 0 thì
                # đi tiếp xuống bước nạp CSV thành cảnh báo `csv_wp_khong_hop_le` (có đủ mã
                # học sinh và CLB), thay vì chặn cả sổ.
                x["diem_w"] = o_w
            nv.append(x)
        # Trần MỖI BUỔI: soát ngay ở bước đọc thử. Để tới lúc nạp thì hàm nạp
        # chỉ bỏ cả buổi của em kèm cảnh báo, còn nguyện vọng cũ của em vẫn
        # nằm trong CSDL — sổ "sẵn sàng" mà kết quả lại khác.
        #
        # Trần lấy từ cấu hình workspace (mặc định 10 và 5). `max_tests` None là không
        # giới hạn. Điểm theo người thì KHÔNG có "thi từng CLB" để mà đếm — mọi nguyện
        # vọng cùng chung một điểm — nên bỏ phép đếm thi.
        gioi_han = [("nv", cau_hinh["max_choices"], "so_nhap_qua_tran_nv")]
        if cau_hinh["max_tests"] is not None and not ca_nhan:
            gioi_han.append(("thi", cau_hinh["max_tests"], "so_nhap_qua_tran_thi"))
        for khoa_dem, tran, ma_loi in gioi_han:
            dem: dict = {}
            for x in nv:
                if khoa_dem == "thi" and not x["thi"]:
                    continue
                if x["club_id"] in buoi_cua:
                    b = buoi_cua[x["club_id"]]
                    dem[b] = dem.get(b, 0) + 1
            for b, n in dem.items():
                if n > tran:
                    loi.append(err(ma_loi, sheet=ten_sheet, dong=so_dong, student_id=sid,
                                   buoi=nhan_buoi(b) or "-", n=n, tran=tran))
        hs_moi = {
            "student_id": sid,
            "name": lay(o, cot.get("name")),
            # Cột Nhóm ưu tiên VẮNG MẶT -> None = "không biết", giữ nhóm cũ.
            # Cột có mà ô trống -> "" = em không thuộc nhóm nào.
            "reserve_group": (lay(o, cot["reserve_group"])
                              if "reserve_group" in cot else None),
            "nv": nv, "dong": so_dong,
            # Điểm theo người (chế độ per_person): chuỗi gốc của ô — số, chữ `thi` hay
            # trống. None = sổ không có cột điểm chung (điểm theo từng CLB, ở `nv`).
            "diem_ca_nhan": (None if cot_diem_cn is None or diem_ca_nhan_hong
                             else o_diem_ca_nhan),
        }
        if cot_w:
            hs_moi["diem_w_mo_coi"] = diem_w_mo_coi
            if not diem_w_mo_coi:
                del hs_moi["diem_w_mo_coi"]
        students.append(hs_moi)
    return students


# ---------------------------------------------------------------------------
# Sổ -> ba văn bản CSV mà ba hàm nạp cũ đã hiểu (và đã được test kỹ)
# ---------------------------------------------------------------------------
def _csv(dong) -> str:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(dong)
    return buf.getvalue()


def thanh_csv(du_lieu: dict) -> dict:
    """{"clubs": csv, "test_selection": csv | "", "preferences": csv | ""}.

    MỌI học sinh có trong sổ đều có mặt ở cả hai tệp học sinh, kể cả em
    không thi CLB nào: sổ là bản đầy đủ, nạp lại sổ phải xoá được lựa chọn
    thi cũ của em đã bỏ thi.
    """
    clubs = [["club_id", "name", "capacity", "reserve_capacity", "reserve_group", "buoi"]]
    for c in du_lieu["clubs"]:
        clubs.append([c["club_id"], c["name"], c["capacity"], c["reserve_capacity"],
                      c["reserve_group"], c["buoi"]])

    hs = du_lieu["students"]
    if not hs:
        return {"clubs": _csv(clubs), "test_selection": "", "preferences": ""}

    n_thi = max([sum(1 for x in s["nv"] if x["thi"]) for s in hs] + [1])
    n_nv = max([len(s["nv"]) for s in hs] + [1])
    # Sổ có cột "Điểm W k" thì tệp nguyện vọng có thêm `wp_k` đi cặp `pref_k` (mục A13).
    co_w = any("diem_w" in x for s in hs for x in s["nv"])
    thi = [["student_id", "name", "reserve_group"]
           + [c for k in range(1, n_thi + 1) for c in (f"test_club_{k}", f"score_{k}")]]
    nv = [["student_id", "name", "reserve_group"]
          + [f"pref_{k}" for k in range(1, n_nv + 1)]
          + ([f"wp_{k}" for k in range(1, n_nv + 1)] if co_w else [])]
    for s in hs:
        dau = [s["student_id"], s["name"], s["reserve_group"] or ""]
        o_thi = [v for x in s["nv"] if x["thi"] for v in (x["club_id"], x["diem"])]
        thi.append(dau + o_thi + [""] * (2 * n_thi - len(o_thi)))
        o_nv = [x["club_id"] for x in s["nv"]]
        o_w = [x.get("diem_w", "") for x in s["nv"]] if co_w else []
        nv.append(dau + o_nv + [""] * (n_nv - len(o_nv))
                  + (o_w + [""] * (n_nv - len(o_w)) if co_w else []))
    return {"clubs": _csv(clubs), "test_selection": _csv(thi), "preferences": _csv(nv)}


def diem_cua_nguoi(s: dict):
    """Điểm theo người của một dòng học sinh trong sổ: số, hoặc None (không có cột điểm
    chung, ô trống, hay chữ `thi` = đã thi mà chưa có điểm)."""
    o = (s.get("diem_ca_nhan") or "").strip()
    if not o or o.lower() == TU_DANH_DAU_THI:
        return None
    so = doc_diem(o)
    return None if so is None or so < 0 else so


def tom_tat(du_lieu: dict) -> dict:
    hs = du_lieu["students"]
    return {
        "n_clb": len(du_lieu["clubs"]),
        "n_hoc_sinh": len(hs),
        "n_buoi": len({c["buoi"] for c in du_lieu["clubs"]}),
        "n_nguyen_vong": sum(len(s["nv"]) for s in hs),
        "n_thi": sum(1 for s in hs for x in s["nv"] if x["thi"]),
        "n_diem": sum(1 for s in hs for x in s["nv"] if x["diem"])
        + sum(1 for s in hs if diem_cua_nguoi(s) is not None),
    }


# ---------------------------------------------------------------------------
# GHI sổ nhập (mẫu trống, mẫu có sẵn CLB, xuất dữ liệu đầu vào, skill)
# ---------------------------------------------------------------------------
HUONG_DAN = [
    "SỔ NHẬP CLB — một tệp duy nhất để nạp vào phần mềm",
    "",
    "Bước 1. Sheet \"1. CLB\": mỗi câu lạc bộ một dòng.",
    "        Tên CLB và Chỉ tiêu là bắt buộc. Buổi chọn trong danh sách thả xuống",
    "        (trường chỉ có một buổi thì để trống cả cột).",
    "        Suất ưu tiên / Nhóm ưu tiên: chỉ điền nếu CLB giữ chỗ cho một nhóm",
    "        học sinh (ví dụ nhóm chinh_sach). Mã CLB để trống, phần mềm tự tạo.",
    "",
    "Bước 2. Sheet \"2. Học sinh\": mỗi học sinh một dòng.",
    "        Mã HS là bắt buộc và không được trùng.",
    "        Nhóm ưu tiên: chỉ điền với học sinh thuộc nhóm đó.",
    "",
    "Bước 3. NV1, NV2, NV3…: chọn tên CLB trong danh sách thả xuống,",
    "        theo thứ tự em thích nhất trước. Không cần điền kín.",
    "        Trường nhiều buổi: cứ điền chung một danh sách — phần mềm tự chia",
    "        theo buổi của từng CLB.",
    "",
    "Bước 4. Điểm 1, Điểm 2…: điểm thi của CLB ngay bên trái.",
    "        Có điểm = em đã thi CLB đó. Để trống = không thi.",
    "        Thi rồi mà chưa có điểm: gõ chữ  thi  rồi chấm sau trong phần mềm.",
    "",
    "Bước 5. Lưu tệp (giữ định dạng .xlsx).",
    "",
    "Bước 6. Mở phần mềm → màn hình Vận hành → kéo tệp này vào ô nạp",
    "        → xem lại phần tóm tắt → bấm Nhập.",
    "",
    "Sổ có lỗi (CLB trùng tên, NV ghi tên CLB không có, điểm không phải số…)",
    "thì phần mềm KHÔNG nạp gì cả và chỉ rõ sheet, dòng cần sửa.",
    "Nạp lại sổ đã sửa là cập nhật — không tạo trùng.",
    "",
    "Ví dụ một dòng học sinh:",
    "  Mã HS   Họ tên          NV1          Điểm 1   NV2           Điểm 2",
    "  HS001   Nguyễn Văn An   CLB Tin học  9,5      CLB Bóng rổ",
    "  → An thích Tin học nhất và đã thi được 9,5; nguyện vọng 2 là Bóng rổ,",
    "    CLB không thi tuyển.",
]


def huong_dan(cfg=None) -> list:
    """Các dòng sheet "Hướng dẫn". `cfg=None` (hay mặc định trường học) cho ra đúng
    `HUONG_DAN` ở trên; workspace khác thì nhãn trong câu đổi theo, và điểm theo người
    có đoạn riêng. Các tiêu đề cột không đổi nhãn (Tên CLB, Chỉ tiêu, Mã HS, Mã CLB,
    Buổi) giữ nguyên chữ như trên sheet."""
    n = _cfg(cfg)
    nhan = n["nhan"]
    if not cfg or (ten_sheet_clb(cfg) == SHEET_CLB and ten_sheet_hs(cfg) == SHEET_HS
                   and nhan_nhom(cfg) == "Nhóm ưu tiên" and nhan_diem(cfg) == "Điểm"
                   and not n["per_person"] and not n["wharton"]
                   and dang_chu(nhan, "slot", "l", "vi") == "câu lạc bộ"
                   and dang_chu(nhan, "person", "l", "vi") == "học sinh"):
        return list(HUONG_DAN)

    def d(*a):
        return dang_chu(nhan, *a)

    clb, hs = ten_sheet_clb(cfg), ten_sheet_hs(cfg)
    slot_l, slot_u = d("slot", "l", "vi"), d("slot", "su", "vi")
    nguoi_l, nhom = d("person", "l", "vi"), nhan_nhom(cfg)
    diem, diem_l = nhan_diem(cfg), d("score", "l", "vi")
    ra = [
        "SỔ NHẬP %s — một tệp duy nhất để nạp vào phần mềm" % slot_u,
        "",
        "Bước 1. Sheet \"%s\": mỗi %s một dòng." % (clb, slot_l),
        "        Tên CLB và Chỉ tiêu là bắt buộc. Buổi chọn trong danh sách thả xuống",
        "        (chỉ có một buổi thì để trống cả cột).",
        "        Suất ưu tiên / %s: chỉ điền nếu %s giữ chỗ cho một nhóm" % (nhom, slot_l),
        "        %s (ví dụ nhóm chinh_sach). Mã CLB để trống, phần mềm tự tạo." % nguoi_l,
        "",
        "Bước 2. Sheet \"%s\": mỗi %s một dòng." % (hs, nguoi_l),
        "        Mã HS là bắt buộc và không được trùng.",
        "        %s: chỉ điền với %s thuộc nhóm đó." % (nhom, nguoi_l),
        "",
        "Bước 3. NV1, NV2, NV3…: chọn tên %s trong danh sách thả xuống," % slot_l,
        "        theo thứ tự thích nhất trước. Không cần điền kín.",
        "        Nhiều buổi: cứ điền chung một danh sách — phần mềm tự chia",
        "        theo buổi của từng %s." % slot_l,
        "",
    ]
    if n["per_person"]:
        ra += [
            "Bước 4. Cột \"%s\" (đứng sau cột %s): %s của cả người đó, MỘT ô cho cả dòng." % (diem, nhom, diem_l),
            "        Có %s = đã thi, và %s ấy áp cho mọi nguyện vọng của dòng. Để trống = không thi." % (diem_l, diem_l),
            "        Thi rồi mà chưa có %s: gõ chữ  thi  rồi chấm sau trong phần mềm." % diem_l,
        ]
        vd = ["  Mã HS   Họ tên          %s   NV1          NV2" % diem,
              "  HS001   Nguyễn Văn An   9,5      Tin học      Bóng rổ",
              "  → An có %s 9,5 cho cả hai nguyện vọng: Tin học rồi Bóng rổ." % diem_l]
    else:
        ra += [
            "Bước 4. %s 1, %s 2…: %s của %s ngay bên trái." % (diem, diem, diem_l, slot_l),
            "        Có %s = đã thi %s đó. Để trống = không thi." % (diem_l, slot_l),
            "        Thi rồi mà chưa có %s: gõ chữ  thi  rồi chấm sau trong phần mềm." % diem_l,
        ]
        vd = ["  Mã HS   Họ tên          NV1          %s 1   NV2           %s 2" % (diem, diem),
              "  HS001   Nguyễn Văn An   Tin học      9,5      Bóng rổ",
              "  → Nguyện vọng 1 là Tin học, đã thi được 9,5; nguyện vọng 2 là Bóng rổ,",
              "    không thi tuyển."]
        if n["wharton"]:
            ra += [
                "        %s W 1, %s W 2…: điểm Wharton, em tự chia cho từng nguyện vọng." % (diem, diem),
                "        Mỗi %s có HAI quỹ, mỗi quỹ đúng 100 điểm cho MỖI BUỔI:" % nguoi_l,
                "        quỹ 1 chia cho các %s em có thi (có %s), chỉ dùng để phá hoà khi bằng %s;"
                % (slot_l, diem_l, diem_l),
                "        quỹ 2 chia cho các %s em không thi, quyết định thứ tự giữa các %s không thi."
                % (slot_l, nguoi_l),
                "        Số nguyên không âm; ô trống tính là 0. Quỹ nào chỉ có một %s thì điền 100."
                % slot_l,
            ]
            vd = ["  Mã HS   Họ tên          NV1       %s 1   %s W 1   NV2        %s 2   %s W 2"
                  % (diem, diem, diem, diem),
                  "  HS001   Nguyễn Văn An   Tin học   9,5      100        Bóng rổ            100",
                  "  → Tin học có thi: 100 điểm quỹ 1 dồn vào đó; Bóng rổ không thi: 100 điểm quỹ 2."]
    ra += [
        "",
        "Bước 5. Lưu tệp (giữ định dạng .xlsx).",
        "",
        "Bước 6. Mở phần mềm → màn hình Vận hành → kéo tệp này vào ô nạp",
        "        → xem lại phần tóm tắt → bấm Nhập.",
        "",
        "Sổ có lỗi (%s trùng tên, NV ghi tên %s không có, %s không phải số…)" % (slot_l, slot_l, diem_l),
        "thì phần mềm KHÔNG nạp gì cả và chỉ rõ sheet, dòng cần sửa.",
        "Nạp lại sổ đã sửa là cập nhật — không tạo trùng.",
        "",
        "Ví dụ một dòng:",
    ] + vd
    return ra


def ten_khong_trung(clubs) -> int:
    """Đổi tên CLB (tại chỗ) để không hai CLB nào trùng `khoa_ten`. Trả số tên đã đổi.

    Sổ chọn CLB theo TÊN, nên tên phải riêng. Dữ liệu từ nơi khác thì không
    chắc: trường mở "CLB Cờ vua" cả Thứ 2 lẫn Thứ 5, hay CSDL có "Toán" và
    "toán". CLB gặp đầu tiên giữ tên; CLB sau thêm buổi vào tên ("CLB Cờ vua
    (Thứ 5)"), cùng buổi thì thêm mã CLB. Tên trống lấy mã CLB.
    """
    da_dung, n_doi = set(), 0
    for c in clubs:
        c["name"] = (c.get("name") or "").strip() or c.get("club_id") or ""
    for c in clubs:
        goc = c["name"]
        if khoa_ten(goc) not in da_dung:
            da_dung.add(khoa_ten(goc))
            continue
        ung_vien = [nhan_buoi(c.get("buoi") or ""), c.get("club_id") or ""]
        ten = next((f"{goc} ({x})" for x in ung_vien
                    if x and khoa_ten(f"{goc} ({x})") not in da_dung), None)
        k = 2
        while ten is None or khoa_ten(ten) in da_dung:
            ten, k = f"{goc} ({k})", k + 1
        c["name"] = ten
        da_dung.add(khoa_ten(ten))
        n_doi += 1
    return n_doi


def ghi_so_nhap(duong_dan_hoac_tep, clubs=(), students=(), so_nv=None, co_nhom=True,
                cfg=None):
    """Ghi sổ nhập ra tệp .xlsx (đường dẫn hoặc tệp nhị phân đang mở).

    clubs:    dict có name, capacity, reserve_capacity, reserve_group, buoi, club_id
    students: dict có student_id, name, reserve_group,
              nv: [{club_id, thi, diem}] (diem: số, chuỗi, hoặc '')
    so_nv:    số cặp NV/Điểm; mặc định nới theo dữ liệu, tối thiểu SO_NV_MAC_DINH.
              Có `cfg` với trần nguyện vọng dưới 10 thì mặc định chỉ bằng đúng trần (nhân
              số buổi) — cột nào cũng điền được, không cột thừa.
    co_nhom:  False thì bỏ hẳn cột Nhóm ưu tiên ở sheet học sinh. Dùng cho sổ
              sinh từ biểu mẫu: biểu mẫu không hỏi nhóm, và cột VẮNG MẶT nghĩa
              là phần mềm giữ nhóm đã gán; cột có mà ô trống là BỎ nhóm.
    cfg:      cấu hình workspace (dict thô, xem `_cfg`; KHÔNG import cau_hinh_ws).
              None -> đúng sổ như trước khi có workspace. Có cfg thì:
                * tên sheet "1. <chỗ xếp>" / "2. <người>" theo nhãn;
                * số cột NV theo `rules.max_choices`;
                * điểm theo CHỖ XẾP (per_slot): cột "<điểm> n" cạnh mỗi NV như cũ;
                  điểm theo NGƯỜI (per_person): MỘT cột "<điểm>" sau cột nhóm;
                * tiêu đề cột nhóm = nhãn của nhóm ưu tiên.
              Cấu hình của trường học mặc định cho ra sổ GIỐNG HỆT cfg=None.
    """
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    # Bản sao: đổi tên cho khỏi trùng mà không đụng dữ liệu của bên gọi.
    clubs, students = [dict(c) for c in clubs], list(students)
    ten_khong_trung(clubs)
    so_buoi = len({c.get("buoi") or "" for c in clubs}) or 1
    n_cfg = _cfg(cfg)
    ca_nhan = n_cfg["per_person"]
    max_choices = n_cfg["max_choices"] if cfg else 0
    dai_nhat = [len(s.get("nv") or []) for s in students]
    if so_nv:
        pass
    elif cfg and max_choices < TRAN_NV_MOI_BUOI:
        # Trần thấp (vd 3): chỉ đúng bằng số được xếp mỗi buổi, không cột thừa.
        so_nv = max([max_choices * so_buoi] + dai_nhat)
    else:
        so_nv = max([max(SO_NV_MAC_DINH, max_choices), 2 * so_buoi] + dai_nhat)
    sheet_clb, sheet_hs = ten_sheet_clb(cfg), ten_sheet_hs(cfg)
    ten_diem = nhan_diem(cfg)

    NEN_TIEU_DE = PatternFill("solid", fgColor="1F3A5F")
    NEN_NHAP = PatternFill("solid", fgColor="FFF8DC")
    NEN_DIEM = PatternFill("solid", fgColor="EAF4EA")
    NEN_DIEM_W = PatternFill("solid", fgColor="E8EEF8")
    CHU_TIEU_DE = Font(bold=True, color="FFFFFF", size=11)
    VIEN = Border(bottom=Side(style="thin", color="D0D0D0"),
                  right=Side(style="thin", color="D0D0D0"))
    GIUA = Alignment(horizontal="center", vertical="center", wrap_text=True)

    wb = Workbook()

    # ---- 1. CLB ---------------------------------------------------------
    ws = wb.active
    ws.title = sheet_clb
    ws.append(cot_clb(cfg))
    for c in clubs:
        ws.append([c.get("name", ""), nhan_buoi(c.get("buoi") or ""),
                   c.get("capacity", ""), c.get("reserve_capacity") or None,
                   c.get("reserve_group") or None, c.get("club_id") or None])
    so_dong_clb = max(len(clubs) + 1 + 20, SO_DONG_CLB_TRONG)
    for i, rong in enumerate([30, 12, 10, 13, 16, 18], start=1):
        ws.column_dimensions[get_column_letter(i)].width = rong
    for o in ws[1]:
        o.fill, o.font, o.alignment = NEN_TIEU_DE, CHU_TIEU_DE, GIUA
    ws.row_dimensions[1].height = 30
    for r in range(2, so_dong_clb + 1):
        for col in range(1, 7):
            o = ws.cell(row=r, column=col)
            o.fill, o.border = NEN_NHAP, VIEN
    ws.freeze_panes = "A2"

    dv_buoi = DataValidation(
        type="list", formula1='"' + ",".join(n for n, _ in NHAN_BUOI) + '"',
        allow_blank=True, showErrorMessage=False)
    dv_buoi.add(f"B2:B{so_dong_clb}")
    dv_chi_tieu = DataValidation(
        type="whole", operator="greaterThan", formula1="0", allow_blank=True,
        showErrorMessage=True, errorTitle="Chỉ tiêu",
        error="Chỉ tiêu phải là số nguyên lớn hơn 0.")
    dv_chi_tieu.add(f"C2:C{so_dong_clb}")
    dv_uu_tien = DataValidation(
        type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
        showErrorMessage=True, errorTitle="Suất ưu tiên",
        error="Suất ưu tiên là số nguyên, không lớn hơn Chỉ tiêu.")
    dv_uu_tien.add(f"D2:D{so_dong_clb}")
    for dv in (dv_buoi, dv_chi_tieu, dv_uu_tien):
        ws.add_data_validation(dv)
    ws.conditional_formatting.add(
        f"A2:A{so_dong_clb}",
        FormulaRule(formula=[f'AND(A2<>"",COUNTIF($A$2:$A${so_dong_clb},A2)>1)'],
                    fill=PatternFill("solid", fgColor="F4B6B6")))

    # ---- 2. Học sinh ----------------------------------------------------
    wh = wb.create_sheet(sheet_hs)
    cot_dau = cot_hs_dau(cfg) if co_nhom else cot_hs_dau(cfg)[:2]
    if ca_nhan:
        cot_dau = cot_dau + [ten_diem]        # MỘT cột điểm chung, ngay sau cột nhóm
    nv1 = len(cot_dau) + 1                    # số thứ tự cột NV1 (tính từ 1)
    co_w = n_cfg["wharton"]                   # thêm cột "Điểm W k" (điểm Wharton, mục A13)
    buoc = 1 if ca_nhan else (3 if co_w else 2)   # khoảng cách giữa hai cột NV liên tiếp
    if ca_nhan:
        tieu_de = cot_dau + [f"NV{k}" for k in range(1, so_nv + 1)]
    elif co_w:
        tieu_de = cot_dau + [c for k in range(1, so_nv + 1)
                             for c in (f"NV{k}", f"{ten_diem} {k}", f"{ten_diem} W {k}")]
    else:
        tieu_de = cot_dau + [c for k in range(1, so_nv + 1)
                             for c in (f"NV{k}", f"{ten_diem} {k}")]
    wh.append(tieu_de)

    def diem_w_o(x):
        """Ô điểm Wharton của một nguyện vọng: số nguyên, chuỗi gốc (để người nhập thấy ô sai),
        hay trống."""
        w = x.get("diem_w")
        if w in (None, ""):
            return None
        if isinstance(w, str) and w.strip().isdigit():
            return int(w.strip())
        return w

    def diem_o(x):
        """Ô điểm của một nguyện vọng: số, chữ thi, hay trống."""
        diem = x.get("diem")
        if diem in (None, ""):
            return TU_DANH_DAU_THI if x.get("thi") else None
        if isinstance(diem, str):
            so = doc_diem(diem)
            return (int(so) if so.is_integer() else so) if so is not None else diem
        if isinstance(diem, float) and diem.is_integer():
            return int(diem)
        return diem

    for s in students:
        hang = [s.get("student_id", ""), s.get("name", "")]
        if co_nhom:
            hang.append(s.get("reserve_group") or None)
        if ca_nhan:
            # Điểm theo người: lấy `diem_ca_nhan` nếu có, không thì điểm đầu tiên của
            # các nguyện vọng (cả dòng chung một điểm).
            if s.get("diem_ca_nhan") is not None:
                hang.append(diem_o({"diem": s["diem_ca_nhan"], "thi": bool(s["diem_ca_nhan"])}))
            else:
                co = next((x for x in (s.get("nv") or []) if x.get("diem") not in (None, "")
                           or x.get("thi")), None)
                hang.append(diem_o(co) if co else None)
            for x in (s.get("nv") or [])[:so_nv]:
                hang.append(next((c["name"] for c in clubs if c.get("club_id") == x["club_id"]),
                                 x["club_id"]))
            wh.append(hang)
            continue
        for x in (s.get("nv") or [])[:so_nv]:
            ten = next((c["name"] for c in clubs if c.get("club_id") == x["club_id"]),
                       x["club_id"])
            hang += [ten, diem_o(x)] + ([diem_w_o(x)] if co_w else [])
        wh.append(hang)
    so_dong_hs = max(len(students) + 1 + 200, SO_DONG_HS_TRONG)
    cot_cuoi = len(tieu_de)
    wh.column_dimensions["A"].width = 11
    wh.column_dimensions["B"].width = 24
    if co_nhom:
        wh.column_dimensions["C"].width = 13
    if ca_nhan:
        wh.column_dimensions[get_column_letter(nv1 - 1)].width = 10   # cột điểm chung
    for col in range(nv1, cot_cuoi + 1):
        wh.column_dimensions[get_column_letter(col)].width = (
            22 if (ca_nhan or (col - nv1) % buoc == 0) else 8)
    for o in wh[1]:
        o.fill, o.font, o.alignment = NEN_TIEU_DE, CHU_TIEU_DE, GIUA
    wh.row_dimensions[1].height = 30
    for r in range(2, so_dong_hs + 1):
        for col in range(1, cot_cuoi + 1):
            o = wh.cell(row=r, column=col)
            la_cot_diem = (col == nv1 - 1) if ca_nhan else (col >= nv1 and (col - nv1) % buoc == 1)
            la_cot_w = co_w and col >= nv1 and (col - nv1) % buoc == 2
            o.fill = NEN_DIEM_W if la_cot_w else (NEN_DIEM if la_cot_diem else NEN_NHAP)
            o.border = VIEN
        # Mã HS là CHỮ: để Excel tự nhận thì 0012345 thành 12345.
        wh.cell(row=r, column=1).number_format = "@"
    wh.freeze_panes = f"{get_column_letter(nv1)}2"

    # Danh sách thả xuống: tên CLB lấy THẲNG từ sheet 1, nên thêm CLB ở
    # sheet 1 là danh sách cập nhật ngay, không phải sinh lại mẫu.
    ten_sheet_trong_cong_thuc = sheet_clb.replace("'", "''")
    dv_nv = DataValidation(
        type="list", formula1=f"'{ten_sheet_trong_cong_thuc}'!$A$2:$A${so_dong_clb}",
        allow_blank=True, showErrorMessage=True, errorStyle="warning",
        errorTitle="Tên CLB",
        error=f"Hãy chọn tên {dang_chu(n_cfg['nhan'], 'slot', 'sl', 'vi')} trong danh sách "
              f"(sheet {sheet_clb}).")
    wh.add_data_validation(dv_nv)
    diem_l = dang_chu(n_cfg["nhan"], "score", "l", "vi")

    def them_kiem_diem(c_d, cuoi):
        # Công thức tham chiếu CHÍNH cột điểm đó, nên mỗi cột một quy tắc.
        dv = DataValidation(
            type="custom", allow_blank=True, showErrorMessage=True,
            errorTitle=ten_diem,
            error=f"{ten_diem} là một số (vd 8,5) hoặc chữ  thi  nếu chưa có {diem_l}.",
            formula1=f'OR(ISNUMBER({c_d}2),LOWER({c_d}2)="thi")')
        dv.add(f"{c_d}2:{c_d}{cuoi}")
        wh.add_data_validation(dv)

    if ca_nhan:
        them_kiem_diem(get_column_letter(nv1 - 1), so_dong_hs)
    for k in range(so_nv):
        c_nv = get_column_letter(nv1 + buoc * k)
        dv_nv.add(f"{c_nv}2:{c_nv}{so_dong_hs}")
        if not ca_nhan:
            them_kiem_diem(get_column_letter(nv1 + 1 + buoc * k), so_dong_hs)
        if co_w:
            c_w = get_column_letter(nv1 + 2 + buoc * k)
            dv_w = DataValidation(
                type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
                showErrorMessage=True, errorTitle=f"{ten_diem} W",
                error="Điểm Wharton là số nguyên từ 0 trở lên (mỗi quỹ cộng đúng 100).")
            dv_w.add(f"{c_w}2:{c_w}{so_dong_hs}")
            wh.add_data_validation(dv_w)
    # Cùng một CLB chọn hai lần trên một dòng -> tô đỏ.
    for k in range(so_nv):
        c = get_column_letter(nv1 + buoc * k)
        dem = "+".join(f'(${get_column_letter(nv1 + buoc * j)}2={c}2)' for j in range(so_nv))
        wh.conditional_formatting.add(
            f"{c}2:{c}{so_dong_hs}",
            FormulaRule(formula=[f'AND({c}2<>"",({dem})>1)'],
                        fill=PatternFill("solid", fgColor="F4B6B6")))
    wh.conditional_formatting.add(
        f"A2:A{so_dong_hs}",
        FormulaRule(formula=[f'AND(A2<>"",COUNTIF($A$2:$A${so_dong_hs},A2)>1)'],
                    fill=PatternFill("solid", fgColor="F4B6B6")))

    # ---- Hướng dẫn ------------------------------------------------------
    hd = wb.create_sheet(SHEET_HD)
    hd.column_dimensions["A"].width = 90
    for i, dong in enumerate(huong_dan(cfg), start=1):
        o = hd.cell(row=i, column=1, value=dong)
        if i == 1:
            o.font = Font(bold=True, size=14, color="1F3A5F")
        elif dong.startswith("Bước"):
            o.font = Font(bold=True)

    # Tên bắt đầu bằng "=" (vd học sinh tên "=1+1") phải là CHỮ, không thành
    # công thức Excel — vừa sai dữ liệu, vừa là lối chèn công thức độc.
    for trang in (ws, wh):
        for hang in trang.iter_rows(min_row=2, max_row=trang.max_row):
            for o in hang:
                if isinstance(o.value, str) and o.value.startswith("="):
                    o.data_type = "s"

    wb.active = 0
    wb.save(duong_dan_hoac_tep)


def tu_csv(clubs_rows, thi_rows, nv_rows):
    """Dữ liệu ba tệp CSV cũ (dict từ csv.DictReader) -> (clubs, students)
    cho `ghi_so_nhap`. Dùng để sinh sổ ví dụ từ các bộ CSV mẫu đã có, và để
    chuyển bộ ba tệp cũ của một trường sang sổ nhập.

    Nguyện vọng theo buổi (`thu_2_pref_1`…) được nối theo thứ tự buổi —
    đúng cách phần mềm vẫn ghi chúng vào CSDL. Trả thêm danh sách
    (student_id, club_id) thi một CLB KHÔNG có trong nguyện vọng: sổ nhập
    không chứa được những ô đó.
    """
    from rbda_priority_pipeline import sap_buoi

    clubs = [{
        "club_id": r["club_id"], "name": r.get("name") or r["club_id"],
        "capacity": int(float(r.get("capacity") or 0)),
        "reserve_capacity": int(float(r.get("reserve_capacity") or 0)),
        "reserve_group": r.get("reserve_group") or "",
        "buoi": (r.get("buoi") or "").strip(),
    } for r in clubs_rows]

    hs: dict = {}

    def lay_hs(r):
        sid = (r.get("student_id") or "").strip()
        s = hs.setdefault(sid, {"student_id": sid, "name": "", "reserve_group": "",
                                "nv": [], "_thi": {}})
        s["name"] = s["name"] or (r.get("name") or "")
        s["reserve_group"] = s["reserve_group"] or (r.get("reserve_group") or "")
        return s

    for r in nv_rows:
        if not (r.get("student_id") or "").strip():
            continue
        s = lay_hs(r)
        cot = list(r.keys())
        theo_buoi: dict = {}
        for c in cot:
            m = re.match(r"^(?P<b>.+)_pref_(?P<k>\d+)$", c or "")
            if m:
                theo_buoi.setdefault(m.group("b"), []).append((int(m.group("k")), c))
        if theo_buoi:
            thu_tu = [c for b in sap_buoi(theo_buoi) for _, c in sorted(theo_buoi[b])]
        else:
            thu_tu = sorted([c for c in cot if (c or "").startswith("pref_")],
                            key=lambda c: int(c.split("_")[1]))
        if "club_id" in cot:                    # dạng dài
            s.setdefault("_dai", []).append(
                (int(r.get("rank") or 999), r["club_id"]))
            continue
        for c in thu_tu:
            v = (r.get(c) or "").strip()
            if v and v not in [x["club_id"] for x in s["nv"]]:
                s["nv"].append({"club_id": v, "thi": False, "diem": ""})
    for s in hs.values():
        for _, cid in sorted(s.pop("_dai", [])):
            if cid not in [x["club_id"] for x in s["nv"]]:
                s["nv"].append({"club_id": cid, "thi": False, "diem": ""})

    for r in thi_rows:
        if not (r.get("student_id") or "").strip():
            continue
        s = lay_hs(r)
        if "club_id" in r:
            if r.get("club_id"):
                s["_thi"][r["club_id"]] = r.get("score") or ""
            continue
        for c, v in r.items():
            m = re.match(r"^test_club_(\d+)$", c or "")
            if m and (v or "").strip():
                s["_thi"][v.strip()] = (r.get(f"score_{m.group(1)}") or "").strip()

    ngoai_nv = []
    for s in hs.values():
        thi = s.pop("_thi")
        for x in s["nv"]:
            if x["club_id"] in thi:
                x["thi"], x["diem"] = True, thi[x["club_id"]]
        trong_nv = {x["club_id"] for x in s["nv"]}
        ngoai_nv += [(s["student_id"], c) for c in thi if c not in trong_nv]
    return clubs, list(hs.values()), ngoai_nv
