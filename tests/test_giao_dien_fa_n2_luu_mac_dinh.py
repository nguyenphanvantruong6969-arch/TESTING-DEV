"""FA-N2 (Playwright + Chromium): màn nhập tại chỗ, bước nguyện vọng khi workspace bật xếp theo loại CLB và
huy chương (V§6.1, D2).

  * em lười: lưu nguyện vọng là có huy chương mặc định 60/30/10 ở 3 CLB không Tự do đầu tiên;
  * đổi thứ tự / bỏ CLB mà huy chương đã lưu vẫn bằng mặc định của thứ tự CŨ -> huy chương đi theo thứ tự mới;
  * đã chỉnh tay -> giữ nguyên và hiện câu nhắc nhẹ.
Không có suy diễn ở máy chủ: trình duyệt gọi `submit_huy_chuong`. Dữ liệu MÔ PHỎNG.
"""
import time

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _fa import bat_fa, dung_fa_clb, dung_hs_fa  # noqa: E402
from test_giao_dien_wharton import _chon, mo  # noqa: E402,F401


def _du_lieu(huy_chuong=None, nv=("T", "S", "G1", "G2")):
    def _f(api, bat=True):
        dung_fa_clb(api, T=(30, "TU_DO"), S=(5, "TUYEN_CHON", 5), G1=(5, "GIOI_HAN"), G2=(5, "GIOI_HAN"))
        dung_hs_fa(api, "HS1", nv={"HS1": list(nv)} if nv else None)
        if bat:
            bat_fa(api)
        if huy_chuong:
            assert api.submit_huy_chuong("HS1", huy_chuong)["ok"]
        return api
    return _f


def _db(api):
    with api._ket_noi_doc() as cur:
        return {r[0]: r[1] for r in cur.execute(
            "SELECT club_id, points FROM wharton_bids WHERE student_id = 'HS1'")}


def _luu_nv(page):
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function(
        "() => document.getElementById('preferencesFeedback').textContent.includes('Đã lưu')")
    page.wait_for_function("() => !document.getElementById('fbHuyChuongStep').hidden")
    page.wait_for_timeout(500)


def test_em_luoi_luu_nguyen_vong_la_co_huy_chuong_mac_dinh(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu(nv=None))
    _chon(page, "HS1")
    for cid in ("T", "S", "G1", "G2"):
        page.locator('#rankingSourceGrid .option-row[data-club-id="%s"]' % cid).click()
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function(
        "() => document.getElementById('preferencesFeedback').textContent.includes('Đã lưu')")
    page.wait_for_function("() => !document.getElementById('fbHuyChuongStep').hidden")
    page.wait_for_timeout(500)
    assert _db(api) == {"S": 60, "G1": 30, "G2": 10}
    assert not loi, loi


def test_doi_thu_tu_ma_chua_chinh_tay_thi_huy_chuong_di_theo(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu({"S": 60, "G1": 30, "G2": 10}))
    _chon(page, "HS1")
    page.wait_for_selector("#fbHuyChuongStep:not([hidden]) select.hc-chon")
    page.locator("#rankingList li").nth(1).locator("button").click()       # bỏ S
    _luu_nv(page)
    assert _db(api) == {"G1": 60, "G2": 30}
    assert page.locator("#hcNhacDaChinh").is_hidden()
    assert not loi, loi


def test_da_chinh_tay_thi_giu_nguyen_va_nhac(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu({"G2": 60, "S": 30, "G1": 10}))
    _chon(page, "HS1")
    page.wait_for_selector("#fbHuyChuongStep:not([hidden]) select.hc-chon")
    page.locator("#rankingList li").nth(1).locator("button").click()       # bỏ S
    _luu_nv(page)
    assert _db(api) == {"G2": 60, "G1": 10}                                 # giữ nguyên phần còn lại
    assert page.locator("#hcNhacDaChinh").is_visible()
    assert not loi, loi


# ----------------------------------------------------------------------------- FA-P2: đổi em giữa lúc lưu

def _hai_em(api, bat=True):
    dung_fa_clb(api, T=(30, "TU_DO"), S=(5, "TUYEN_CHON", 5), G1=(5, "GIOI_HAN"), G2=(5, "GIOI_HAN"))
    dung_hs_fa(api, "HS1", "HS2")
    if bat:
        bat_fa(api)
    return api


@pytest.mark.parametrize("ham_giu", ["submit_preferences", "get_student_entry_state"])
def test_sang_em_khac_giua_luc_luu_van_luu_huy_chuong_em_truoc(mo, ham_giu):  # noqa: F811
    """FA-P2: người nhập lưu nguyện vọng của HS1 rồi bấm ngay sang HS2 khi lời gọi `ham_giu` của HS1 chưa về. HS1 vẫn
    phải có huy chương mặc định (FA-N2); màn hình HS2 không bị vẽ lại bằng dữ liệu HS1."""
    page, api, loi = mo(du_lieu=_hai_em)
    _chon(page, "HS1")
    for cid in ("T", "S", "G1", "G2"):
        page.locator('#rankingSourceGrid .option-row[data-club-id="%s"]' % cid).click()
    page.evaluate("""(ham) => {   /* giữ lời gọi `ham` của HS1 tới khi thả; bọc cả Proxy của cầu nối */
      const goc = window.pywebview.api;
      window.__nha = [];
      window.pywebview = { api: new Proxy({}, { has: () => true, get: (_t, ten) => (...a) =>
        (ten === ham && a[0] === "HS1")
          ? new Promise((ok) => window.__nha.push(() => ok(goc[ten](...a).finally(() => { window.__xong = true; }))))
          : goc[ten](...a) }) };
    }""", ham_giu)
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function("() => window.__nha.length >= 1")
    the = page.locator('#studentSearchResults .hs-card[data-student-id="HS2"]')
    the.click()
    the.click()     # nguyện vọng còn "chưa lưu" khi lời gọi lưu chưa về: lần bấm 1 chỉ cảnh báo (roiDiNeuDuoc)
    _chon(page, "HS2")
    page.evaluate("() => window.__nha.forEach((f) => f())")
    # SM-2: chờ ĐIỀU KIỆN thật (không chờ cố định): lời gọi bị giữ đã về, rồi huy chương HS1 đã vào CSDL (tối đa 5 s)
    page.wait_for_function("() => window.__xong === true", timeout=5000)
    het = time.monotonic() + 5
    while _db(api) != {"S": 60, "G1": 30, "G2": 10} and time.monotonic() < het:
        page.wait_for_timeout(50)
    assert _db(api) == {"S": 60, "G1": 30, "G2": 10}
    assert "HS2" in page.locator("#currentStudentLabel").inner_text()
    assert page.locator("#rankingList li").count() == 0               # HS2 chưa có nguyện vọng
    assert not loi, loi
