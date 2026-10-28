"""A13.10, nhãn "Xét điểm thi" / "Xét điểm quyết tâm" thay "Tầng 1" / "Tầng 2" (Playwright + Chromium).

Chỉ đổi CHỮ HIỂN THỊ. Mã, biến, cột và mã lỗi vẫn là `tier`, `tang1`, `tang2`. Dữ liệu MÔ PHỎNG.

  * giao diện VI và EN: nhãn mới có mặt, nhãn cũ không còn trong chữ người dùng thấy;
  * tệp xuất Excel: tiêu đề cột đã khoá ở test_diem_chuan.py::test_tep_xuat_co_trang_diem_chuan_moi_clb_buoi_mot_dong;
  * hướng dẫn: không còn "Tầng 1" / "Tầng 2" chỉ hai nhóm xếp;
  * chuỗi giao diện mới không xưng hô, không nhắc "Wharton" (test_van_phong_tu_nhien quét thêm).
"""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton, chen_bids, dung_clb  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

CU_VI = re.compile(r"[Tt]ầng\s*[12]\b")
CU_EN = re.compile(r"\b[Tt]ier\s*[12]\b")


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo():
        bat_wharton(api)
        dung_clb(api, A=4, B=10, C=3)
        bids = []
        for i in range(8):
            sid = "HS%d" % (i + 1)
            assert api.create_student_if_missing(sid, "Em số %d" % (i + 1))["ok"]
            assert api.submit_preferences(sid, ["A", "B"])["ok"]
            p = 95 - 10 * i
            bids += [(sid, "A", 2, p), (sid, "B", 2, 100 - p)]
        chen_bids(api, bids)
        assert api.run_pipeline(seed=3)["ok"]
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.locator('#qlTabs [data-ql-tab="dc"]').click()
        page.wait_for_selector("#adminDiemChuanBlock:not([hidden]) #dcChiTiet:not([hidden])")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _chu_nhin_thay(page):
    """Chữ hiển thị của khối Điểm chuẩn, kèm tên truy cập (aria-label, title) và bảng ẩn chữ."""
    return page.evaluate("""() => {
        const goc = document.querySelector('#adminDiemChuanBlock');
        const ra = [goc.innerText, goc.textContent];
        goc.querySelectorAll('[aria-label],[title]').forEach(n => {
          ra.push(n.getAttribute('aria-label') || '', n.getAttribute('title') || '');
        });
        return ra.join('\\n');
    }""")


def test_nhan_moi_vi_co_mat_nhan_cu_het(mo):
    page, loi = mo()
    chu = _chu_nhin_thay(page)
    assert "Xét điểm thi" in chu and "Xét điểm quyết tâm" in chu, chu
    assert not CU_VI.search(chu), CU_VI.search(chu)
    assert "Wharton" not in chu
    assert not loi, loi


def test_nhan_moi_en_co_mat_nhan_cu_het(mo):
    page, loi = mo()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("() => document.querySelector('#adminDiemChuanBlock h2').textContent === 'Cut-off points'")
    chu = _chu_nhin_thay(page)
    assert "Exam-based" in chu and "Commitment points" in chu, chu
    assert not CU_EN.search(chu), CU_EN.search(chu)
    assert "Wharton" not in chu
    assert not loi, loi


def test_chuoi_i18n_dc_khong_con_nhan_cu_khong_xung_ho():
    """Mọi khoá `dc_*` trong i18n.js (VI và EN): không còn tầng/tier, không xưng hô, không Wharton."""
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        mat = f.read()
    cac = re.findall(r'^\s*(dc_[a-z0-9_]+):\s*"((?:[^"\\]|\\.)*)"', mat, flags=re.M)
    assert len(cac) >= 60                                   # hai ngôn ngữ
    tang = [v for k, v in cac if k in ("dc_tang1", "dc_tang2")]
    assert sorted(tang) == sorted([
        "Xét điểm thi", "Xét điểm quyết tâm", "Exam-based", "Commitment points"])
    for k, v in cac:
        assert not CU_VI.search(v) and not CU_EN.search(v), (k, v)
        assert not re.search(r"\btầng\b|\btier\b", v, re.I), (k, v)
        assert "Wharton" not in v, (k, v)
        assert not re.search(r"\b(em|các em|bạn|you|your)\b", v, re.I), (k, v)


def test_huong_dan_khong_con_tang_1_2():
    for ten in ("HUONG_DAN_SU_DUNG.md", "README.md", "GIAI_THICH_DE_HIEU.html", "BAO_CAO_CACH_CHAY.html",
                "TAI_LIEU_DU_LIEU.md", os.path.join("mau_csv", "vi_du_day_du", "GIAI_THICH.md")):
        with open(os.path.join(GOC, ten), encoding="utf-8") as f:
            mat = f.read()
        assert not CU_VI.search(mat), (ten, CU_VI.search(mat))
    with open(os.path.join(GOC, "api_xuat.py"), encoding="utf-8") as f:
        assert not CU_VI.search(f.read())


def test_en_moi_cho_deu_la_commitment_points_khong_con_preference_points():
    """Giao diện EN (i18n.js) và thông báo lỗi EN (i18n_errors.py, i18n_loi.js): một tên duy nhất."""
    for ten in ("i18n.js", "i18n_errors.py", "i18n_loi.js"):
        with open(os.path.join(GOC, ten), encoding="utf-8") as f:
            mat = f.read()
        assert not re.search(r"preference points?", mat, re.I), ten
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        assert "Commitment points" in f.read()
