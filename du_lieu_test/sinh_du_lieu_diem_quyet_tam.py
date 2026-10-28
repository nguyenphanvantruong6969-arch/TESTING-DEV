# -*- coding: utf-8 -*-
"""Sinh lại bộ sổ nhập mẫu CÓ ĐIỂM QUYẾT TÂM (mục A13.6). MỘT lệnh, seed cố định.

    python du_lieu_test/sinh_du_lieu_diem_quyet_tam.py            # ghi vào du_lieu_test/
    python du_lieu_test/sinh_du_lieu_diem_quyet_tam.py --ra ./ra  # ghi chỗ khác

Ra 6 tệp `SO_NHAP_DQT_{120HS,800HS}_{HOP_LE,CO_LOI,TRONG}.xlsx` cùng `DQT_BANG_LOI.json` (em nào
lỗi gì) và `DQT_KIEU_CHIA.json` (kiểu chia điểm của từng em).

DỮ LIỆU MÔ PHỎNG: tên bịa, điểm do máy sinh. Không phải khảo sát thật.

  * NHỎ  (120HS): giữ NGUYÊN nguyện vọng và điểm thi của `SO_NHAP_MAU_120HS_3BUOI.xlsx`,
    chỉ THÊM điểm quyết tâm — để so bật / tắt tính năng trên cùng một dữ liệu.
  * LỚN  (800HS): 800 em, 20 CLB, 4 buổi, sinh bằng `sinh_ngau_nhien` của kỹ năng
    `sinh-du-lieu-clb` với seed cố định.

Ghi sổ chỉ qua `so_nhap.ghi_so_nhap` (qua kỹ năng), không tự dựng định dạng hai hàng tiêu đề.
"""

import argparse
import copy
import io
import json
import os
import sys

_DAY = os.path.dirname(os.path.abspath(__file__))
_GOC = os.path.dirname(_DAY)
sys.path.insert(0, _GOC)
sys.path.insert(0, os.path.join(_GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts"))
import sinh_du_lieu as sk  # noqa: E402

SO_GOC_NHO = os.path.join(_DAY, "SO_NHAP_MAU_120HS_3BUOI.xlsx")
SEED_DQT = 27102026           # ngày chốt quyết định (27/10/2026); cùng seed cho HOP_LE và CO_LOI
SEED_LON = 8002026            # seed của `sinh_ngau_nhien` cho bản LỚN
BUOI_LON = ["thu_2", "thu_3", "thu_5", "thu_6"]
CLB_MOI_BUOI_LON = 5          # 4 buổi × 5 = 20 CLB
SO_EM_MOI_LOAI = {"120HS": 3, "800HS": 8}
CAC_BIEN_THE = ("HOP_LE", "CO_LOI", "TRONG")


def ten_tep(co, bien_the):
    return "SO_NHAP_DQT_%s_%s.xlsx" % (co, bien_the)


def _ghi_json(thu_muc, ten, noi_dung):
    with io.open(os.path.join(thu_muc, ten), "w", encoding="utf-8") as f:
        json.dump(noi_dung, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def _ap_va_ghi(thu_muc, co, bt, clb, hs):
    """Áp điểm lên bản sao (clb, hs), soát, ghi sổ. Trả (kiểu chia, bảng lỗi)."""
    che_do = bt.lower()
    clb, hs = copy.deepcopy(clb), copy.deepcopy(hs)
    kieu, bang = sk.ap_diem_quyet_tam(clb, hs, SEED_DQT, che_do, "tron", SO_EM_MOI_LOAI[co])
    loi = sk.soat(clb, hs) + (sk.soat_diem_quyet_tam(clb, hs) if che_do == "hop_le" else [])
    if loi:
        raise SystemExit("Không ghi %s:\n   ✗ %s" % (ten_tep(co, bt), "\n   ✗ ".join(loi)))
    sk.ghi_bo(thu_muc, clb, hs, sk.CFG_DQT, ten_tep(co, bt))
    return kieu, bang


def main(argv=None):
    # Cửa sổ lệnh / ống dẫn Windows mặc định cp1252: in tiếng Việt sẽ ném UnicodeEncodeError.
    for _luong in (sys.stdout, sys.stderr):
        if hasattr(_luong, "reconfigure"):
            _luong.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ra", default=_DAY, help="thư mục ghi (mặc định: du_lieu_test/)")
    ns = p.parse_args(argv)
    os.makedirs(ns.ra, exist_ok=True)

    nho = sk.doc_bo(SO_GOC_NHO)
    lon = sk.sinh_ngau_nhien(800, BUOI_LON, CLB_MOI_BUOI_LON, SEED_LON)
    loi = sk.soat(*lon)
    if loi:
        raise SystemExit("Bản lớn không hợp lệ:\n   ✗ " + "\n   ✗ ".join(loi))

    bang_loi, kieu_chia = {}, {}
    for co, (clb, hs) in (("120HS", nho), ("800HS", lon)):
        for bt in CAC_BIEN_THE:
            kieu, bang = _ap_va_ghi(ns.ra, co, bt, clb, hs)
            kieu_chia[ten_tep(co, bt)] = kieu
            if bt == "CO_LOI":
                bang_loi[ten_tep(co, bt)] = bang
            print("   →", os.path.join(ns.ra, ten_tep(co, bt)))
    _ghi_json(ns.ra, "DQT_BANG_LOI.json", bang_loi)
    _ghi_json(ns.ra, "DQT_KIEU_CHIA.json", kieu_chia)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
