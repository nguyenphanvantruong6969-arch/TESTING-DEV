# -*- coding: utf-8 -*-
"""T4M-BK1: CSV mẫu (cách C) và bảng kiểm thêm cột tay cho list ECA.

CSV mẫu: một dòng tiêu đề + MỘT dòng ví dụ (dữ liệu giả, không ô trống) để Microsoft Lists đoán đúng kiểu cột
khi "Create a list based on a spreadsheet". Tạo list từ CSV không thêm cột vào list CÓ SẴN: với ECA có sẵn dùng
bảng kiểm KIEM_COT_ECA.md.

TH: chưa chạy trên Power Apps / SharePoint.
"""

import csv
import os

from . import cot_lists


def ghi_csv_mau(ra_dir, tat_ca=None):
    """Ghi <ten>_mau.csv cho từng list (UTF-8 có BOM, CRLF như tệp Lists). Trả danh sách tên tệp.
    `tat_ca` (FA-M5): {tên list: [cột]}; None = `cot_lists.TAT_CA`."""
    ten_tep = []
    for ten_list, cot in (tat_ca or cot_lists.TAT_CA).items():
        ten = ten_list + "_mau.csv"
        with open(os.path.join(ra_dir, ten), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, lineterminator="\r\n")
            w.writerow([c.ten for c in cot])
            w.writerow([c.vi_du for c in cot])
        ten_tep.append(ten)
    return ten_tep


_KIEU_VI = {"Text": "Một dòng văn bản", "Number": "Số", "DateTime": "Ngày và giờ", "Choice": "Lựa chọn (Choice)"}


def tao_kiem_cot_eca(fa=False):
    L = ["TH: chưa chạy trên Power Apps / SharePoint",
         "Nguồn: T4M_DAC_TA_SUA_APP.md §1 (cột dữ liệu), T4M_KET_QUA_TAI_LIEU.md §8.1 (cách C)",
         "",
         "# Bảng kiểm thêm cột vào list ECA có sẵn (cách C)",
         "",
         "Làm trên **bản sao** của list ECA. Với mỗi cột: mở list, xem đã có cột tên đó chưa; **chỉ thêm nếu chưa có**.",
         "Tên nội bộ phải đúng từng chữ (đặt tên cột khi tạo, đừng đổi tên sau: đổi tên hiển thị không đổi tên nội bộ).",
         "Cột `Title` mặc định của SharePoint để nguyên. Giá trị Choice dưới đây theo dữ liệu giả; **giá trị thật của "
         "trường là HỎI-IT** (CoSo, CapDo, Goi).",
         "",
         "| ☐ | Tên cột | Kiểu | Bắt buộc | Lựa chọn | Đã có sẵn? (ghi có/không) |",
         "|---|---|---|---|---|---|"]
    for c in (cot_lists.ECA_FA if fa else cot_lists.ECA):
        L.append("| ☐ | `%s` | %s | %s | %s |  |" % (c.ten, _KIEU_VI[c.kieu], "có" if c.bat_buoc else "không",
                                                   ", ".join(c.lua_chon) if c.lua_chon else ""))
    L += ["",
          "Sau khi thêm: xuất List ra CSV, chạy `chuyen_forms_sang_phan_mem.py --chi-thi --lists`; đạt khi 0 cảnh báo "
          "ở phần Lists (R13, R37 của `T4M_DAC_TA_SUA_APP.md`).",
          "Cột `WP1`…`WP7` kiểu Số: đặt số chữ số thập phân = 0 nếu giao diện cho phép (ô điểm chỉ nhận số nguyên ≥ 0).",
          ""]
    if fa:
        L += ["FA-DAA (FA-M5, TH): bảng trên là cột ECA của chế độ FA. Khác bảng thường: **không** có `THI1`…`THI7`; thêm `HC_TuChinh`; "
              "`TrangThai` có `DRAFT` (tự lưu, bộ chuyển đổi bỏ qua), `SUBMITTED`, `Đã khóa`; `WP1`…`WP7` chỉ nhận 60, 30, 10 hoặc rỗng "
              "(`T4M_DAC_TA_SUA_APP.md` §12). Chạy `chuyen_forms_sang_phan_mem.py --fa-daa --lists`.", ""]
    return "\n".join(L)


def ghi_kiem_cot_eca(duong, fa=False):
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(tao_kiem_cot_eca(fa))
