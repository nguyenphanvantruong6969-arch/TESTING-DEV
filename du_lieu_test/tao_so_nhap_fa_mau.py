# -*- coding: utf-8 -*-
"""Sinh `SO_NHAP_FA_MAU_120HS.xlsx`: sổ nhập MẪU cho workspace bật FA-DAA (FG-2).

    python du_lieu_test/tao_so_nhap_fa_mau.py [--ra DUONG_DAN.xlsx] [--seed 20261113]

DỮ LIỆU MÔ PHỎNG: tên, nguyện vọng, điểm thi và huy chương do máy bịa theo `random.Random(seed)`,
cùng seed cho cùng nội dung (tệp ghi cả dấu thời gian cố định). Không phải khảo sát thật.

Hợp lệ cho FA (`fa_daa.kiem_truoc_fa`, `kiem_ho_so_huy_chuong`): 120 em, hai buổi, mỗi buổi có
một CLB Tự do (nhận mọi em), hai CLB Giới hạn và một CLB Tuyển chọn (có điểm sàn); mỗi em xếp
3-4 CLB mỗi buổi, đặt huy chương 60 / 30 / 10 trên CLB không Tự do, mỗi giá trị tối đa một lần
mỗi buổi; điểm thi chỉ ở CLB Tuyển chọn.
"""
import argparse
import datetime
import os
import random
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)

import openpyxl  # noqa: E402

import so_nhap  # noqa: E402

SEED_MAC_DINH = 20261113
MAC_DINH_RA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
N_HOC_SINH = 120
BUOI = ["thu_2", "thu_5"]
# (hậu tố tên, loại, chỉ tiêu, điểm sàn)
CLB_MOI_BUOI = [("Tự do", so_nhap.TU_DO, 120, None),
                ("Giới hạn A", so_nhap.GIOI_HAN, 25, None),
                ("Giới hạn B", so_nhap.GIOI_HAN, 25, None),
                ("Tuyển chọn", so_nhap.TUYEN_CHON, 20, 5)]
TEN_CLB = {"thu_2": ["Bóng rổ", "Cờ vua", "Âm nhạc", "Robot"],
           "thu_5": ["Bóng đá", "Hội hoạ", "Tin học", "Tranh biện"]}
GHI_CHU = [
    "",
    "DỮ LIỆU MÔ PHỎNG: tên học sinh, nguyện vọng, điểm thi và huy chương do máy bịa theo seed cố định",
    "(du_lieu_test/tao_so_nhap_fa_mau.py). Không phải học sinh hay khảo sát có thật.",
    "Sổ này hợp lệ cho workspace bật FA-DAA: mỗi buổi có một CLB Tự do; huy chương chỉ 60 / 30 / 10.",
]


def dung_so(seed: int = SEED_MAC_DINH):
    """(clubs, students) cho `so_nhap.ghi_so_nhap`, tất định theo `seed`."""
    rd = random.Random(seed)
    clubs, theo_buoi = [], {}
    for b in BUOI:
        theo_buoi[b] = []
        for ten, (hau_to, loai, cho, san) in zip(TEN_CLB[b], CLB_MOI_BUOI):
            cid = "%s_%d" % (b.upper(), len(theo_buoi[b]) + 1)
            c = {"club_id": cid, "name": "CLB %s (%s)" % (ten, hau_to), "capacity": cho,
                 "reserve_capacity": 0, "reserve_group": "", "buoi": b, "loai": loai,
                 "diem_san": san, "so_toi_thieu": None, "suc_chua_phong": None}
            clubs.append(c)
            theo_buoi[b].append(c)
    students = []
    for i in range(1, N_HOC_SINH + 1):
        nv = []
        for b in BUOI:
            tu_do = theo_buoi[b][0]
            khac = theo_buoi[b][1:]
            chon = rd.sample(khac, rd.choice([2, 3])) + [tu_do]      # Tự do xếp cuối
            gia_tri = rd.sample([60, 30, 10], len(chon) - 1)          # huy chương: không Tự do
            for k, c in enumerate(chon):
                x = {"club_id": c["club_id"], "thi": False, "diem": ""}
                if c["loai"] == so_nhap.TUYEN_CHON:
                    x["thi"], x["diem"] = True, str(rd.randint(3, 10))
                if c["loai"] != so_nhap.TU_DO:
                    x["diem_w"] = gia_tri[k]
                nv.append(x)
        students.append({"student_id": "FA%03d" % i, "name": "Học sinh mô phỏng %03d" % i,
                         "reserve_group": "", "nv": nv})
    return clubs, students


def ghi(ra: str, seed: int = SEED_MAC_DINH) -> str:
    clubs, students = dung_so(seed)
    so_nhap.ghi_so_nhap(ra, clubs, students, luon_co_cot_w=True, che_do_fa=True)
    wb = openpyxl.load_workbook(ra)
    hd = wb[so_nhap.SHEET_HD]
    for dong in GHI_CHU:
        hd.cell(row=hd.max_row + 1, column=1, value=dong or None)
    moc = datetime.datetime(2026, 11, 13)          # dấu thời gian cố định: chạy lại ra cùng tệp
    wb.properties.created = wb.properties.modified = moc
    wb.save(ra)
    return ra


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ra", default=MAC_DINH_RA)
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH)
    a = ap.parse_args()
    print(ghi(a.ra, a.seed))
