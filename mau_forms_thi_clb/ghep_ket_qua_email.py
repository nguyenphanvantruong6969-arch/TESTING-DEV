# -*- coding: utf-8 -*-
"""FA-S11 (TH = chưa thử trên Microsoft thật): ghép email vào kết quả để nạp list `KetQua` (FA_SAU_XEP.md §2).

Dùng (CHỈ trên máy IT; EMAIL_MA_HS.csv là dữ liệu cá nhân, không gửi đi, không đưa lên kho mã):
    python ghep_ket_qua_email.py ket_qua_ly_do.csv EMAIL_MA_HS.csv --ra KETQUA_NHAP_LIST.csv

`ket_qua_ly_do.csv` do kiosk xuất (`export_ly_do_csv`); `EMAIL_MA_HS.csv` (cột Email, student_id) do bộ chuyển đổi
`chuyen_forms_sang_phan_mem.py --fa-daa` ghi. Mỗi dòng kết quả giữ nguyên; em không có trong tệp email: cảnh báo,
dòng vẫn ghi với Email rỗng. Email hạ chữ thường (app lọc theo email).
"""

import argparse
import csv
import sys

COT_KETQUA = ["Email", "MaHS", "Buoi", "CLB", "Nhom", "MaLyDo", "CauGiaiThich", "STB", "ViTriCho"]
TU_LY_DO = ["student_id", "buoi", "club", "group", "reason", "sentence", "stb", "waitlist_pos"]


def _doc(duong):
    with open(duong, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ghep(duong_ly_do, duong_email, duong_ra):
    """Ghi `duong_ra` (cột COT_KETQUA, utf-8-sig); trả danh sách cảnh báo (chuỗi)."""
    email = {}
    for d in _doc(duong_email):
        sid = (d.get("student_id") or "").strip()
        if sid:
            email[sid] = (d.get("Email") or "").strip().lower()
    canh_bao, thieu = [], []
    hang = []
    for d in _doc(duong_ly_do):
        sid = (d.get("student_id") or "").strip()
        if sid not in email and sid not in thieu:
            thieu.append(sid)
        hang.append([email.get(sid, "")] + [d.get(k, "") for k in TU_LY_DO])
    for sid in thieu:
        canh_bao.append("học sinh %s không có trong tệp email — dòng vẫn ghi, cột Email rỗng" % sid)
    with open(duong_ra, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COT_KETQUA)
        w.writerows(hang)
    return canh_bao


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ly_do", help="ket_qua_ly_do.csv (kiosk)")
    ap.add_argument("email", help="EMAIL_MA_HS.csv (bộ chuyển đổi --fa-daa)")
    ap.add_argument("--ra", default="KETQUA_NHAP_LIST.csv")
    a = ap.parse_args(argv)
    for cb in ghep(a.ly_do, a.email, a.ra):
        print("CẢNH BÁO: " + cb, file=sys.stderr)
    print("Đã ghi %s." % a.ra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
