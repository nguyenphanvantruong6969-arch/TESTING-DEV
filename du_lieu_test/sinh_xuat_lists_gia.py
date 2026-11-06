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

Tùy chọn (T4M-Q5c, mặc định TẮT nên tệp mặc định giữ nguyên từng byte): `so_nv` tới 7 nguyện vọng mỗi ngày
(cột NV1..NV7), `co_tick` thêm THI1..THIn (`Có` hoặc trống; chỉ CLB có đề, tối đa 5 mỗi ngày) và `co_wp` thêm
WP1..WPn (điểm quyết tâm: quỹ 1 = CLB đã tick, quỹ 2 = các CLB còn lại, mỗi quỹ không rỗng cộng đúng 100).
Tick và điểm sinh bằng bộ ngẫu nhiên RIÊNG nên bật chúng không đổi nguyện vọng đã sinh.
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

TRAN_THI_MOI_NGAY = 5                         # tick tối đa mỗi ngày (bieu_mau.TRAN_THI_MOI_BUOI)
XAC_SUAT_TICK = 0.6

COT = ["Email", "HoTen", "CoSo", "Khoi", "Lop", "Thu",
       "NV1", "NV2", "NV3", "CapDo", "Goi", "TrangThai", "Created"]


def cot_csv(so_nv=SO_NV, co_tick=False, co_wp=False):
    """Tiêu đề cột của tệp: mặc định đúng `COT`."""
    return (COT[:6] + ["NV%d" % k for k in range(1, so_nv + 1)]
            + (["THI%d" % k for k in range(1, so_nv + 1)] if co_tick else [])
            + (["WP%d" % k for k in range(1, so_nv + 1)] if co_wp else []) + COT[9:])

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


def _chia_100(n, rng):
    """n số nguyên dương cộng đúng 100 (n = 1 thì [100])."""
    if n == 1:
        return [100]
    cat = [0] + sorted(rng.sample(range(1, 100), n - 1)) + [100]
    return [cat[i + 1] - cat[i] for i in range(n)]


def sinh(so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH, clb_theo_ngay=None, so_nv=SO_NV,
         co_tick=False, co_wp=False, clb_co_de=None):
    """Trả về danh sách dòng (dict theo `cot_csv`), `so_hs` × 5 dòng, thứ tự: từng em, từng ngày.

    `clb_theo_ngay` ({tên ngày trong NGAY: [mã CLB]}) cho mã CLB thật thay cho mã giả T2-CLB01…
    (T4M-DEMO: để khớp de_thi.json). Bỏ trống thì như cũ, từng byte.

    `so_nv` (<= 10): số ô nguyện vọng mỗi ngày. `co_tick`: thêm THIk; chỉ tick CLB trong `clb_co_de` (tập
    mã CLB có đề thi; None = mọi CLB), tối đa 5 mỗi ngày. `co_wp`: thêm WPk hợp lệ (xem docstring tệp)."""
    rng = random.Random(seed)
    rng2 = random.Random(seed * 7919 + 13)         # tick + điểm: riêng, để không đổi dòng NV
    clb = _clb_theo_ngay(rng) if clb_theo_ngay is None else clb_theo_ngay
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
            nv = [""] * so_nv
            goi = ""
            if co_goi and ngay in NGAY_GOI:
                goi = TEN_GOI                  # gói chiếm ngày này: không có NV riêng
            elif rng.random() >= XAC_SUAT_NGAY_TRONG:
                so_chon = rng.randint(1, so_nv)
                chon = rng.sample(clb[ngay], min(so_chon, len(clb[ngay])))
                nv[:len(chon)] = chon
            d = {
                "Email": email, "HoTen": ten, "CoSo": co_so, "Khoi": khoi, "Lop": lop,
                "Thu": ngay, "CapDo": cap, "Goi": goi, "TrangThai": trang_thai,
                "Created": "2026-11-%02dT%02d:%02d:00Z" % (
                    1 + (idx + j) % 9, 7 + (idx * 3 + j) % 12, (idx * 7 + j * 11) % 60),
            }
            d.update({"NV%d" % (k + 1): nv[k] for k in range(so_nv)})
            if co_tick or co_wp:
                chon = [x for x in nv if x]
                tick = []
                if co_tick:
                    for x in chon:
                        if (clb_co_de is None or x in clb_co_de) and len(tick) < TRAN_THI_MOI_NGAY \
                                and rng2.random() < XAC_SUAT_TICK:
                            tick.append(x)
                diem = {}
                if co_wp:
                    for tap in (tick, [x for x in chon if x not in tick]):
                        diem.update(zip(tap, _chia_100(len(tap), rng2)) if tap else ())
                for k in range(so_nv):
                    if co_tick:
                        d["THI%d" % (k + 1)] = "Có" if nv[k] and nv[k] in tick else ""
                    if co_wp:
                        d["WP%d" % (k + 1)] = str(diem[nv[k]]) if nv[k] else ""
            dong.append(d)
    return dong


def gai_quy_khong_du(dong, so_nv=SO_NV):
    """Cố ý làm MỘT quỹ điểm quyết tâm cộng thiếu (T4M-Q5c): lấy dòng đầu có email chữ thường và một quỹ từ hai CLB
    trở lên, bớt tối đa 10 điểm ở CLB đầu của quỹ ấy. Sửa tại chỗ `dong` (kết quả của `sinh` có co_wp).
    Trả {email, thu, quy (1/2), club_id, thieu}, hoặc None nếu không có dòng phù hợp."""
    for d in dong:
        if d["Email"] != d["Email"].lower() or "THI1" not in d:
            continue
        for quy in (1, 2):
            tap = [k for k in range(1, so_nv + 1)
                   if d["NV%d" % k] and (d["THI%d" % k] == "Có") == (quy == 1)] 
            if len(tap) >= 2 and int(d["WP%d" % tap[0]] or 0) > 0:
                k = tap[0]
                thieu = min(10, int(d["WP%d" % k]))
                d["WP%d" % k] = str(int(d["WP%d" % k]) - thieu)
                return {"email": d["Email"], "thu": d["Thu"], "quy": quy, "club_id": d["NV%d" % k],
                        "thieu": thieu}
    return None


def ghi_dong(duong, dong, so_nv=SO_NV, co_tick=False, co_wp=False):
    """Ghi CSV UTF-8 CÓ BOM, xuống dòng CRLF như tệp Lists xuất ra, từ các dòng của `sinh`."""
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot_csv(so_nv, co_tick, co_wp), lineterminator="\r\n")
        w.writeheader()
        w.writerows(dong)
    return len(dong)


def ghi_csv(duong, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH, clb_theo_ngay=None, so_nv=SO_NV,
            co_tick=False, co_wp=False, clb_co_de=None):
    """Ghi CSV của `sinh(...)`; trả số dòng."""
    dong = sinh(so_hs=so_hs, seed=seed, clb_theo_ngay=clb_theo_ngay, so_nv=so_nv,
                co_tick=co_tick, co_wp=co_wp, clb_co_de=clb_co_de)
    return ghi_dong(duong, dong, so_nv, co_tick, co_wp)


def main():
    ap = argparse.ArgumentParser(description="Sinh tệp giả giống Export to CSV của SharePoint List (mô hình rộng).")
    ap.add_argument("--so-hs", type=int, default=SO_HS_MAC_DINH)
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH)
    ap.add_argument("--ra", default="lists_gia.csv")
    ap.add_argument("--so-nv", type=int, default=SO_NV, help="số ô nguyện vọng mỗi ngày (tối đa 10)")
    ap.add_argument("--tick", action="store_true", help="thêm cột THIk (tick chọn thi, tối đa 5 mỗi ngày)")
    ap.add_argument("--wp", action="store_true", help="thêm cột WPk (điểm quyết tâm, hai quỹ 100)")
    a = ap.parse_args()
    n = ghi_csv(a.ra, so_hs=a.so_hs, seed=a.seed, so_nv=a.so_nv, co_tick=a.tick, co_wp=a.wp)
    print("Đã ghi %d dòng (%d em × %d ngày) vào %s" % (n, a.so_hs, len(NGAY), a.ra))


if __name__ == "__main__":
    main()
