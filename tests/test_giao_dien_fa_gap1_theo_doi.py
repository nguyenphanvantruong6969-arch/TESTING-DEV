"""GAP-1 / GAP-2 (Playwright + Chromium): theo dõi sau khi xếp ở thẻ "Chi tiết và xuất tệp".

  * cờ `fa_diem_danh` tắt: không có khung điểm danh;
  * bật: khung `#diemDanhPanel` liệt kê thành viên CLB; chọn "vắng không phép" hai buổi -> dòng hiện "đã giải phóng
    chỗ" và CSDL có một dòng `release`;
  * trình hướng dẫn tạo không gian làm việc có ô `#wzFaDiemDanh` (tắt sẵn), bật thì lưu `fa_diem_danh: true`.
Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import fa_sau_xep as sx  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_fa_gap1_diem_danh import _dung  # noqa: E402
from test_ws_wharton_giao_dien import _cho_ten, _toi_buoc_luat  # noqa: E402
from test_ws_wharton_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(du_lieu):
        du_lieu(api)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="others"]').click()
        page.wait_for_selector("#resultsTableBody tr", state="attached")
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _tat(api):
    _dung(api, diem_danh=False)


def test_co_tat_khong_co_khung_diem_danh(mo):
    page, _, loi = mo(_tat)
    page.wait_for_timeout(300)
    assert page.locator("#diemDanhPanel[hidden]").count() == 1
    assert page.locator("#moiPanel[hidden]").count() == 1
    assert not loi, loi


def _so_release(api):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh WHERE kind='release'").fetchone()[0]


def test_vang_khong_phep_hai_buoi_thi_hien_da_giai_phong(mo):
    page, api, loi = mo(_dung)
    page.wait_for_selector("#diemDanhPanel:not([hidden])")
    page.select_option("#diemDanhClb", "G")
    page.wait_for_function("() => document.querySelectorAll('#diemDanhBang tr').length === 2")
    with api._ket_noi_doc() as cur:
        vt, _, _ = sx.doc_vi_tri(cur)
    em = sorted(s for (s, _), c in vt.items() if c == "G")[0]
    for so in ("1", "2"):
        page.select_option('#diemDanhBang select.dd-o[data-student-id="%s"][data-buoi-so="%s"]' % (em, so),
                           "VANG_KHONG_PHEP")
    page.wait_for_selector('#diemDanhBang tr[data-student-id="%s"] .dd-giai-phong' % em)
    assert _so_release(api) == 1
    assert "Vắng không phép" in page.locator("#diemDanhBang").inner_text()
    assert not loi, loi


def test_wizard_co_o_diem_danh_tat_san_va_luu_khi_bat(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt theo dõi")
    assert not page.locator("#wzFaDiemDanh").is_checked()
    page.locator("#wzFaDaa").check()
    page.locator("#wzFaDiemDanh").check()
    page.locator("#wzTiep").click()
    assert page.locator("#rvFaDiemDanh").inner_text() == "Bật"
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt theo dõi")
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert rules["fa_diem_danh"] is True and rules["fa_daa"] is True
    assert not loi, loi


def test_giai_phong_thi_hien_loi_moi_va_bam_nhan(mo):
    """GAP-2: chỗ được giải phóng -> khung `#moiPanel` có một lời mời đang chờ; bấm "Nhận" -> trạng thái NHAN."""
    page, api, loi = mo(_dung)
    page.wait_for_selector("#diemDanhPanel:not([hidden])")
    assert page.locator("#moiPanel:not([hidden])").count() == 1
    page.select_option("#diemDanhClb", "G")
    page.wait_for_function("() => document.querySelectorAll('#diemDanhBang tr').length === 2")
    with api._ket_noi_doc() as cur:
        vt, _, _ = sx.doc_vi_tri(cur)
    em = sorted(s for (s, _), c in vt.items() if c == "G")[0]
    for so in ("1", "2"):
        page.select_option('#diemDanhBang select.dd-o[data-student-id="%s"][data-buoi-so="%s"]' % (em, so),
                           "VANG_KHONG_PHEP")
    nut = page.locator('#moiDanhSach button.moi-tra-loi[data-ket-qua="nhan"]')
    nut.wait_for()
    assert nut.count() == 1
    nut.click()
    page.wait_for_function("() => document.getElementById('moiDanhSach').textContent.includes('Đã nhận')")
    assert page.locator("#moiDanhSach button.moi-tra-loi").count() == 0
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh WHERE kind='invite_accept'").fetchone()[0] == 1
    assert not loi, loi
