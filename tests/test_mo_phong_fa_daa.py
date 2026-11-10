"""FA-10: bộ mô phỏng so sánh chế độ cũ với FA-DAA và hành vi hai kỳ của D1. Chỉ bảng số, không nhận định.
Dữ liệu là dữ liệu MÔ PHỎNG."""
import os
import subprocess
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import mo_phong_fa_daa as mp  # noqa: E402

COT = {
    "so_sanh": {"che_do", "pt_nv1", "pt_top2", "pt_khong_clb", "nhan"},
    "ly_do": {"ket_qua", "ly_do", "pt_dong", "nhan"},
    "boc_tham_theo_hanh_vi": {"hanh_vi", "pt_thua_boc_tham_fa", "nhan"},
    "hai_ky": {"dieu_kien", "so_em_mau", "so_em_co_lech", "so_thua_ky_1", "so_em_co_loi",
               "pt_co_loi_tren_mau", "nhan"},
}


@pytest.fixture(scope="module")
def kq():
    return mp.chay_mo_phong(n=50, so_seed=2, so_mau=4, n_hai_ky=30)


def test_du_bang_va_du_cot(kq):
    assert set(kq) == set(COT)
    for ten, cot in COT.items():
        assert kq[ten], ten
        assert all(set(d) == cot for d in kq[ten]), ten


def test_moi_bang_ghi_nhan_so_lieu_mo_phong(kq):
    for dong in kq.values():
        assert all(d["nhan"] == "SỐ LIỆU MÔ PHỎNG" for d in dong)
    assert "SỐ LIỆU MÔ PHỎNG" in mp.in_bang("x", kq["so_sanh"])


def test_xac_dinh_theo_hat_giong_va_doi_khi_doi_hat_giong(kq):
    assert mp.chay_mo_phong(n=50, so_seed=2, so_mau=4, n_hai_ky=30) == kq
    assert mp.chay_mo_phong(n=50, so_seed=2, so_mau=4, n_hai_ky=30, seed0=7) != kq


def test_so_hop_ly(kq):
    cu, fa = kq["so_sanh"]
    assert (cu["che_do"], fa["che_do"]) == ("cu_diem_hai_quy", "fa_daa")
    assert fa["pt_khong_clb"] == 0.0                 # V§13.3: Tự do không từ chối -> mọi em có CLB
    for d in kq["so_sanh"]:
        assert 0 <= d["pt_nv1"] <= d["pt_top2"] <= 100
    assert abs(sum(d["pt_dong"] for d in kq["ly_do"]) - 100) < 1
    k, c = kq["hai_ky"]
    assert (k["dieu_kien"], c["dieu_kien"]) == ("khong_bu", "co_bu")
    assert c["so_em_co_loi"] >= k["so_em_co_loi"]    # bù chỉ có thể thêm lợi cho em thua kỳ 1


def test_khong_co_cau_nhan_dinh_va_khong_ma_hoc_sinh(kq):
    van_ban = " ".join(mp.in_bang(t, d) for t, d in kq.items())
    for tu in ("kết luận", "cho thấy", "chứng tỏ", "nên "):
        assert tu not in van_ban.lower()
    assert "s0" not in van_ban                       # mã học sinh mô phỏng dạng s000


def test_chay_dong_lenh(tmp_path):
    ra = subprocess.run([sys.executable, os.path.join(GOC, "du_lieu_test", "mo_phong_fa_daa.py"),
                         "--n", "40", "--so-seed", "1", "--hai-ky", "3"], capture_output=True, text=True,
                        encoding="utf-8", timeout=120, cwd=str(tmp_path))
    assert ra.returncode == 0, ra.stderr
    assert ra.stdout.count("SỐ LIỆU MÔ PHỎNG") >= 4


def test_khong_sua_dau_vao_chay_fa():
    dl = mp.sinh_du_lieu(n=30, seed=3)
    pr, hu, tk, di = mp.dang_ky(dl)
    import copy
    sao = copy.deepcopy((pr, hu, tk, di))
    mp.chay_fa(dl, pr, hu, tk, di, 3)
    assert sao == (pr, hu, tk, di)


def test_khoan_bu_dua_em_len_dau_bang_boc_tham_va_giu_thu_tu_nguoi_khac():
    dl = mp.sinh_du_lieu(n=30, seed=3)
    goc = mp._stb(dl, 5)
    bu = mp._stb(dl, 5, truoc={"s017"})
    assert bu["s017"] == 1 and sorted(bu.values()) == list(range(1, 31))
    nguoi_khac = [s for s in sorted(goc, key=goc.get) if s != "s017"]
    assert nguoi_khac == [s for s in sorted(bu, key=bu.get) if s != "s017"]


def test_dem_nv1_top2_khong_clb_tren_ban_tay():
    dl = mp.sinh_du_lieu(n=3, seed=1, so_buoi=1)
    s = dl["sids"][0]
    that = mp._vi_tri(dl, s, "thu_2")
    for ket, mong in ((that[0], (1, 1, 0)), (that[1], (0, 1, 0)), (that[-1], (0, 0, 0)), (None, (0, 0, 1))):
        cong = dict(tong=0, nv1=0, top2=0, khong=0)
        mp._dem_tc(dl, {s: {"thu_2": ket}}, cong)
        assert (cong["nv1"], cong["top2"], cong["khong"]) == mong and cong["tong"] == 1
