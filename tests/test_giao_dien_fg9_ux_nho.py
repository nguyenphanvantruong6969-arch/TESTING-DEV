"""FG-9 (STEP0, spec §3) (Playwright + Chromium): "Tải sổ nhập mẫu" có nút "Mở thư mục" trong thông báo (đường đầy đủ
nằm ở tooltip); thanh bên bỏ số 01–07; chỉ số "chưa có chỗ nào · Cần xử lý" bấm được và mở + cuộn tới khung
"Học sinh chưa có CLB nào". Dữ liệu MÔ PHỎNG.

Ghi chú STEP0: bản thảo spec nói "01–06"; trên HEAD có thêm thẻ "Chuẩn bị đợt" (07, ẩn mặc định) nên test kiểm MỌI số.
"""
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_fa_m6b_sau_ket_qua import _dung  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)
from test_giao_dien_fg6_danh_sach_loi import mo_dau  # noqa: E402,F401 (fixture)


def test_thanh_ben_khong_con_so_thu_tu(mo_dau):  # noqa: F811
    page, api, loi = mo_dau(_dung)
    chu = page.evaluate("() => [...document.querySelectorAll('.nav-item .nav-icon')].map((e) => e.textContent.trim())")
    assert all(not re.fullmatch(r"\d+", c) for c in chu), chu
    assert not loi, loi


def test_tai_so_mau_co_nut_mo_thu_muc_va_tooltip_duong_dan(mo_dau, tmp_path):  # noqa: F811
    page, api, loi = mo_dau(_dung)
    tai_ve = tmp_path / "tai_ve"
    tai_ve.mkdir()
    api.thu_muc_xuat = str(tai_ve)
    goi = []
    page.route("**/__api__/mo_thu_muc", lambda r: (goi.append(1), r.fulfill(
        status=200, content_type="application/json", body='{"ok": true, "data": {}, "errors": []}')))
    page.locator("#btnTaiSoMau").click()
    nut = page.locator("#toastStack").get_by_role("button", name=re.compile("Mở thư mục"))
    nut.wait_for()
    assert str(tai_ve) not in page.locator("#toastStack").inner_text()          # đường đầy đủ không nằm trong câu
    assert page.locator('#toastStack [title*="%s"]' % os.path.basename(str(tai_ve))).count() >= 1   # mà ở tooltip
    truoc = len(goi)
    nut.click()
    for _ in range(40):
        if len(goi) > truoc:
            break
        page.wait_for_timeout(50)
    assert len(goi) > truoc
    assert not loi, loi


def test_chi_so_chua_co_cho_bam_duoc_va_mo_khung(mo, tmp_path):  # noqa: F811
    page, api, loi = mo(_dung)
    o = page.locator('.kpi-o[data-muc="chuaCoChoPanel"]')
    o.wait_for()
    assert o.evaluate("e => e.tagName") in ("BUTTON", "A")
    o.click()
    page.wait_for_function("() => document.querySelector('#chuaCoChoPanel .panel-toggle')"
                           ".getAttribute('aria-expanded') === 'true'")
    page.wait_for_timeout(800)                                                   # chờ cuộn mượt
    h = page.locator("#chuaCoChoPanel").bounding_box()
    assert 0 <= h["y"] <= 1400, h                                                # khung nằm trong màn hình
    assert not loi, loi
