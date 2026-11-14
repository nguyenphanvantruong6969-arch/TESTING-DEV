"""Gộp SG (person A integration): SG-10 (CLB Tự do không có % lấp đầy) và SG-6 (giờ / địa điểm của CLB)
sửa cùng mấy dòng trong `api_bao_cao.get_club_fill_stats`, `api_xuat` (đầu khối "Theo CLB") và
`js/09_the_xem.js` (`veKqTheoClb`). Khi gộp giữ CẢ HAI hành vi; test này chứng minh một CLB Tự do có khai giờ và
địa điểm vẫn có đủ hai thứ.

Dữ liệu là dữ liệu MÔ PHỎNG dựng trong test.
"""

from test_sg10_clb_tu_do import _chu_xuat, _dung_fa

GIO, DIA = "Thứ 4, 15:00", "Phòng B2"


def _khai_gio(api, club_id="T"):
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET gio = ?, dia_diem = ? WHERE club_id = ?", (GIO, DIA, club_id))


def test_thong_ke_clb_tu_do_co_ca_tu_do_va_gio(api):
    _dung_fa(api)
    _khai_gio(api)
    t = {c["club_id"]: c for c in api.get_club_fill_stats()["data"]}["T"]
    assert t["tu_do"] is True and t["ti_le_choi"] is None
    assert (t["gio"], t["dia_diem"]) == (GIO, DIA)
    ds = api.get_danh_sach_clb("T")["data"]
    assert ds["tu_do"] is True and (ds["gio"], ds["dia_diem"]) == (GIO, DIA)


def test_xuat_clb_tu_do_co_ca_khong_gioi_han_va_gio(api, tmp_path):
    _dung_fa(api)
    _khai_gio(api)
    van = "\n".join(" | ".join(r) for dong in _chu_xuat(api, tmp_path).values() for r in dong)
    assert "12/5" not in van
    dau = [d for d in van.splitlines() if "Đã xếp 12 · không giới hạn chỗ" in d]
    assert dau and GIO in dau[0] and DIA in dau[0]


def test_giao_dien_theo_clb_tu_do_co_ca_khong_gioi_han_va_gio(api):
    """Màn Kết quả → Theo CLB: dòng đếm của CLB Tự do có khai giờ = "… không giới hạn chỗ · <giờ> · <địa điểm>"."""
    import pytest
    pytest.importorskip("playwright", reason="chưa cài playwright")
    import test_giao_dien_sg10_clb_tu_do as ui
    from _trinh_duyet import CHROMIUM
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    gen = ui.mo.__wrapped__(api)
    mo = next(gen)
    try:
        page, loi = mo(lambda a: (ui._fa(a), _khai_gio(a)))
        dem = ui._theo_clb(page, "T")
        page.wait_for_function("() => document.getElementById('kqDem').textContent.includes('không giới hạn chỗ')")
        van = dem.inner_text()
        assert "/5" not in van and GIO in van and DIA in van
        assert not loi
    finally:
        next(gen, None)
