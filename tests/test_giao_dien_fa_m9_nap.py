"""FA-M9 (Playwright + Chromium; TH = chưa thử trên Microsoft thật): bước 4 "Nạp kết quả từ biểu mẫu" của thẻ "Chuẩn bị đợt".

  * đường B: thả 1 tệp đăng ký + 2 tệp bài thi (đề A, đề B) -> hiện loại và đề đoán -> chuyển -> xem trước -> Nhập sổ ->
    số học sinh trong app.db khớp;
  * đường A: lệch giữa hai đề -> hộp xác nhận -> "Giữ điểm đã chấm" -> xem trước;
  * tệp không nhận ra / sai đường: báo trên dòng, nút Chuyển khoá; chưa chọn đường: nhắc.
Dữ liệu MÔ PHỎNG.
"""
import json
import os
import shutil
import sqlite3

import openpyxl
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import forms_dot  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_fa_m3_chuyen import _lc, _tep_dang_ky  # noqa: E402
from test_fa_m9_thuan import _bo, _bo_lech, _de_3_de  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(duong, de, sn):
        ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
        if duong:
            assert api.dat_fa_duong(duong)["ok"]
        with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
            json.dump(de, f, ensure_ascii=False)
        shutil.copyfile(sn, forms_dot.duong_so_nhap_clb_dot(api.db_path))
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1600}, bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
        page.locator('.nav-item[data-tab="chuan_bi"]').click()
        page.wait_for_function("() => window.ChuanBi.duong() === %s" % json.dumps(duong))
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _doi_email(duong, tu, den):
    wb = openpyxl.load_workbook(duong)
    for r in wb.active.iter_rows(min_row=2):
        r[3].value = r[3].value.replace(tu, den)
        r[4].value = r[3].value
    wb.save(duong)


def _dem_hs(api):
    con = sqlite3.connect(api.db_path)
    try:
        return con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    finally:
        con.close()


def test_duong_b_tha_dang_ky_va_hai_bai_thi_xem_truoc_roi_nhap(mo, api, tmp_path):
    de = _de_3_de()
    _, thi_a, sn = _bo(tmp_path, de, "A", so_em=3, nhan="thi_A.xlsx")
    tb = tmp_path / "b"
    tb.mkdir()
    _, thi_b, _ = _bo(tb, de, "B", so_em=3, nhan="thi_B.xlsx")
    _doi_email(thi_b, "e", "f")
    dk = _tep_dang_ky(tmp_path, de, [dict(sid="HS%s%d" % (c, i), email="%s%d@x.vn" % (c, i), nv1=_lc(de, "clb_covua"))
                                     for c in "ef" for i in range(3)], ten="dk.xlsx")
    page, loi = mo("B", de, sn)
    page.locator("#cb-nap-tep").set_input_files([dk, thi_a, thi_b])
    page.wait_for_selector("#cb-nap-bang tbody tr:nth-child(3)")
    hang = {r.get_attribute("data-ten"): r for r in page.locator("#cb-nap-bang tbody tr").all()}
    assert set(hang) == {"dk.xlsx", "thi_A.xlsx", "thi_B.xlsx"}
    assert "Đăng ký" in hang["dk.xlsx"].locator(".cb-nap-loai").inner_text()
    assert "Bài thi" in hang["thi_A.xlsx"].locator(".cb-nap-loai").inner_text()
    assert hang["thi_A.xlsx"].locator("select").input_value() == "A"
    assert hang["thi_B.xlsx"].locator("select").input_value() == "B"
    assert hang["dk.xlsx"].locator("select").count() == 0
    page.locator("#cb-nap-chuyen").click()
    page.wait_for_selector("#cb-nap-xem-truoc")
    assert "6 học sinh" in page.locator("#cb-nap-xem-truoc").inner_text()
    assert _dem_hs(api) == 0                                           # xem trước chưa ghi gì
    page.locator("#cb-nap-nhap").click()
    page.wait_for_selector('#cb-buoc-4 [data-trang-thai="xanh"]:has-text("Đã nhập")')
    assert "6 học sinh" in page.locator('#cb-buoc-4 [data-trang-thai="xanh"]').last.inner_text()
    assert _dem_hs(api) == 6
    assert not loi, loi


def test_duong_a_lech_giua_hai_de_hien_hop_xac_nhan(mo, api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo_lech(tmp_path, de)
    page, loi = mo("A", de, sn)
    page.locator("#cb-nap-tep").set_input_files([lst] + thi)
    page.wait_for_selector("#cb-nap-bang tbody tr:nth-child(3)")
    page.locator("#cb-nap-chuyen").click()
    page.wait_for_selector("#cb-nap-xac-nhan")
    assert "clb_covua" in page.locator("#cb-nap-xac-nhan").inner_text()
    assert page.locator("#cb-nap-xem-truoc").count() == 0 and page.locator("#cb-nap-nhap").count() == 0
    assert not os.path.exists(os.path.join(forms_dot.thu_muc_nap(api.db_path), "SO_NHAP_CLB.xlsx"))
    page.locator("#cb-nap-giu").click()
    page.wait_for_selector("#cb-nap-xem-truoc")
    assert "20 học sinh" in page.locator("#cb-nap-xem-truoc").inner_text()
    assert page.locator("#cb-nap-xac-nhan").count() == 0
    # mở lại thẻ: các tệp đã tải vẫn được nhớ (không cần thả lại)
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="chuan_bi"]').click()
    page.wait_for_selector("#cb-nap-bang tbody tr:nth-child(3)")
    assert not loi, loi


def test_tep_la_va_sai_duong_khoa_nut_chuyen(mo, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    la = str(tmp_path / "la.xlsx")
    wb = openpyxl.Workbook()
    wb.active.append(["ID", "Cột lạ"])
    wb.save(la)
    dk = _tep_dang_ky(tmp_path, de, [dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"))], ten="dk.xlsx")
    page, loi = mo("A", de, sn)
    page.locator("#cb-nap-tep").set_input_files([lst, thi, la, dk])
    page.wait_for_selector("#cb-nap-bang tbody tr:nth-child(4)")
    assert page.locator("#cb-nap-bang tr.cb-nap-tep-loi").count() == 2
    assert page.locator("#cb-nap-chuyen").is_disabled()
    page.locator("#cb-nap-tep").set_input_files([lst, thi])
    page.wait_for_function("() => document.querySelectorAll('#cb-nap-bang tbody tr').length === 2")
    assert page.locator("#cb-nap-chuyen").is_enabled()
    assert not loi, loi


def test_chua_chon_duong_nhac(mo, tmp_path):
    de = _de_3_de()
    _, _, sn = _bo(tmp_path, de, "A")
    page, loi = mo(None, de, sn)
    page.wait_for_selector('#cb-buoc-4 [data-trang-thai="chua"]')
    assert page.locator("#cb-nap-tep").count() == 0
    assert not loi, loi
