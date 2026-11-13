"""FA-D7L: điểm thi lẻ đến 0,1 (tuỳ chọn, mặc định TẮT), tập đạt / không đạt điểm sàn giữ nguyên.

Chứng minh (cũng ở docstring `quy_diem_10_le`): với x >= 0 và t = floor(10x)/10 thì floor(t + 1/2) == floor(x + 1/2),
vì mọi nửa-nguyên n − 1/2 là bội của 1/10, nên x >= n − 1/2 <=> t >= n − 1/2. Lưu t (cắt bớt), so với điểm sàn sau khi
làm tròn nửa lên (`fa_daa.dat_diem_san`) -> đúng tập em đạt như điểm nguyên hôm nay. Dữ liệu MÔ PHỎNG.
"""
import copy
import os
import random
import sys
from fractions import Fraction

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import fa_daa  # noqa: E402
import fa_ly_do  # noqa: E402
import mo_phong_fa_daa as mp  # noqa: E402
import phan_tich_cau_hoi as pt  # noqa: E402
import so_nhap  # noqa: E402
from test_fa_m3_chuyen import _lc, _so_nhap_clb, _tep_dang_ky, _tep_thi  # noqa: E402


# ---------------------------------------------------------------- 1. tính chất làm tròn
def _ngau_nhien(rng):
    toi_da = rng.choice([1, 3, 4, 7, 10, 12, 15, 20, 30, 37, 100])
    k = rng.random()
    if k < 0.2:
        diem = rng.randint(0, toi_da)
    elif k < 0.6:                                    # bội 0,05 (x.x5, x.45 ...)
        diem = Fraction(rng.randint(0, 20 * toi_da), 20)
    else:
        diem = Fraction(rng.randint(0, 1000 * toi_da), 1000)
    return float(diem) if rng.random() < 0.5 else str(float(diem)), toi_da


def test_quy_diem_10_le_giu_tap_dat():
    rng = random.Random(2026)
    ca = [(rng, None) for _ in range(10000)]
    bien = [(0, 10), (10, 10), (4.45, 10), (4.5, 10), (4.55, 10), (0.445, 1), (8.95, 10), (2.25, 5), (9.99, 10)]
    for diem, toi_da in bien + [_ngau_nhien(r) for r, _ in ca]:
        le = cv.quy_diem_10_le(diem, toi_da)
        t = Fraction(str(le))
        assert t * 10 == int(t * 10) and 0 <= t <= 10                # đúng một chữ số lẻ
        assert (t + Fraction(1, 2)) // 1 == cv.quy_diem_10(diem, toi_da), (diem, toi_da, le)
        assert t <= Fraction(str(diem)) / Fraction(str(toi_da)) * 10   # cắt bớt, không làm tròn lên
    assert cv.quy_diem_10_le(4.45, 10) == 4.4 and cv.quy_diem_10(4.45, 10) == 4
    assert cv.quy_diem_10_le(7, 10) == 7 and type(cv.quy_diem_10_le(7, 10)) is int
    assert cv.quy_diem_10_le(3, 4) == 7.5


def test_diem_dieu_chinh_le_giu_tap_dat():
    rng = random.Random(11)
    for _ in range(10000):
        tho = Fraction(rng.randint(0, 1000), 100)
        dich = rng.choice([0, 0.0, rng.uniform(-3, 3), round(rng.uniform(-2, 2), 2), -0.05, 0.05, 0.45])
        le = pt.diem_dieu_chinh_le(tho, dich)
        t = Fraction(str(le))
        assert t * 10 == int(t * 10) and 0 <= t <= 10
        assert (t + Fraction(1, 2)) // 1 == pt.diem_dieu_chinh(tho, dich), (tho, dich, le)
    assert pt.diem_dieu_chinh_le(Fraction(445, 100), 0) == 4.4 and pt.diem_dieu_chinh(Fraction(445, 100), 0) == 4
    assert pt.diem_dieu_chinh_le(Fraction(98, 10), 1) == 10 and pt.diem_dieu_chinh_le(Fraction(1, 10), -1) == 0


# ---------------------------------------------------------------- 2. bộ chuyển đổi: tắt = như cũ
@pytest.fixture
def de():
    return bm.doc_de_thi()


def _o(p):
    wb = openpyxl.load_workbook(p)
    return {ws.title: [list(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}


def _chuyen(de, tmp_path, ten, **kw):
    de2 = copy.deepcopy(de)
    de2["diem_moi_cau"] = 3
    dk = _tep_dang_ky(tmp_path, de2, [
        dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"), nv2=_lc(de, "clb_vanhoc")),
        dict(sid="HS2", email="b@x.vn", nv1=_lc(de, "clb_covua")),
        dict(sid="HS3", email="c@x.vn", nv1=_lc(de, "clb_covua"))], ten="dk_%s.xlsx" % ten)
    thi = _tep_thi(tmp_path, de2, [("a@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:10:00", {"clb_covua": 3}),
                                   ("b@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:09:00", {"clb_covua": 5}),
                                   ("c@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:08:00", {"clb_covua": 1})],
                   ten="thi_%s.xlsx" % ten)
    ra = tmp_path / ten
    cv.chuyen_fa_daa(str(ra), de2, _so_nhap_clb(tmp_path, de2), dang_ky_xlsx=[dk], quiz_xlsx=[thi],
                     bo_cau={("clb_covua", "A", 5)}, **kw)
    return str(ra / cv.TEN_SO)


def _diem(p):
    du = so_nhap.doc_so_nhap(openpyxl.load_workbook(p))
    assert not du["loi"], du["loi"]
    return {s["student_id"]: float({n["club_id"]: n.get("diem") for n in s["nv"]}["clb_covua"])
            for s in du["students"]}


def test_co_tat_so_nhap_nhu_cu_co_bat_diem_le(de, tmp_path):
    goc = _chuyen(de, tmp_path, "goc")
    tat = _chuyen(de, tmp_path, "tat", diem_le=False)
    bat = _chuyen(de, tmp_path, "bat", diem_le=True)
    assert _o(goc) == _o(tat)                                        # tắt: từng ô y hệt
    # bỏ câu 5 -> 4 câu: 3/4 = 7,5 ; 4/4 = 10 ; 1/4 = 2,5
    assert _diem(goc) == {"HS1": 8, "HS2": 10, "HS3": 3}
    assert _diem(bat) == {"HS1": 7.5, "HS2": 10, "HS3": 2.5}
    assert {s: fa_daa.dat_diem_san(d, 5) for s, d in _diem(bat).items()} == \
        {s: d >= 5 for s, d in _diem(goc).items()}


def test_cli_diem_le_chi_voi_fa_daa(tmp_path):
    with pytest.raises(SystemExit):
        cv.main(["x.xlsx", "--diem-le", "--ra", str(tmp_path)])


# ---------------------------------------------------------------- 4. dat_diem_san
def test_dat_diem_san():
    assert fa_daa.dat_diem_san(4.4, 5) is False
    assert fa_daa.dat_diem_san(4.5, 5) is True
    assert fa_daa.dat_diem_san(5, 5) is True
    assert fa_daa.dat_diem_san(4.4999999999, 5) is False            # REAL lưu trong SQLite, đọc qua str
    assert fa_daa.dat_diem_san(4.45, 5) is False and fa_daa.dat_diem_san(4.45, 4) is True
    assert fa_daa.dat_diem_san(0.1 + 0.2 + 4.2, 5) is True           # 4.5 có nhiễu số thực
    for d in range(11):
        for s in range(11):
            assert fa_daa.dat_diem_san(d, s) is (d >= s) and fa_daa.dat_diem_san(float(d), s) is (d >= s)


def test_ly_do_hien_mot_chu_so_le():
    dong = {"outcome": "REJECTED", "reason": "SCORE", "cut_score": 7.3, "diem_em": 7.1}
    assert "điểm chuẩn 7,3, em 7,1" in fa_ly_do.cau_ly_do(dong, "CLB X")
    dong = {"outcome": "REJECTED", "reason": "SCORE", "cut_score": 8.0, "diem_em": 6}
    assert "điểm chuẩn 8, em 6" in fa_ly_do.cau_ly_do(dong, "CLB X")
    assert "mốc 5 điểm" in fa_ly_do.cau_ly_do({"outcome": "REMOVED", "reason": "BELOW_PASS", "cut_score": 5}, "X")


# ---------------------------------------------------------------- 3. kiosk: mô phỏng
def _x(dl, s, c):
    h = dl["hs"][s]
    return Fraction(str(round(5 + 2.5 * h["nang_luc"] + h["nhieu"][c], 6)))


def _chay(dl, diem_ham, seed):
    prefs, huy, ticks, diem = mp.dang_ky(dl)
    diem = {c: {s: diem_ham(_x(dl, s, c)) for s in d} for c, d in diem.items()}
    stb = mp._stb(dl, seed)
    bo = mp._bo(dl, prefs, ticks, diem, stb)
    kq = fa_daa.chay_fa_daa(fa_clb=dl["fa_clb"], giu_cho=[], huy_chuong=huy, seed=seed, **bo)
    return kq, fa_daa.ly_do_ket_qua(kq, prefs, huy, dl["fa_clb"])


def _nguyen(x):
    return pt.diem_dieu_chinh(x, 0)


def _le(x):
    return pt.diem_dieu_chinh_le(x, 0)


def test_kiosk_diem_nguyen_khong_doi_diem_le_cung_tap_duoi_san_it_boc_tham_hon():
    tc = {"nguyen": [0, 0], "le": [0, 0]}                         # [LOTTERY, mọi REJECTED] ở CLB Tuyển chọn
    for seed in range(20):
        dl = mp.sinh_du_lieu(n=200, seed=seed, k=6)
        kq_n, ly_n = _chay(dl, _nguyen, seed)
        kq_l, ly_l = _chay(dl, _le, seed)
        duoi = lambda kq: {(r["student_id"], r["club_id"]) for r in kq.loai_bo if r["ly_do"] == "BELOW_PASS"}  # noqa
        assert duoi(kq_n) == duoi(kq_l)
        for ten, ly in (("nguyen", ly_n), ("le", ly_l)):
            for r in ly:
                if r["outcome"] == "REJECTED" and dl["fa_clb"][r["club_id"]]["loai"] == fa_daa.TUYEN_CHON:
                    tc[ten][1] += 1
                    tc[ten][0] += r["reason"] == "LOTTERY"
    ti_le = {k: v[0] / v[1] for k, v in tc.items()}
    print("MÔ PHỎNG FA-D7L (20 seed, 200 HS, 6 CLB/buổi): LOTTERY / REJECTED ở CLB Tuyển chọn — "
          "điểm nguyên %d/%d = %.1f%%, điểm lẻ %d/%d = %.1f%%"
          % (tc["nguyen"][0], tc["nguyen"][1], 100 * ti_le["nguyen"], tc["le"][0], tc["le"][1], 100 * ti_le["le"]))
    assert tc["nguyen"][1] > 0 and ti_le["le"] <= ti_le["nguyen"]


def test_kiosk_diem_nguyen_giong_het_truoc(monkeypatch):
    """Điểm nguyên: `dat_diem_san` == `diem >= san`, nên chay_fa_daa ra đúng từng dòng như phép so cũ."""
    for seed in range(5):
        dl = mp.sinh_du_lieu(n=120, seed=seed)
        moi = _chay(dl, _nguyen, seed)[1]
        monkeypatch.setattr(fa_daa, "dat_diem_san", lambda d, s: d >= s)
        cu = _chay(dl, _nguyen, seed)[1]
        monkeypatch.undo()
        assert moi == cu


def test_nhap_so_nhap_giu_diem_le_va_xet_san_lam_tron(de, tmp_path, api):
    """Sổ nhập có điểm lẻ cho CLB Tuyển chọn: kiosk lưu nguyên 7,5 / 2,5 (không làm tròn, không từ chối); xét điểm sàn
    theo điểm làm tròn: 4,5 đạt sàn 5, 4,4 không."""
    import base64

    import cau_hinh_ws as ch
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
    p = _chuyen(de, tmp_path, "bat", diem_le=True)
    kq = api.import_so_nhap(base64.b64encode(open(p, "rb").read()).decode())
    assert kq["ok"], kq
    with api._ket_noi_doc() as cur:
        d = dict(cur.execute("SELECT student_id, score FROM club_scores WHERE club_id = 'clb_covua'").fetchall())
    assert d == {"HS1": 7.5, "HS2": 10, "HS3": 2.5}
    assert api.submit_club_scores("clb_covua", [{"student_id": "HS1", "score": 4.5},
                                                {"student_id": "HS3", "score": 4.4}])["ok"]
    with api._ket_noi_doc() as cur:
        clubs, _hs, prefs = fa_daa.doc_clubs_va_nguyen_vong(cur)
        _, cap, _ = fa_daa.doc_du_lieu_fa(cur)
        diem = {}
        for cid, sid, x in cur.execute("SELECT club_id, student_id, score FROM club_scores"):
            diem.setdefault(cid, {})[sid] = x
    rows = {r["club_id"]: r for r in fa_daa.bang_nhu_cau(clubs, prefs, diem, clubs, cap)}
    assert rows["clb_covua"]["so_dat_san"] == 2                      # HS1 4,5 và HS2 10; HS3 4,4 không đạt


def test_api_nap_forms_doc_co_diem_le_giong_cli(api, tmp_path):
    """Bước 4 "Nạp kết quả từ biểu mẫu": `rules.fa_diem_le` (mặc định tắt) -> cùng Sổ nhập như CLI `--diem-le`."""
    import forms_dot
    forms_dot.nap_mau_forms()
    from test_fa_m9_nap_tep_forms import b64, dat_dot, nap_dir
    from test_fa_m9_thuan import _bo, _de_3_de, _de_ra_tep, _diem_covua, _gia_tri_so_nhap

    de3 = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de3, "A", dung=3)
    dat_dot(api, de3, sn)
    assert api.get_fa_diem_le()["data"]["diem_le"] is False
    lc = {"bo_cau": [["clb_covua", "A", 5]]}                          # 4 câu: 3/4 -> 7,5
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {"thi.xlsx": "A"}, lc)
    assert res["ok"] and res["data"]["trang_thai"] == "xong", res
    assert set(_diem_covua(nap_dir(api)).values()) == {8.0}
    assert ma_loi(api.dat_fa_diem_le("co")) == ["ws_cau_hinh_hong"]
    assert api.dat_fa_diem_le(True)["ok"] and api.get_fa_diem_le()["data"]["diem_le"] is True
    res = api.chuyen_tep_forms(None, {"thi.xlsx": "A"}, lc)
    assert res["ok"] and res["data"]["trang_thai"] == "xong", res
    assert set(_diem_covua(nap_dir(api)).values()) == {7.5}
    for co, ten in ((["--diem-le"], "cli_le"), ([], "cli")):
        assert cv.main(["--fa-daa", "--so-nhap-clb", sn, "--lists", lst, "--de", _de_ra_tep(tmp_path, de3),
                        "--bien-the-tep", "thi.xlsx=A", "--bo-cau", "clb_covua-A-5", "--ra", str(tmp_path / ten),
                        thi] + co) == 0
    assert _gia_tri_so_nhap(nap_dir(api)) == _gia_tri_so_nhap(str(tmp_path / "cli_le"))
    assert _gia_tri_so_nhap(str(tmp_path / "cli")) != _gia_tri_so_nhap(str(tmp_path / "cli_le"))


def ma_loi(kq):
    return [e["code"] for e in kq["errors"]]
