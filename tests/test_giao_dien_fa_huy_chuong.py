"""FA-UI-3 (Playwright + Chromium): ở màn nhập tại chỗ, khi workspace bật xếp theo loại CLB và huy chương,
bước 3 là "Huy chương" thay cho điểm quyết tâm.

  * ba ô vàng / bạc / đồng điền sẵn theo thứ tự nguyện vọng, bỏ CLB Tự do (D2);
  * đổi được mọi huy chương: chọn một CLB đang có huy chương khác thì hai huy chương đổi chỗ, đủ 6 cách đặt;
  * CLB Tự do không có trong lựa chọn; vàng ở CLB Tuyển chọn thì hiện câu nhắc (V§6.1);
  * lưu qua `submit_huy_chuong`; server từ chối thì hiện lỗi, CSDL không đổi;
  * FA tắt: bước điểm quyết tâm như cũ, không có bước huy chương.
Dữ liệu MÔ PHỎNG.
"""
import itertools

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _fa import bat_fa, dung_fa_clb, dung_hs_fa  # noqa: E402
from test_giao_dien_wharton import _chon, mo  # noqa: E402,F401

VANG, BAC, DONG = 60, 30, 10


def _du_lieu(api, bat=True):
    # T: Tự do; S: Tuyển chọn; G1, G2: Giới hạn. Nguyện vọng: T S G1 G2 -> mặc định vàng S, bạc G1, đồng G2.
    dung_fa_clb(api, T=(30, "TU_DO"), S=(5, "TUYEN_CHON", 5), G1=(5, "GIOI_HAN"), G2=(5, "GIOI_HAN"))
    dung_hs_fa(api, "HS1", nv={"HS1": ["T", "S", "G1", "G2"]})
    if bat:
        bat_fa(api)
    return api


def _du_lieu_tat(api, bat=True):
    return _du_lieu(api, bat=False)


def _cho(page):
    page.wait_for_selector("#fbHuyChuongStep:not([hidden]) select.hc-chon")


def _o(page, diem):
    return page.locator('#fbHuyChuongBody select.hc-chon[data-diem="%d"]' % diem)


def _dat(page):
    return {d: _o(page, d).input_value() for d in (VANG, BAC, DONG)}


def _db(api):
    with api._ket_noi_doc() as cur:
        return {r[0]: r[1] for r in cur.execute(
            "SELECT club_id, points FROM wharton_bids WHERE student_id = 'HS1'")}


def test_fa_tat_khong_co_buoc_huy_chuong(mo):  # noqa: F811 (fixture dùng lại)
    page, _, loi = mo(du_lieu=_du_lieu_tat)
    _chon(page, "HS1")
    page.wait_for_selector("#fbWhartonStep:not([hidden]) .wh-khung")
    assert page.locator("#fbHuyChuongStep").is_hidden()
    assert not loi, loi


def test_dien_san_theo_thu_tu_bo_clb_tu_do_va_luu(mo):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo(du_lieu=_du_lieu)
    _chon(page, "HS1")
    _cho(page)
    assert page.locator("#fbWhartonStep").is_hidden()
    assert _dat(page) == {VANG: "S", BAC: "G1", DONG: "G2"}
    for d in (VANG, BAC, DONG):                                       # CLB Tự do không nhận huy chương
        assert "T" not in _o(page, d).locator("option").evaluate_all("os => os.map(o => o.value)")
    page.locator("#btnSubmitHuyChuong").click()
    page.wait_for_function("() => document.getElementById('huyChuongFeedback').textContent.trim() !== ''")
    assert _db(api) == {"S": VANG, "G1": BAC, "G2": DONG}
    assert not loi, loi


def test_doi_cho_dat_du_sau_cach(mo):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo(du_lieu=_du_lieu)
    _chon(page, "HS1")
    _cho(page)
    thay = set()
    for p in itertools.permutations(["S", "G1", "G2"]):
        _o(page, VANG).select_option(p[0])
        _o(page, BAC).select_option(p[1])
        dat = _dat(page)
        assert len(set(dat.values())) == 3                            # đổi chỗ, không trùng
        thay.add((dat[VANG], dat[BAC], dat[DONG]))
    assert len(thay) == 6
    _o(page, VANG).select_option("G2")
    _o(page, BAC).select_option("S")
    page.locator("#btnSubmitHuyChuong").click()
    page.wait_for_function("() => document.getElementById('huyChuongFeedback').textContent.trim() !== ''")
    assert _db(api) == {"G2": VANG, "S": BAC, "G1": DONG}
    assert not loi, loi


def test_vang_o_clb_tuyen_chon_co_cau_nhac(mo):  # noqa: F811 (fixture dùng lại)
    page, _, loi = mo(du_lieu=_du_lieu)
    _chon(page, "HS1")
    _cho(page)
    assert page.locator("#hcNhacTuyenChon").is_visible()               # vàng đang ở S (Tuyển chọn)
    _o(page, VANG).select_option("G1")
    assert page.locator("#hcNhacTuyenChon").is_hidden()
    assert not loi, loi


def test_server_tu_choi_thi_hien_loi_va_khong_ghi(mo):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo(du_lieu=_du_lieu)
    _chon(page, "HS1")
    _cho(page)
    # Giả một lựa chọn trình duyệt không đưa ra (CLB Tự do): server mới là nơi quyết định.
    page.evaluate("""() => { const s = document.querySelector('select.hc-chon[data-diem="60"]');
        const o = document.createElement('option'); o.value = 'T'; o.textContent = 'T'; s.append(o); s.value = 'T'; }""")
    page.locator("#btnSubmitHuyChuong").click()
    page.wait_for_selector("#huyChuongFeedback.is-error", timeout=8000)
    assert page.locator("#huyChuongFeedback").inner_text().strip()
    assert _db(api) == {}
    assert not loi, loi
