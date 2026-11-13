"""
fable_gh_giam_may_rui.py — research script for goal G-H "reducing luck" (docs/fable/04_GH_REDUCING_LUCK.md).
NOT production code. All data is SIMULATED (seeded generators, no real students). Prints tables only.

    python du_lieu_test/fable_gh_giam_may_rui.py kiem      # research DA == production `chay_fa_daa` (same lottery)
    python du_lieu_test/fable_gh_giam_may_rui.py bang      # main table, school size
    python du_lieu_test/fable_gh_giam_may_rui.py doi_cho   # improvement cycles after DA (measurement mode)

The script carries its own small student-proposing DA (`da_ngay`) so that things the production core does not
offer (one lottery PER CLUB, non-integer scores) can be measured. `kiem` checks that with the production settings
it gives exactly the production assignment. Model: `fable_ga2_giai_phap.sinh_truong` (800 students, 3 days,
7 clubs/day: 1 FREE, 2 LIMITED, 4 SELECTIVE with pass mark 5; lists of 6; non-FREE seats = 70 % of students).

LEVERS (nothing new is asked from students)
  seats    C0 equal seats (baseline) | C1 same total, proportional to THIS term's first-choice demand |
           C2 same total, proportional to demand of ANOTHER simulated cohort ("last term") |
           C3 only increases: +15 % seats, given to over-demanded clubs
  score    step 1 (integer 0-10, baseline) | 0.5 | 0.1   (same underlying performance, finer reporting)
  lottery  STB one number per student per day (baseline) | MTB one independent number per student PER CLUB
  medals   D0 current default | D1 default skips clubs the student cannot enter
"""

import os
import random
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_GOC, os.path.join(_GOC, "du_lieu_test")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mo_phong_fa_daa as mp  # noqa: E402
from fable_ga2_giai_phap import GH, NHAN, TC, TD, _stb_ngau_nhien, chay1, sinh_truong  # noqa: E402

GT = (60, 30, 10)
SAN = 5


def diem(dl, s, c, buoc):
    h = dl["hs"][s]
    x = 5 + 2.5 * h["nang_luc"] + h["nhieu"][c]
    return min(10.0, max(0.0, round(x / buoc) * buoc))


def _vao_duoc(dl, s, c, buoc):
    """Pass/fail is ALWAYS judged on the integer score, so every scenario filters the same students; a finer
    step only changes the ORDER among students who passed."""
    return dl["fa_clb"][c]["loai"] != TC or diem(dl, s, c, 1) >= SAN


def huy_mac_dinh(dl, pr_ngay, buoc, d1):
    ra = {}
    for s, ds in pr_ngay.items():
        uv = [c for c in ds if dl["fa_clb"][c]["loai"] != TD and (not d1 or _vao_duoc(dl, s, c, buoc))]
        ra[s] = dict(zip(uv, GT))
    return ra


def da_ngay(dl, b, pr_ngay, huy, cho, so, buoc):
    """Student-proposing DA for one day. `so` = {club: {student: lottery number}} (same dict for every club = STB).
    Returns assignment and, per student, the list of (club, reason) rejections above the final club."""
    cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
    tu_do = next(c for c in cs if dl["fa_clb"][c]["loai"] == TD)
    ds = {}
    for s, goc in pr_ngay.items():
        d = [c for c in goc if _vao_duoc(dl, s, c, buoc)]
        ds[s] = d if tu_do in d else d + [tu_do]

    def khoa(s, c):
        m = -(huy.get(s) or {}).get(c, 0)
        if dl["fa_clb"][c]["loai"] == TC:
            return (-diem(dl, s, c, buoc), m, so[c][s])
        return (0.0, m, so[c][s])

    giu = {c: [] for c in cs}
    vi_tri = {s: 0 for s in ds}
    cho_xet = list(ds)
    bi_loai = {s: [] for s in ds}
    while cho_xet:
        s = cho_xet.pop()
        c = ds[s][vi_tri[s]]
        giu[c].append((khoa(s, c), s))
        if dl["fa_clb"][c]["loai"] != TD and len(giu[c]) > cho[c]:
            giu[c].sort()
            _, ra = giu[c].pop()
            bi_loai[ra].append(c)
            vi_tri[ra] += 1
            cho_xet.append(ra)
    a = {s: ds[s][vi_tri[s]] for s in ds}
    cuoi = {c: max(giu[c])[0] for c in cs if giu[c]}
    ly_do = {}
    for s, bo in bi_loai.items():
        ly_do[s] = []
        for c in bo:
            ks, km = khoa(s, c), cuoi[c]
            ly_do[s].append((c, "SCORE" if ks[0] != km[0] else "MEDAL" if ks[1] != km[1] else "LOTTERY"))
    return a, ly_do, giu


def kiem(so_seed=3):
    """Research DA vs production wrapper, production settings (integer scores, STB, D0 medals, equal seats)."""
    lech = tong = 0
    for sd in range(so_seed):
        dl = sinh_truong(seed=sd)
        prefs, huy, ticks, dm = mp.dang_ky(dl)
        for b in dl["ds_buoi"]:
            stb = _stb_ngau_nhien(dl, (sd, b))
            a_sx, _, pr = chay1(dl, b, prefs, huy, ticks, dm, stb)
            cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
            a, _, _ = da_ngay(dl, b, pr, huy, {c: dl["clubs"][c]["capacity"] for c in cs}, {c: stb for c in cs}, 1)
            tong += len(a)
            lech += sum(1 for s in a if a[s] != a_sx[s])
    print("research DA vs `chay_fa_daa`: %d student-days compared, %d differ — %s" % (tong, lech, NHAN))


def _nhu_cau(dl, b, pr_ngay, buoc):
    """First-choice demand per non-FREE club: each student's first listed club they can enter, if it is not FREE."""
    dem = {c: 0 for c in dl["clubs"] if dl["buoi_cua"][c] == b and dl["fa_clb"][c]["loai"] != TD}
    for s, ds in pr_ngay.items():
        c = next((x for x in ds if _vao_duoc(dl, s, x, buoc)), None)
        if c in dem:
            dem[c] += 1
    return dem


def _chia(tong, trong_so, san=10):
    w = sum(trong_so.values()) or 1
    ra = {c: max(san, int(round(tong * v / w))) for c, v in trong_so.items()}
    return ra


def cho_ngoi(dl, b, pr_ngay, buoc, kieu, dl_truoc=None, pr_truoc=None):
    cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
    goc = {c: dl["clubs"][c]["capacity"] for c in cs}
    kg = [c for c in cs if dl["fa_clb"][c]["loai"] != TD]
    tong = sum(goc[c] for c in kg)
    if kieu == "C0":
        return goc
    if kieu in ("C1", "C2"):
        nc = _nhu_cau(dl, b, pr_ngay, buoc) if kieu == "C1" else _nhu_cau(dl_truoc, b, pr_truoc, buoc)
        return dict(goc, **_chia(tong, nc))
    nc = _nhu_cau(dl, b, pr_ngay, buoc)                       # C3: +15 % seats, only where demand exceeds seats
    du = {c: max(0, nc[c] - goc[c]) for c in kg}
    them = int(round(0.15 * tong))
    w = sum(du.values())
    return dict(goc, **{c: goc[c] + (int(round(them * du[c] / w)) if w else 0) for c in kg})


def _khoa_hoc_sinh_khac(dl, seed):
    """Another cohort facing the SAME clubs (same hotness): stands in for "last term"."""
    r = random.Random("ky-truoc-%d" % seed)
    dl2 = dict(dl)
    dl2["hs"] = {s: {"hanh_vi": r.choices(mp.HANH_VI, weights=(0.3, 0.5, 0.2))[0],
                     "thich": {c: 0.5 * dl["hot"][c] + 0.5 * r.random() for c in dl["clubs"]},
                     "nang_luc": r.gauss(0, 1), "nhieu": {c: r.uniform(-1, 1) for c in dl["clubs"]}}
                 for s in dl["sids"]}
    return dl2


def _so(dl, b, sd, kieu):
    cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
    if kieu == "STB":
        stb = _stb_ngau_nhien(dl, (sd, b))
        return {c: stb for c in cs}
    return {c: _stb_ngau_nhien(dl, (sd, b, c)) for c in cs}


def _chien_luoc(dl, s, ds, a0, giu0, ly0, buoc):
    """`gan_toi_uu` of G-A.2 on the research DA: medals first where they can change the result."""
    tranh = {c for bo in ly0.values() for c, _ in bo}

    def nhom(c):
        if c not in tranh:
            return 1
        if dl["fa_clb"][c]["loai"] == GH:
            return 0
        cat = -max(giu0[c])[0][0] if giu0[c] else None
        d = diem(dl, s, c, buoc)
        return 0 if cat is not None and abs(d - cat) < 1e-9 else (1 if cat is not None and d > cat else 2)
    uv = [c for c in ds if dl["fa_clb"][c]["loai"] != TD and _vao_duoc(dl, s, c, buoc)]
    return dict(zip(sorted(uv, key=lambda c: (nhom(c), uv.index(c))), GT))


KICH_BAN = [
    ("S0 baseline", "C0", 1, "STB"),
    ("S1 seats ~ this term's demand", "C1", 1, "STB"),
    ("S2 seats ~ last term's demand", "C2", 1, "STB"),
    ("S3 +15% seats where over-demanded", "C3", 1, "STB"),
    ("S4 score step 0.5", "C0", 0.5, "STB"),
    ("S5 score step 0.1", "C0", 0.1, "STB"),
    ("S6 lottery per club (MTB)", "C0", 1, "MTB"),
    ("S7 = S2 + S5", "C2", 0.1, "STB"),
]


def bang(so_seed=10):
    print("### G-H main table, school size (%d data seeds x 3 days x 800 students) — %s" % (so_seed, NHAN))
    print("Profile: 30 % luoi and 50 % that_tha keep the default medals; 20 % chien_luoc use the informed rule.")
    print("| scenario | medals | rejections per 100 student-days | decided by SCORE / MEDAL / LOTTERY % |"
          " % student-days with a lottery loss | % students with a lottery loss on 2-3 days | % true NV1 |"
          " mean utility | utility luoi / that_tha / chien_luoc | bottom 10 %: mean 3-day utility |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for ten, kieu_cho, buoc, kieu_so in KICH_BAN:
        for d1 in (False, True):
            ld = {"SCORE": 0, "MEDAL": 0, "LOTTERY": 0}
            n_sd = thua_sd = nv1 = 0
            u_tong = 0.0
            u_hv = {h: [0, 0.0] for h in mp.HANH_VI}
            nhieu_ngay = n_hs = 0
            day = []
            for sd in range(so_seed):
                dl = sinh_truong(seed=sd)
                prefs = mp.dang_ky(dl)[0]
                dl_tr = _khoa_hoc_sinh_khac(dl, sd)
                prefs_tr = mp.dang_ky(dl_tr)[0]
                u3 = {s: 0.0 for s in dl["sids"]}
                so_thua = {s: 0 for s in dl["sids"]}
                for b in dl["ds_buoi"]:
                    pr = {s: [c for c in prefs[s] if dl["buoi_cua"][c] == b] for s in dl["sids"]}
                    pr_tr = {s: [c for c in prefs_tr[s] if dl["buoi_cua"][c] == b] for s in dl["sids"]}
                    cho = cho_ngoi(dl, b, pr, buoc, kieu_cho, dl_tr, pr_tr)
                    huy = huy_mac_dinh(dl, pr, buoc, d1)
                    cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
                    truoc = _stb_ngau_nhien(dl, (sd, b, "truoc"))
                    a0, ly0, giu0 = da_ngay(dl, b, pr, huy, cho, {c: truoc for c in cs}, buoc)
                    for s in dl["sids"]:
                        if dl["hs"][s]["hanh_vi"] == "chien_luoc":
                            huy[s] = _chien_luoc(dl, s, pr[s], a0, giu0, ly0, buoc)
                    a, ly, _ = da_ngay(dl, b, pr, huy, cho, _so(dl, b, sd, kieu_so), buoc)
                    for s in dl["sids"]:
                        vt = mp._vi_tri(dl, s, b)
                        u = dl["hs"][s]["thich"][a[s]]
                        n_sd += 1
                        u_tong += u
                        nv1 += a[s] == vt[0]
                        u3[s] += u
                        t = u_hv[dl["hs"][s]["hanh_vi"]]
                        t[0] += 1
                        t[1] += u
                        co = False
                        for _, r in ly[s]:
                            ld[r] += 1
                            co = co or r == "LOTTERY"
                        thua_sd += co
                        so_thua[s] += co
                v = sorted(u3.values())
                day.append(sum(v[:len(v) // 10]) / (len(v) // 10))
                nhieu_ngay += sum(1 for s in so_thua if so_thua[s] >= 2)
                n_hs += len(so_thua)
            m = sum(ld.values()) or 1
            print("| %s | %s | %.1f | %.0f / %.0f / %.0f | %.1f | %.1f | %.1f | %.4f | %s | %.3f |" % (
                ten, "D1" if d1 else "D0", 100 * m / n_sd, 100 * ld["SCORE"] / m, 100 * ld["MEDAL"] / m,
                100 * ld["LOTTERY"] / m, 100 * thua_sd / n_sd, 100 * nhieu_ngay / n_hs, 100 * nv1 / n_sd,
                u_tong / n_sd, " / ".join("%.3f" % (u_hv[h][1] / u_hv[h][0]) for h in mp.HANH_VI),
                sum(day) / len(day)))


def doi_cho(so_seed=10):
    """MEASUREMENT MODE (label: không bảo đảm ổn định): stable improvement cycles (`fa_vong_doi_cho`) run after the
    research DA, medals D0, informed profile as in `bang`. Only lottery order is overridden, never score or medal."""
    import fa_vong_doi_cho as vd
    print("### G-H improvement cycles after DA, measurement mode (%s) — %s" % (vd.NHAN_KHONG_BAO_DAM, NHAN))
    print("| seats | % student-days that move to a club they ranked higher | % true NV1 before -> after |"
          " mean utility before -> after | by type, % who move: luoi / that_tha / chien_luoc |")
    print("|---|---|---|---|---|")
    for kieu_cho in ("C0", "C2"):
        n = doi = 0
        nv = [0, 0]
        u = [0.0, 0.0]
        hv = {h: [0, 0] for h in mp.HANH_VI}
        for sd in range(so_seed):
            dl = sinh_truong(seed=sd)
            prefs = mp.dang_ky(dl)[0]
            dl_tr = _khoa_hoc_sinh_khac(dl, sd)
            prefs_tr = mp.dang_ky(dl_tr)[0]
            for b in dl["ds_buoi"]:
                pr = {s: [c for c in prefs[s] if dl["buoi_cua"][c] == b] for s in dl["sids"]}
                pr_tr = {s: [c for c in prefs_tr[s] if dl["buoi_cua"][c] == b] for s in dl["sids"]}
                cho = cho_ngoi(dl, b, pr, 1, kieu_cho, dl_tr, pr_tr)
                huy = huy_mac_dinh(dl, pr, 1, False)
                cs = [c for c in dl["clubs"] if dl["buoi_cua"][c] == b]
                truoc = _stb_ngau_nhien(dl, (sd, b, "truoc"))
                a0, ly0, giu0 = da_ngay(dl, b, pr, huy, cho, {c: truoc for c in cs}, 1)
                for s in dl["sids"]:
                    if dl["hs"][s]["hanh_vi"] == "chien_luoc":
                        huy[s] = _chien_luoc(dl, s, pr[s], a0, giu0, ly0, 1)
                a, _, _ = da_ngay(dl, b, pr, huy, cho, _so(dl, b, sd, "STB"), 1)
                tu_do = next(c for c in cs if dl["fa_clb"][c]["loai"] == TD)
                ds = {}
                for s in dl["sids"]:
                    d = [c for c in pr[s] if _vao_duoc(dl, s, c, 1)]
                    ds[s] = d if tu_do in d else d + [tu_do]
                khoa = {c: {} for c in cs}
                for s, d in ds.items():
                    for c in d:
                        m = -(huy.get(s) or {}).get(c, 0)
                        khoa[c][s] = (-diem(dl, s, c, 1), m) if dl["fa_clb"][c]["loai"] == TC else (0.0, 0 if c == tu_do else m)
                a2, _ = vd.chay_chu_trinh(dict(a), ds, khoa)
                for s in dl["sids"]:
                    vt = mp._vi_tri(dl, s, b)
                    n += 1
                    doi += a2[s] != a[s]
                    t = hv[dl["hs"][s]["hanh_vi"]]
                    t[0] += 1
                    t[1] += a2[s] != a[s]
                    for i, x in enumerate((a, a2)):
                        nv[i] += x[s] == vt[0]
                        u[i] += dl["hs"][s]["thich"][x[s]]
        print("| %s | %.1f | %.1f -> %.1f | %.4f -> %.4f | %s |" % (
            kieu_cho, 100 * doi / n, 100 * nv[0] / n, 100 * nv[1] / n, u[0] / n, u[1] / n,
            " / ".join("%.1f" % (100 * hv[h][1] / hv[h][0]) for h in mp.HANH_VI)))


if __name__ == "__main__":
    for _l in (sys.stdout, sys.stderr):
        if hasattr(_l, "reconfigure"):
            _l.reconfigure(encoding="utf-8", errors="replace")
    {"kiem": kiem, "bang": bang, "doi_cho": doi_cho}[sys.argv[1] if len(sys.argv) > 1 else "kiem"]()
