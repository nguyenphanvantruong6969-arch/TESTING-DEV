"""Điểm Wharton (mục A13, FA-DAA): khoá ưu tiên, kiểm hồ sơ, điểm hiệu lực.

Mỗi học sinh có hai quỹ điểm ảo cho MỖI BUỔI: quỹ 1 chia cho các CLB em có thi (chỉ để phá
hoà khi bằng điểm thi), quỹ 2 chia cho các CLB không thi (tiêu chí chính của tầng 2). Điểm
Wharton được xét TRƯỚC số bốc thăm; số bốc thăm và cách chèn em đến muộn giữ nguyên.

Điều phải giữ:
  * Thứ hạng nguyện vọng không bao giờ vào khoá ưu tiên (W1, W8) — chữ ký hàm và hoán vị.
  * `diem_wharton=None` cho kết quả TRÙNG KHÍT như trước (bất biến 1).
  * Kết quả ổn định theo `verify_stability` (W6) và hàm lựa chọn thoả bất biến 8.
  * Dữ liệu dưới đây là dữ liệu MÔ PHỎNG, không phải khảo sát thật.
"""

import copy
import inspect
import itertools
import random
import re
from types import SimpleNamespace

import pytest

import rbda_priority_pipeline as rp
from i18n_errors import MESSAGES, format_message


# ------------------------------------------------------------------ hàm dựng dữ liệu

def du_lieu(cap, prefs, diem_thi, stb, tick=None, reserve=None, buoi=None,
            nhom_du_tru=None):
    """Dựng đúng định dạng đầu vào của `run_rbda`.

    cap:      {cid: sức chứa}
    prefs:    {sid: [cid, ...]} theo thứ tự nguyện vọng
    diem_thi: {cid: {sid: điểm}}
    stb:      {sid: số bốc thăm}
    tick:     {sid: set(cid)} ô "muốn thi"; mặc định là các CLB em có điểm thi
    reserve:  {cid: reserve_capacity}, mặc định 0
    buoi:     {cid: nhãn buổi}
    nhom_du_tru: {"hs": {sid: nhóm}, "clb": {cid: nhóm}} cho `default_reserve_eligible_fn`

    Trả về (students, clubs, tested_scores, applicants, preferences, stb_lottery).
    """
    reserve = reserve or {}
    buoi = buoi or {}
    nhom_du_tru = nhom_du_tru or {}
    nhom_hs = nhom_du_tru.get("hs", {})
    nhom_clb = nhom_du_tru.get("clb", {})

    preferences = {sid: list(ds) for sid, ds in prefs.items()}
    stb_lottery = dict(stb)
    mot_hs = sorted(set(preferences) | set(stb_lottery))
    students = {sid: {"stb": stb_lottery[sid], "reserve_group": nhom_hs.get(sid)}
                for sid in mot_hs}

    clubs = {}
    for cid, suc_chua in cap.items():
        thong_tin = {"capacity": suc_chua, "reserve_capacity": reserve.get(cid, 0)}
        if cid in buoi:
            thong_tin["buoi"] = buoi[cid]
        if cid in nhom_clb:
            thong_tin["reserve_group"] = nhom_clb[cid]
        clubs[cid] = thong_tin

    tested_scores = {cid: {sid: float(v) for sid, v in diem_thi.get(cid, {}).items()}
                     for cid in cap}
    if tick is None:
        tick = {sid: {cid for cid in cap if sid in tested_scores[cid]} for sid in mot_hs}
    dang_ky_thi = {cid: [sid for sid in mot_hs if cid in tick.get(sid, set())]
                   for cid in cap}
    applicants = rp.hop_ung_vien(dang_ky_thi, preferences)
    return students, clubs, tested_scores, applicants, preferences, stb_lottery


def chay(d, diem_wharton=None, tier_rank=None, eligible=None, bo_qua_du_tru=False):
    """Gọi `rp.run_rbda` trên bộ `d` do `du_lieu` trả về.

    Chỉ truyền tham số tuỳ chọn khi có giá trị, để cùng một hàm dùng được cả khi so với lời
    gọi cũ. `eligible` mặc định không ai đủ điều kiện dự trữ.
    """
    students, clubs, tested_scores, applicants, preferences, stb_lottery = d
    elig = eligible if eligible is not None else (lambda s, c: False)
    kw = {}
    if diem_wharton is not None:
        kw["diem_wharton"] = diem_wharton
    if tier_rank is not None:
        kw["tier_rank"] = tier_rank
    if bo_qua_du_tru:
        kw["bo_qua_du_tru"] = True
    return rp.run_rbda(students, clubs, tested_scores, applicants, preferences,
                       stb_lottery, elig, **kw)


# ------------------------------------------------------------------ khung

def test_helper_dung_du_lieu_va_chay_duoc():
    """Hàm dựng dữ liệu cho ra đúng định dạng của `run_rbda` (chưa dính Wharton)."""
    d = du_lieu(
        cap={"Debate": 1},
        prefs={"An": ["Debate"], "Binh": ["Debate"]},
        diem_thi={},
        stb={"An": 0, "Binh": 1},
    )
    students, clubs, scores, app, prefs, stb = d
    assert sorted(students) == ["An", "Binh"]
    assert clubs["Debate"] == {"capacity": 1, "reserve_capacity": 0}
    assert scores == {"Debate": {}}
    assert app == {"Debate": ["An", "Binh"]}
    kq = chay(d)
    assert kq.assignment == {"An": "Debate", "Binh": None}


def test_co_ham_wharton():
    ham = ["khoa_uu_tien_wharton", "uu_tien_wharton", "kiem_ho_so_wharton",
           "tu_dien_wharton_mot_clb", "diem_wharton_hieu_luc"]
    hang = ["WHARTON_NGAN_SACH", "WHARTON_TU_DIEN_MOT_CLB", "WHARTON_VANG_THI"]
    thieu = [ten for ten in ham + hang if not hasattr(rp, ten)]
    assert not thieu, "rbda_priority_pipeline chưa có: %s" % thieu


# ------------------------------------------------------------------ khoá ưu tiên (Bước 4)

class TestKhoaUuTien:
    def test_dang_khoa_hai_tang(self):
        assert rp.khoa_uu_tien_wharton("a", 8.0, 30, 0, 5) == (0, -8.0, (), -30, 5, "a")
        assert rp.khoa_uu_tien_wharton("a", None, 0, 70, 5) == (1, -70, 5, "a")

    def test_moi_khoa_tang_1_nho_hon_moi_khoa_tang_2(self):
        # kể cả khi tầng 2 dồn hết 100 điểm và tầng 1 không có điểm nào
        tang_1 = [rp.khoa_uu_tien_wharton("x", d, 0, 0, 99) for d in (0.0, 3.5, 10.0)]
        tang_2 = [rp.khoa_uu_tien_wharton("y", None, 0, 100, 0)]
        assert max(tang_1) < min(tang_2)

    def test_w3_diem_thi_dung_truoc_diem_wharton(self):
        thap_dong_het = rp.khoa_uu_tien_wharton("a", 7.0, 100, 0, 1)
        cao_khong_dong = rp.khoa_uu_tien_wharton("b", 7.5, 0, 0, 2)
        assert cao_khong_dong < thap_dong_het

    def test_bang_diem_thi_thi_w1_lon_hon_dung_truoc_bat_ke_stb(self):
        lon = rp.khoa_uu_tien_wharton("a", 8.0, 60, 0, 99)
        nho = rp.khoa_uu_tien_wharton("b", 8.0, 40, 0, 0)
        assert lon < nho

    def test_bang_ca_w1_thi_stb_nho_hon_dung_truoc(self):
        assert (rp.khoa_uu_tien_wharton("a", 8.0, 50, 0, 1)
                < rp.khoa_uu_tien_wharton("b", 8.0, 50, 0, 2))

    def test_bang_ca_stb_thi_xep_theo_ma_hoc_sinh(self):
        assert (rp.khoa_uu_tien_wharton("a", 8.0, 50, 0, 3)
                < rp.khoa_uu_tien_wharton("b", 8.0, 50, 0, 3))
        assert (rp.khoa_uu_tien_wharton("a", None, 0, 50, 3)
                < rp.khoa_uu_tien_wharton("b", None, 0, 50, 3))

    def test_tang_2_w2_lon_hon_dung_truoc_bat_ke_stb(self):
        assert (rp.khoa_uu_tien_wharton("a", None, 0, 70, 99)
                < rp.khoa_uu_tien_wharton("b", None, 0, 30, 0))

    def test_w1_chu_ky_khong_co_nguyen_vong(self):
        ten = set(inspect.signature(rp.khoa_uu_tien_wharton).parameters)
        assert ten == {"student_id", "diem_thi", "w1", "w2", "stb"}
        for t in ten:
            assert not any(x in t for x in ("pref", "rank", "nguyen_vong", "nv")), t

    def test_hang_cau_hinh(self):
        assert rp.WHARTON_NGAN_SACH == 100
        assert rp.WHARTON_TU_DIEN_MOT_CLB is True
        assert rp.WHARTON_VANG_THI == "tier2_zero_points"


# ------------------------------------------------------------------ hàm bọc (Bước 5)

def _bo_cho_mot_clb(rng, n=None, trung_stb=False):
    """(applicants, tested, stb) ngẫu nhiên cho MỘT CLB; điểm thi là bội số của 0.25 để hay
    trùng điểm."""
    n = n or rng.randint(2, 12)
    sids = ["s%02d" % i for i in range(n)]
    applicants = list(sids)
    rng.shuffle(applicants)
    tested = {sid: rng.randint(20, 40) * 0.25 for sid in sids if rng.random() < 0.5}
    if trung_stb:
        stb = {sid: rng.randint(0, 3) for sid in sids}
    else:
        so = list(range(n))
        rng.shuffle(so)
        stb = dict(zip(sids, so))
    return applicants, tested, stb


class TestUuTienWharton:
    def test_thieu_stb_nem_value_error_giong_het_ham_cu(self):
        for stb in ({"a": 1, "b": None}, {"a": 1}, {}):
            with pytest.raises(ValueError) as cu:
                rp.compute_club_priority("X", ["a", "b", "c"], {"a": 5.0}, stb)
            with pytest.raises(ValueError) as moi:
                rp.uu_tien_wharton("X", ["a", "b", "c"], {"a": 5.0}, stb, {})
            assert str(moi.value) == str(cu.value)

    def test_diem_wharton_bang_nhau_thi_y_het_compute_club_priority(self):
        rng = random.Random(20261024)
        for i in range(200):
            applicants, tested, stb = _bo_cho_mot_clb(rng, trung_stb=(i % 4 == 0))
            mong_doi = rp.compute_club_priority("X", applicants, tested, stb)
            assert rp.uu_tien_wharton("X", applicants, tested, stb, {}) == mong_doi
            deu = {sid: 37 for sid in applicants}
            assert rp.uu_tien_wharton("X", applicants, tested, stb, deu) == mong_doi

    def test_tang_2_diem_wharton_cao_thang_du_stb_lon_hon(self):
        # Ha có STB lớn (thua) nhưng 80 điểm; Khoa STB nhỏ nhưng 20 điểm
        ra = rp.uu_tien_wharton("X", ["Khoa", "Ha"], {}, {"Ha": 9, "Khoa": 0},
                                {"Ha": 80, "Khoa": 20})
        assert ra == ["Ha", "Khoa"]

    def test_tang_1_diem_thi_truoc_roi_moi_den_wharton(self):
        tested = {"a": 7.0, "b": 7.5, "c": 7.5}
        ra = rp.uu_tien_wharton("X", ["a", "b", "c"], tested,
                                {"a": 0, "b": 1, "c": 2}, {"a": 100, "b": 0, "c": 40})
        # b và c cao điểm hơn a dù a dồn hết 100 điểm; c bằng điểm b nhưng nhiều Wharton hơn
        assert ra == ["c", "b", "a"]

    def test_tang_duoc_xac_dinh_bang_co_diem_thi_nen_diem_0_van_la_tang_1(self):
        ra = rp.uu_tien_wharton("X", ["khong_thi", "thi_0"], {"thi_0": 0.0},
                                {"khong_thi": 0, "thi_0": 9}, {"khong_thi": 100})
        assert ra == ["thi_0", "khong_thi"]

    def test_tier_rank_nhom_tot_hon_dung_truoc_nguoi_khong_nhom_cuoi(self):
        tested = {"a": 5.0, "c": 9.0}
        stb = {"a": 3, "b": 2, "c": 1, "d": 0}
        wh = {"a": 10, "b": 90, "c": 50, "d": 100}
        tier_rank = {"a": 0, "b": 0, "c": 1}          # d không có nhóm
        ra = rp.uu_tien_wharton("X", ["a", "b", "c", "d"], tested, stb, wh,
                                tier_rank=tier_rank)
        assert ra == ["a", "b", "c", "d"]
        # nhóm 0 trước nhóm 1 trước người không nhóm, bất kể điểm thi hay điểm Wharton
        assert ra.index("c") > ra.index("b") and ra.index("d") == 3

    def test_tier_rank_trong_cung_nhom_giong_khi_loc_rieng_nhom_do(self):
        rng = random.Random(7)
        for _ in range(60):
            applicants, tested, stb = _bo_cho_mot_clb(rng, n=rng.randint(4, 12))
            wh = {sid: rng.randint(0, 100) for sid in applicants if rng.random() < 0.7}
            tier_rank = {sid: rng.randint(0, 2) for sid in applicants if rng.random() < 0.8}
            ra = rp.uu_tien_wharton("X", applicants, tested, stb, wh, tier_rank=tier_rank)
            cuoi = max(tier_rank.values(), default=-1) + 1
            for hang in sorted(set(tier_rank.get(s, cuoi) for s in applicants)):
                nhom = [s for s in applicants if tier_rank.get(s, cuoi) == hang]
                rieng = rp.uu_tien_wharton(
                    "X", nhom, {s: tested[s] for s in nhom if s in tested}, stb, wh)
                assert [s for s in ra if s in set(nhom)] == rieng
            # và các nhóm nằm liền nhau theo đúng hạng
            hang_theo_vi_tri = [tier_rank.get(s, cuoi) for s in ra]
            assert hang_theo_vi_tri == sorted(hang_theo_vi_tri)

    def test_diem_wharton_bang_nhau_voi_tier_rank_y_het_uu_tien_theo_nhom(self):
        rng = random.Random(11)
        for _ in range(60):
            applicants, tested, stb = _bo_cho_mot_clb(rng, n=rng.randint(3, 12))
            tier_rank = {sid: rng.randint(0, 2) for sid in applicants if rng.random() < 0.8}
            mong_doi = rp.uu_tien_theo_nhom("X", applicants, tested, stb, tier_rank)
            assert rp.uu_tien_wharton("X", applicants, tested, stb, {},
                                      tier_rank=tier_rank) == mong_doi

    def test_w1_chu_ky_khong_co_nguyen_vong(self):
        ten = set(inspect.signature(rp.uu_tien_wharton).parameters)
        assert ten == {"club_id", "applicants_for_club", "tested_scores_for_club",
                       "stb_lottery", "diem_wharton_clb", "tier_rank"}
        assert not any("pref" in t for t in ten)
        # hàm gốc giữ nguyên bốn tham số cũ
        assert list(inspect.signature(rp.compute_club_priority).parameters) == [
            "club_id", "applicants_for_club", "tested_scores_for_club", "stb_lottery"]


# ------------------------------------------------------------------ bộ sinh ngẫu nhiên

def sinh_du_lieu(rng, n_hs=12, n_clb=5, co_du_tru=False, co_nhom=False, so_buoi=1):
    """Một bộ dữ liệu MÔ PHỎNG ngẫu nhiên đủ để chạy `run_rbda` / `run_rbda_nhieu_buoi`.

    Điểm thi là bội số của 0.25 (hay trùng điểm); mỗi em thi khoảng 40 % số CLB trong danh sách
    của mình. `so_buoi > 1` thì CLB i thuộc buổi `b{i % so_buoi}`. `co_du_tru` cho một số CLB
    có suất dự trữ và nhóm "G"; `co_nhom` cho `tier_rank`. Trả về SimpleNamespace.
    """
    cids = ["c%d" % i for i in range(n_clb)]
    sids = ["s%02d" % i for i in range(n_hs)]
    cap = {c: rng.randint(1, 3) for c in cids}
    buoi = {c: "b%d" % (i % so_buoi) for i, c in enumerate(cids)} if so_buoi > 1 else None
    reserve, nhom = {}, None
    if co_du_tru:
        reserve = {c: rng.randint(0, cap[c]) for c in cids}
        nhom = {"hs": {s: "G" for s in sids if rng.random() < 0.5},
                "clb": {c: "G" for c in cids if reserve[c] > 0}}
    prefs = {}
    for s in sids:
        k = rng.randint(1, min(4, n_clb))
        prefs[s] = rng.sample(cids, k)
    diem_thi = {c: {} for c in cids}
    for s in sids:
        for c in prefs[s]:
            if rng.random() < 0.4:
                diem_thi[c][s] = rng.randint(20, 40) * 0.25
    so = list(range(n_hs))
    rng.shuffle(so)
    stb = dict(zip(sids, so))
    d = du_lieu(cap, prefs, diem_thi, stb, reserve=reserve, buoi=buoi, nhom_du_tru=nhom)
    students, clubs = d[0], d[1]
    eligible = rp.default_reserve_eligible_fn(students, clubs)
    tier_rank = ({s: rng.randint(0, 2) for s in sids if rng.random() < 0.8}
                 if co_nhom else None)
    return SimpleNamespace(
        d=d, cap=cap, prefs=prefs, diem_thi=diem_thi, stb=stb, buoi=buoi, reserve=reserve,
        nhom=nhom, eligible=eligible, tier_rank=tier_rank, sids=sids, cids=cids)


def diem_ngau_nhien(rng, bo):
    """Điểm hiệu lực ngẫu nhiên (0..100) cho mọi cặp (CLB, em có CLB đó trong danh sách)."""
    ra = {c: {} for c in bo.cids}
    for s, ds in bo.prefs.items():
        for c in ds:
            ra[c][s] = rng.randint(0, 100)
    return ra


# ------------------------------------------------------------------ nối vào run_rbda (Bước 6)

class TestNoiVaoRunRbda:
    def test_vd1_diem_wharton_quyet_dinh_truoc_stb_tang_2(self):
        d = du_lieu(
            cap={"Debate": 1, "NhiepAnh": 5, "Robotics": 5},
            prefs={"An": ["Debate", "NhiepAnh"], "Binh": ["Debate", "Robotics"]},
            diem_thi={}, stb={"An": 1, "Binh": 0},       # STB đặt NGƯỢC: Bình đứng trước
        )
        dw = {"Debate": {"An": 70, "Binh": 30}, "NhiepAnh": {"An": 30},
              "Robotics": {"Binh": 70}}
        kq = chay(d, diem_wharton=dw)
        assert kq.assignment == {"An": "Debate", "Binh": "Robotics"}
        # đối chứng: không có Wharton thì STB quyết định, Bình lấy Debate
        assert chay(d).assignment == {"An": "NhiepAnh", "Binh": "Debate"}

    def test_vd2_tang_1_dung_truoc_tang_2_du_wharton_tang_2_bang_100(self):
        d = du_lieu(
            cap={"Robotics": 1, "VanHoc": 5},
            prefs={"Chi": ["Robotics"], "Dung": ["Robotics", "VanHoc"]},
            diem_thi={"Robotics": {"Chi": 6.5}},
            stb={"Dung": 0, "Chi": 1},
        )
        dw = {"Robotics": {"Chi": 100, "Dung": 100}, "VanHoc": {"Dung": 0}}
        assert chay(d, diem_wharton=dw).assignment == {"Chi": "Robotics", "Dung": "VanHoc"}

    def test_vd3_bang_diem_thi_thi_wharton_quy_1_pha_hoa(self):
        d = du_lieu(
            cap={"Toan": 1, "Hoa": 1, "Ly": 1},
            prefs={"Em": ["Toan", "Hoa"], "Giang": ["Toan", "Ly"]},
            diem_thi={"Toan": {"Em": 8.25, "Giang": 8.25}, "Hoa": {"Em": 7.0},
                      "Ly": {"Giang": 9.0}},
            stb={"Giang": 0, "Em": 1},
        )
        dw = {"Toan": {"Em": 60, "Giang": 40}, "Hoa": {"Em": 40}, "Ly": {"Giang": 60}}
        assert chay(d, diem_wharton=dw).assignment == {"Em": "Toan", "Giang": "Ly"}
        # đối chứng: STB một mình xếp Giang trước, Giang lấy Toán
        assert chay(d).assignment["Giang"] == "Toan"

    def test_vd4_bang_ca_diem_wharton_thi_den_stb(self):
        def lam(stb):
            d = du_lieu(cap={"Debate": 1, "CoVua": 5},
                        prefs={"Ha": ["Debate", "CoVua"], "Khoa": ["Debate", "CoVua"]},
                        diem_thi={}, stb=stb)
            dw = {"Debate": {"Ha": 50, "Khoa": 50}, "CoVua": {"Ha": 50, "Khoa": 50}}
            return chay(d, diem_wharton=dw).assignment["Ha"]
        assert lam({"Ha": 0, "Khoa": 1}) == "Debate"
        assert lam({"Ha": 1, "Khoa": 0}) == "CoVua"

    def _vd5(self, prefs_lan):
        d = du_lieu(
            cap={"Toan": 5, "Debate": 1, "CoVua": 5},
            prefs={"Lan": prefs_lan, "Minh": ["Debate", "CoVua"]},
            diem_thi={"Toan": {"Lan": 9.0}},
            stb={"Minh": 0, "Lan": 1},
        )
        dw = {"Toan": {"Lan": 100}, "Debate": {"Lan": 100, "Minh": 80},
              "CoVua": {"Minh": 20}}
        return chay(d, diem_wharton=dw)

    def test_vd5_thu_hang_nguyen_vong_khong_vao_khoa(self):
        a = self._vd5(["Debate", "Toan"])
        assert a.assignment == {"Lan": "Debate", "Minh": "CoVua"}
        b = self._vd5(["Toan", "Debate"])            # giữ nguyên điểm, đảo thứ hạng
        assert b.base_rank == a.base_rank            # thứ tự ưu tiên mọi CLB y hệt
        # Lan được CLB đứng đầu danh sách mới của em, là CLB kém hơn theo thứ tự thật
        assert b.assignment == {"Lan": "Toan", "Minh": "Debate"}

    def test_w7_tat_dinh_chay_hai_lan_ra_y_het(self):
        rng = random.Random(70)
        for _ in range(10):
            bo = sinh_du_lieu(rng, co_nhom=True)
            dw = diem_ngau_nhien(rng, bo)
            a = chay(bo.d, diem_wharton=dw, tier_rank=bo.tier_rank)
            b = chay(bo.d, diem_wharton=dw, tier_rank=bo.tier_rank)
            assert (a.assignment, a.base_rank, a.rejection_log) == (
                b.assignment, b.base_rank, b.rejection_log)

    def test_mac_dinh_none_giu_nguyen_ket_qua_cu(self):
        rng = random.Random(1024)
        for i in range(30):
            bo = sinh_du_lieu(rng, n_hs=rng.randint(4, 14), n_clb=rng.randint(2, 6),
                              co_du_tru=(i % 2 == 0), co_nhom=(i % 3 == 0))
            students, clubs, scores, app, prefs, stb = bo.d
            cu = rp.run_rbda(students, clubs, scores, app, prefs, stb, bo.eligible,
                             tier_rank=bo.tier_rank)
            moi = rp.run_rbda(students, clubs, scores, app, prefs, stb, bo.eligible,
                              tier_rank=bo.tier_rank, diem_wharton=None)
            for ten in ("assignment", "base_rank", "matched_tier", "rank_in_student_pref",
                        "rounds_run"):
                assert getattr(moi, ten) == getattr(cu, ten), (i, ten)

    def test_diem_wharton_that_su_doi_ket_qua(self):
        """Đối chứng ngược: nếu `diem_wharton` bị bỏ qua lặng lẽ thì test này đỏ."""
        rng = random.Random(5)
        khac = 0
        for _ in range(30):
            bo = sinh_du_lieu(rng, n_hs=14, n_clb=3)
            dw = diem_ngau_nhien(rng, bo)
            if chay(bo.d, diem_wharton=dw).base_rank != chay(bo.d).base_rank:
                khac += 1
        assert khac >= 20

    def test_nhieu_buoi_moi_buoi_bang_run_rbda_rieng_buoi_do(self):
        rng = random.Random(88)
        for seed in range(8):
            bo = sinh_du_lieu(rng, n_hs=12, n_clb=6, so_buoi=2, co_du_tru=(seed % 2 == 0))
            dw = diem_ngau_nhien(rng, bo)
            students, clubs, scores, app, prefs, stb = bo.d
            ket = rp.run_rbda_nhieu_buoi(
                students, clubs, scores, app, prefs, stb, bo.eligible, seed=seed,
                diem_wharton=dw)
            theo_buoi = rp.nhom_theo_buoi(clubs)
            assert len(ket.ds_buoi) == 2
            for buoi, ds_clb in theo_buoi.items():
                clubs_b, scores_b, app_b, prefs_b = rp.cat_du_lieu_theo_buoi(
                    buoi, ds_clb, clubs, scores, app, prefs)
                rieng = rp.run_rbda(students, clubs_b, scores_b, app_b, prefs_b,
                                    ket.stb_theo_buoi[buoi], bo.eligible, diem_wharton=dw)
                assert ket.per_buoi[buoi].assignment == rieng.assignment, (seed, buoi)
                assert ket.per_buoi[buoi].base_rank == rieng.base_rank, (seed, buoi)


# ------------------------------------------------------------------ mã lỗi song ngữ (Bước 7)

MA_WHARTON = [
    "wharton_nguyen_vong_chua_xep", "wharton_chua_dung_het", "wharton_vuot_ngan_sach",
    "wharton_diem_khong_hop_le", "wharton_ngoai_tap", "wharton_tang_lech", "wharton_vang_thi",
]

# Tham số mà câu cần (ngoài các chỗ giữ nhãn {person}, {slot}…); các bước sau gọi err() đúng
# những tên này.
THAM_SO_WHARTON = {
    "wharton_nguyen_vong_chua_xep": {"student_id", "tran", "n", "n_trung"},
    "wharton_chua_dung_het": {"student_id", "thieu", "quy"},
    "wharton_vuot_ngan_sach": {"student_id", "tong", "quy", "ngan_sach"},
    "wharton_diem_khong_hop_le": {"student_id", "gia_tri", "club_id"},
    "wharton_ngoai_tap": {"student_id", "quy", "club_id"},
    "wharton_tang_lech": {"student_id", "club_id"},
    "wharton_vang_thi": {"student_id", "club_id", "diem", "diem_bo"},
}

NHAN_CONG_TY = {
    "person": {"vi": "Nhân viên", "en": "Employee"},
    "slot": {"vi": "Dự án", "en": "Project"},
    "session": {"vi": "Ca", "en": "Shift"},
    "group": {"vi": "Cấp bậc", "en": "Level"},
    "score": {"vi": "Điểm", "en": "Score"},
}


class TestMaLoi:
    @pytest.mark.parametrize("ma", MA_WHARTON)
    def test_co_du_vi_va_en(self, ma):
        assert ma in MESSAGES
        assert MESSAGES[ma].get("vi") and MESSAGES[ma].get("en")

    def test_cau_vi_mo_dau_dung_giong(self):
        assert MESSAGES["wharton_nguyen_vong_chua_xep"]["vi"].startswith(
            "Nguyện vọng chưa được sắp xếp xong.")
        assert MESSAGES["wharton_chua_dung_het"]["vi"].startswith(
            "Chưa dùng hết điểm quyết tâm")

    @pytest.mark.parametrize("ma", MA_WHARTON)
    def test_khong_viet_cung_nhan_trong_cau(self, ma):
        vi = re.sub(r"\{\w+\}", "", MESSAGES[ma]["vi"]).lower()    # bỏ chỗ giữ như {club_id}
        en = re.sub(r"\{\w+\}", "", MESSAGES[ma]["en"]).lower()
        for tu in ("học sinh", "câu lạc bộ", "clb"):
            assert tu not in vi, (ma, tu)
        for tu in ("student", "club"):
            assert tu not in en, (ma, tu)

    @pytest.mark.parametrize("ma", MA_WHARTON)
    @pytest.mark.parametrize("nhan", [None, NHAN_CONG_TY], ids=["truong_hoc", "cong_ty"])
    @pytest.mark.parametrize("lang", ["vi", "en"])
    def test_dien_duoc_tham_so_va_nhan(self, ma, nhan, lang):
        tham_so = {ten: "X" for ten in THAM_SO_WHARTON[ma]}
        cau = format_message(ma, tham_so, lang, nhan)
        assert cau != ma
        assert "{" not in cau and "}" not in cau, cau
        assert cau.count("X") >= len(THAM_SO_WHARTON[ma])      # mọi tham số đều hiện ra
        if nhan is NHAN_CONG_TY:
            # nhãn của workspace thay chỗ giữ: câu công ty không còn chữ của trường học
            assert "học sinh" not in cau.lower() and "câu lạc bộ" not in cau.lower()


# ------------------------------------------------------------------ kiểm hồ sơ (Bước 8, W5)

BM = rp.BUOI_MAC_DINH


def loi(ma, **tham_so):
    return {"code": ma, "params": tham_so}


def _clb(*ten, buoi=None):
    return {c: ({"capacity": 1, "reserve_capacity": 0, **({"buoi": buoi[c]} if buoi else {})})
            for c in ten}


def kiem(prefs, thi, w1, w2, clubs=None, **kw):
    """Gọi `kiem_ho_so_wharton` với bộ CLB một buổi suy ra từ chính hồ sơ nếu không đưa vào."""
    if clubs is None:
        moi = {c for ds in prefs.values() for c in ds}
        clubs = _clb(*sorted(moi))
    return rp.kiem_ho_so_wharton(prefs, thi, w1, w2, clubs, **kw)


class TestKiemHoSo:
    def test_ho_so_hop_le_tra_rong(self):
        assert kiem({"a": ["X", "Y", "Z"]}, {"a": {"X"}},
                    {"a": {"X": 100}}, {"a": {"Y": 60, "Z": 40}}) == []

    def test_v5_dan_100_diem_vao_mot_clb_la_hop_le(self):
        assert kiem({"a": ["X", "Y", "Z"]}, {}, {}, {"a": {"X": 100, "Y": 0, "Z": 0}}) == []
        assert kiem({"a": ["X", "Y"]}, {"a": {"X"}}, {"a": {"X": 100}}, {"a": {"Y": 100}}) == []

    # ---- V1
    def test_v1_nguyen_vong_rong(self):
        assert kiem({"a": []}, {}, {}, {}) == [
            loi("wharton_nguyen_vong_chua_xep", student_id="a", tran=10, n=0, n_trung=0,
                buoi=BM)]

    def test_v1_co_diem_nhung_khong_co_nguyen_vong(self):
        # em chỉ xuất hiện ở w1: báo thiếu nguyện vọng và điểm đặt vào tập rỗng
        ra = kiem({}, {}, {"a": {"X": 100}}, {}, clubs=_clb("X"))
        assert ra == [
            loi("wharton_nguyen_vong_chua_xep", student_id="a", tran=10, n=0, n_trung=0,
                buoi=BM),
            loi("wharton_ngoai_tap", student_id="a", quy=1, club_id="X", buoi=BM)]

    def test_v1_11_clb_trong_mot_buoi(self):
        ds = ["c%02d" % i for i in range(11)]
        ra = kiem({"a": ds}, {}, {}, {"a": {"c00": 100}})
        assert ra == [loi("wharton_nguyen_vong_chua_xep", student_id="a", tran=10, n=11,
                          n_trung=0, buoi=BM)]

    def test_v1_10_clb_la_du(self):
        ds = ["c%02d" % i for i in range(10)]
        assert kiem({"a": ds}, {}, {}, {"a": {"c00": 100}}) == []

    def test_v1_mot_clb_lap_lai(self):
        ra = kiem({"a": ["X", "Y", "X"]}, {}, {}, {"a": {"X": 50, "Y": 50}})
        assert ra == [loi("wharton_nguyen_vong_chua_xep", student_id="a", tran=10, n=3,
                          n_trung=1, buoi=BM)]

    def test_v1_tran_tuy_chinh(self):
        ra = kiem({"a": ["X", "Y", "Z"]}, {}, {}, {"a": {"X": 100}}, tran_nguyen_vong=2)
        assert ra == [loi("wharton_nguyen_vong_chua_xep", student_id="a", tran=2, n=3,
                          n_trung=0, buoi=BM)]

    # ---- V2 / V3
    def test_tong_90_bao_thieu_10(self):
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 50, "Y": 40}})
        assert ra == [loi("wharton_chua_dung_het", student_id="a", thieu=10, quy=2, buoi=BM)]
        ra = kiem({"a": ["X", "Y"]}, {"a": {"X", "Y"}}, {"a": {"X": 50, "Y": 40}}, {})
        assert ra == [loi("wharton_chua_dung_het", student_id="a", thieu=10, quy=1, buoi=BM)]

    def test_tong_110_bao_vuot_ngan_sach(self):
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 60, "Y": 50}})
        assert ra == [loi("wharton_vuot_ngan_sach", student_id="a", tong=110, quy=2,
                          ngan_sach=100, buoi=BM)]

    def test_bien_ngan_sach_99_100_101(self):
        """A13.12 (4.5): sát ngưỡng — 99 thiếu 1, 100 hợp lệ, 101 vượt 1 (ở cả hai quỹ)."""
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 50, "Y": 49}})
        assert ra == [loi("wharton_chua_dung_het", student_id="a", thieu=1, quy=2, buoi=BM)]
        assert kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 50, "Y": 50}}) == []
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 51, "Y": 50}})
        assert ra == [loi("wharton_vuot_ngan_sach", student_id="a", tong=101, quy=2,
                          ngan_sach=100, buoi=BM)]
        ra = kiem({"a": ["X", "Y"]}, {"a": {"X", "Y"}}, {"a": {"X": 51, "Y": 50}}, {})
        assert ra == [loi("wharton_vuot_ngan_sach", student_id="a", tong=101, quy=1,
                          ngan_sach=100, buoi=BM)]

    def test_ngan_sach_tuy_chinh(self):
        assert kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 30, "Y": 20}}, ngan_sach=50) == []

    @pytest.mark.parametrize("xau", [12.5, True, -5, "10", 100.0, None])
    def test_gia_tri_khong_hop_le(self, xau):
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": xau, "Y": 50}})
        assert ra == [
            loi("wharton_diem_khong_hop_le", student_id="a", club_id="X", gia_tri=repr(xau),
                buoi=BM),
            loi("wharton_chua_dung_het", student_id="a", thieu=50, quy=2, buoi=BM)]

    def test_so_nguyen_bang_0_la_hop_le(self):
        assert kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 100, "Y": 0}}) == []

    def test_khoa_ngoai_nguyen_vong_bao_ngoai_tap(self):
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 50, "Y": 50, "Q": 10}},
                  clubs=_clb("X", "Y", "Q"))
        assert ra == [loi("wharton_ngoai_tap", student_id="a", quy=2, club_id="Q", buoi=BM)]

    def test_clb_la_khong_co_trong_bang_clb_roi_vao_buoi_mac_dinh(self):
        ra = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 50, "Y": 50, "Ghost": 1}},
                  clubs=_clb("X", "Y"))
        assert ra == [loi("wharton_ngoai_tap", student_id="a", quy=2, club_id="Ghost",
                          buoi=BM)]

    def test_diem_quy_1_dat_cho_clb_khong_tick_thi_la_ngoai_tap(self):
        ra = kiem({"a": ["X", "Y"]}, {"a": {"X"}}, {"a": {"X": 50, "Y": 50}}, {})
        assert ra == [
            loi("wharton_ngoai_tap", student_id="a", quy=1, club_id="Y", buoi=BM),
            loi("wharton_chua_dung_het", student_id="a", thieu=50, quy=1, buoi=BM),
            loi("wharton_chua_dung_het", student_id="a", thieu=100, quy=2, buoi=BM)]

    def test_ma_tran_diem_o_o_moi_o_chi_mot_loi(self):
        # khoá ngoài tập mang giá trị xấu: chỉ báo ngoài tập, không báo thêm giá trị
        ra = kiem({"a": ["X"]}, {}, {}, {"a": {"X": 100, "Q": 12.5}}, clubs=_clb("X", "Q"))
        assert ra == [loi("wharton_ngoai_tap", student_id="a", quy=2, club_id="Q", buoi=BM)]

    # ---- V4
    def test_v4_t1_rong_thi_w1_phai_rong(self):
        ra = kiem({"a": ["X"]}, {}, {"a": {"X": 100}}, {"a": {"X": 100}})
        assert ra == [loi("wharton_ngoai_tap", student_id="a", quy=1, club_id="X", buoi=BM)]

    def test_v4_t2_rong_thi_w2_phai_rong(self):
        ra = kiem({"a": ["X"]}, {"a": {"X"}}, {"a": {"X": 100}}, {"a": {"X": 5}})
        assert ra == [loi("wharton_ngoai_tap", student_id="a", quy=2, club_id="X", buoi=BM)]

    def test_bo_clb_khoi_nguyen_vong_thi_diem_cu_thanh_ngoai_tap(self):
        truoc = kiem({"a": ["X", "Y", "Z"]}, {}, {}, {"a": {"X": 40, "Y": 30, "Z": 30}})
        assert truoc == []
        sau = kiem({"a": ["X", "Y"]}, {}, {}, {"a": {"X": 40, "Y": 30, "Z": 30}},
                   clubs=_clb("X", "Y", "Z"))
        assert sau == [
            loi("wharton_ngoai_tap", student_id="a", quy=2, club_id="Z", buoi=BM),
            loi("wharton_chua_dung_het", student_id="a", thieu=30, quy=2, buoi=BM)]

    # ---- nhiều lỗi, thứ tự cố định
    def test_nhieu_loi_day_du_theo_thu_tu_co_dinh(self):
        prefs = {"b": ["X", "Y"], "a": ["X", "Y"]}
        w2 = {"b": {"X": 10, "Y": 10}, "a": {"X": 70, "Y": 70}}
        ra = kiem(prefs, {}, {}, w2)
        assert ra == [
            loi("wharton_vuot_ngan_sach", student_id="a", tong=140, quy=2, ngan_sach=100,
                buoi=BM),
            loi("wharton_chua_dung_het", student_id="b", thieu=80, quy=2, buoi=BM)]
        assert kiem(prefs, {}, {}, w2) == ra                      # chạy lại: cùng danh sách
        # đảo thứ tự khoá trong dict đầu vào: kết quả không đổi
        dao = {"a": dict(reversed(list(w2["a"].items()))), "b": w2["b"]}
        assert kiem({"a": prefs["a"], "b": prefs["b"]}, {}, {}, dao) == ra

    # ---- nhiều buổi
    def _hai_buoi(self):
        buoi = {"X1": "thu_2", "Y1": "thu_2", "X2": "thu_3", "Y2": "thu_3"}
        return _clb("X1", "Y1", "X2", "Y2", buoi=buoi)

    def test_hai_buoi_moi_buoi_tong_100_moi_quy_la_hop_le(self):
        clubs = self._hai_buoi()
        prefs = {"a": ["X1", "Y1", "X2", "Y2"]}
        thi = {"a": {"X1", "X2"}}
        w1 = {"a": {"X1": 100, "X2": 100}}
        w2 = {"a": {"Y1": 100, "Y2": 100}}
        assert kiem(prefs, thi, w1, w2, clubs=clubs) == []

    def test_50_cong_50_chia_cho_hai_buoi_thi_moi_buoi_thieu_50(self):
        clubs = self._hai_buoi()
        prefs = {"a": ["X1", "Y1", "X2", "Y2"]}
        thi = {"a": {"X1", "X2"}}
        w1 = {"a": {"X1": 50, "X2": 50}}
        w2 = {"a": {"Y1": 100, "Y2": 100}}
        assert kiem(prefs, thi, w1, w2, clubs=clubs) == [
            loi("wharton_chua_dung_het", student_id="a", thieu=50, quy=1, buoi="thu_2"),
            loi("wharton_chua_dung_het", student_id="a", thieu=50, quy=1, buoi="thu_3")]

    def test_buoi_khong_co_clb_quy_2_thi_khong_doi_100_diem_quy_2(self):
        clubs = self._hai_buoi()
        prefs = {"a": ["X1", "X2"]}
        thi = {"a": {"X1", "X2"}}
        assert kiem(prefs, thi, {"a": {"X1": 100, "X2": 100}}, {}, clubs=clubs) == []

    def test_loi_o_mot_buoi_khong_lan_sang_buoi_kia(self):
        clubs = self._hai_buoi()
        prefs = {"a": ["X1", "Y1", "X2", "Y2"]}
        thi = {"a": {"X1", "X2"}}
        w1 = {"a": {"X1": 100, "X2": 100}}
        w2 = {"a": {"Y1": 100, "Y2": 90}}
        assert kiem(prefs, thi, w1, w2, clubs=clubs) == [
            loi("wharton_chua_dung_het", student_id="a", thieu=10, quy=2, buoi="thu_3")]

    def test_v1_dem_theo_tung_buoi_khong_dem_ca_tuan(self):
        # 6 buổi x 2 CLB = 12 nguyện vọng cả tuần nhưng mỗi buổi chỉ 2: hợp lệ
        buoi = {}
        prefs_a, w2_a = [], {}
        for i in range(2, 8):
            for k in range(2):
                c = "c%d_%d" % (i, k)
                buoi[c] = "thu_%d" % i
                prefs_a.append(c)
            w2_a["c%d_0" % i] = 100
        clubs = _clb(*buoi, buoi=buoi)
        assert kiem({"a": prefs_a}, {}, {}, {"a": w2_a}, clubs=clubs) == []

    def test_moi_loi_deu_co_buoi_va_truong_mot_buoi_la_buoi_mac_dinh(self):
        ra = kiem({"a": [], "b": ["X", "Y"], "c": ["X"]}, {"c": {"X"}},
                  {"c": {"X": 90}}, {"b": {"X": 1, "Y": 1, "Q": 5}}, clubs=_clb("X", "Y", "Q"))
        assert ra
        assert all(e["params"]["buoi"] == BM for e in ra)


# ------------------------------------------------------------------ tự điền một CLB (Bước 9)

def tu_dien(prefs, thi, w1, w2, clubs=None, **kw):
    if clubs is None:
        moi = {c for ds in prefs.values() for c in ds}
        clubs = _clb(*sorted(moi))
    return rp.tu_dien_wharton_mot_clb(prefs, thi, w1, w2, clubs, **kw)


class TestTuDien:
    def test_quy_chi_co_mot_clb_va_trong_thi_dien_100(self):
        w1, w2 = tu_dien({"a": ["X", "Y"]}, {"a": {"X"}}, {}, {})
        assert w1 == {"a": {"X": 100}}
        assert w2 == {"a": {"Y": 100}}

    def test_mot_quy_mot_clb_quy_kia_nhieu_clb_chi_dien_quy_mot_clb(self):
        w1, w2 = tu_dien({"a": ["X", "Y", "Z"]}, {"a": {"X"}}, {}, {})
        assert w1 == {"a": {"X": 100}}
        assert w2 == {}                      # T2 có hai CLB: em tự chia

    def test_tap_co_hai_clb_khong_dien(self):
        assert tu_dien({"a": ["X", "Y"]}, {"a": {"X", "Y"}}, {}, {}) == ({}, {})
        assert tu_dien({"a": ["X", "Y"]}, {}, {}, {}) == ({}, {})

    def test_quy_da_co_khoa_ke_ca_gia_tri_0_thi_khong_dien(self):
        w1, w2 = tu_dien({"a": ["X", "Y"]}, {"a": {"X"}}, {"a": {"X": 0}}, {"a": {"Y": 0}})
        assert w1 == {"a": {"X": 0}} and w2 == {"a": {"Y": 0}}

    def test_quy_da_co_khoa_ngoai_tap_cung_khong_dien(self):
        # có khoá (dù sai chỗ) nghĩa là em đã đụng tới quỹ này: để kiem_ho_so_wharton báo
        w1, _ = tu_dien({"a": ["X", "Y"]}, {"a": {"X"}}, {"a": {"Y": 100}}, {})
        assert w1 == {"a": {"Y": 100}}

    def test_nhieu_buoi_dien_rieng_tung_buoi(self):
        buoi = {"X1": "thu_2", "Y1": "thu_2", "X2": "thu_3", "Z2": "thu_3", "Y2": "thu_3"}
        clubs = _clb(*buoi, buoi=buoi)
        prefs = {"a": ["X1", "Y1", "X2", "Z2", "Y2"]}
        thi = {"a": {"X1", "X2", "Z2"}}
        w1, w2 = tu_dien(prefs, thi, {}, {}, clubs=clubs)
        # thứ 2: T1={X1}, T2={Y1} cùng một CLB -> điền cả hai; thứ 3: T1 hai CLB -> không,
        # T2={Y2} -> điền
        assert w1 == {"a": {"X1": 100}}
        assert w2 == {"a": {"Y1": 100, "Y2": 100}}

    def test_nhieu_buoi_buoi_nay_da_co_khoa_buoi_kia_van_dien(self):
        buoi = {"X1": "thu_2", "X2": "thu_3"}
        clubs = _clb(*buoi, buoi=buoi)
        prefs = {"a": ["X1", "X2"]}
        thi = {"a": {"X1", "X2"}}
        w1, w2 = tu_dien(prefs, thi, {"a": {"X1": 100}}, {}, clubs=clubs)
        assert w1 == {"a": {"X1": 100, "X2": 100}} and w2 == {}

    def test_khong_sua_dict_dau_vao(self):
        prefs = {"a": ["X", "Y"], "b": ["X", "Y"]}
        thi = {"a": {"X"}, "b": {"X"}}
        w1 = {"b": {"X": 100}}
        w2 = {"b": {"Y": 100}, "c": {"Q": 3}}
        truoc = copy.deepcopy((prefs, thi, w1, w2))
        ra1, ra2 = tu_dien(prefs, thi, w1, w2)
        assert (prefs, thi, w1, w2) == truoc
        assert ra1 is not w1 and ra2 is not w2
        assert ra1["b"] is not w1["b"]
        assert ra1 == {"a": {"X": 100}, "b": {"X": 100}}
        assert ra2 == {"a": {"Y": 100}, "b": {"Y": 100}, "c": {"Q": 3}}

    def test_tat_bang_bat_false_tra_ban_sao_y_het(self):
        w1, w2 = {"b": {"X": 5}}, {"c": {"Q": 3}}
        ra1, ra2 = tu_dien({"a": ["X", "Y"]}, {"a": {"X"}}, w1, w2, bat=False)
        assert (ra1, ra2) == (w1, w2)
        assert ra1 is not w1 and ra1["b"] is not w1["b"]

    def test_mac_dinh_la_bat(self):
        assert rp.WHARTON_TU_DIEN_MOT_CLB is True
        assert tu_dien({"a": ["X"]}, {}, {}, {}) == ({}, {"a": {"X": 100}})

    def test_ngan_sach_tuy_chinh(self):
        assert tu_dien({"a": ["X"]}, {}, {}, {}, ngan_sach=50) == ({}, {"a": {"X": 50}})

    def test_em_khong_co_nguyen_vong_giu_nguyen(self):
        w1, w2 = tu_dien({"a": []}, {}, {"z": {"X": 1}}, {})
        assert (w1, w2) == ({"z": {"X": 1}}, {})

    def test_ho_so_da_tu_dien_qua_kiem_khong_con_loi_ve_quy_do(self):
        prefs = {"a": ["X", "Y", "Z"]}
        thi = {"a": {"X"}}
        w1, w2 = tu_dien(prefs, thi, {}, {"a": {"Y": 70, "Z": 30}})
        assert kiem(prefs, thi, w1, w2) == []
        # chưa tự điền: quỹ 1 thiếu 100
        assert kiem(prefs, thi, {}, {"a": {"Y": 70, "Z": 30}}) == [
            loi("wharton_chua_dung_het", student_id="a", thieu=100, quy=1, buoi=BM)]

    def test_chay_lap_cho_cung_ket_qua(self):
        prefs = {"a": ["X", "Y"], "b": ["X"]}
        thi = {"a": {"X"}}
        mot = tu_dien(prefs, thi, {}, {})
        hai = tu_dien(prefs, thi, *mot)
        assert hai == mot


# ------------------------------------------------------------------ điểm hiệu lực (Bước 10)

def chia_diem(rng, ds, ngan_sach=100):
    """Chia ngẫu nhiên `ngan_sach` điểm nguyên không âm cho các CLB trong `ds`."""
    ds = list(ds)
    if not ds:
        return {}
    cat = sorted(rng.randint(0, ngan_sach) for _ in range(len(ds) - 1))
    bien = [0] + cat + [ngan_sach]
    return {c: bien[i + 1] - bien[i] for i, c in enumerate(ds)}


def sinh_bo(seed, n_hs=12, n_clb=5, co_du_tru=False, co_nhom=False, so_buoi=1):
    """Bộ dữ liệu mô phỏng CÓ hồ sơ Wharton hợp lệ.

    `w1` chia 100 điểm cho các CLB em có điểm thi, `w2` chia 100 điểm cho các CLB còn lại, mỗi
    buổi một lần; rồi đi qua `diem_wharton_hieu_luc` thành `bo.diem_hl`.
    """
    rng = random.Random(seed)
    bo = sinh_du_lieu(rng, n_hs, n_clb, co_du_tru, co_nhom, so_buoi)
    scores, clubs = bo.d[2], bo.d[1]
    w1, w2 = {}, {}
    for s in bo.sids:
        for ds in rp.gom_theo_buoi(bo.prefs[s], clubs).values():
            t1 = [c for c in ds if s in scores[c]]
            t2 = [c for c in ds if s not in scores[c]]
            if t1:
                w1.setdefault(s, {}).update(chia_diem(rng, t1))
            if t2:
                w2.setdefault(s, {}).update(chia_diem(rng, t2))
    bo.w1, bo.w2 = w1, w2
    bo.tick = {s: {c for c in bo.prefs[s] if s in scores[c]} for s in bo.sids}
    bo.diem_hl, bo.canh_bao = rp.diem_wharton_hieu_luc(bo.prefs, w1, w2, scores)
    return bo


class TestDiemHieuLuc:
    def test_bo_sinh_ra_la_ho_so_hop_le_va_khong_co_canh_bao(self):
        for seed in range(20):
            bo = sinh_bo(seed, so_buoi=1 + seed % 3, n_clb=6)
            assert rp.kiem_ho_so_wharton(bo.prefs, bo.tick, bo.w1, bo.w2, bo.d[1]) == []
            assert bo.canh_bao == []

    def test_vd6_vang_thi_roi_xuong_tang_2_voi_diem_quy_2(self):
        d = du_lieu(
            cap={"Ly": 1},
            prefs={"An": ["Ly"], "Binh": ["Ly"], "Quan": ["Ly"]},
            diem_thi={"Ly": {"An": 5.0, "Binh": 4.0}},          # Quân tick thi mà vắng
            stb={"Quan": 0, "An": 1, "Binh": 2},                # STB của Quân nhỏ nhất
            tick={"An": {"Ly"}, "Binh": {"Ly"}, "Quan": {"Ly"}},
        )
        prefs, scores = d[4], d[2]
        w1 = {"An": {"Ly": 100}, "Binh": {"Ly": 100}, "Quan": {"Ly": 100}}
        hl, thong_bao = rp.diem_wharton_hieu_luc(prefs, w1, {}, scores)
        assert hl["Ly"]["Quan"] == 0
        assert thong_bao == [loi("wharton_vang_thi", student_id="Quan", club_id="Ly",
                                 diem=0, diem_bo=100)]
        kq = chay(d, diem_wharton=hl)
        order = sorted(kq.base_rank["Ly"], key=kq.base_rank["Ly"].get)
        assert order == ["An", "Binh", "Quan"]
        assert kq.assignment == {"An": "Ly", "Binh": None, "Quan": None}

    def test_vang_thi_ma_w2_co_khoa_clb_do_thi_lay_diem_w2_van_canh_bao(self):
        hl, thong_bao = rp.diem_wharton_hieu_luc(
            {"Quan": ["Ly"]}, {"Quan": {"Ly": 100}}, {"Quan": {"Ly": 30}}, {"Ly": {}})
        assert hl == {"Ly": {"Quan": 30}}
        assert thong_bao == [loi("wharton_vang_thi", student_id="Quan", club_id="Ly",
                                 diem=30, diem_bo=100)]

    def test_t2_chuyen_len_t1_bao_tang_lech_va_diem_la_0(self):
        hl, thong_bao = rp.diem_wharton_hieu_luc(
            {"a": ["X", "Y"]}, {}, {"a": {"X": 60, "Y": 40}}, {"X": {"a": 7.0}})
        assert hl == {"X": {"a": 0}, "Y": {"a": 40}}
        assert thong_bao == [loi("wharton_tang_lech", student_id="a", club_id="X")]

    def test_co_diem_thi_ma_khong_co_trong_w1_lan_w2_thi_la_0_khong_bao_loi(self):
        hl, thong_bao = rp.diem_wharton_hieu_luc(
            {"a": ["X", "Y"]}, {}, {"a": {"Y": 100}}, {"X": {"a": 7.0}})
        assert hl["X"]["a"] == 0 and thong_bao == []

    def test_diem_thi_0_van_la_tang_1(self):
        hl, _ = rp.diem_wharton_hieu_luc(
            {"a": ["X"]}, {"a": {"X": 100}}, {"a": {"X": 9}}, {"X": {"a": 0.0}})
        assert hl == {"X": {"a": 100}}

    def test_moi_cap_clb_hoc_sinh_trong_nguyen_vong_deu_co_diem(self):
        bo = sinh_bo(3, n_hs=10, n_clb=4)
        for s, ds in bo.prefs.items():
            for c in ds:
                assert s in bo.diem_hl[c]

    def test_thong_bao_theo_thu_tu_co_dinh_khong_phu_thuoc_thu_tu_nhap(self):
        prefs = {"b": ["Y", "X"], "a": ["Y", "X"]}
        w1 = {"b": {"X": 100, "Y": 100}, "a": {"X": 100, "Y": 100}}
        thi = {"X": {}, "Y": {}}
        _, mot = rp.diem_wharton_hieu_luc(prefs, w1, {}, thi)
        _, hai = rp.diem_wharton_hieu_luc(
            {"a": ["X", "Y"], "b": ["X", "Y"]}, w1, {}, thi)
        assert [(e["params"]["student_id"], e["params"]["club_id"]) for e in mot] == [
            ("a", "X"), ("a", "Y"), ("b", "X"), ("b", "Y")]
        assert mot == hai

    def test_chinh_sach_la_thi_nem_value_error(self):
        with pytest.raises(ValueError):
            rp.diem_wharton_hieu_luc({"a": ["X"]}, {}, {}, {}, chinh_sach="khac")

    def test_mac_dinh_dung_hang_cau_hinh(self):
        assert inspect.signature(rp.diem_wharton_hieu_luc).parameters[
            "chinh_sach"].default == rp.WHARTON_VANG_THI

    def test_w4_hai_quy_khong_tron_lan(self):
        rng = random.Random(404)
        doi_w1 = doi_w2 = 0
        for _ in range(25):
            bo = sinh_bo(rng.randrange(10 ** 6), n_hs=10, n_clb=5)
            _, _, scores, applicants, prefs, stb = bo.d
            for s in bo.sids:
                t1 = [c for c in prefs[s] if s in scores[c]]
                t2 = [c for c in prefs[s] if s not in scores[c]]
                # đổi w1 của em s: điểm hiệu lực ở mọi CLB tầng 2 của s không đổi
                w1_doi = copy.deepcopy(bo.w1)
                if t1:
                    w1_doi[s] = chia_diem(rng, t1)
                    doi_w1 += (w1_doi[s] != bo.w1[s])
                moi, _ = rp.diem_wharton_hieu_luc(prefs, w1_doi, bo.w2, scores)
                for c in t2:
                    assert moi[c][s] == bo.diem_hl[c][s]
                    assert (rp.uu_tien_wharton(c, applicants[c], scores[c], stb, moi[c])
                            == rp.uu_tien_wharton(c, applicants[c], scores[c], stb,
                                                  bo.diem_hl[c]))
                # và ngược lại: đổi w2 thì các CLB tầng 1 không đổi
                w2_doi = copy.deepcopy(bo.w2)
                if t2:
                    w2_doi[s] = chia_diem(rng, t2)
                    doi_w2 += (w2_doi[s] != bo.w2[s])
                moi, _ = rp.diem_wharton_hieu_luc(prefs, bo.w1, w2_doi, scores)
                for c in t1:
                    assert moi[c][s] == bo.diem_hl[c][s]
                    assert (rp.uu_tien_wharton(c, applicants[c], scores[c], stb, moi[c])
                            == rp.uu_tien_wharton(c, applicants[c], scores[c], stb,
                                                  bo.diem_hl[c]))
        assert doi_w1 >= 20 and doi_w2 >= 20           # test thật sự có đổi điểm


class TestW9TuHoSoTho:
    """VD1–VD5 đi từ w1/w2 thô: kiểm hồ sơ -> điểm hiệu lực -> run_rbda; phải trùng Bước 6."""

    def _chay(self, d, tick, w1, w2, **kw):
        prefs, scores, clubs = d[4], d[2], d[1]
        assert rp.kiem_ho_so_wharton(prefs, tick, w1, w2, clubs) == []
        hl, thong_bao = rp.diem_wharton_hieu_luc(prefs, w1, w2, scores)
        assert thong_bao == []
        return chay(d, diem_wharton=hl, **kw), hl

    def test_vd1(self):
        d = du_lieu(cap={"Debate": 1, "NhiepAnh": 5, "Robotics": 5},
                    prefs={"An": ["Debate", "NhiepAnh"], "Binh": ["Debate", "Robotics"]},
                    diem_thi={}, stb={"An": 1, "Binh": 0})
        w2 = {"An": {"Debate": 70, "NhiepAnh": 30}, "Binh": {"Debate": 30, "Robotics": 70}}
        kq, hl = self._chay(d, {}, {}, w2)
        assert kq.assignment == {"An": "Debate", "Binh": "Robotics"}
        assert hl == {"Debate": {"An": 70, "Binh": 30}, "NhiepAnh": {"An": 30},
                      "Robotics": {"Binh": 70}}

    def test_vd2(self):
        d = du_lieu(cap={"Robotics": 1, "VanHoc": 5},
                    prefs={"Chi": ["Robotics"], "Dung": ["Robotics", "VanHoc"]},
                    diem_thi={"Robotics": {"Chi": 6.5}}, stb={"Dung": 0, "Chi": 1})
        tick = {"Chi": {"Robotics"}}
        kq, _ = self._chay(d, tick, {"Chi": {"Robotics": 100}},
                           {"Dung": {"Robotics": 100, "VanHoc": 0}})
        assert kq.assignment == {"Chi": "Robotics", "Dung": "VanHoc"}

    def test_vd3(self):
        d = du_lieu(cap={"Toan": 1, "Hoa": 1, "Ly": 1},
                    prefs={"Em": ["Toan", "Hoa"], "Giang": ["Toan", "Ly"]},
                    diem_thi={"Toan": {"Em": 8.25, "Giang": 8.25}, "Hoa": {"Em": 7.0},
                              "Ly": {"Giang": 9.0}},
                    stb={"Giang": 0, "Em": 1})
        tick = {"Em": {"Toan", "Hoa"}, "Giang": {"Toan", "Ly"}}
        kq, hl = self._chay(d, tick, {"Em": {"Toan": 60, "Hoa": 40},
                                      "Giang": {"Toan": 40, "Ly": 60}}, {})
        assert kq.assignment == {"Em": "Toan", "Giang": "Ly"}
        assert hl == {"Toan": {"Em": 60, "Giang": 40}, "Hoa": {"Em": 40}, "Ly": {"Giang": 60}}

    @pytest.mark.parametrize("stb,nguoi_duoc", [({"Ha": 0, "Khoa": 1}, "Ha"),
                                                ({"Ha": 1, "Khoa": 0}, "Khoa")])
    def test_vd4(self, stb, nguoi_duoc):
        d = du_lieu(cap={"Debate": 1, "CoVua": 5},
                    prefs={"Ha": ["Debate", "CoVua"], "Khoa": ["Debate", "CoVua"]},
                    diem_thi={}, stb=stb)
        w2 = {"Ha": {"Debate": 50, "CoVua": 50}, "Khoa": {"Debate": 50, "CoVua": 50}}
        kq, _ = self._chay(d, {}, {}, w2)
        assert kq.assignment[nguoi_duoc] == "Debate"

    def test_vd5_hai_thu_tu_nguyen_vong_cung_diem(self):
        def lam(prefs_lan):
            d = du_lieu(cap={"Toan": 5, "Debate": 1, "CoVua": 5},
                        prefs={"Lan": prefs_lan, "Minh": ["Debate", "CoVua"]},
                        diem_thi={"Toan": {"Lan": 9.0}}, stb={"Minh": 0, "Lan": 1})
            return self._chay(
                d, {"Lan": {"Toan"}}, {"Lan": {"Toan": 100}},
                {"Lan": {"Debate": 100}, "Minh": {"Debate": 80, "CoVua": 20}})[0]
        a, b = lam(["Debate", "Toan"]), lam(["Toan", "Debate"])
        assert a.assignment == {"Lan": "Debate", "Minh": "CoVua"}
        assert b.assignment == {"Lan": "Toan", "Minh": "Debate"}
        assert a.base_rank == b.base_rank


# ------------------------------------------------------------------ test tính chất (Bước 11)
#
# Các test dưới đây chạy trên mã đã viết xong. Đỏ mà test đúng thì đó là LỖI THẬT của cơ chế:
# báo cáo bộ dữ liệu nhỏ nhất tái hiện được, không nới test.

def _chay_bo(bo, bo_qua_du_tru=False, dung_tier_rank=True):
    tr = bo.tier_rank if dung_tier_rank else None
    return chay(bo.d, diem_wharton=bo.diem_hl, tier_rank=tr, eligible=bo.eligible,
                bo_qua_du_tru=bo_qua_du_tru)


class TestTinhChat:
    def test_w2_tang_2_giu_cho_thi_khong_co_nguoi_tang_1_bi_tu_choi_va_thich_hon(self):
        """W2: chạy KHÔNG dự trữ và KHÔNG nhóm xếp cứng. Với dự trữ, một em tầng 2 đủ diện dự
        trữ được giữ suất trước em tầng 1 là ĐÚNG thiết kế; với `tier_rank`, nhóm đứng trước
        cả tầng. Hai chế độ đó thuộc W6 (ổn định), không thuộc W2."""
        kiem_tra = 0
        for seed in range(60):
            bo = sinh_bo(1000 + seed, n_hs=14, n_clb=4)
            kq = _chay_bo(bo)
            scores, prefs = bo.d[2], bo.d[4]
            bi_tu_choi_tang_1 = {}
            for _vong, sid, cid in kq.rejection_log:
                if sid in scores[cid]:
                    bi_tu_choi_tang_1.setdefault(cid, []).append(sid)
            for sid, cid in kq.assignment.items():
                if cid is None or sid in scores[cid]:
                    continue                                    # chỉ xét em tầng 2 đang giữ chỗ
                kiem_tra += 1
                for t in bi_tu_choi_tang_1.get(cid, []):
                    hien_tai = kq.assignment[t]
                    vi_tri_hien_tai = (prefs[t].index(hien_tai) if hien_tai in prefs[t]
                                       else len(prefs[t]))
                    thich_hon = prefs[t].index(cid) < vi_tri_hien_tai
                    assert not thich_hon, (seed, cid, sid, t)
        assert kiem_tra >= 50                                   # test không rỗng

    def test_w1_hoan_vi_nguyen_vong_khong_doi_base_rank(self):
        rng = random.Random(101)
        for i in range(40):
            bo = sinh_bo(2000 + i, n_hs=12, n_clb=5, co_du_tru=(i % 2 == 0),
                         co_nhom=(i % 3 == 0))
            truoc = _chay_bo(bo).base_rank
            hoan = {s: rng.sample(ds, len(ds)) for s, ds in bo.prefs.items()}
            students, clubs, scores, _app, _prefs, stb = bo.d
            d2 = du_lieu(bo.cap, hoan, bo.diem_thi, stb, tick=bo.tick, reserve=bo.reserve,
                         nhom_du_tru=bo.nhom)
            sau = chay(d2, diem_wharton=bo.diem_hl, tier_rank=bo.tier_rank,
                       eligible=rp.default_reserve_eligible_fn(d2[0], d2[1])).base_rank
            assert sau == truoc, i

    def test_w6_on_dinh_mot_buoi_co_du_tru_nhom_xep_cung(self):
        so_bo = 0
        # (a) có dự trữ thật, nhóm dự trữ thật qua default_reserve_eligible_fn
        for seed in range(20):
            bo = sinh_bo(3000 + seed, n_hs=14, n_clb=5, co_du_tru=True)
            kq = _chay_bo(bo)
            students, clubs, _s, _a, prefs, _stb = bo.d
            assert rp.verify_stability(kq, clubs, prefs, bo.eligible) == [], seed
            so_bo += 1
        # (b) nhóm xếp cứng + bỏ qua dự trữ, đúng cách api dùng (có cả CLB có suất dự trữ)
        for seed in range(20):
            bo = sinh_bo(4000 + seed, n_hs=14, n_clb=5, co_du_tru=True, co_nhom=True)
            kq = _chay_bo(bo, bo_qua_du_tru=True)
            assert rp.verify_stability(kq, bo.d[1], bo.d[4], bo.eligible,
                                       bo_qua_du_tru=True) == [], seed
            so_bo += 1
        # (c) nhóm xếp cứng VÀ dự trữ cùng bật
        for seed in range(10):
            bo = sinh_bo(5000 + seed, n_hs=14, n_clb=5, co_du_tru=True, co_nhom=True)
            kq = _chay_bo(bo)
            assert rp.verify_stability(kq, bo.d[1], bo.d[4], bo.eligible) == [], seed
            so_bo += 1
        assert so_bo == 50

    @pytest.mark.parametrize("co_du_tru,co_nhom,bo_qua", [
        (False, False, False), (True, False, False), (True, True, True), (True, True, False)])
    def test_w6_on_dinh_nhieu_buoi(self, co_du_tru, co_nhom, bo_qua):
        for seed in range(8):
            bo = sinh_bo(6000 + seed, n_hs=14, n_clb=6, co_du_tru=co_du_tru,
                         co_nhom=co_nhom, so_buoi=2 + seed % 2)
            students, clubs, scores, app, prefs, stb = bo.d
            ket = rp.run_rbda_nhieu_buoi(
                students, clubs, scores, app, prefs, stb, bo.eligible, seed=seed,
                tier_rank=bo.tier_rank, bo_qua_du_tru=bo_qua, diem_wharton=bo.diem_hl)
            assert len(ket.ds_buoi) >= 2
            van_de = rp.verify_stability_tuan(ket, clubs, prefs, bo.eligible,
                                              bo_qua_du_tru=bo_qua)
            assert all(not v for v in van_de.values()), (seed, van_de)

    def test_w8_khai_that_thu_tu_la_tot_nhat_moi_hoan_vi_deu_khong_hon(self):
        rng = random.Random(808)
        thu = doi_ket_qua = 0
        for i in range(15):
            bo = sinh_bo(7000 + i, n_hs=rng.randint(4, 8), n_clb=rng.randint(2, 4),
                         co_du_tru=(i % 3 == 0))
            students, clubs, scores, _app, prefs, stb = bo.d
            that = _chay_bo(bo).assignment
            for sid in bo.sids:
                gia = prefs[sid]
                vi_tri = lambda c, gia=gia: gia.index(c) if c in gia else len(gia)
                for hv in itertools.permutations(gia):
                    khai = dict(prefs)
                    khai[sid] = list(hv)
                    d2 = du_lieu(bo.cap, khai, bo.diem_thi, stb, tick=bo.tick,
                                 reserve=bo.reserve, nhom_du_tru=bo.nhom)
                    kq = chay(d2, diem_wharton=bo.diem_hl,
                              eligible=rp.default_reserve_eligible_fn(d2[0], d2[1]))
                    thu += 1
                    doi_ket_qua += (kq.assignment[sid] != that[sid])
                    assert vi_tri(kq.assignment[sid]) >= vi_tri(that[sid]), (
                        i, sid, hv, kq.assignment[sid], that[sid])
        assert thu >= 200 and doi_ket_qua >= 10          # đã thử đủ và có lúc khai sai là thiệt

    def test_bat_bien_8_thay_the_duoc_va_luat_tong_cau(self):
        """Hàm lựa chọn của CLB (thứ tự nền `uu_tien_wharton` + dự trữ mềm) phải thoả hai điều
        kiện trước khi dùng (bất biến 8): với P ⊆ P', em bị loại ở P thì vẫn bị loại ở P'
        (thay thế được), và |C(P)| ≤ |C(P')| (luật tổng cầu)."""
        rng = random.Random(8888)
        so_lan_loai = 0
        for _ in range(400):
            n = rng.randint(3, 12)
            applicants, tested, stb = _bo_cho_mot_clb(rng, n=n)
            wh = {s: rng.randint(0, 100) for s in applicants if rng.random() < 0.8}
            tier_rank = ({s: rng.randint(0, 2) for s in applicants if rng.random() < 0.7}
                         if rng.random() < 0.5 else None)
            thu_tu = rp.uu_tien_wharton("X", applicants, tested, stb, wh, tier_rank=tier_rank)
            rank = {s: i for i, s in enumerate(thu_tu)}
            dien_du_tru = {s for s in applicants if rng.random() < 0.4}
            suc_chua = rng.randint(1, 4)
            du_tru = rng.randint(0, suc_chua)

            def chon(pool):
                return set(rp.club_choice_function(
                    pool, suc_chua, du_tru, lambda s: s in dien_du_tru, rank)[0])

            lon = [s for s in applicants if rng.random() < 0.8]
            nho = [s for s in lon if rng.random() < 0.6]
            c_nho, c_lon = chon(nho), chon(lon)
            bi_loai = set(nho) - c_nho
            so_lan_loai += len(bi_loai)
            assert bi_loai.isdisjoint(c_lon), (nho, lon)        # thay thế được
            assert len(c_nho) <= len(c_lon), (nho, lon)         # luật tổng cầu
        assert so_lan_loai >= 100                               # có người bị loại để kiểm
