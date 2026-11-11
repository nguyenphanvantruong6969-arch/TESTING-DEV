"""FA-8 (Z6, FA-DAA): tính chất chấp nhận V§13 trên ~200 bộ nhỏ ngẫu nhiên (chỉ `random` của stdlib).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG sinh trong test (6-12 học sinh, 1-2 buổi, mỗi buổi 1 CLB Tự do và
1-3 CLB Giới hạn / Tuyển chọn, có huy chương và giữ chỗ). Mỗi bộ có seed cố định, nên lỗi tái lập được.

  13.1 khai thật thứ tự là tối ưu khi cố định huy chương (thử MỌI hoán vị; không đóng CLB thiếu người)
  13.2 ổn định (`verify_stability` rỗng)     13.3 CLB Tự do không từ chối   13.4 không vượt chỉ tiêu
  13.5 cùng seed cùng kết quả                13.6 dưới sàn không vào Tuyển chọn
  13.7 không bị từ chối khi người khoá thấp hơn được nhận   13.8 huy chương hợp lệ
  13.9 mọi từ chối có lý do hợp lệ           13.10 thuộc FA-7 (`test_fa_nhu_cau.py`)
  13.11 đóng CLB thiếu người thì hội tụ      13.12 ưu tiên bù: hoãn (D1)
"""

import copy
import itertools
import random

import pytest

import fa_daa
import rbda_priority_pipeline as rp

N_BO = 200
MA_LY_DO = {"SCORE", "MEDAL", "LOTTERY", "RESERVED", "BELOW_PASS", "NOT_ATTEMPTED", "CLUB_CLOSED",
            "KHONG_DANG_KY", "HET_NGUYEN_VONG", "ACCEPTED"}


def _bo(seed, toi_thieu=False):
    r = random.Random(seed)
    n = r.randint(6, 12)
    sids = ["s%02d" % i for i in range(n)]
    clubs, fa = {}, {}
    for b in range(r.randint(1, 2)):
        buoi = "b%d" % (b + 1)
        clubs["T%d" % (b + 1)] = {"capacity": 1, "reserve_capacity": 0, "reserve_group": None,
                                  "buoi": buoi}
        fa["T%d" % (b + 1)] = {"loai": "TU_DO", "diem_san": None, "so_toi_thieu": None,
                               "suc_chua_phong": r.choice([None, 3])}
        for k in range(r.randint(1, 3)):
            cid = "C%d%d" % (b + 1, k)
            loai = r.choice(["GIOI_HAN", "TUYEN_CHON"])
            clubs[cid] = {"capacity": r.randint(1, 3), "reserve_capacity": 0,
                          "reserve_group": None, "buoi": buoi}
            fa[cid] = {"loai": loai, "diem_san": r.randint(2, 7) if loai == "TUYEN_CHON" else None,
                       "so_toi_thieu": (r.randint(1, 3) if toi_thieu else None),
                       "suc_chua_phong": None}
    stb = dict(zip(sids, r.sample(range(1, n + 1), n)))
    students = {s: {"stb": stb[s], "reserve_group": None} for s in sids}
    prefs, diem, huy, ticks = {}, {c: {} for c in clubs}, {}, {c: [] for c in clubs}
    for s in sids:
        if r.random() < 0.1:
            continue
        ds = [c for c in clubs if r.random() < 0.6]
        r.shuffle(ds)
        if not ds:
            continue
        prefs[s] = ds
        for c in ds:
            if fa[c]["loai"] == "TUYEN_CHON" and r.random() < 0.8:
                ticks[c].append(s)
                diem[c][s] = float(r.randint(0, 10))
        for buoi in {clubs[c]["buoi"] for c in ds}:
            mc = [c for c in ds if clubs[c]["buoi"] == buoi and fa[c]["loai"] != "TU_DO"]
            huy.setdefault(s, {}).update(dict(zip(mc, r.sample((60, 30, 10), 3)[:len(mc)])))
    gc = []
    for cid, f in fa.items():
        if f["loai"] != "TU_DO" and r.random() < 0.4:
            ung = [s for s in prefs if cid in prefs[s]]
            if ung:
                gc.append((cid, r.choice(ung)))
    return dict(students=students, clubs=clubs, tested_scores=diem,
                applicants=rp.hop_ung_vien(ticks, prefs), preferences=prefs, stb_lottery=stb,
                fa_clb=fa, giu_cho=gc, huy_chuong=huy)


def _chay(bo, seed=0, **kw):
    return fa_daa.chay_fa_daa(**{**copy.deepcopy(bo), "seed": seed, **kw})


def _ngay(kq):
    return rp.nhom_theo_buoi(kq.clubs)


def _khoa(kq, bo, buoi, s, c):
    """Khoá ưu tiên độc lập với mã nguồn: (-giữ chỗ, -điểm, -huy chương, bốc thăm của buổi)."""
    stb = kq.ket_qua.stb_theo_buoi[buoi]
    diem = kq.tested_scores.get(c, {}).get(s) if bo["fa_clb"][c]["loai"] == "TUYEN_CHON" else None
    return (-(1 if kq.reserve_fn(s, c) else 0), -(diem or 0),
            -(bo["huy_chuong"].get(s) or {}).get(c, 0), stb[s])


SEEDS = range(N_BO)


@pytest.mark.parametrize("seed", SEEDS)
def test_13_2_on_dinh_va_hop_le(seed):
    bo = _bo(seed)
    kq = _chay(bo, seed)
    on_dinh = rp.verify_stability_tuan(kq.ket_qua, kq.clubs, kq.preferences, kq.reserve_fn)
    assert all(not v for v in on_dinh.values()), on_dinh
    for buoi, kb in kq.ket_qua.per_buoi.items():
        clubs_b, _, _, prefs_b = rp.cat_du_lieu_theo_buoi(
            buoi, _ngay(kq)[buoi], kq.clubs, kq.tested_scores, kq.applicants, kq.preferences)
        assert rp.sanity_check_result(kb, clubs_b, prefs_b) == []


@pytest.mark.parametrize("seed", SEEDS)
def test_13_3_13_4_tu_do_khong_tu_choi_va_khong_vuot_chi_tieu(seed):
    bo = _bo(seed)
    kq = _chay(bo, seed)
    for buoi in kq.ket_qua.ds_buoi:
        dem: dict = {}
        for s, c in kq.ket_qua.per_buoi[buoi].assignment.items():
            assert c is not None, (s, buoi)                       # mọi học sinh có CLB (V§8.6)
            dem[c] = dem.get(c, 0) + 1
        for c, n in dem.items():
            if bo["fa_clb"][c]["loai"] != "TU_DO":
                assert n <= bo["clubs"][c]["capacity"], (c, n)    # 13.4
        for s, ds in bo["preferences"].items():                   # 13.3: xếp CLB Tự do -> không bị bỏ rơi
            tu_do = [c for c in ds if bo["fa_clb"][c]["loai"] == "TU_DO"
                     and bo["clubs"][c]["buoi"] == buoi]
            if tu_do:
                cuoi = kq.ket_qua.assignment[s][buoi]
                trong_ngay = [c for c in ds if bo["clubs"][c]["buoi"] == buoi]
                assert trong_ngay.index(cuoi) <= trong_ngay.index(tu_do[0]), (s, cuoi)


@pytest.mark.parametrize("seed", SEEDS)
def test_13_5_cung_seed_cung_ket_qua(seed):
    bo = _bo(seed)
    a, b = _chay(bo, seed), _chay(bo, seed)
    assert a.ket_qua.assignment == b.ket_qua.assignment and a.nhom == b.nhom
    assert a.fallback == b.fallback and a.dong_cua == b.dong_cua


@pytest.mark.parametrize("seed", SEEDS)
def test_13_6_duoi_san_khong_vao_tuyen_chon(seed):
    bo = _bo(seed)
    kq = _chay(bo, seed)
    for s, theo in kq.ket_qua.assignment.items():
        for buoi, c in theo.items():
            if c is not None and bo["fa_clb"][c]["loai"] == "TUYEN_CHON":
                d = bo["tested_scores"][c].get(s)
                assert d is not None and d >= bo["fa_clb"][c]["diem_san"], (s, c, d)


@pytest.mark.parametrize("seed", SEEDS)
def test_13_7_khong_bi_tu_choi_khi_nguoi_khoa_thap_hon_duoc_nhan(seed):
    bo = _bo(seed)
    kq = _chay(bo, seed)
    ket = kq.ket_qua
    for buoi in ket.ds_buoi:
        asg = ket.per_buoi[buoi].assignment
        for c in _ngay(kq)[buoi]:
            if bo["fa_clb"][c]["loai"] == "TU_DO":
                continue
            tv = [m for m, x in asg.items() if x == c]
            for s, p in kq.preferences.items():
                if c not in p or asg[s] == c:
                    continue
                trong = [x for x in p if bo["clubs"][x]["buoi"] == buoi]
                if asg[s] is not None and trong.index(c) > trong.index(asg[s]):
                    continue                                        # s xếp CLB cuối tốt hơn c
                for m in tv:
                    assert _khoa(kq, bo, buoi, s, c) > _khoa(kq, bo, buoi, m, c), (s, m, c)


@pytest.mark.parametrize("seed", SEEDS)
def test_13_8_huy_chuong_hop_le(seed):
    bo = _bo(seed)
    assert fa_daa.kiem_ho_so_huy_chuong(bo["preferences"], bo["huy_chuong"], {
        c: {**bo["clubs"][c], **bo["fa_clb"][c]} for c in bo["clubs"]}) == []
    for s, m in bo["huy_chuong"].items():
        for buoi in {bo["clubs"][c]["buoi"] for c in m}:
            trong = [v for c, v in m.items() if bo["clubs"][c]["buoi"] == buoi]
            assert len(trong) <= 3 and len(set(trong)) == len(trong)   # tối đa 3 huy chương / ngày


@pytest.mark.parametrize("seed", SEEDS)
def test_13_9_moi_tu_choi_co_ly_do_hop_le(seed):
    bo = _bo(seed, toi_thieu=True)
    kq = _chay(bo, seed)
    rows = fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])
    cac = {(r["student_id"], r["club_id"]) for r in rows}
    for s, p in bo["preferences"].items():
        for buoi in kq.ket_qua.ds_buoi:
            trong = [c for c in p if bo["clubs"][c]["buoi"] == buoi]
            cuoi = kq.ket_qua.assignment[s][buoi]
            for c in (trong[:trong.index(cuoi)] if cuoi in trong else trong):
                assert (s, c) in cac
    assert all(r["reason"] in MA_LY_DO for r in rows)
    assert all(r["reason"] != "LOTTERY" or (r["n_hoa"] >= 1 and r["k_cho"] >= 1) for r in rows)


@pytest.mark.parametrize("seed", SEEDS)
def test_13_11_dong_clb_thieu_nguoi_hoi_tu(seed):
    bo = _bo(seed, toi_thieu=True)
    kq = _chay(bo, seed)                                 # không treo, không ném assert
    n_clb = sum(1 for f in bo["fa_clb"].values() if f["loai"] != "TU_DO")
    assert len(kq.dong_cua) <= n_clb
    dong = {d["club_id"] for d in kq.dong_cua}
    for buoi in kq.ket_qua.ds_buoi:
        dem: dict = {}
        for c in kq.ket_qua.per_buoi[buoi].assignment.values():
            dem[c] = dem.get(c, 0) + 1
        for c in _ngay(kq)[buoi]:
            f = bo["fa_clb"][c]
            if f["loai"] != "TU_DO" and f["so_toi_thieu"]:
                assert c in dong or dem.get(c, 0) >= f["so_toi_thieu"], (c, dem.get(c, 0))
                assert c not in dong or dem.get(c, 0) == 0
    assert _chay(bo, seed).dong_cua == kq.dong_cua        # chạy lại cùng STB: giống hệt
    on_dinh = rp.verify_stability_tuan(kq.ket_qua, kq.clubs, kq.preferences, kq.reserve_fn)
    assert all(not v for v in on_dinh.values())


@pytest.mark.parametrize("seed", range(40))
def test_13_1_khai_that_thu_tu_la_toi_uu(seed):
    bo = _bo(seed)
    goc = _chay(bo, seed)

    def hang(kq, s, bo_):
        ra = {}
        for buoi, c in kq.ket_qua.assignment[s].items():
            thuc = [x for x in bo_["preferences"].get(s, []) if bo_["clubs"][x]["buoi"] == buoi]
            ra[buoi] = thuc.index(c) if c in thuc else len(thuc)      # CLB dự phòng xếp sau mọi CLB đã chọn
        return ra

    n_thu = 0
    for s, ds in bo["preferences"].items():
        if len(ds) > 4:
            continue
        thuc = hang(goc, s, bo)
        for hv in itertools.permutations(ds):
            bo2 = copy.deepcopy(bo)
            bo2["preferences"][s] = list(hv)
            kq2 = fa_daa.chay_fa_daa(**{**copy.deepcopy(bo2), "seed": seed})
            kh = {buoi: (kq2.ket_qua.assignment[s][buoi]) for buoi in thuc}
            for buoi, c in kh.items():
                tl = [x for x in bo["preferences"][s] if bo["clubs"][x]["buoi"] == buoi]
                r2 = tl.index(c) if c in tl else len(tl)
                assert r2 >= thuc[buoi], (s, hv, buoi, c)            # không hoán vị nào tốt hơn
            n_thu += 1
    assert n_thu >= 1


def test_13_1_that_su_da_thu_hoan_vi():
    tong = 0
    for seed in range(40):
        bo = _bo(seed)
        tong += sum(len(list(itertools.permutations(ds))) for ds in bo["preferences"].values()
                    if len(ds) <= 4)
    assert tong > 1000


@pytest.mark.skip(reason="V§13.12 ưu tiên bù: hoãn sang kỳ 2 (D1); chưa làm trong kỳ này")
def test_13_12_uu_tien_bu():
    raise AssertionError("D1 chưa làm")
