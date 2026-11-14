# -*- coding: utf-8 -*-
"""FA-SC diễn tập I4 (phần tách): sau khi công bố, MỘT em đến muộn được nạp thêm, và em này xếp CLB Tự do ở nguyện
vọng 1 của mọi ngày nên KHÔNG tranh chỗ của ai. Em cũ có đổi CLB không? Nếu có thì thay đổi đó không do tranh chỗ mà
do bộ số bốc thăm THEO NGÀY (`sinh_stb_theo_buoi`, chế độ `stb_ngay`) được tính lại khi số học sinh đổi.
Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c


def _so_theo_ngay(api):
    d = api.get_so_boc_tham_theo_buoi()["data"]
    return {b: {h["student_id"]: h["so"][b] for h in d["hoc_sinh"] if h["so"].get(b) is not None}
            for b in d["ds_buoi"]}, d["che_do"]


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    day_du = c.sinh_dot(so_hs, seed)
    loai = c.de_fa()[1]
    muon = day_du["hs"][-1]
    for b, xs in muon["nv"].items():                     # em muộn: CLB Tự do đứng đầu mọi ngày, không thi
        muon["nv"][b] = sorted(xs, key=lambda x: loai[x] != "TU_DO")
    muon["thi"] = {}
    som = copy.deepcopy(day_du)
    som["hs"] = som["hs"][:-1]
    r = c.chay(som, os.path.join(ra, "lan_1"), seed)
    api, db = r["api"], r["db"]
    goc_truoc = dict(c.sql(db, "SELECT student_id, stb_number FROM students"))
    ngay_truoc, che_do = _so_theo_ngay(api)
    c.chuyen_va_nap_them(api, day_du, os.path.join(ra, "lan_2"), r["de"], r["loai"])
    kq = api.run_pipeline(seed=seed)
    sau = c.ket_qua(db)
    goc_sau = dict(c.sql(db, "SELECT student_id, stb_number FROM students"))
    ngay_sau, _ = _so_theo_ngay(api)
    cu = sorted(goc_truoc, key=goc_truoc.get)
    ngay_giu = sum(1 for b in ngay_truoc
                   if sorted(ngay_truoc[b], key=ngay_truoc[b].get) == sorted(ngay_truoc[b], key=ngay_sau[b].get))
    o_doi, em_doi = c.so_sanh(r["ket_qua"], sau, bo_qua=(muon["sid"],))
    return c.in_bang("d16 I4 một em đến muộn KHÔNG tranh chỗ", [
        ("chạy lại ok / chế độ bốc thăm", "%s / %s" % (kq["ok"], che_do)),
        ("em muộn được xếp vào CLB Tự do ở mọi ngày", all(loai[v] == "TU_DO" for k, v in sau.items() if k[0] == muon["sid"])),
        ("thứ tự số bốc thăm GỐC giữa các em cũ giữ nguyên", cu == sorted(cu, key=goc_sau.get)),
        ("số ngày mà thứ tự số bốc thăm THEO NGÀY giữa các em cũ giữ nguyên", "%d / %d" % (ngay_giu, len(ngay_truoc))),
        ("em CŨ (đã công bố) đổi CLB", em_doi),
        ("lượt (em cũ, ngày) đổi CLB", o_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
