"""
fable_ga_kiem.py — research script for goal G-A (docs/fable/03_RESEARCH_MEMO.md). NOT production code.
Reads `fa_daa.chay_fa_daa` and `du_lieu_test/mo_phong_fa_daa.py` read-only. All data is SIMULATED
(seeded random generators, no real students). Prints tables only, no commentary.

    python du_lieu_test/fable_ga_kiem.py phan_vi_du      # smallest counterexamples (D3, reasons)
    python du_lieu_test/fable_ga_kiem.py tim_lech        # random search for profitable rank misreports
    python du_lieu_test/fable_ga_kiem.py huy_chuong      # medal best response by behaviour type
    python du_lieu_test/fable_ga_kiem.py quan_the        # population view: who loses
"""

import copy
import itertools
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
GT = (60, 30, 10)


# ----------------------------------------------------------------------------- tiny instances
def _nho(clb, hs, giu_cho=()):
    """clb {cid: (loai, capacity, diem_san, so_toi_thieu)}; hs {sid: (stb, [prefs], {cid: score})}."""
    clubs = {c: {"capacity": v[1], "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"}
             for c, v in clb.items()}
    fa = {c: {"loai": v[0], "diem_san": v[2], "so_toi_thieu": v[3], "suc_chua_phong": None}
          for c, v in clb.items()}
    students = {s: {"stb": v[0], "reserve_group": None} for s, v in hs.items()}
    prefs = {s: list(v[1]) for s, v in hs.items()}
    diem = {c: {} for c in clb}
    ticks = {c: [] for c in clb}
    huy = {}
    for s, v in hs.items():
        for c, d in v[2].items():
            diem[c][s] = float(d)
            ticks[c].append(s)
        mc = [c for c in v[1] if clb[c][0] != "TU_DO"][:3]          # default medals (D2)
        huy[s] = dict(zip(mc, GT))
    return dict(students=students, clubs=clubs, tested_scores=diem,
                applicants=rp.hop_ung_vien(ticks, prefs), preferences=prefs,
                stb_lottery={s: v[0] for s, v in hs.items()}, fa_clb=fa, giu_cho=list(giu_cho),
                huy_chuong=huy)


def _kq(bo, **kw):
    kq = fa_daa.chay_fa_daa(**copy.deepcopy(bo), **kw)
    return {s: next(iter(v.values()), None) for s, v in kq.ket_qua.assignment.items()}, kq


def phan_vi_du():
    print("## CE1: D3 closing loop, profitable rank misreport (2 students)")
    clb = {"A": ("TUYEN_CHON", 1, 5, None), "C": ("GIOI_HAN", 2, None, 2), "F": ("TU_DO", 1, None, None)}
    that = {"s": (2, ["A", "C", "F"], {"A": 8}), "t": (1, ["C", "A", "F"], {"A": 9})}
    a, kq = _kq(_nho(clb, that))
    print("truthful  s:A>C>F t:C>A>F ->", a, "closed:", [d["club_id"] for d in kq.dong_cua])
    lech = dict(that, s=(2, ["C", "A", "F"], {"A": 8}))
    bo = _nho(clb, lech)
    bo["huy_chuong"]["s"] = {"A": 60, "C": 30}                      # medals unchanged: only rank moves
    a2, kq2 = _kq(bo)
    print("misreport s:C>A>F          ->", a2, "closed:", [d["club_id"] for d in kq2.dong_cua])

    print("\n## CE2: D3 closing order (largest shortfall first) closes a viable club (3 students)")
    clb = {"X": ("GIOI_HAN", 3, None, 3), "Y": ("GIOI_HAN", 3, None, 3), "F": ("TU_DO", 1, None, None)}
    hs = {"a": (1, ["X", "F"], {}), "b": (2, ["Y", "X", "F"], {}), "c": (3, ["Y", "X", "F"], {})}
    a, kq = _kq(_nho(clb, hs))
    print("code order      ->", a, "closed:", [d["club_id"] for d in kq.dong_cua])
    clb2 = dict(clb, Y=("GIOI_HAN", 3, None, 99))                    # force Y to close first
    a2, kq2 = _kq(_nho(clb2, hs))
    print("close Y first   ->", a2, "closed:", [d["club_id"] for d in kq2.dong_cua])

    print("\n## CE3: reasons (`ly_do_ket_qua`) when group priority (`tier_rank`) is on")
    clb = {"A": ("GIOI_HAN", 1, None, None), "F": ("TU_DO", 1, None, None)}
    hs = {"k12": (2, ["A", "F"], {}), "k11": (1, ["A", "F"], {})}
    bo = _nho(clb, hs)
    a, kq = _kq(bo, tier_rank={"k12": 0, "k11": 1})
    print("assignment:", a)
    try:
        ly = fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])
        print("reasons:", [(r["student_id"], r["club_id"], r["outcome"], r["reason"]) for r in ly])
    except ValueError as e:
        print("ValueError:", e)
    bo["huy_chuong"]["k11"] = {"A": 30}                              # weaker medal, weaker group
    a, kq = _kq(bo, tier_rank={"k12": 0, "k11": 1})
    ly = fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])
    print("k11 silver, k12 gold:", [(r["student_id"], r["outcome"], r["reason"]) for r in ly
                                    if r["club_id"] == "A"])


# ----------------------------------------------------------------------------- random search
def _hang(kq, s, thuc, clubs):
    ra = {}
    for buoi, c in kq.ket_qua.assignment[s].items():
        tl = [x for x in thuc if clubs[x]["buoi"] == buoi]
        ra[buoi] = tl.index(c) if c in tl else len(tl)
    return ra


def tim_lech(so_seed=200):
    """Per generator setting: instances where SOME student strictly gains (true rank in some day, no day
    worse) by a permutation or a sub-list of the true list. Medals fixed. Generator = tests/test_fa_tinh_chat._bo."""
    import test_fa_tinh_chat as t
    print("### Rank-misreport search — %s" % NHAN)
    print("| min quota (so_toi_thieu) | instances | instances with a profitable misreport | students tried |"
          " students who gain | stability failures on prepared inputs |")
    print("|---|---|---|---|---|---|")
    vi_du = None
    for toi_thieu in (False, True):
        n_bo = n_hs = n_loi = bo_loi = n_bat = 0
        for seed in range(so_seed):
            bo = t._bo(seed, toi_thieu=toi_thieu)
            goc = fa_daa.chay_fa_daa(**copy.deepcopy(bo), seed=seed)
            vs = rp.verify_stability_tuan(goc.ket_qua, goc.clubs, goc.preferences, goc.reserve_fn)
            n_bat += any(vs.values())
            n_bo += 1
            co = False
            for s, ds in bo["preferences"].items():
                if len(ds) > 4:
                    continue
                n_hs += 1
                thuc = _hang(goc, s, ds, bo["clubs"])
                loi = False
                for k in range(0, len(ds) + 1):
                    for hv in itertools.permutations(ds, k):
                        if list(hv) == ds:
                            continue
                        bo2 = copy.deepcopy(bo)
                        bo2["preferences"][s] = list(hv)
                        kq2 = fa_daa.chay_fa_daa(**bo2, seed=seed)
                        r2 = _hang(kq2, s, ds, bo["clubs"])
                        if all(r2[b] <= thuc[b] for b in thuc) and any(r2[b] < thuc[b] for b in thuc):
                            loi = True
                            if vi_du is None:
                                vi_du = (seed, s, ds, hv, thuc, r2)
                            break
                    if loi:
                        break
                n_loi += loi
                co = co or loi
            bo_loi += co
        print("| %s | %d | %d | %d | %d | %d |" % ("on" if toi_thieu else "off", n_bo, bo_loi, n_hs, n_loi, n_bat))
    if vi_du:
        print("\nfirst example (seed, student, true list, report, true rank per day before, after):", vi_du)


# ----------------------------------------------------------------------------- medals
def _chay_ngay(dl, prefs, huy, ticks, diem, seed, buoi):
    stb = mp._stb(dl, seed)
    bo = mp._bo(dl, prefs, ticks, diem, stb)
    kq = fa_daa.chay_fa_daa(fa_clb=dl["fa_clb"], giu_cho=[], huy_chuong=huy, seed=seed, chi_buoi=[buoi], **bo)
    return {s: v.get(buoi) for s, v in kq.ket_qua.assignment.items()}, kq


def _cach_dat(dl, ds_ngay):
    """All placements of gold/silver/bronze on the non-FREE clubs the student listed that day."""
    mc = [c for c in ds_ngay if dl["fa_clb"][c]["loai"] != fa_daa.TU_DO]
    k = min(3, len(mc))
    return [dict(zip(p, GT)) for p in itertools.permutations(mc, k)]


def _mac_dinh(dl, ds_ngay):
    mc = [c for c in ds_ngay if dl["fa_clb"][c]["loai"] != fa_daa.TU_DO][:3]
    return dict(zip(mc, GT))


def _gh_truoc(dl, ds_ngay):
    """Information-free heuristic: medals first on LIMITED clubs (medal is the first key there), in rank
    order, then SELECTIVE clubs in rank order."""
    mc = [c for c in ds_ngay if dl["fa_clb"][c]["loai"] != fa_daa.TU_DO]
    mc = ([c for c in mc if dl["fa_clb"][c]["loai"] == fa_daa.GIOI_HAN]
          + [c for c in mc if dl["fa_clb"][c]["loai"] == fa_daa.TUYEN_CHON])[:3]
    return dict(zip(mc, GT))


def _truot(dl, s, ds_ngay):
    """Default order, but skipping SELECTIVE clubs where the student is below the pass mark (medal would be dead)."""
    mc = [c for c in ds_ngay if dl["fa_clb"][c]["loai"] != fa_daa.TU_DO
          and not (dl["fa_clb"][c]["loai"] == fa_daa.TUYEN_CHON and mp._diem_thi(dl, s, c) < dl["fa_clb"][c]["diem_san"])][:3]
    return dict(zip(mc, GT))


def _it_hot(dl, ds_ngay):
    """The script's `chien_luoc` rule: top three non-FREE, gold on the least hot."""
    mc = [c for c in ds_ngay if dl["fa_clb"][c]["loai"] != fa_daa.TU_DO][:3]
    return dict(zip(sorted(mc, key=lambda c: (dl["hot"][c], c)), GT))


def _do(dl, s, b, c):
    """(true utility, got true first choice, true rank 1..K) of club c for student s on day b."""
    vt = mp._vi_tri(dl, s, b)
    if c is None:
        return 0.0, 0, len(vt) + 1
    return dl["hs"][s]["thich"][c], int(c == vt[0]), vt.index(c) + 1


def huy_chuong(n=100, so_seed=5, k=5, l_toi_da=4, n_chon=4, n_do=4, mau=None, ti_le=(0.3, 0.5, 0.2)):
    """Unilateral deviation, everyone else as generated. For each sampled student-day: default placement vs
    two fixed heuristics vs the best placement chosen on `n_chon` lottery draws and EVALUATED on `n_do` other
    draws (out-of-sample), plus the hindsight bound (best placement per draw). Rank list held as the type reports it."""
    tong = {h: dict(m=0, u0=0.0, t0=0, r0=0, ub=0.0, tb=0, rb=0, ug=0.0, uh=0.0, ut=0.0, loi=0, sau=0, doi=0,
                    hai=0.0, duoc=0.0, lang=0, lang_cl=0, loc=0)
            for h in mp.HANH_VI}
    hai_theo = {h: 0 for h in mp.HANH_VI}
    for sd in range(so_seed):
        dl = mp.sinh_du_lieu(n=n, seed=sd, k=k, l_toi_da=l_toi_da, ti_le=ti_le)
        prefs, huy, ticks, diem = mp.dang_ky(dl)
        r = random.Random(1000 + sd)
        ds_hs = sorted(dl["sids"]) if mau is None else r.sample(sorted(dl["sids"]), mau)
        seeds_chon = [sd * 100 + i for i in range(n_chon)]
        seeds_do = [sd * 100 + 50 + i for i in range(n_do)]
        nen = {}
        for b in dl["ds_buoi"]:
            for x in seeds_chon + seeds_do:
                nen[(b, x)] = _chay_ngay(dl, prefs, huy, ticks, diem, x, b)
        for s in ds_hs:
            hv = dl["hs"][s]["hanh_vi"]
            for b in dl["ds_buoi"]:
                ds_ngay = [c for c in prefs[s] if dl["buoi_cua"][c] == b]
                md = _mac_dinh(dl, ds_ngay)
                khac = {c: v for c, v in huy.get(s, {}).items() if dl["buoi_cua"][c] != b}

                def chay(dat, x):
                    h2 = dict(huy)
                    h2[s] = dict(khac, **dat)
                    return _chay_ngay(dl, prefs, h2, ticks, diem, x, b)[0]

                cach = _cach_dat(dl, ds_ngay)
                diem_chon = [sum(_do(dl, s, b, chay(d, x)[s])[0] for x in seeds_chon) for d in cach]
                u_md_chon = sum(_do(dl, s, b, chay(md, x)[s])[0] for x in seeds_chon)
                tot = cach[max(range(len(cach)), key=lambda i: diem_chon[i])] if cach else md
                if max(diem_chon, default=u_md_chon) <= u_md_chon + 1e-12:
                    tot = md
                t = tong[hv]
                t["m"] += 1
                t["doi"] += tot != md
                # wasted default gold: club removed before DA (below pass mark)
                vang = next((c for c, v in md.items() if v == 60), None)
                kq0 = nen[(b, seeds_do[0])][1]
                bo_truoc = {(x["student_id"], x["club_id"]) for x in kq0.loai_bo}
                t["loc"] += (s, vang) in bo_truoc
                for x in seeds_do:
                    a0 = chay(md, x)
                    ab = chay(tot, x) if tot != md else a0
                    u0, t0, r0 = _do(dl, s, b, a0[s])
                    ub, tb, rb = _do(dl, s, b, ab[s])
                    t["u0"] += u0; t["t0"] += t0; t["r0"] += r0
                    t["ub"] += ub; t["tb"] += tb; t["rb"] += rb
                    t["ug"] += _do(dl, s, b, chay(_gh_truoc(dl, ds_ngay), x)[s])[0]
                    t["uh"] += _do(dl, s, b, chay(_it_hot(dl, ds_ngay), x)[s])[0]
                    t["ut"] += _do(dl, s, b, chay(_truot(dl, s, ds_ngay), x)[s])[0]
                    best = max((_do(dl, s, b, chay(d, x)[s])[0] for d in cach), default=u0)
                    t["sau"] += best > u0 + 1e-12
                    if tot != md:
                        for o in dl["sids"]:
                            if o == s or a0[o] == ab[o]:
                                continue
                            d_o = _do(dl, o, b, ab[o])[0] - _do(dl, o, b, a0[o])[0]
                            if d_o < 0:
                                t["hai"] += 1
                                hai_theo[dl["hs"][o]["hanh_vi"]] += 1
                            elif d_o > 0:
                                t["duoc"] += 1
    print("### Medal best response, unilateral, by behaviour type — %s" % NHAN)
    print("(n=%d, K=%d clubs/day, list<=%d, %d data seeds; best placement chosen on %d lottery draws, evaluated on"
          " %d other draws; utility = true liking 0..1)" % (n, k, l_toi_da, so_seed, n_chon, n_do))
    print("| type | student-days | default: mean utility | default: % true NV1 | default: mean true rank |"
          " best response: mean utility | BR: % true NV1 | BR: mean true rank | % student-days where BR != default |"
          " hindsight: % draws where some placement beats default | LIMITED-first rule: mean utility |"
          " least-hot-first rule: mean utility | skip-filtered default: mean utility | % default gold on a club filtered out (BELOW_PASS) |")
    print("|" + "---|" * 14)
    for h in mp.HANH_VI:
        t = tong[h]
        m = t["m"] * n_do
        if not m:
            continue
        print("| %s | %d | %.4f | %.1f | %.3f | %.4f | %.1f | %.3f | %.1f | %.1f | %.4f | %.4f | %.4f | %.1f |" % (
            h, t["m"], t["u0"] / m, 100 * t["t0"] / m, t["r0"] / m, t["ub"] / m, 100 * t["tb"] / m,
            t["rb"] / m, 100 * t["doi"] / t["m"], 100 * t["sau"] / m, t["ug"] / m, t["uh"] / m, t["ut"] / m,
            100 * t["loc"] / t["m"]))
    dev = sum(t["doi"] for t in tong.values()) * n_do
    print("\n### Externality of one student's best response — %s" % NHAN)
    print("| deviations x draws | other students made worse per deviation-draw | made better |"
          " harmed: luoi | harmed: that_tha | harmed: chien_luoc |")
    print("|---|---|---|---|---|---|")
    if dev:
        print("| %d | %.3f | %.3f | %d | %d | %d |" % (
            dev, sum(t["hai"] for t in tong.values()) / dev, sum(t["duoc"] for t in tong.values()) / dev,
            hai_theo["luoi"], hai_theo["that_tha"], hai_theo["chien_luoc"]))


def quan_the(n=100, so_seed=10, k=5, l_toi_da=4, n_do=4):
    """Population view. Same data and lottery, three medal profiles: (0) everyone default; (1) the `chien_luoc`
    students use the LIMITED-first rule; (2) everyone uses it. Mean true utility / % true NV1 by type."""
    ten = ("all default", "chien_luoc use LIMITED-first", "all use LIMITED-first")
    cong = {(i, h): [0, 0.0, 0, 0] for i in range(3) for h in mp.HANH_VI}
    for sd in range(so_seed):
        dl = mp.sinh_du_lieu(n=n, seed=sd, k=k, l_toi_da=l_toi_da)
        prefs, _, ticks, diem = mp.dang_ky(dl)
        ho_so = [{}, {}, {}]
        for s in dl["sids"]:
            hv = dl["hs"][s]["hanh_vi"]
            for b in dl["ds_buoi"]:
                ds_ngay = [c for c in prefs[s] if dl["buoi_cua"][c] == b]
                md, gh = _mac_dinh(dl, ds_ngay), _gh_truoc(dl, ds_ngay)
                ho_so[0].setdefault(s, {}).update(md)
                ho_so[1].setdefault(s, {}).update(gh if hv == "chien_luoc" else md)
                ho_so[2].setdefault(s, {}).update(gh)
        for i in range(3):
            for x in range(n_do):
                for b in dl["ds_buoi"]:
                    a, kq = _chay_ngay(dl, prefs, ho_so[i], ticks, diem, sd * 100 + x, b)
                    ly = fa_daa.ly_do_ket_qua(kq, prefs, ho_so[i], dl["fa_clb"])
                    thua = {r["student_id"] for r in ly if r["reason"] == "LOTTERY" and r["outcome"] == "REJECTED"}
                    for s in dl["sids"]:
                        u, t1, _ = _do(dl, s, b, a[s])
                        c = cong[(i, dl["hs"][s]["hanh_vi"])]
                        c[0] += 1; c[1] += u; c[2] += t1; c[3] += s in thua
    print("### Population view: who gains, who loses — %s" % NHAN)
    print("(n=%d, K=%d, list<=%d, %d data seeds x %d lottery draws)" % (n, k, l_toi_da, so_seed, n_do))
    print("| medal profile | type | mean utility | % true NV1 | % student-days with a lottery loss |")
    print("|---|---|---|---|---|")
    for i in range(3):
        for h in mp.HANH_VI:
            c = cong[(i, h)]
            print("| %s | %s | %.4f | %.1f | %.1f |" % (ten[i], h, c[1] / c[0], 100 * c[2] / c[0], 100 * c[3] / c[0]))


if __name__ == "__main__":
    for _l in (sys.stdout, sys.stderr):
        if hasattr(_l, "reconfigure"):
            _l.reconfigure(encoding="utf-8", errors="replace")
    lenh = sys.argv[1] if len(sys.argv) > 1 else "phan_vi_du"
    {"phan_vi_du": phan_vi_du, "tim_lech": tim_lech, "huy_chuong": huy_chuong, "quan_the": quan_the}[lenh]()
