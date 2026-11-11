"""GAP-12 (V§12): mô phỏng đầy đủ — kiểu học sinh "tính toán" (học mốc kỳ trước, dời vàng khỏi CLB quá tải), bảng cũ /
mới theo từng kiểu và % thua bốc thăm theo kiểu. Chỉ bảng số. Dữ liệu là dữ liệu MÔ PHỎNG."""
import os
import subprocess
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import fa_daa  # noqa: E402
import mo_phong_fa_daa as mp  # noqa: E402

COT_MOI = {"che_do", "hanh_vi", "pt_nv1", "pt_top2", "pt_khong_clb", "pt_thua_boc_tham", "nhan"}


@pytest.fixture(scope="module")
def kq():
    return mp.chay_mo_phong_day_du(n=40, so_seed=2, so_mau=3, n_hai_ky=20)


def test_bang_cu_khong_doi_bang_moi_du_cot(kq):
    cu = mp.chay_mo_phong(n=40, so_seed=2, so_mau=3, n_hai_ky=20)
    assert set(cu) == {"so_sanh", "ly_do", "boc_tham_theo_hanh_vi", "hai_ky"}
    assert {k: v for k, v in kq.items() if k in cu} == cu
    moi = kq["theo_loai_cu_moi"]
    assert all(set(d) == COT_MOI and d["nhan"] == "SỐ LIỆU MÔ PHỎNG" for d in moi)
    assert [(d["che_do"], d["hanh_vi"]) for d in moi] == [
        (m, h) for m in ("cu_diem_hai_quy", "fa_daa") for h in mp.HANH_VI_DAY_DU]
    assert mp.HANH_VI_DAY_DU == ("luoi", "that_tha", "chien_luoc", "tinh_toan")
    for d in moi:
        assert 0 <= d["pt_nv1"] <= d["pt_top2"] <= 100
        assert (d["pt_thua_boc_tham"] is None) == (d["che_do"] == "cu_diem_hai_quy")


def test_xac_dinh_theo_hat_giong(kq):
    assert mp.chay_mo_phong_day_du(n=40, so_seed=2, so_mau=3, n_hai_ky=20) == kq
    assert mp.theo_loai(n=40, so_seed=2, seed0=5) != mp.theo_loai(n=40, so_seed=2, seed0=0)


def _em_va_clb(dl):
    """Một em và một CLB Tuyển chọn em xếp trong danh sách thật."""
    for s in dl["sids"]:
        pr, _, _, _ = mp.dang_ky(dl, hanh_vi_ep={s: "tinh_toan"})
        tc = [c for c in pr[s] if dl["fa_clb"][c]["loai"] == fa_daa.TUYEN_CHON]
        if tc:
            return s, tc[0]
    raise AssertionError("không có em nào xếp CLB Tuyển chọn")


def test_tinh_toan_bo_clb_duoi_moc_va_doi_vang():
    dl = mp.sinh_du_lieu(n=30, seed=4)
    s, c = _em_va_clb(dl)
    d = mp._diem_thi(dl, s, c)
    ep = {s: "tinh_toan"}
    bang = {x: {"diem": None, "day": False} for x in dl["clubs"]}
    pr, _, _, _ = mp.dang_ky(dl, hanh_vi_ep=ep, cat_ky_truoc=dict(bang, **{c: {"diem": d, "day": False}}))
    assert c in pr[s]                                              # bằng mốc: vẫn giữ
    pr, _, _, _ = mp.dang_ky(dl, hanh_vi_ep=ep, cat_ky_truoc=dict(bang, **{c: {"diem": d + 1, "day": False}}))
    assert c not in pr[s]                                          # dưới mốc: bỏ
    # Vàng: CLB Giới hạn xếp cao nhất KHÔNG quá tải kỳ trước; các CLB Giới hạn khác của buổi đều quá tải.
    pr0, huy0, _, _ = mp.dang_ky(dl, hanh_vi_ep=ep)
    for b in dl["ds_buoi"]:
        gh = [x for x in pr0[s] if dl["buoi_cua"][x] == b and dl["fa_clb"][x]["loai"] == fa_daa.GIOI_HAN]
        if len(gh) >= 1:
            dich = gh[-1]
            cat = dict(bang, **{x: {"diem": None, "day": x != dich} for x in gh})
            _, huy, _, _ = mp.dang_ky(dl, hanh_vi_ep=ep, cat_ky_truoc=cat)
            assert huy[s][dich] == 60
            assert sorted(huy[s].values()) == sorted(huy0[s].values())  # vẫn đúng một bộ vàng/bạc/đồng
            return
    pytest.skip("em không có CLB Giới hạn")                         # pragma: no cover


def test_khong_co_cau_nhan_dinh_khong_ma_hoc_sinh(kq):
    van = mp.in_bang("theo_loai_cu_moi", kq["theo_loai_cu_moi"])
    for tu in ("kết luận", "cho thấy", "chứng tỏ", "nên "):
        assert tu not in van.lower()
    assert "s0" not in van


def test_dong_lenh_day_du(tmp_path):
    r = subprocess.run([sys.executable, os.path.join(GOC, "du_lieu_test", "mo_phong_fa_daa.py"), "--n", "30",
                        "--so-seed", "1", "--hai-ky", "2", "--day-du"], capture_output=True, text=True,
                       encoding="utf-8", timeout=300)
    assert r.returncode == 0, r.stderr
    assert "theo_loai_cu_moi" in r.stdout and "tinh_toan" in r.stdout
    r2 = subprocess.run([sys.executable, os.path.join(GOC, "du_lieu_test", "mo_phong_fa_daa.py"), "--n", "30",
                         "--so-seed", "1", "--hai-ky", "2"], capture_output=True, text=True, encoding="utf-8",
                        timeout=300)
    assert "theo_loai_cu_moi" not in r2.stdout


def test_ban_ghi_nho_d1_co_so_lieu_mo_phong_va_lenh():
    """GAP-14: bản ghi nhớ D1 tồn tại, ghi rõ SỐ LIỆU MÔ PHỎNG và lệnh đã chạy; không viết mã cho D1."""
    p = os.path.join(GOC, "docs", "ke_hoach", "FA_GAPS_D1_MEMO.md")
    chu = open(p, encoding="utf-8").read()
    assert "SỐ LIỆU MÔ PHỎNG" in chu and "du_lieu_test/mo_phong_fa_daa.py --n 100 --so-seed 5 --hai-ky 15" in chu
    assert "A, B hay C" in chu and "bất biến 2" in chu
    kq = mp.chay_mo_phong(n=100, so_seed=5, so_mau=15)["hai_ky"]
    for d in kq:                                    # số trong bản ghi nhớ khớp lần chạy lại
        assert "| %s | %d | %d | %d | %d | %s |" % (d["dieu_kien"], d["so_em_mau"], d["so_em_co_lech"],
                                                    d["so_thua_ky_1"], d["so_em_co_loi"], d["pt_co_loi_tren_mau"]) in chu
