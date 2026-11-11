"""forms_dot.py — đường dẫn và nạp mô-đun cho bước "Chuẩn bị đợt" (FA-M7 G0), dùng chung cho api_forms*.py.

Mô-đun thuần, không giao diện. Mọi tệp của một đợt nằm trong `<thư mục chứa app.db>/forms/` (dữ liệu cá nhân như
email KHÔNG vào app.db). Thư mục con chỉ tạo khi cần.
"""
import os
import sys

_GOC = os.path.dirname(os.path.abspath(__file__))
TEN_THU_MUC_MAU = "mau_forms_thi_clb"


def nap_mau_forms() -> str:
    """Đưa `mau_forms_thi_clb/` vào `sys.path` (từ mã nguồn hoặc từ `sys._MEIPASS`); gọi lại không chèn thêm."""
    goc = getattr(sys, "_MEIPASS", None) or _GOC
    duong = os.path.join(goc, TEN_THU_MUC_MAU)
    if duong not in sys.path:
        sys.path.append(duong)
    return duong


def _tao(duong: str) -> str:
    os.makedirs(duong, exist_ok=True)
    return duong


def thu_muc_forms(db_path: str) -> str:
    return _tao(os.path.join(os.path.dirname(os.path.abspath(db_path)), "forms"))


def duong_de_dot(db_path: str) -> str:
    return os.path.join(thu_muc_forms(db_path), "de_thi.json")


def duong_so_nhap_clb_dot(db_path: str) -> str:
    return os.path.join(thu_muc_forms(db_path), "SO_NHAP_CLB_CLB.xlsx")


def thu_muc_nap(db_path: str) -> str:
    return _tao(os.path.join(thu_muc_forms(db_path), "nap"))


def thu_muc_tai_len(db_path: str) -> str:
    return _tao(os.path.join(thu_muc_nap(db_path), "tai_len"))


def duong_email_ma_hs(db_path: str) -> str:
    return os.path.join(thu_muc_nap(db_path), "EMAIL_MA_HS.csv")


def thu_muc_bieu_mau(db_path: str) -> str:
    return _tao(os.path.join(thu_muc_forms(db_path), "bieu_mau"))


def doc_de_dot(db_path: str) -> dict:
    """Đề thi của đợt (`forms/de_thi.json`) qua `bieu_mau.doc_de_thi`. Thiếu tệp -> FileNotFoundError."""
    nap_mau_forms()
    import bieu_mau
    duong = duong_de_dot(db_path)
    if not os.path.isfile(duong):
        raise FileNotFoundError(duong)
    return bieu_mau.doc_de_thi(duong)
