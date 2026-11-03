# -*- coding: utf-8 -*-
"""Thêm cột LỚP MÔ PHỎNG vào các bộ mẫu giao người dùng (A14, C2). MỘT lệnh.

    python du_lieu_test/them_lop_vao_mau.py

DỮ LIỆU MÔ PHỎNG: lớp (10A1 … 12A3) do máy gán bằng `random.Random(seed)` với seed cố định ở
bảng DICH dưới đây; không phải khảo sát thật, không gõ tay. Chạy lại cho ra đúng cùng byte.

Lớp CHỈ để hiển thị, sắp, lọc, xuất cho giáo viên chủ nhiệm: thuật toán không đọc nó, nên
`match_results` của mọi bộ mẫu giữ NGUYÊN (có test so với băm chốt trước khi thêm lớp).

Làm gì với mỗi bộ:
  1. gán MỘT lớp cho mỗi học sinh (gom mã từ các tệp học sinh của bộ, sắp theo mã); hai tệp
     chọn thi và nguyện vọng của cùng bộ nhận cùng một lớp cho cùng một em;
  2. chèn cột `class_id` NGAY SAU `reserve_group` (CSV, và .xlsx nếu có), giữ nguyên BOM và
     kiểu xuống dòng của tệp;
  3. dựng lại các Sổ nhập `.xlsx` bằng `mau_csv/tao_so_nhap.py` (cột "Lớp" ngay sau "Họ tên");
     sổ mẫu trống cũng có cột Lớp.

KHÔNG đụng `bo_sach` (dữ liệu của đề tài) và mọi dữ liệu đã dùng cho số liệu công bố.
"""

import copy
import csv
import io
import os
import random
import re
import sys

import openpyxl
from openpyxl.styles import Font

_DAY = os.path.dirname(os.path.abspath(__file__))
_GOC = os.path.dirname(_DAY)
sys.path.insert(0, _GOC)
sys.path.insert(0, os.path.join(_GOC, "mau_csv"))

MAU = os.path.join(_GOC, "mau_csv")
LOP = ("10A1", "10A2", "10A3", "11A1", "11A2", "11A3", "12A1", "12A2", "12A3")
# (thư mục, [tệp CSV học sinh], [tệp .xlsx tương ứng], seed)
DICH = [
    (os.path.join(_DAY, "vi_du_huong_dan"),
     ["VIDU_02_chon_CLB_muon_thi.csv", "VIDU_03_xep_hang_nguyen_vong.csv"],
     ["VIDU_02_chon_CLB_muon_thi.xlsx", "VIDU_03_xep_hang_nguyen_vong.xlsx"], 112026201),
    (os.path.join(MAU, "vi_du_day_du"),
     ["02_chon_CLB_muon_thi.csv", "03_xep_hang_nguyen_vong.csv"], [], 112026202),
    (os.path.join(MAU, "vi_du_ca_tuan"),
     ["02_chon_CLB_muon_thi.csv", "03_xep_hang_nguyen_vong.csv"], [], 112026203),
    (MAU, ["07_chon_club_thi_nhieu_buoi.csv", "08_nguyen_vong_nhieu_buoi.csv"], [], 112026204),
]


def gan_lop(ids, seed) -> dict:
    """{mã: lớp} — hàm thuần của danh sách mã (sắp theo mã) và seed."""
    rng = random.Random(seed)
    return {sid: rng.choice(LOP) for sid in sorted(set(ids))}


def _doc_csv_tho(duong):
    """(bom, xuống dòng, dòng) — dòng là list[list[str]]; để GHI LẠI đúng byte nếu không đổi gì."""
    with io.open(duong, "rb") as f:
        tho = f.read()
    bom = tho.startswith(b"\xef\xbb\xbf")
    xuong = "\r\n" if b"\r\n" in tho else "\n"
    with io.open(duong, encoding="utf-8-sig", newline="") as f:
        return bom, xuong, list(csv.reader(f))


def _ghi_csv_tho(duong, bom, xuong, dong):
    with io.open(duong, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        csv.writer(f, lineterminator=xuong).writerows(dong)


def _them_cot_csv(duong, lop):
    bom, xuong, dong = _doc_csv_tho(duong)
    tieu = dong[0]
    if "class_id" in tieu:                                  # chạy lại: bỏ cột cũ
        j = tieu.index("class_id")
        dong = [r[:j] + r[j + 1:] for r in dong]
        tieu = dong[0]
    j = tieu.index("reserve_group") + 1
    moi = [tieu[:j] + ["class_id"] + tieu[j:]]
    moi += [r[:j] + [lop.get((r[0] or "").strip(), "")] + r[j:] for r in dong[1:]]
    _ghi_csv_tho(duong, bom, xuong, moi)
    return len(dong) - 1


def _ma_tu_csv(duong):
    return [(r[0] or "").strip() for r in _doc_csv_tho(duong)[2][1:] if r and (r[0] or "").strip()]


def _them_cot_xlsx(duong, lop):
    wb = openpyxl.load_workbook(duong)
    ws = wb.worksheets[0]
    tieu = [c.value for c in ws[1]]
    if "class_id" in tieu:                                  # chạy lại: bỏ cột cũ
        ws.delete_cols(tieu.index("class_id") + 1)
        tieu = [c.value for c in ws[1]]
    j = tieu.index("reserve_group") + 2                      # số thứ tự cột (từ 1) của cột mới
    ws.insert_cols(j)
    mau = ws.cell(row=1, column=j - 1)
    o = ws.cell(row=1, column=j, value="class_id")
    o.font, o.fill, o.alignment, o.border = (copy.copy(mau.font), copy.copy(mau.fill),
                                             copy.copy(mau.alignment), copy.copy(mau.border))
    for i in range(2, ws.max_row + 1):
        sid = str(ws.cell(row=i, column=1).value or "").strip()
        if sid in lop:
            ws.cell(row=i, column=j, value=lop[sid])
    if "Ghi chú" in wb.sheetnames:
        gc = wb["Ghi chú"]
        if not any(str(c.value or "").startswith("Cột class_id") for c in gc["A"]):
            gc.append([""])
            for chu in ("Cột class_id = LỚP MÔ PHỎNG của học sinh (chỉ để hiển thị / lọc / xuất,",
                        "không ảnh hưởng kết quả xếp). Sinh bằng",
                        "du_lieu_test/them_lop_vao_mau.py (seed cố định)."):
                gc.append([chu])
            gc.cell(row=gc.max_row - 2, column=1).font = Font(bold=False)
    wb.save(duong)


def main():
    import tao_so_nhap as tsn
    for thu_muc, csvs, xlsxs, seed in DICH:
        ma = []
        for t in csvs:
            ma += _ma_tu_csv(os.path.join(thu_muc, t))
        lop = gan_lop(ma, seed)
        for t in csvs:
            p = os.path.join(thu_muc, t)
            n = _them_cot_csv(p, lop)
            print("  %-60s +class_id, %d em" % (os.path.relpath(p, _GOC), n))
        for t in xlsxs:
            _them_cot_xlsx(os.path.join(thu_muc, t), lop)
            print("  %-60s +class_id" % os.path.relpath(os.path.join(thu_muc, t), _GOC))
    # Sổ nhập dựng lại từ bộ ba CSV (đọc cột class_id) và sổ mẫu trống (có cột Lớp)
    print("  sổ", tsn.tao_mau_trong())
    for ten_bo in tsn.BO_VI_DU:
        print("  sổ", tsn.tao_vi_du(ten_bo))
    for thu_muc, tien_to, duoi, ten in tsn.BO_DU_LIEU_TEST[:1]:
        print("  sổ", tsn.tao_du_lieu_test_mot(thu_muc, tien_to, duoi, ten))


if __name__ == "__main__":
    main()
