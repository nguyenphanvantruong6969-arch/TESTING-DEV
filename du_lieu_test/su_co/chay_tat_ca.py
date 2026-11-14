# -*- coding: utf-8 -*-
"""FA-SC: chạy mọi kịch bản diễn tập `dNN_*.py` trong thư mục này và ghi `KET_QUA_DIEN_TAP.md` vào `--ra`.

    python du_lieu_test/su_co/chay_tat_ca.py --ra THU_MUC_TAM [--seed 42] [--so-hs 120]

Tất định theo `--seed`. Mọi số là SỐ LIỆU MÔ PHỎNG (học sinh giả, sinh ngẫu nhiên có hạt giống); không phải khảo sát
thật. Chỉ đọc mã sản phẩm; mọi tệp ghi vào `--ra` (đừng trỏ vào thư mục có `app.db` thật)."""
import glob
import importlib
import os
import sys

import chung as c


def chay_tat_ca(ra, seed=c.SEED, so_hs=c.SO_HS):
    ket = []
    for duong in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "d[0-9][0-9]_*.py"))):
        ten = os.path.splitext(os.path.basename(duong))[0]
        mod = importlib.import_module(ten)
        thu_muc = os.path.join(ra, ten)
        os.makedirs(thu_muc)
        ket.append((ten, mod.dien_tap(thu_muc, seed, so_hs)))
    dong = ["# FA-SC: kết quả diễn tập (SỐ LIỆU MÔ PHỎNG)", "",
            "Sinh bởi `du_lieu_test/su_co/chay_tat_ca.py`, seed %d, %d học sinh giả. Không phải số liệu thật." % (seed, so_hs),
            ""]
    for ten, kq in ket:
        dong += ["## %s (`%s.py`)" % (kq["ten"], ten), "", "| Đo | Giá trị |", "|---|---|"]
        dong += ["| %s | %s |" % (k, v) for k, v in kq["so_lieu"]]
        dong.append("")
    duong_md = os.path.join(ra, "KET_QUA_DIEN_TAP.md")
    with open(duong_md, "w", encoding="utf-8") as f:
        f.write("\n".join(dong))
    print("Đã ghi %s" % duong_md)
    return ket


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    def _tat_ca(ra, seed, so_hs):
        return chay_tat_ca(ra, seed, so_hs)

    c.main(_tat_ca, __doc__)
