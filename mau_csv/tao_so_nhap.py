"""Sinh các tệp Sổ nhập CLB (.xlsx) — mẫu trống và hai sổ ví dụ.

Chạy lại mỗi khi sửa `so_nhap.py` hoặc các bộ CSV ví dụ, để sổ và CSV không
lệch nhau:

    ./.venv/bin/python mau_csv/tao_so_nhap.py

Tạo ra:
    mau_csv/SO_NHAP_CLB.xlsx                         mẫu trống, phát cho trường
    mau_csv/vi_du_day_du/SO_NHAP_CLB_vi_du.xlsx      3 buổi · 9 CLB · 24 HS
    mau_csv/vi_du_ca_tuan/SO_NHAP_CLB_vi_du.xlsx     6 buổi · 18 CLB · 60 HS
    du_lieu_test/vi_du_huong_dan/SO_NHAP_VIDU.xlsx   bộ 10 em của HUONG_DAN_SU_DUNG.md
    du_lieu_test/bo_sach/SO_NHAP_SACH.xlsx           140 em, 0 cảnh báo
    du_lieu_test/SO_NHAP_TEST.xlsx                   120 em, cạnh tranh cao
    du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx            cố ý sai 5 chỗ: thử bảng lỗi

Từ A14 sổ mẫu trống và các sổ ví dụ có thêm cột "Lớp" ngay sau "Họ tên" (lớp MÔ PHỎNG, gán bởi
`du_lieu_test/them_lop_vao_mau.py`). `SO_NHAP_CO_LOI_CO_Y.xlsx` giữ bố cục cũ (không cột Lớp)
vì `LOI_CO_Y` trỏ vào ô cụ thể.

Từ A13.4 sheet học sinh có HAI hàng tiêu đề. Các sổ trong `du_lieu_test/` được giữ nguyên ở
dạng MỘT hàng cũ (phần mềm vẫn đọc được, và chúng thử luôn đường đọc dạng cũ); chạy lại
kịch bản này sẽ ghi chúng ở dạng hai hàng, và `LOI_CO_Y` bên dưới đã theo dạng hai hàng.

Các sổ ví dụ sinh THẲNG từ bộ ba tệp cũ cùng thư mục, nên nạp sổ hay nạp ba
tệp đều ra cùng một CSDL — `tests/test_so_nhap.py` canh điều đó.
"""

import csv
import re
import os
import sys

import openpyxl

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THU_MUC))

import cau_hinh_ws  # noqa: E402
import so_nhap  # noqa: E402

TEN_MAU = "SO_NHAP_CLB.xlsx"
TEN_VI_DU = "SO_NHAP_CLB_vi_du.xlsx"
BO_VI_DU = ("vi_du_day_du", "vi_du_ca_tuan")


GOC = os.path.dirname(THU_MUC)
DLT = os.path.join(GOC, "du_lieu_test")

# (thư mục, tiền tố bộ ba tệp cũ, đuôi, tên sổ)
BO_DU_LIEU_TEST = [
    (os.path.join(DLT, "vi_du_huong_dan"), "VIDU", ".csv", "SO_NHAP_VIDU.xlsx"),
    (os.path.join(DLT, "bo_sach"), "SACH", ".csv", "SO_NHAP_SACH.xlsx"),
    (DLT, "TEST", ".xlsx", "SO_NHAP_TEST.xlsx"),
]
TEN_BA_TEP = ("01_danh_sach_CLB", "02_chon_CLB_muon_thi", "03_xep_hang_nguyen_vong")


def _doc(duong_dan):
    """Một tệp cũ (.csv, hoặc .xlsx đọc trang đầu) -> [dict]."""
    if duong_dan.endswith(".csv"):
        with open(duong_dan, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    wb = openpyxl.load_workbook(duong_dan, read_only=True, data_only=True)
    dong = [[so_nhap.o_thanh_chu(v) for v in r]
            for r in wb.worksheets[0].iter_rows(values_only=True)]
    wb.close()
    dong = [r for r in dong if any(r)]
    return [dict(zip(dong[0], r)) for r in dong[1:]]


_RE_PREF = re.compile(r"^(?:(?P<buoi>.+)_)?pref_(?P<k>\d+)$")


def _gan_diem_w(students, dong_nv):
    """Gắn `diem_w` (A13.13) vào nguyện vọng từ cột `wp_k` / `<buoi>_wp_k` của tệp nguyện vọng.

    Ghép cột `wp` với cột `pref` cùng tiền tố buổi và cùng hậu tố số (như phần mềm). Không có
    cột `wp` thì không làm gì (sổ cũ giữ nguyên).
    """
    if not dong_nv or not any(re.match(r"^(?:.+_)?wp_\d+$", c or "") for c in dong_nv[0]):
        return
    theo_sid = {s["student_id"]: s for s in students}
    for r in dong_nv:
        s = theo_sid.get((r.get("student_id") or "").strip())
        if not s:
            continue
        cid_w = {}
        for c in r:
            if _RE_PREF.match(c or ""):
                cid, w = (r.get(c) or "").strip(), (r.get(c.replace("pref_", "wp_")) or "").strip()
                if cid and w:
                    cid_w[cid] = int(float(w))
        for x in s["nv"]:
            if x["club_id"] in cid_w:
                x["diem_w"] = cid_w[x["club_id"]]


def _tu_ba_tep(thu_muc, ten, duoi=".csv", tien_to=""):
    dong = [_doc(os.path.join(thu_muc, tien_to + t + duoi)) for t in ten]
    clubs, students, ngoai_nv = so_nhap.tu_csv(*dong)
    if ngoai_nv:
        raise SystemExit(f"{thu_muc}: thi CLB không có trong nguyện vọng: {ngoai_nv}")
    _gan_diem_w(students, dong[2])
    return clubs, students


def tao_vi_du(ten_bo: str) -> str:
    goc = os.path.join(THU_MUC, ten_bo)
    clubs, students = _tu_ba_tep(goc, TEN_BA_TEP)
    ra = os.path.join(goc, TEN_VI_DU)
    # A13.7: có cột Điểm quyết tâm; A14: có cột Lớp (lớp MÔ PHỎNG từ them_lop_vao_mau.py)
    so_nhap.ghi_so_nhap(ra, clubs, students, luon_co_cot_w=True, co_lop=True)
    return ra


def tao_mau_trong() -> str:
    ra = os.path.join(THU_MUC, TEN_MAU)
    # Cùng cấu hình mặc định như `tao_so_nhap_mau` của phần mềm: MỌI sheet (cả Hướng dẫn) khớp nhau (T1a).
    # A13.7: mẫu trống có cột Điểm quyết tâm; A14: và cột Lớp
    so_nhap.ghi_so_nhap(ra, cfg=cau_hinh_ws.chuan_hoa({}), luon_co_cot_w=True, co_lop=True)
    return ra


def tao_du_lieu_test_mot(thu_muc, tien_to, duoi, ten) -> str:
    clubs, students = _tu_ba_tep(thu_muc, TEN_BA_TEP, duoi, tien_to + "_")
    p = os.path.join(thu_muc, ten)
    # có cột wp trong CSV thì sổ có cột Điểm quyết tâm; có class_id thì sổ có cột Lớp (A14)
    so_nhap.ghi_so_nhap(p, clubs, students, co_lop=any(s.get("class_id") for s in students))
    return p


def tao_du_lieu_test() -> list:
    return [tao_du_lieu_test_mot(*b) for b in BO_DU_LIEU_TEST]


# Sổ cố ý sai: từ bộ 10 em, mỗi lỗi một chỗ, để thử bảng lỗi của màn hình
# nạp. (sheet, ô, giá trị mới, lỗi phần mềm phải báo)
LOI_CO_Y = [
    # Sheet học sinh có hai hàng tiêu đề: dữ liệu bắt đầu từ hàng 3.
    (so_nhap.SHEET_HS, "D4", "CLB Bóng chuyền", "so_nhap_clb_khong_co"),
    (so_nhap.SHEET_HS, "E5", "tám", "so_nhap_diem_sai"),
    (so_nhap.SHEET_HS, "A7", "HS04", "so_nhap_hs_trung"),
    (so_nhap.SHEET_HS, "F9", "=D9", "so_nhap_nv_trung"),
    (so_nhap.SHEET_CLB, "C3", 0, "so_nhap_chi_tieu_sai"),
]


def tao_so_co_loi() -> str:
    clubs, students = _tu_ba_tep(os.path.join(DLT, "vi_du_huong_dan"), TEN_BA_TEP,
                                 ".csv", "VIDU_")
    p = os.path.join(DLT, "SO_NHAP_CO_LOI_CO_Y.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, students)
    wb = openpyxl.load_workbook(p)
    for sheet, o, gia_tri, _ in LOI_CO_Y:
        # "=D9": chép đúng tên ở NV1 sang NV2 — chọn một CLB hai lần.
        if isinstance(gia_tri, str) and gia_tri.startswith("="):
            gia_tri = wb[sheet][gia_tri[1:]].value
        wb[sheet][o] = gia_tri
    wb.save(p)
    return p


if __name__ == "__main__":
    for p in [tao_mau_trong()] + [tao_vi_du(bo) for bo in BO_VI_DU] \
            + tao_du_lieu_test() + [tao_so_co_loi()]:
        print("da tao", os.path.relpath(p, GOC))
