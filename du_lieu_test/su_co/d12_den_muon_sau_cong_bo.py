# -*- coding: utf-8 -*-
"""FA-SC diễn tập I4 / S8: đã chạy và công bố, rồi 5 em đăng ký muộn được nạp thêm và chạy lại (bốc thăm đã khoá).
Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

SO_MUON = 5


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    day_du = c.sinh_dot(so_hs, seed)
    muon = [h["sid"] for h in day_du["hs"][-SO_MUON:]]
    som = copy.deepcopy(day_du)
    som["hs"] = som["hs"][:-SO_MUON]
    r = c.chay(som, os.path.join(ra, "lan_1"), seed)
    api, db = r["api"], r["db"]
    stb_truoc = dict(c.sql(db, "SELECT student_id, stb_number FROM students"))
    nap = c.chuyen_va_nap_them(api, day_du, os.path.join(ra, "lan_2"), r["de"], r["loai"])
    kq = api.run_pipeline(seed=seed)
    sau = c.ket_qua(db)
    stb_sau = dict(c.sql(db, "SELECT student_id, stb_number FROM students"))
    cu = sorted(stb_truoc, key=stb_truoc.get)
    giu_thu_tu = cu == sorted(cu, key=stb_sau.get)
    o_doi, em_doi = c.so_sanh(r["ket_qua"], sau, bo_qua=muon)
    xuong = sum(1 for k, v in r["ket_qua"].items()
                if k[0] not in muon and sau.get(k) != v and r["loai"][v] != "TU_DO" and r["loai"].get(sau.get(k)) == "TU_DO")
    return c.in_bang("d12 I4 %d em đến muộn sau khi công bố" % SO_MUON, [
        ("nạp thêm ok / chạy lại ok", "%s / %s" % (nap["ok"], kq["ok"])),
        ("thứ tự bốc thăm giữa các em cũ giữ nguyên (bất biến 3)", giu_thu_tu),
        ("run_history có mấy dòng (bất biến 4)", c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0]),
        ("em CŨ (đã công bố) đổi CLB", em_doi),
        ("lượt em cũ rớt từ CLB có chỉ tiêu xuống CLB Tự do", xuong),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
