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

import inspect
import random
from types import SimpleNamespace

import pytest

import rbda_priority_pipeline as rp


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
