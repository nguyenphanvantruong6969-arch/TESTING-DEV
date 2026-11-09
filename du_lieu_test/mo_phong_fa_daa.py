"""
mo_phong_fa_daa.py  (FA-10)
===========================
So sánh chế độ CŨ (điểm thi + hai quỹ điểm quyết tâm) với FA-DAA (ba loại CLB + huy chương một quỹ) trên CÙNG dữ
liệu mô phỏng, và đo hành vi hai kỳ của khoản bù D1 ("xếp CLB đông lên NV1 cố ý").

    ./.venv/bin/python du_lieu_test/mo_phong_fa_daa.py
    ./.venv/bin/python du_lieu_test/mo_phong_fa_daa.py --n 120 --so-seed 10 --hai-ky 30

CHỈ IN BẢNG SỐ, mỗi bảng ghi "SỐ LIỆU MÔ PHỎNG". KHÔNG có câu nhận định hay kết luận: phần đó do học sinh tự viết.
Mọi dữ liệu là dữ liệu sinh ngẫu nhiên có hạt giống (`random.Random`), không có người thật.

MÔ HÌNH (giả định của mô phỏng, KHÔNG phải số liệu khảo sát)
- Mỗi buổi có K CLB: 1 Tự do, 2 Giới hạn, còn lại Tuyển chọn (điểm sàn 5). Độ "hot" mỗi CLB ~ U(0,1)^2.
- Độ thích của em với CLB = 0,6 * hot + 0,4 * sở thích riêng (U(0,1)); em xếp tối đa L CLB mỗi buổi.
- Năng lực ~ N(0,1); điểm Tuyển chọn = làm tròn(5 + 2,5 * năng lực + U(-1,1)) kẹp 0..10.
- Hành vi: lười (xếp theo độ hot chung, huy chương mặc định), thật thà (xếp theo độ thích thật, mặc định),
  chiến lược (xếp thật, đặt huy chương vào CLB ít hot nhất trong ba CLB đầu).
- Chế độ cũ: mọi CLB có chỉ tiêu thật (cả Tự do); hai quỹ 60/30/10 cho tối đa ba CLB có thi và ba CLB không thi.
- D1 hai kỳ: em lệch xếp CLB Giới hạn hot nhất lên NV1 ở kỳ 1. "Có bù" = thua bốc thăm kỳ 1 thì kỳ 2 được xếp trước
  mọi người trong bốc thăm. Lợi ích = tổng độ thích của CLB nhận được ở hai kỳ (0 nếu không có CLB).
"""

import argparse
import math
import os
import random
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _GOC not in sys.path:
    sys.path.insert(0, _GOC)

import fa_daa  # noqa: E402
import rbda_priority_pipeline as rp  # noqa: E402

NHAN = "SỐ LIỆU MÔ PHỎNG"
HANH_VI = ("luoi", "that_tha", "chien_luoc")
BUOI = ("thu_2", "thu_3")
SO_MAU = 3                     # số huy chương mỗi buổi


def sinh_du_lieu(n=100, seed=0, k=5, l_toi_da=4, ti_le=(0.3, 0.5, 0.2), so_buoi=2):
    """Một trường mô phỏng: CLB, độ hot, học sinh với sở thích, năng lực, hành vi. Cùng (n, seed) -> giống hệt."""
    r = random.Random(seed)
    clubs, fa_clb, hot, buoi_cua = {}, {}, {}, {}
    ds_buoi = list(BUOI[:so_buoi])
    for b in ds_buoi:
        for i in range(k):
            cid = "%s_c%d" % (b, i)
            loai = fa_daa.TU_DO if i == 0 else (fa_daa.GIOI_HAN if i <= 2 else fa_daa.TUYEN_CHON)
            hs = 0.7 if loai == fa_daa.GIOI_HAN else 0.5
            if loai == fa_daa.TU_DO:
                hs = 1.3
            cho = max(2, int(math.ceil(n / k * hs)))
            clubs[cid] = {"capacity": cho, "reserve_capacity": 0, "reserve_group": None, "buoi": b}
            fa_clb[cid] = {"loai": loai, "diem_san": 5 if loai == fa_daa.TUYEN_CHON else None,
                           "so_toi_thieu": None, "suc_chua_phong": None}
            hot[cid] = r.random() ** 2
            buoi_cua[cid] = b
    sids = ["s%03d" % i for i in range(n)]
    hs = {}
    for s in sids:
        hv = r.choices(HANH_VI, weights=ti_le)[0]
        thich = {c: 0.6 * hot[c] + 0.4 * r.random() for c in clubs}
        hs[s] = {"hanh_vi": hv, "thich": thich, "nang_luc": r.gauss(0, 1), "nhieu": {c: r.uniform(-1, 1) for c in clubs}}
    return {"n": n, "seed": seed, "ds_buoi": ds_buoi, "clubs": clubs, "fa_clb": fa_clb, "hot": hot,
            "buoi_cua": buoi_cua, "sids": sids, "hs": hs, "l": l_toi_da}


def _diem_thi(dl, s, c):
    h = dl["hs"][s]
    return int(min(10, max(0, round(5 + 2.5 * h["nang_luc"] + h["nhieu"][c]))))


def dang_ky(dl, hanh_vi_ep=None, lech=None):
    """Nguyện vọng + huy chương + điểm thi của mỗi em. `hanh_vi_ep` {s: hành vi} ghi đè; `lech` = tập em xếp CLB
    Giới hạn hot nhất lên NV1 (D1)."""
    prefs, huy, ticks, diem = {}, {}, {c: [] for c in dl["clubs"]}, {c: {} for c in dl["clubs"]}
    lech = lech or set()
    for s in dl["sids"]:
        h = dl["hs"][s]
        hv = (hanh_vi_ep or {}).get(s, h["hanh_vi"])
        ds = []
        for b in dl["ds_buoi"]:
            cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
            khoa = (lambda c: -dl["hot"][c]) if hv == "luoi" else (lambda c: -h["thich"][c])
            top = sorted(cs, key=lambda c: (khoa(c), c))[:dl["l"]]
            if s in lech:
                gh = [c for c in cs if dl["fa_clb"][c]["loai"] == fa_daa.GIOI_HAN]
                if gh:
                    nong = max(gh, key=lambda c: (dl["hot"][c], c))
                    top = [nong] + [c for c in top if c != nong]
            ds += top
            mc = [c for c in top if dl["fa_clb"][c]["loai"] != fa_daa.TU_DO][:SO_MAU]
            if hv == "chien_luoc":
                mc = sorted(mc, key=lambda c: (dl["hot"][c], c))
            huy.setdefault(s, {}).update(dict(zip(mc, (60, 30, 10))))
        prefs[s] = ds
        for c in ds:
            if dl["fa_clb"][c]["loai"] == fa_daa.TUYEN_CHON:
                ticks[c].append(s)
                diem[c][s] = float(_diem_thi(dl, s, c))
    return prefs, huy, ticks, diem


def _stb(dl, seed, truoc=()):
    """Bốc thăm có hạt giống; `truoc` = những em được xếp trước mọi người (khoản bù D1)."""
    r = random.Random("stb-%d-%d" % (dl["seed"], seed))
    ds = sorted(dl["sids"])
    r.shuffle(ds)
    ds = [s for s in ds if s in truoc] + [s for s in ds if s not in truoc]
    return {s: i + 1 for i, s in enumerate(ds)}


def _bo(dl, prefs, ticks, diem, stb):
    students = {s: {"stb": stb[s], "reserve_group": None} for s in dl["sids"]}
    tested = {c: dict(diem.get(c, {})) for c in dl["clubs"]}
    return dict(students=students, clubs=dl["clubs"], tested_scores=tested,
                applicants=rp.hop_ung_vien(ticks, prefs), preferences=prefs, stb_lottery=stb)


def chay_fa(dl, prefs, huy, ticks, diem, seed, stb=None):
    stb = stb or _stb(dl, seed)
    bo = _bo(dl, prefs, ticks, diem, stb)
    kq = fa_daa.chay_fa_daa(fa_clb=dl["fa_clb"], giu_cho=[], huy_chuong=huy, seed=seed, **bo)
    ly_do = fa_daa.ly_do_ket_qua(kq, prefs, huy, dl["fa_clb"])
    return kq.ket_qua.assignment, ly_do


def diem_cu(dl, prefs, ticks):
    """Hai quỹ cũ mỗi buổi: quỹ 1 cho CLB có thi, quỹ 2 cho CLB không thi; mỗi quỹ 60/30/10 cho tối đa ba CLB đầu."""
    ra = {}
    for s, ds in prefs.items():
        for b in dl["ds_buoi"]:
            trong = [c for c in ds if dl["buoi_cua"][c] == b]
            co = [c for c in trong if s in ticks.get(c, ())][:SO_MAU]
            khong = [c for c in trong if s not in ticks.get(c, ())][:SO_MAU]
            for nhom in (co, khong):
                for c, d in zip(nhom, (60, 30, 10)):
                    ra.setdefault(s, {})[c] = d
    return ra


def chay_cu(dl, prefs, ticks, diem, seed):
    stb = _stb(dl, seed)
    bo = _bo(dl, prefs, ticks, diem, stb)
    kq = rp.run_rbda_nhieu_buoi(is_reserve_eligible_fn=lambda s, c: False, seed=seed,
                                diem_wharton=diem_cu(dl, prefs, ticks), **bo)
    return kq.assignment


def _vi_tri(dl, s, buoi):
    """Danh sách THẬT của em trong buổi (theo độ thích), không phụ thuộc cách em khai."""
    th = dl["hs"][s]["thich"]
    return sorted((c for c in dl["clubs"] if dl["buoi_cua"][c] == buoi), key=lambda c: (-th[c], c))


def _dem_tc(dl, assignment, cong):
    """Cộng dồn: số em-buổi, được NV1 thật, nằm top 2 thật, không có CLB."""
    for s, theo in assignment.items():
        for b in dl["ds_buoi"]:
            c = theo.get(b)
            cong["tong"] += 1
            ds = _vi_tri(dl, s, b)
            if c is None:
                cong["khong"] += 1
            else:
                cong["nv1"] += c == ds[0]
                cong["top2"] += c in ds[:2]


def so_sanh(n=100, so_seed=5, seed0=0):
    """Bảng 1 (cũ vs FA), bảng 2 (lý do FA), bảng 3 (thua bốc thăm theo hành vi). Chỉ số, không nhận định."""
    cong = {m: dict(tong=0, nv1=0, top2=0, khong=0) for m in ("cu", "fa")}
    ly_do_dem, tong_dong = {}, 0
    thua, dem_hv = {h: 0 for h in HANH_VI}, {h: 0 for h in HANH_VI}
    for sd in range(seed0, seed0 + so_seed):
        dl = sinh_du_lieu(n=n, seed=sd)
        prefs, huy, ticks, diem = dang_ky(dl)
        _dem_tc(dl, chay_cu(dl, prefs, ticks, diem, sd), cong["cu"])
        asg, ly_do = chay_fa(dl, prefs, huy, ticks, diem, sd)
        _dem_tc(dl, asg, cong["fa"])
        for r in ly_do:
            k = (r["outcome"], r["reason"])
            ly_do_dem[k] = ly_do_dem.get(k, 0) + 1
            tong_dong += 1
        bi_thua = {r["student_id"] for r in ly_do if r["reason"] == "LOTTERY" and r["outcome"] == "REJECTED"}
        for s in dl["sids"]:
            dem_hv[dl["hs"][s]["hanh_vi"]] += 1
            thua[dl["hs"][s]["hanh_vi"]] += s in bi_thua

    def pt(a, b):
        return round(100.0 * a / b, 1) if b else 0.0
    b1 = [{"che_do": m, "pt_nv1": pt(c["nv1"], c["tong"]), "pt_top2": pt(c["top2"], c["tong"]),
           "pt_khong_clb": pt(c["khong"], c["tong"]), "nhan": NHAN}
          for m, c in (("cu_diem_hai_quy", cong["cu"]), ("fa_daa", cong["fa"]))]
    b2 = [{"ket_qua": o, "ly_do": ly, "pt_dong": pt(v, tong_dong), "nhan": NHAN}
          for (o, ly), v in sorted(ly_do_dem.items())]
    b3 = [{"hanh_vi": h, "pt_thua_boc_tham_fa": pt(thua[h], dem_hv[h]), "nhan": NHAN} for h in HANH_VI]
    return {"so_sanh": b1, "ly_do": b2, "boc_tham_theo_hanh_vi": b3}


def hai_ky(n=60, so_seed=3, so_mau=15, seed0=0):
    """D1: tỉ lệ em MÀ việc xếp CLB hot nhất lên NV1 ở kỳ 1 có lợi hơn thật thà cả hai kỳ, không bù và có bù.
    Một buổi, mọi người khác thật thà. Chỉ đo, KHÔNG cài khoản bù vào phần mềm."""
    tong = dict(mau=0, co_lech=0, loi_khong_bu=0, loi_co_bu=0, thua_ky1=0)
    for sd in range(seed0, seed0 + so_seed):
        dl = sinh_du_lieu(n=n, seed=sd, so_buoi=1, ti_le=(0.0, 1.0, 0.0))

        def lai(c, s, b):
            return dl["hs"][s]["thich"][c] if c else 0.0

        pr, hu, tk, di = dang_ky(dl)
        asg1, _ = chay_fa(dl, pr, hu, tk, di, sd)
        asg2, _ = chay_fa(dl, pr, hu, tk, di, sd + 1000)
        for s in sorted(dl["sids"])[:so_mau]:
            tong["mau"] += 1
            u_that = lai(asg1[s].get("thu_2"), s, "thu_2") + lai(asg2[s].get("thu_2"), s, "thu_2")
            pr_l, hu_l, tk_l, di_l = dang_ky(dl, lech={s})
            if pr_l[s] == pr[s]:
                continue                                    # đã xếp CLB đó NV1 sẵn: lệch không đổi gì
            tong["co_lech"] += 1
            a1, ly = chay_fa(dl, pr_l, hu_l, tk_l, di_l, sd)
            nong = pr_l[s][0]
            thua = a1[s].get("thu_2") != nong
            tong["thua_ky1"] += thua
            u1 = lai(a1[s].get("thu_2"), s, "thu_2")
            tong["loi_khong_bu"] += (u1 + lai(asg2[s].get("thu_2"), s, "thu_2")) > u_that + 1e-12
            if thua:
                a2, _ = chay_fa(dl, pr, hu, tk, di, sd + 1000, stb=_stb(dl, sd + 1000, truoc={s}))
                tong["loi_co_bu"] += (u1 + lai(a2[s].get("thu_2"), s, "thu_2")) > u_that + 1e-12
            else:
                tong["loi_co_bu"] += (u1 + lai(asg2[s].get("thu_2"), s, "thu_2")) > u_that + 1e-12

    def pt(a, b):
        return round(100.0 * a / b, 1) if b else 0.0
    return {"hai_ky": [
        {"dieu_kien": "khong_bu", "so_em_mau": tong["mau"], "so_em_co_lech": tong["co_lech"],
         "so_thua_ky_1": tong["thua_ky1"], "so_em_co_loi": tong["loi_khong_bu"],
         "pt_co_loi_tren_mau": pt(tong["loi_khong_bu"], tong["mau"]), "nhan": NHAN},
        {"dieu_kien": "co_bu", "so_em_mau": tong["mau"], "so_em_co_lech": tong["co_lech"],
         "so_thua_ky_1": tong["thua_ky1"], "so_em_co_loi": tong["loi_co_bu"],
         "pt_co_loi_tren_mau": pt(tong["loi_co_bu"], tong["mau"]), "nhan": NHAN}]}


def chay_mo_phong(n=100, so_seed=5, so_mau=15, n_hai_ky=60, seed0=0):
    """Toàn bộ bảng. Cùng tham số -> giống hệt."""
    ra = so_sanh(n=n, so_seed=so_seed, seed0=seed0)
    ra.update(hai_ky(n=n_hai_ky, so_seed=max(1, so_seed // 2), so_mau=so_mau, seed0=seed0))
    return ra


def in_bang(ten, dong):
    if not dong:
        return ""
    cot = [c for c in dong[0]]
    ra = ["### %s — %s" % (ten, NHAN), "| " + " | ".join(cot) + " |", "|" + "---|" * len(cot)]
    ra += ["| " + " | ".join(str(d[c]) for c in cot) + " |" for d in dong]
    return "\n".join(ra) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--so-seed", type=int, default=5)
    ap.add_argument("--hai-ky", type=int, default=15, help="số em mẫu mỗi seed cho bảng hai kỳ")
    a = ap.parse_args(argv)
    kq = chay_mo_phong(n=a.n, so_seed=a.so_seed, so_mau=a.hai_ky)
    for ten, dong in kq.items():
        print(in_bang(ten, dong))


if __name__ == "__main__":
    main()
