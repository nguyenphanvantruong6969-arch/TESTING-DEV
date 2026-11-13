"""
fable_ga2_giai_phap.py — research script for memo section G-A.2 (docs/fable/03_RESEARCH_MEMO.md). NOT production
code; reads `fa_daa` / `rbda_priority_pipeline` read-only. All data is SIMULATED (seeded generators, no real
students). Prints tables only, no commentary.

    python du_lieu_test/fable_ga2_giai_phap.py f1          # minimum-quota rules: misreport search + school size
    python du_lieu_test/fable_ga2_giai_phap.py f3          # group priority + FA: reserve and reason-key checks
    python du_lieu_test/fable_ga2_giai_phap.py f2          # medal designs at school size (population)
    python du_lieu_test/fable_ga2_giai_phap.py f2_br       # medal designs: sampled best response (slow)
    python du_lieu_test/fable_ga2_giai_phap.py boc_tham    # cross-day lottery variants

SCHOOL-SIZE MODEL (`sinh_truong`; assumptions of the simulation, not survey data)
- n = 800 students, 3 days, 7 clubs per day: 1 FREE, 2 LIMITED, 4 SELECTIVE (pass mark 5). Lists: 6 of 7 per day.
- Non-FREE seats per day = 70 % of n, split equally. Club "hotness" ~ U(0,1), FREE clubs x 0.5.
- Liking = 0.5 * hot + 0.5 * own taste U(0,1). Ability, scores and behaviour types as in `mo_phong_fa_daa.py`.
"""

import copy
import itertools
import math
import os
import random
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_GOC, os.path.join(_GOC, "du_lieu_test"), os.path.join(_GOC, "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fa_daa  # noqa: E402
import mo_phong_fa_daa as mp  # noqa: E402
import rbda_priority_pipeline as rp  # noqa: E402

NHAN = "SỐ LIỆU MÔ PHỎNG"
BUOI3 = ("thu_2", "thu_3", "thu_4")
TD, GH, TC = fa_daa.TU_DO, fa_daa.GIOI_HAN, fa_daa.TUYEN_CHON


# ============================================================================ F1: minimum quota rules
def _du_dieu_kien(bo, s, c):
    f = bo["fa_clb"][c]
    if f["loai"] != TC:
        return True
    d = bo["tested_scores"].get(c, {}).get(s)
    return d is not None and d >= (f["diem_san"] or 0)


def dong_truoc(bo):
    """Rule E ("hopeless clubs only", decided BEFORE the lottery, one pass, no order): close club C when the number
    of eligible students who list C ABOVE every FREE club of that day is below `so_toi_thieu`. Returns a new `bo`
    with C removed from every list and all minimums cleared, plus the list of closed clubs."""
    bo = copy.deepcopy(bo)
    dong = []
    for c, f in bo["fa_clb"].items():
        if f["loai"] == TD or not f["so_toi_thieu"]:
            continue
        b = bo["clubs"][c]["buoi"]
        dem = 0
        for s, ds in bo["preferences"].items():
            ngay = [x for x in ds if bo["clubs"][x]["buoi"] == b]
            if c not in ngay or not _du_dieu_kien(bo, s, c):
                continue
            truoc = ngay[:ngay.index(c)]
            dem += not any(bo["fa_clb"][x]["loai"] == TD for x in truoc)
        if dem < f["so_toi_thieu"]:
            dong.append(c)
    for c in dong:
        for ds in bo["preferences"].values():
            if c in ds:
                ds.remove(c)
        bo["applicants"][c] = []
    for f in bo["fa_clb"].values():
        f["so_toi_thieu"] = None
    return bo, dong


def _chay_che_do(bo, che_do, seed):
    if che_do == "D3":
        return fa_daa.chay_fa_daa(**copy.deepcopy(bo), seed=seed)
    if che_do == "E":
        return fa_daa.chay_fa_daa(**dong_truoc(bo)[0], seed=seed)
    bo2 = copy.deepcopy(bo)                                   # "none": minimums ignored
    for f in bo2["fa_clb"].values():
        f["so_toi_thieu"] = None
    return fa_daa.chay_fa_daa(**bo2, seed=seed)


def _hang_ngay(kq, s, thuc_ngay, b):
    c = kq.ket_qua.assignment[s].get(b)
    return thuc_ngay.index(c) if c in thuc_ngay else len(thuc_ngay)


def f1_tim_lech(so_seed=200):
    """Per rule: students who strictly gain on some day by reporting ANY ordered sub-list of that day's clubs
    (reorder, drop, or ADD clubs they did not list), other days truthful, medals fixed."""
    import test_fa_tinh_chat as t
    print("### F1-a Rank-misreport search incl. added clubs — %s" % NHAN)
    print("| rule | instances | instances with a profitable misreport | student-days tried | student-days that gain |"
          " clubs closed | open clubs below their minimum |")
    print("|---|---|---|---|---|---|---|")
    for che_do in ("D3", "E", "none"):
        n_bo = bo_loi = n_thu = n_loi = n_dong = n_thieu = 0
        for seed in range(so_seed):
            bo = t._bo(seed, toi_thieu=True)
            goc = _chay_che_do(bo, che_do, seed)
            n_bo += 1
            dem = {}
            for theo in goc.ket_qua.assignment.values():
                for c in theo.values():
                    dem[c] = dem.get(c, 0) + 1
            dong = {d["club_id"] for d in goc.dong_cua} | (set(dong_truoc(bo)[1]) if che_do == "E" else set())
            n_dong += len(dong)
            n_thieu += sum(1 for c, f in bo["fa_clb"].items() if f["loai"] != TD and f["so_toi_thieu"]
                           and c not in dong and 0 < dem.get(c, 0) < f["so_toi_thieu"])
            co = False
            for s, ds in bo["preferences"].items():
                for b in sorted({bo["clubs"][c]["buoi"] for c in bo["clubs"]}):
                    thuc = [c for c in ds if bo["clubs"][c]["buoi"] == b]
                    cs = [c for c in bo["clubs"] if bo["clubs"][c]["buoi"] == b]
                    if len(cs) > 4:
                        continue
                    n_thu += 1
                    r0 = _hang_ngay(goc, s, thuc, b)
                    khac = [c for c in ds if bo["clubs"][c]["buoi"] != b]
                    loi = False
                    for k in range(len(cs) + 1):
                        for hv in itertools.permutations(cs, k):
                            if list(hv) == thuc:
                                continue
                            bo2 = copy.deepcopy(bo)
                            bo2["preferences"][s] = list(hv) + khac
                            if _hang_ngay(_chay_che_do(bo2, che_do, seed), s, thuc, b) < r0:
                                loi = True
                                break
                        if loi:
                            break
                    n_loi += loi
                    co = co or loi
            bo_loi += co
        print("| %s | %d | %d | %d | %d | %d | %d |" % (che_do, n_bo, bo_loi, n_thu, n_loi, n_dong, n_thieu))


def sinh_truong(n=800, seed=0, k=7, so_buoi=3, ti_le=(0.3, 0.5, 0.2), ti_le_cho=0.7, hanh_vi=mp.HANH_VI):
    r = random.Random("truong-%d" % seed)
    clubs, fa_clb, hot, buoi_cua = {}, {}, {}, {}
    ds_buoi = list(BUOI3[:so_buoi])
    cho = int(math.ceil(n * ti_le_cho / (k - 1)))
    for b in ds_buoi:
        for i in range(k):
            cid = "%s_c%d" % (b, i)
            loai = TD if i == 0 else (GH if i <= 2 else TC)
            clubs[cid] = {"capacity": n if loai == TD else cho, "reserve_capacity": 0, "reserve_group": None, "buoi": b}
            fa_clb[cid] = {"loai": loai, "diem_san": 5 if loai == TC else None, "so_toi_thieu": None,
                           "suc_chua_phong": None}
            hot[cid] = r.random() * (0.5 if loai == TD else 1.0)
            buoi_cua[cid] = b
    sids = ["s%04d" % i for i in range(n)]
    hs = {}
    for s in sids:
        hv = r.choices(hanh_vi, weights=ti_le)[0]
        hs[s] = {"hanh_vi": hv, "thich": {c: 0.5 * hot[c] + 0.5 * r.random() for c in clubs},
                 "nang_luc": r.gauss(0, 1), "nhieu": {c: r.uniform(-1, 1) for c in clubs}}
    return {"n": n, "seed": seed, "ds_buoi": ds_buoi, "clubs": clubs, "fa_clb": fa_clb, "hot": hot,
            "buoi_cua": buoi_cua, "sids": sids, "hs": hs, "l": k - 1}


def _stb_ngau_nhien(dl, khoa):
    ds = sorted(dl["sids"])
    random.Random("stb-%s" % (khoa,)).shuffle(ds)
    return {s: i + 1 for i, s in enumerate(ds)}


def chay1(dl, b, prefs, huy, ticks, diem, stb, fa_clb=None):
    """One day, cut by hand so the supplied lottery is used as is (single-day short-circuit of the core)."""
    fa_clb = fa_clb or dl["fa_clb"]
    cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
    tap = set(cs)
    pr = {s: [c for c in prefs[s] if c in tap] for s in dl["sids"]}
    kq = fa_daa.chay_fa_daa(
        students={s: {"stb": stb[s], "reserve_group": None} for s in dl["sids"]},
        clubs={c: dl["clubs"][c] for c in cs}, tested_scores={c: dict(diem.get(c, {})) for c in cs},
        applicants=rp.hop_ung_vien({c: ticks.get(c, []) for c in cs}, pr), preferences=pr, stb_lottery=stb,
        fa_clb={c: fa_clb[c] for c in cs}, giu_cho=[],
        huy_chuong={s: {c: v for c, v in (huy.get(s) or {}).items() if c in tap} for s in dl["sids"]}, seed=0)
    return {s: next(iter(v.values()), None) for s, v in kq.ket_qua.assignment.items()}, kq, pr


def f1_truong(so_seed=20, toi_thieu=25):
    """School size: every non-FREE club gets `so_toi_thieu`; compare the three rules on the same data and lottery."""
    print("\n### F1-b School-size comparison of minimum rules (minimum %d per non-FREE club) — %s" % (toi_thieu, NHAN))
    print("| rule | club-days closed | open club-days below minimum | students in a club below minimum |"
          " mean utility | % true NV1 | DA runs per day (max) | club-days within 1 of the minimum (pivot zone) |")
    print("|---|---|---|---|---|---|---|---|")
    for che_do in ("D3", "E", "none"):
        dong = thieu = hs_thieu = lan = sat = 0
        u = nv1 = tong = 0
        for sd in range(so_seed):
            dl = sinh_truong(seed=sd)
            prefs, huy, ticks, diem = mp.dang_ky(dl)
            fa = copy.deepcopy(dl["fa_clb"])
            for f in fa.values():
                if f["loai"] != TD:
                    f["so_toi_thieu"] = toi_thieu
            for b in dl["ds_buoi"]:
                stb = _stb_ngau_nhien(dl, (sd, b))
                fa_b, pr_b, da_dong = fa, prefs, []
                if che_do != "D3":
                    cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
                    bo = dict(fa_clb={c: fa[c] for c in cs}, clubs={c: dl["clubs"][c] for c in cs},
                              tested_scores=diem, preferences={s: [c for c in prefs[s] if c in cs] for s in dl["sids"]},
                              applicants={c: [] for c in cs})
                    if che_do == "E":
                        bo2, da_dong = dong_truoc(bo)
                        pr_b = bo2["preferences"]
                    fa_b = copy.deepcopy(fa)
                    for f in fa_b.values():
                        f["so_toi_thieu"] = None
                a, kq, _ = chay1(dl, b, pr_b, huy, ticks, diem, stb, fa_clb=fa_b)
                dong += len(kq.dong_cua) + len(da_dong)
                lan = max(lan, len(kq.dong_cua) + 1)
                dem = {}
                for c in a.values():
                    dem[c] = dem.get(c, 0) + 1
                for c, m in dem.items():
                    sat += bool(c) and dl["fa_clb"][c]["loai"] != TD and abs(m - toi_thieu) <= 1
                    if c and dl["fa_clb"][c]["loai"] != TD and m < toi_thieu:
                        thieu += 1
                        hs_thieu += m
                for s in dl["sids"]:
                    vt = mp._vi_tri(dl, s, b)
                    tong += 1
                    u += dl["hs"][s]["thich"][a[s]] if a[s] else 0
                    nv1 += a[s] == vt[0]
        print("| %s | %d | %d | %d | %.4f | %.1f | %d | %d |" % (che_do, dong, thieu, hs_thieu, u / tong, 100 * nv1 / tong, lan, sat))
    print("(%d data seeds x 3 days x 6 non-FREE clubs = %d club-days)" % (so_seed, so_seed * 18))


# ============================================================================ F3: group priority with FA
def f3(so_seed=300):
    """Random small instances + random groups. Current call (bo_qua_du_tru=True, as the pipeline passes with strict
    groups) vs candidate (bo_qua_du_tru=False). Checks: blocking pairs; reservations honoured; every rejected
    student's candidate key (-reserved, group, -score, -medal, lottery) is not better than the worst admitted."""
    import test_fa_tinh_chat as t
    print("### F3 Group priority + FA-DAA on %d random instances — %s" % (so_seed, NHAN))
    print("| call | blocking pairs (instances) | usable reservations | reservations NOT honoured |"
          " rejections checked | rejections contradicting key (-reserved, group, -score, -medal, lottery) |"
          " `ly_do_ket_qua` raises (instances) | wrong reason code vs first differing key element |")
    print("|---|---|---|---|---|---|---|---|")
    for ten, bq in (("current: bo_qua_du_tru=True", True), ("candidate: bo_qua_du_tru=False", False)):
        n_bat = n_gc = n_gc_sai = n_tc = n_tc_sai = n_nem = n_ma_sai = 0
        for seed in range(so_seed):
            bo = t._bo(seed)
            r = random.Random(7000 + seed)
            tier = {s: r.randint(0, 2) for s in bo["students"]}
            kq = fa_daa.chay_fa_daa(**copy.deepcopy(bo), seed=seed, tier_rank=tier, bo_qua_du_tru=bq)
            vs = rp.verify_stability_tuan(kq.ket_qua, kq.clubs, kq.preferences, kq.reserve_fn, bo_qua_du_tru=bq)
            n_bat += any(vs.values())
            ly = None
            try:
                ly = fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])
            except ValueError:
                n_nem += 1
            asg = kq.ket_qua.assignment
            for (c, s) in set(bo["giu_cho"]):
                if bo["fa_clb"][c]["loai"] == TD or c not in kq.preferences.get(s, []):
                    continue
                n_gc += 1
                b = bo["clubs"][c]["buoi"]
                ngay = [x for x in kq.preferences[s] if bo["clubs"][x]["buoi"] == b]
                co = asg[s].get(b)
                n_gc_sai += not (co in ngay and ngay.index(co) <= ngay.index(c))

            def khoa(s, c, b):
                d = kq.tested_scores.get(c, {}).get(s) if bo["fa_clb"][c]["loai"] == TC else None
                return (-(1 if kq.reserve_fn(s, c) else 0), tier[s], -(d or 0),
                        -(bo["huy_chuong"].get(s) or {}).get(c, 0), kq.ket_qua.stb_theo_buoi[b][s])

            tv = {}
            for s, theo in asg.items():
                for b, c in theo.items():
                    if c:
                        tv.setdefault(c, []).append(s)
            ma = ("RESERVED", "GROUP", "SCORE", "MEDAL", "LOTTERY")
            dung = {}
            for s, ds in kq.preferences.items():
                for b in asg[s]:
                    ngay = [x for x in ds if bo["clubs"][x]["buoi"] == b]
                    co = asg[s].get(b)
                    for c in (ngay[:ngay.index(co)] if co in ngay else ngay):
                        n_tc += 1
                        ks, km = khoa(s, c, b), max(khoa(m, c, b) for m in tv[c])
                        n_tc_sai += ks < km
                        dung[(s, c)] = next(ma[i] for i in range(5) if ks[i] != km[i])
            if ly is not None:
                n_ma_sai += sum(1 for x in ly if x["outcome"] == "REJECTED"
                                and dung.get((x["student_id"], x["club_id"])) not in (None, x["reason"]))
        print("| %s | %d | %d | %d | %d | %d | %d | %d |" % (ten, n_bat, n_gc, n_gc_sai, n_tc, n_tc_sai, n_nem, n_ma_sai))


if __name__ == "__main__":
    for _l in (sys.stdout, sys.stderr):
        if hasattr(_l, "reconfigure"):
            _l.reconfigure(encoding="utf-8", errors="replace")
    lenh = sys.argv[1] if len(sys.argv) > 1 else "f1"
    if lenh == "f1":
        f1_tim_lech()
        f1_truong()
    elif lenh == "f3":
        f3()
    else:
        import fable_ga2_huy_chuong as hc
        {"f2": hc.f2, "f2_br": hc.f2_br, "boc_tham": hc.boc_tham}[lenh]()
