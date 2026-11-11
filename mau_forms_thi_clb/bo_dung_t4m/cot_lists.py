# -*- coding: utf-8 -*-
"""T4M-BK1: MỘT định nghĩa cột cho bốn list (ECA, CLB, BaiThi, NHAT_KY_DA_LAM).

Nguồn của site script, CSV mẫu và bảng kiểm thêm cột. Tên cột ECA lấy từ hợp đồng của bộ sinh Lists giả
(`sinh_xuat_lists_gia.cot_csv(7, True, True)` bỏ cột hệ thống `Created`); CLB = tiêu đề `tao_mau_forms.ghi_clb_csv`;
BaiThi và NHAT_KY_DA_LAM theo `T4M_FLOW_DA_LAM.md` §2, §6. Không đọc tệp ngoài, không import bộ sinh cũ.

TH: chưa chạy trên Power Apps / SharePoint.
"""

import uuid
from collections import namedtuple

SO_NV = 7
# Cột: tên nội bộ (= tên trong hợp đồng), tên hiển thị, kiểu (Text/Number/DateTime/Choice), lựa chọn, bắt buộc, ví dụ giả
Cot = namedtuple("Cot", "ten hien_thi kieu lua_chon bat_buoc vi_du")

# Lựa chọn theo bộ sinh giả; giá trị THẬT của trường là HỎI-IT (CoSo, CapDo, Goi).
THU = ("Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6")
TRANG_THAI = ("Đang mở", "Đã khóa")
CO_SO = ("CS1", "CS2")
CAP_DO = ("N5-A", "N5-B", "N4-A", "N3-A")
GOI = ("3A",)

NS = "rbda-t4m"


def _nhom(tien_to, kieu, bat_buoc_dau, vi_du):
    return [Cot("%s%d" % (tien_to, k), "%s%d" % (tien_to, k), kieu, (), bat_buoc_dau and k == 1, vi_du(k))
            for k in range(1, SO_NV + 1)]


ECA = ([Cot("Email", "Email", "Text", (), True, "hs0001@truong-gia.example.test"),
        Cot("HoTen", "HoTen", "Text", (), False, "Nguyễn Văn An"),
        Cot("CoSo", "CoSo", "Choice", CO_SO, True, "CS1"),
        Cot("Khoi", "Khoi", "Number", (), True, "10"),
        Cot("Lop", "Lop", "Text", (), True, "10A1"),
        Cot("Thu", "Thu", "Choice", THU, True, "Thứ 2")]
       + _nhom("NV", "Text", False, lambda k: "T2-CLB%02d" % k)
       + _nhom("THI", "Text", False, lambda k: "Có")
       + _nhom("WP", "Number", False, lambda k: str(10 * k))
       + [Cot("CapDo", "CapDo", "Choice", CAP_DO, False, "N5-A"),
          Cot("Goi", "Goi", "Choice", GOI, False, "3A"),
          Cot("TrangThai", "TrangThai", "Choice", TRANG_THAI, True, "Đang mở")])

CLB = [Cot("ClubId", "ClubId", "Text", (), True, "T2-CLB01"),
       Cot("Ten", "Ten", "Text", (), True, "CLB giả một"),
       Cot("Buoi", "Buoi", "Text", (), True, "Thứ Hai"),
       Cot("FormUrl", "FormUrl", "Text", (), False, "LIEN-KET-GIA")]

BAI_THI = [Cot("Email", "Email", "Text", (), True, "hs0001@truong-gia.example.test"),
           Cot("ClubId", "ClubId", "Text", (), True, "T2-CLB01"),
           Cot("ResponseId", "ResponseId", "Text", (), True, "1"),
           Cot("NopLuc", "NopLuc", "DateTime", (), True, "2026-11-01T08:00:00Z")]

NHAT_KY = [Cot("ClubId", "ClubId", "Text", (), True, "T2-CLB01"),
           Cot("ResponseId", "ResponseId", "Text", (), False, "1"),
           Cot("Gio", "Gio", "DateTime", (), True, "2026-11-01T08:00:00Z"),
           Cot("KetQua", "KetQua", "Text", (), True, "loi")]

# Thứ tự tạo list cố định (đầu ra phải giống từng byte).
TAT_CA = {"ECA": ECA, "CLB": CLB, "BaiThi": BAI_THI, "NHAT_KY_DA_LAM": NHAT_KY}

# FA-M5 (TH): list ECA cho FA-DAA đường A (đặc tả `T4M_DAC_TA_SUA_APP.md` §12). Thay hai quỹ điểm quyết tâm bằng huy chương MỘT quỹ:
# `WPk` = 60 / 30 / 10 hoặc rỗng; `HC_TuChinh` = "Có" khi em tự chỉnh huy chương của ngày đó; `TrangThai` có DRAFT (tự lưu,
# bộ chuyển đổi bỏ qua) và SUBMITTED. Không còn `THIk` (em xếp CLB Tuyển chọn nào thì phải thi CLB đó; chưa thi = NOT_ATTEMPTED).
TRANG_THAI_FA = ("DRAFT", "SUBMITTED", "Đã khóa")
ECA_FA = ([c for c in ECA if c.ten not in {"THI%d" % k for k in range(1, SO_NV + 1)} | {"TrangThai"}]
          + [Cot("HC_TuChinh", "HC_TuChinh", "Text", (), False, "Có"),
             Cot("TrangThai", "TrangThai", "Choice", TRANG_THAI_FA, True, "SUBMITTED")])
TAT_CA_FA = dict(TAT_CA, ECA=ECA_FA)


def guid_cot(ten_list, ten_cot):
    """GUID cố định của cột: uuid5(NAMESPACE_URL, "rbda-t4m/<list>/<cột>"). Chạy lại không thêm cột lần hai."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "%s/%s/%s" % (NS, ten_list, ten_cot)))
