"""
fable_ga2_huy_chuong.py — medal designs and cross-day lottery variants at school size (memo section G-A.2).
Research only, SIMULATED data. Run through `fable_ga2_giai_phap.py f2 | f2_br | boc_tham`.

MEDAL DESIGNS (same registration data for all; nothing new is asked from students)
  D0  current: gold/silver/bronze 60/30/10, default = first three non-FREE clubs in rank order
  D1  same values, default skips SELECTIVE clubs where the student has no score or is below the pass mark
  D2  three EQUAL medals, default as D1
  D3  ONE medal, default as D1
  D4  no medals (LIMITED: lottery only; SELECTIVE: score then lottery)
STRATEGIC RULE `gan_toi_uu` (stand-in for a well-informed student, uses the outcome of ONE earlier draw as "last
term"): medals go first to clubs where a medal can change the result (contested LIMITED; contested SELECTIVE where
own score equals the last admitted score), then to clubs the student would enter anyway, last to clubs out of reach.
"""

import itertools
import random
import statistics

import fa_daa
import mo_phong_fa_daa as mp
from fable_ga2_giai_phap import GH, NHAN, TC, TD, _stb_ngau_nhien, chay1, sinh_truong

THIET_KE = {"D0": ((60, 30, 10), False), "D1": ((60, 30, 10), True), "D2": ((60, 60, 60), True),
            "D3": ((60,), True), "D4": ((), True)}


def _ngay(dl, prefs, s, b):
    return [c for c in prefs[s] if dl["buoi_cua"][c] == b]


def _dat_yeu_cau(dl, s, c):
    return dl["fa_clb"][c]["loai"] != TC or mp._diem_thi(dl, s, c) >= dl["fa_clb"][c]["diem_san"]


def _ung_vien(dl, s, ds_ngay, bo_loc):
    return [c for c in ds_ngay if dl["fa_clb"][c]["loai"] != TD and (not bo_loc or _dat_yeu_cau(dl, s, c))]


def mac_dinh(dl, prefs, tk, b=None):
    gt, bo_loc = THIET_KE[tk]
    ra = {}
    for s in dl["sids"]:
        for bb in ([b] if b else dl["ds_buoi"]):
            ra.setdefault(s, {}).update(dict(zip(_ung_vien(dl, s, _ngay(dl, prefs, s, bb), bo_loc), gt)))
    return ra


def moc_ky_truoc(dl, b, kq, a, prefs, huy):
    """{club: (contested?, lowest admitted score)} from one earlier run of the same day."""
    ly = fa_daa.ly_do_ket_qua(kq, prefs, huy, dl["fa_clb"])
    tranh = {r["club_id"] for r in ly if r["outcome"] == "REJECTED"}
    cat = {}
    for s, c in a.items():
        if c and dl["fa_clb"][c]["loai"] == TC:
            cat[c] = min(cat.get(c, 99), mp._diem_thi(dl, s, c))
    return {c: (c in tranh, cat.get(c)) for c in dl["clubs"] if dl["buoi_cua"][c] == b}, ly


def gan_toi_uu(dl, s, ds_ngay, moc, gt):
    def nhom(c):
        tranh, cat = moc[c]
        if not tranh:
            return 1
        if dl["fa_clb"][c]["loai"] == GH:
            return 0
        d = mp._diem_thi(dl, s, c)
        return 0 if cat is not None and d == cat else (1 if cat is not None and d > cat else 2)
    uv = _ung_vien(dl, s, ds_ngay, True)
    return dict(zip(sorted(uv, key=lambda c: (nhom(c), uv.index(c))), gt))


def _do(dl, s, b, c):
    vt = mp._vi_tri(dl, s, b)
    return (dl["hs"][s]["thich"][c] if c else 0.0), int(c == vt[0]), int(c in vt[:2])


def _dem(dl, b, a, ly, cong, huy):
    thua = {r["student_id"] for r in ly if r["reason"] == "LOTTERY" and r["outcome"] == "REJECTED"}
    for r in ly:
        if r["outcome"] == "REJECTED":
            cong["ly_do"][r["reason"]] = cong["ly_do"].get(r["reason"], 0) + 1
    for s in dl["sids"]:
        t = cong[dl["hs"][s]["hanh_vi"]]
        u, n1, t2 = _do(dl, s, b, a[s])
        t[0] += 1; t[1] += u; t[2] += n1; t[3] += t2; t[4] += s in thua
        for c in (huy.get(s) or {}):
            if dl["buoi_cua"][c] == b:
                t[5] += 1
                t[6] += not _dat_yeu_cau(dl, s, c)


def f2(so_seed=5, n=800):
    """Population view at school size. Profiles: everyone default; the 20 % `chien_luoc` students use `gan_toi_uu`."""
    print("### F2-a Medal designs at school size, by behaviour type — %s" % NHAN)
    print("(n=%d, 3 days, 7 clubs/day, %d data seeds, 1 lottery draw each; model in `fable_ga2_giai_phap.sinh_truong`)"
          % (n, so_seed))
    print("| design | profile | type | mean utility | % true NV1 | % true top 2 | % student-days with a lottery loss |"
          " % medals on a club the student cannot enter |")
    print("|---|---|---|---|---|---|---|---|")
    tong_ly_do = {}
    for tk in THIET_KE:
        for ho_so in ("all default", "chien_luoc strategic"):
            if tk == "D4" and ho_so != "all default":
                continue
            cong = {h: [0, 0.0, 0, 0, 0, 0, 0] for h in mp.HANH_VI}
            cong["ly_do"] = {}
            for sd in range(so_seed):
                dl = sinh_truong(n=n, seed=sd)
                prefs, _, ticks, diem = mp.dang_ky(dl)
                for b in dl["ds_buoi"]:
                    huy = mac_dinh(dl, prefs, tk, b)
                    if ho_so != "all default":
                        a0, kq0, _ = chay1(dl, b, prefs, huy, ticks, diem, _stb_ngau_nhien(dl, (sd, b, "truoc")))
                        moc, _ = moc_ky_truoc(dl, b, kq0, a0, prefs, huy)
                        for s in dl["sids"]:
                            if dl["hs"][s]["hanh_vi"] == "chien_luoc":
                                huy[s] = gan_toi_uu(dl, s, _ngay(dl, prefs, s, b), moc, THIET_KE[tk][0])
                    a, kq, _ = chay1(dl, b, prefs, huy, ticks, diem, _stb_ngau_nhien(dl, (sd, b)))
                    _dem(dl, b, a, fa_daa.ly_do_ket_qua(kq, prefs, huy, dl["fa_clb"]), cong, huy)
            tong_ly_do[(tk, ho_so)] = cong["ly_do"]
            for h in mp.HANH_VI:
                t = cong[h]
                print("| %s | %s | %s | %.4f | %.1f | %.1f | %.1f | %s |" % (
                    tk, ho_so, h, t[1] / t[0], 100 * t[2] / t[0], 100 * t[3] / t[0], 100 * t[4] / t[0],
                    ("%.1f" % (100 * t[6] / t[5])) if t[5] else "-"))
    print("\n### F2-b What decides a rejection (share of REJECTED rows) — %s" % NHAN)
    print("| design | profile | SCORE % | MEDAL % | LOTTERY % | rejections |")
    print("|---|---|---|---|---|---|")
    for (tk, ho_so), d in tong_ly_do.items():
        m = sum(d.values()) or 1
        print("| %s | %s | %.1f | %.1f | %.1f | %d |" % (tk, ho_so, 100 * d.get("SCORE", 0) / m,
                                                      100 * d.get("MEDAL", 0) / m, 100 * d.get("LOTTERY", 0) / m, m))


def _cach_dat(uv, gt, toi_da=4):
    uv = uv[:toi_da + (1 if len(set(gt)) == 1 and len(gt) > 1 else 0)]
    k = min(len(gt), len(uv))
    if len(set(gt)) == 1:
        return [dict(zip(p, gt)) for p in itertools.combinations(uv, k)]
    return [dict(zip(p, gt)) for p in itertools.permutations(uv, k)]


def f2_br(so_seed=3, mau=30, n=800, n_chon=2, n_do=3):
    """Sampled unilateral best response per design: one student-day at a time, everyone else default. Best placement
    (medals on the first 4-5 enterable non-FREE clubs) chosen on `n_chon` draws, evaluated on `n_do` other draws."""
    print("### F2-c Sampled best response per medal design, school size — %s" % NHAN)
    print("(n=%d, %d data seeds x %d sampled student-days per design; chosen on %d draws, evaluated on %d others)"
          % (n, so_seed, mau, n_chon, n_do))
    print("| design | type | student-days | default utility | best-response utility | gain | `gan_toi_uu` rule utility |"
          " % BR != default | others worse per deviation-draw | others better |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for tk in ("D0", "D1", "D2", "D3"):
        gt = THIET_KE[tk][0]
        cong = {h: dict(m=0, u0=0.0, ub=0.0, ug=0.0, doi=0, hai=0, duoc=0) for h in mp.HANH_VI}
        for sd in range(so_seed):
            dl = sinh_truong(n=n, seed=sd)
            prefs, _, ticks, diem = mp.dang_ky(dl)
            r = random.Random(500 + sd)
            for s in r.sample(dl["sids"], mau):
                b = r.choice(dl["ds_buoi"])
                huy = mac_dinh(dl, prefs, tk, b)
                md = dict(huy.get(s) or {})
                ds_ngay = _ngay(dl, prefs, s, b)
                stb_c = [_stb_ngau_nhien(dl, (sd, b, "c", i)) for i in range(n_chon)]
                stb_d = [_stb_ngau_nhien(dl, (sd, b, "d", i)) for i in range(n_do)]

                def chay(dat, stb):
                    h2 = dict(huy)
                    h2[s] = dat
                    return chay1(dl, b, prefs, h2, ticks, diem, stb)

                a0, kq0, _ = chay(md, _stb_ngau_nhien(dl, (sd, b, "truoc")))
                moc, _ = moc_ky_truoc(dl, b, kq0, a0, prefs, huy)
                gtu = gan_toi_uu(dl, s, ds_ngay, moc, gt)
                cach = _cach_dat(_ung_vien(dl, s, ds_ngay, True), gt)
                u_md = sum(_do(dl, s, b, chay(md, x)[0][s])[0] for x in stb_c)
                tot, u_tot = md, u_md
                for d in cach:
                    if d == md:
                        continue
                    u = sum(_do(dl, s, b, chay(d, x)[0][s])[0] for x in stb_c)
                    if u > u_tot + 1e-12:
                        tot, u_tot = d, u
                t = cong[dl["hs"][s]["hanh_vi"]]
                t["m"] += 1
                t["doi"] += tot != md
                for x in stb_d:
                    am = chay(md, x)[0]
                    ab = chay(tot, x)[0] if tot != md else am
                    t["u0"] += _do(dl, s, b, am[s])[0]
                    t["ub"] += _do(dl, s, b, ab[s])[0]
                    t["ug"] += _do(dl, s, b, (chay(gtu, x)[0] if gtu != md else am)[s])[0]
                    if tot != md:
                        for o in dl["sids"]:
                            if o != s and am[o] != ab[o]:
                                d_o = _do(dl, o, b, ab[o])[0] - _do(dl, o, b, am[o])[0]
                                t["hai"] += d_o < 0
                                t["duoc"] += d_o > 0
        for h in mp.HANH_VI:
            t = cong[h]
            m = t["m"] * n_do
            if not m:
                continue
            dv = (t["doi"] * n_do) or 1
            print("| %s | %s | %d | %.4f | %.4f | %+.4f | %.4f | %.1f | %.2f | %.2f |" % (
                tk, h, t["m"], t["u0"] / m, t["ub"] / m, (t["ub"] - t["u0"]) / m, t["ug"] / m,
                100 * t["doi"] / t["m"], t["hai"] / dv, t["duoc"] / dv))


def boc_tham(so_seed=10, n=800):
    """Cross-day lottery variants (all exogenous: none reads reports or outcomes). `doc_lap` = independent per day
    (what `stb_ngay` does); `giong` = same order every day; `xoay_khoi` = split the base order into 3 blocks, rotate
    the blocks by one each day, reshuffle inside each block per day."""
    print("### Cross-day lottery variants, design D0, all default — %s" % NHAN)
    print("(n=%d, 3 days, %d data seeds)" % (n, so_seed))
    print("| lottery | mean utility per day | SD across students of 3-day total utility | bottom 10 %: mean 3-day utility |"
          " % students with a lottery loss on 0 / 1 / 2 / 3 days | % students in the worst lottery third on all 3 days |")
    print("|---|---|---|---|---|---|")
    for che_do in ("doc_lap", "giong", "xoay_khoi"):
        tong, sd_, day, dem, xau, n_hs = [], [], [], [0, 0, 0, 0], 0, 0
        for sd in range(so_seed):
            dl = sinh_truong(n=n, seed=sd)
            prefs, _, ticks, diem = mp.dang_ky(dl)
            goc = sorted(dl["sids"])
            random.Random("goc-%d" % sd).shuffle(goc)
            u = {s: 0.0 for s in dl["sids"]}
            thua_n = {s: 0 for s in dl["sids"]}
            cuoi = {s: 0 for s in dl["sids"]}
            for i, b in enumerate(dl["ds_buoi"]):
                if che_do == "doc_lap":
                    stb = _stb_ngau_nhien(dl, (sd, b, "bt"))
                elif che_do == "giong":
                    stb = {s: j + 1 for j, s in enumerate(goc)}
                else:
                    k = len(goc) // 3
                    khoi = [goc[:k], goc[k:2 * k], goc[2 * k:]]
                    khoi = khoi[i % 3:] + khoi[:i % 3]
                    ds = []
                    for j, kh in enumerate(khoi):
                        kh = list(kh)
                        random.Random("khoi-%d-%s-%d" % (sd, b, j)).shuffle(kh)
                        ds += kh
                    stb = {s: j + 1 for j, s in enumerate(ds)}
                huy = mac_dinh(dl, prefs, "D0", b)
                a, kq, _ = chay1(dl, b, prefs, huy, ticks, diem, stb)
                ly = fa_daa.ly_do_ket_qua(kq, prefs, huy, dl["fa_clb"])
                thua = {r["student_id"] for r in ly if r["reason"] == "LOTTERY" and r["outcome"] == "REJECTED"}
                for s in dl["sids"]:
                    u[s] += _do(dl, s, b, a[s])[0]
                    thua_n[s] += s in thua
                    cuoi[s] += stb[s] > 2 * len(goc) / 3
            v = sorted(u.values())
            tong.append(statistics.mean(v) / 3)
            sd_.append(statistics.pstdev(v))
            day.append(statistics.mean(v[:len(v) // 10]))
            for s in dl["sids"]:
                dem[thua_n[s]] += 1
                xau += cuoi[s] == 3
                n_hs += 1
        print("| %s | %.4f | %.4f | %.4f | %s | %.1f |" % (
            che_do, statistics.mean(tong), statistics.mean(sd_), statistics.mean(day),
            " / ".join("%.1f" % (100 * x / n_hs) for x in dem), 100 * xau / n_hs))
