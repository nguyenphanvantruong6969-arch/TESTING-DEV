"""Thông báo nổi (toast) của toàn ứng dụng (A13.5, vấn đề #5; Playwright + Chromium).

Quy tắc Truong chốt (27/10/2026):
  * thành công tự đóng sau 6 giây; câu dài thêm thời gian theo độ dài, tối đa 10 giây; rê chuột hoặc
    đưa tiêu điểm vào thì tạm dừng đếm;
  * lỗi và cảnh báo giữ tới khi bấm ×;
  * thành công kèm cảnh báo thì tách: thông báo xanh tự đóng, cảnh báo thành thông báo vàng riêng;
  * giữ tối đa `TOAST_TOI_DA` thông báo; vùng thông báo không đè tiêu đề trang hay thanh tab;
  * `prefers-reduced-motion: reduce` thì không có hiệu ứng chuyển động;
  * thành công `aria-live="polite"`, lỗi `role="alert"` (`aria-live="assertive"`).

Đồng hồ giả của Playwright (`page.clock`) để không phải chờ thật.
"""

import datetime
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

GOC_GIO = datetime.datetime(2026, 10, 27, 9, 0, 0)


@pytest.fixture
def mo(tmp_path, api):
    """mo(dong_ho=True, **tuy_chon_trang) -> (page, loi). Đồng hồ giả dừng sau khi trang mở."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(dong_ho=True, **tuy_chon):
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        tuy_chon.setdefault("viewport", {"width": 1280, "height": 800})
        page = br.new_page(locale="vi-VN", bypass_csp=True, **tuy_chon)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        if dong_ho:
            page.clock.install(time=GOC_GIO)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        if dong_ho:
            page.clock.pause_at(GOC_GIO + datetime.timedelta(seconds=30))
        page.evaluate("document.getElementById('toastStack').innerHTML = ''")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _hien(page, noi_dung, loai, tuy_chon=None):
    page.evaluate("([m, l, o]) => { showToast(m, l, o || undefined); }", [noi_dung, loai, tuy_chon])


def _con(page, chon=""):
    return page.locator("#toastStack .toast:not(.is-leaving)" + chon).count()


def _chay(page, ms):
    page.clock.run_for(ms)


# ------------------------------------------------------------------ thành công tự đóng

def test_thanh_cong_ngan_dong_sau_6_giay(mo):
    page, loi = mo()
    _hien(page, "Xong: 6 CLB, 30 học sinh", "success")
    assert _con(page) == 1
    _chay(page, 5900)
    assert _con(page) == 1, "đóng sớm hơn 6 giây"
    _chay(page, 200)
    _chay(page, 400)                                   # hiệu ứng đóng
    assert _con(page) == 0 and page.locator("#toastStack .toast").count() == 0
    assert not loi, loi


def test_cau_dai_o_lau_hon_nhung_khong_qua_10_giay(mo):
    page, loi = mo()
    _hien(page, "Đã xuất kết quả của 30 học sinh. " + "x" * 90, "success")      # ~124 ký tự
    _chay(page, 6500)
    assert _con(page) == 1, "câu dài phải ở lâu hơn 6 giây"
    _chay(page, 4000)
    _chay(page, 400)
    assert _con(page) == 0
    page.evaluate("document.getElementById('toastStack').innerHTML = ''")
    _hien(page, "y" * 600, "success")                 # rất dài: vẫn không quá 10 giây
    _chay(page, 9900)
    assert _con(page) == 1
    _chay(page, 200)
    _chay(page, 400)
    assert _con(page) == 0
    assert not loi, loi


def test_re_chuot_vao_thi_tam_dung_roi_dem_tiep(mo):
    page, loi = mo()
    _hien(page, "Xong", "success")
    page.locator("#toastStack .toast").hover()
    _chay(page, 30000)
    assert _con(page) == 1, "rê chuột vào mà vẫn tự đóng"
    page.mouse.move(5, 5)                              # rời khỏi thông báo
    _chay(page, 5900)
    assert _con(page) == 1
    _chay(page, 400)
    _chay(page, 400)
    assert _con(page) == 0
    assert not loi, loi


def test_tieu_diem_vao_thi_tam_dung(mo):
    page, loi = mo()
    _hien(page, "Xong", "success", {"sticky": False})
    page.evaluate("document.querySelector('#toastStack .toast').tabIndex = 0;"
                  "document.querySelector('#toastStack .toast').focus()")
    _chay(page, 30000)
    assert _con(page) == 1
    assert not loi, loi


# ------------------------------------------------------------------ lỗi, cảnh báo, tách

def test_loi_va_canh_bao_con_sau_15_giay_bam_x_thi_dong(mo):
    page, loi = mo()
    _hien(page, "Không lưu được.", "error")
    _hien(page, "Dữ liệu có thể đã cũ.", "warn")
    _chay(page, 15000)
    assert _con(page, ".is-error") == 1 and _con(page, ".is-warn") == 1
    page.locator(".toast.is-error .toast-close").click()
    page.locator(".toast.is-warn .toast-close").click()
    _chay(page, 500)
    assert _con(page) == 0
    assert not loi, loi


def test_thanh_cong_kem_canh_bao_tach_thanh_hai_thong_bao(mo):
    page, loi = mo()
    _hien(page, "Xong: 6 CLB, 30 học sinh", "success", {"canhBao": "Có 2 dòng bị bỏ qua."})
    assert _con(page, ".is-success") == 1 and _con(page, ".is-warn") == 1
    assert "Có 2 dòng" in page.locator(".toast.is-warn").inner_text()
    assert "Có 2 dòng" not in page.locator(".toast.is-success").inner_text()
    _chay(page, 7000)
    _chay(page, 500)
    assert _con(page, ".is-success") == 0, "thông báo xanh phải tự đóng"
    assert _con(page, ".is-warn") == 1, "cảnh báo phải ở lại"
    assert not loi, loi


def test_giu_toi_da_toast_toi_da(mo):
    page, loi = mo()
    toi_da = page.evaluate("TOAST_TOI_DA")
    for i in range(5):
        _hien(page, "Lỗi số %d" % i, "error")
    assert _con(page) == toi_da == 4
    giu = page.eval_on_selector_all(
        "#toastStack .toast:not(.is-leaving)", "ns => ns.map(n => n.textContent)")
    assert not any("Lỗi số 0" in c for c in giu)                           # bỏ cái cũ nhất
    assert not loi, loi


# ------------------------------------------------------------------ vị trí, chuyển động, aria

def test_vung_thong_bao_khong_de_len_tieu_de_hay_thanh_tab(mo):
    page, loi = mo(dong_ho=False)
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#qlTabs")
    for i in range(4):
        _hien(page, "Lỗi dài một chút để cao hơn: " + "z" * 60 + str(i), "error")
    page.wait_for_timeout(300)
    stack = page.locator("#toastStack").bounding_box()
    assert stack and stack["height"] > 50
    for chon in ("#view-admin h1", "#view-admin .view-desc", "#qlTabs"):
        o = page.locator(chon).bounding_box()
        giao = not (stack["x"] + stack["width"] <= o["x"] or o["x"] + o["width"] <= stack["x"]
                    or stack["y"] + stack["height"] <= o["y"] or o["y"] + o["height"] <= stack["y"])
        assert not giao, (chon, stack, o)
    assert not loi, loi


def test_giam_chuyen_dong_thi_khong_co_hieu_ung(mo):
    page, loi = mo(dong_ho=False, reduced_motion="reduce")
    _hien(page, "Xong", "success")
    ten = page.evaluate("getComputedStyle(document.querySelector('#toastStack .toast')).animationName")
    assert ten == "none", ten
    page.close()


def test_co_chuyen_dong_thi_van_co_hieu_ung(mo):
    page, loi = mo(dong_ho=False, reduced_motion="no-preference")
    _hien(page, "Xong", "success")
    ten = page.evaluate("getComputedStyle(document.querySelector('#toastStack .toast')).animationName")
    assert ten != "none"


def test_aria_thanh_cong_polite_loi_alert(mo):
    page, loi = mo(dong_ho=False)
    _hien(page, "Xong", "success")
    _hien(page, "Hỏng", "error")
    ok = page.locator(".toast.is-success")
    assert ok.get_attribute("aria-live") == "polite"
    bad = page.locator(".toast.is-error")
    assert bad.get_attribute("role") == "alert"
    assert bad.get_attribute("aria-live") == "assertive"
    assert page.get_attribute("#toastStack", "aria-live") == "polite"
    assert not loi, loi
