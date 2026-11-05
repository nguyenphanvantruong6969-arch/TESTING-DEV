# -*- coding: utf-8 -*-
"""T4M-NC GĐ3: sinh tệp GIẢ có hình dạng như "Export to CSV" của một SharePoint List (mô hình RỘNG).

    python du_lieu_test/sinh_xuat_lists_gia.py                       # 1.500 em -> ./lists_gia.csv
    python du_lieu_test/sinh_xuat_lists_gia.py --so-hs 200 --seed 5 --ra ./ra.csv

Mô hình rộng: MỘT DÒNG cho mỗi (học sinh, ngày), có sẵn ba cột nguyện vọng NV1..NV3
(1.500 em × 5 ngày = 7.500 dòng, dưới trần xuất CSV 30.000 dòng). Dùng để thử bộ chuyển đổi
(Lists -> Sổ nhập) và để IT/Truong so với tệp xuất thật của list thử.

DỮ LIỆU MÔ PHỎNG: tên, email (miền `example.test`), lớp, câu lạc bộ đều bịa; không phải dữ liệu thật
của trường nào. Chỉ dùng thư viện chuẩn; `random.Random(seed)` nên cùng seed cho cùng từng byte.
Tệp ghi UTF-8 CÓ BOM (như Excel/Lists), dấu phân cách `,`, ô trống = chuỗi rỗng.
"""

import argparse
import csv
import random

SEED_MAC_DINH = 5112026          # 05/11/2026
SO_HS_MAC_DINH = 1500
MIEN_GIA = "@truong-gia.example.test"
NGAY = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
NGAY_GOI = ["Thứ 2", "Thứ 4", "Thứ 5"]       # gói tiếng Nhật (ví dụ "3A") chiếm ba ngày này
TEN_GOI = "3A"
CAP_DO = ["N5-A", "N5-B", "N4-A", "N3-A"]    # cấp độ do trường chỉ định (điều kiện tham gia)
CO_SO = ["CS1", "CS2"]
KHOI = [6, 7, 8, 9, 10, 11, 12]
SO_CLB_MOI_NGAY = (6, 9)                      # dưới 10 lớp mỗi buổi
SO_NV = 3
XAC_SUAT_NGAY_TRONG = 0.12                    # em bỏ trống cả ngày
XAC_SUAT_TIENG_NHAT = 0.04
XAC_SUAT_HOA = 0.18                           # email viết hoa (để thử bước hạ chữ thường)
XAC_SUAT_DANG_MO = 0.02

COT = ["Email", "HoTen", "CoSo", "Khoi", "Lop", "Thu",
       "NV1", "NV2", "NV3", "CapDo", "Goi", "TrangThai", "Created"]

_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ"]
_DEM = ["Văn", "Thị", "Minh", "Ngọc", "Quốc", "Thanh", "Đức", "Hải", "Thu", "Gia"]
_TEN = ["An", "Bình", "Chi", "Dũng", "Giang", "Hà", "Khánh", "Linh", "Nam", "Phúc",
        "Quân", "Sơn", "Trang", "Uyên", "Vy", "Yến"]


def _clb_theo_ngay(rng):
    """Mã CLB giả của từng ngày, ví dụ T2-CLB01. Mã sinh theo thứ tự cố định để tái lập."""
    ket = {}
    for i, ngay in enumerate(NGAY):
        so = rng.randint(*SO_CLB_MOI_NGAY)
        ket[ngay] = ["T%d-CLB%02d" % (i + 2, k + 1) for k in range(so)]
    return ket


def _email(idx, rng):
    local = "hs%04d" % idx
    if rng.random() < XAC_SUAT_HOA:
        local = local.upper() if rng.random() < 0.5 else local.capitalize()
    return local + MIEN_GIA


def sinh(so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH):
    """Trả về danh sách dòng (dict theo `COT`), `so_hs` × 5 dòng, thứ tự: từng em, từng ngày."""
    rng = random.Random(seed)
    clb = _clb_theo_ngay(rng)
    dong = []
    for idx in range(1, so_hs + 1):
        email = _email(idx, rng)
        ten = "%s %s %s" % (rng.choice(_HO), rng.choice(_DEM), rng.choice(_TEN))
        co_so = rng.choice(CO_SO)
        khoi = rng.choice(KHOI)
        lop = "%dA%d" % (khoi, rng.randint(1, 6))
        cap = rng.choice(CAP_DO) if rng.random() < XAC_SUAT_TIENG_NHAT else ""
        co_goi = bool(cap) and rng.random() < 0.5
        trang_thai = "Đang mở" if rng.random() < XAC_SUAT_DANG_MO else "Đã khóa"
        for j, ngay in enumerate(NGAY):
            nv = [""] * SO_NV
            goi = ""
            if co_goi and ngay in NGAY_GOI:
                goi = TEN_GOI                  # gói chiếm ngày này: không có NV riêng
            elif rng.random() >= XAC_SUAT_NGAY_TRONG:
                so_chon = rng.randint(1, SO_NV)
                chon = rng.sample(clb[ngay], min(so_chon, len(clb[ngay])))
                nv[:len(chon)] = chon
            dong.append({
                "Email": email, "HoTen": ten, "CoSo": co_so, "Khoi": khoi, "Lop": lop,
                "Thu": ngay, "NV1": nv[0], "NV2": nv[1], "NV3": nv[2],
                "CapDo": cap, "Goi": goi, "TrangThai": trang_thai,
                "Created": "2026-11-%02dT%02d:%02d:00Z" % (
                    1 + (idx + j) % 9, 7 + (idx * 3 + j) % 12, (idx * 7 + j * 11) % 60),
            })
    return dong


def ghi_csv(duong, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH):
    """Ghi CSV UTF-8 CÓ BOM, xuống dòng CRLF như tệp Lists xuất ra."""
    dong = sinh(so_hs=so_hs, seed=seed)
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT, lineterminator="\r\n")
        w.writeheader()
        w.writerows(dong)
    return len(dong)


def main():
    ap = argparse.ArgumentParser(description="Sinh tệp giả giống Export to CSV của SharePoint List (mô hình rộng).")
    ap.add_argument("--so-hs", type=int, default=SO_HS_MAC_DINH)
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH)
    ap.add_argument("--ra", default="lists_gia.csv")
    a = ap.parse_args()
    n = ghi_csv(a.ra, so_hs=a.so_hs, seed=a.seed)
    print("Đã ghi %d dòng (%d em × %d ngày) vào %s" % (n, a.so_hs, len(NGAY), a.ra))


if __name__ == "__main__":
    main()
