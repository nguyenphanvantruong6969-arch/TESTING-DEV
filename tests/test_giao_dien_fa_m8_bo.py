"""FA-M8 (Playwright + Chromium; TH = chưa thử trên Microsoft thật): bước 3 "Tạo bộ biểu mẫu" của thẻ Chuẩn bị đợt.

Chưa chọn đường / chưa có đề -> nút tắt + lời nhắc; đủ -> bấm tạo ra tệp zip ở Tải xuống, có thông báo tên tệp, nút
"Mở thư mục"; bỏ tích "Một biểu mẫu cho mọi buổi" đổi bộ; "Hai đề cho CLB Tuyển chọn" chỉ bật khi đề có biến thể.
Dữ liệu MÔ PHỎNG.
"""
import copy
import json
import os
import zipfile

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import forms_dot  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

forms_dot.nap_mau_forms()
import bieu_mau  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api, tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []
    api.thu_muc_xuat = str(tmp_path / "tai_ve")
    os.makedirs(api.thu_muc_xuat)
    api.da_mo = []
    api.mo_thu_muc = lambda path: (api.da_mo.append(path), {"ok": True, "data": {}, "errors": []})[1]

    def _mo(duong=None, de=None, bien_the=False):
        cau_hinh = {"fa_daa": True}
        if duong:
            cau_hinh["fa_duong"] = duong
        ch.ghi_cau_hinh(api.db_path, {"rules": cau_hinh})
        if de:
            d = bieu_mau.doc_de_thi()
            if bien_the:
                c = next(x for x in d["cau_lac_bo"] if x["de_thi"])
                c["de_thi_bien_the"] = [copy.deepcopy(c["de_thi"]), copy.deepcopy(c["de_thi"])]
            with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1600}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
        page.locator('.nav-item[data-tab="chuan_bi"]').click()
        page.wait_for_selector("#cb-bo-tao")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _zip(api):
    return sorted(f for f in os.listdir(api.thu_muc_xuat) if f.startswith("BO_BIEU_MAU_") and f.endswith(".zip"))


def test_chua_chon_duong_nut_tat(mo, api):
    page, loi = mo(de=True)
    assert page.locator("#cb-bo-tao").is_disabled()
    assert "đường A hoặc B" in page.locator("#cb-buoc-3").inner_text()
    assert not loi, loi


def test_chua_co_de_nut_tat(mo, api):
    page, loi = mo(duong="B")
    assert page.locator("#cb-bo-tao").is_disabled()
    assert "đề thi ở bước 2" in page.locator("#cb-buoc-3").inner_text()
    assert not loi, loi


def test_tao_bo_ra_zip_va_mo_thu_muc(mo, api):
    page, loi = mo(duong="B", de=True)
    assert page.locator("#cb-bo-mot").is_checked()                       # mặc định tích
    assert page.locator("#cb-bo-bien-the").is_disabled()                 # đề không có biến thể
    assert page.locator("#cb-bo-mo").count() == 0
    page.locator("#cb-bo-tao").click()
    page.wait_for_selector("#cb-bo-ket-qua")
    zips = _zip(api)
    assert len(zips) == 1 and zips[0] in page.locator("#cb-bo-ket-qua").inner_text()
    page.wait_for_selector(".toast")
    with zipfile.ZipFile(os.path.join(api.thu_muc_xuat, zips[0])) as z:
        assert "00_DOC_TRUOC.md" in z.namelist()
    page.locator("#cb-bo-mo").click()
    page.wait_for_function("() => true")
    for _ in range(40):
        if api.da_mo:
            break
        page.wait_for_timeout(50)
    assert api.da_mo and api.da_mo[0].endswith(zips[0])
    assert not loi, loi


def test_bo_tich_mot_bieu_mau_doi_bo(mo, api):
    page, loi = mo(duong="B", de=True)
    page.locator("#cb-bo-tao").click()
    page.wait_for_selector("#cb-bo-ket-qua")
    page.locator("#cb-bo-mot").uncheck()
    page.locator("#cb-bo-tao").click()
    page.wait_for_function("() => document.querySelector('#cb-bo-ket-qua') && "
                           "document.querySelector('#cb-bo-ket-qua').textContent.includes('(2)')")
    zips = _zip(api)
    assert len(zips) == 2
    dem = []
    for z in zips:
        with zipfile.ZipFile(os.path.join(api.thu_muc_xuat, z)) as zf:
            dem.append(len(zf.namelist()))
    assert dem[0] != dem[1]
    assert not loi, loi


def test_bien_the_chi_bat_khi_de_co_bien_the(mo, api):
    page, loi = mo(duong="B", de=True, bien_the=True)
    assert page.locator("#cb-bo-bien-the").is_enabled()
    page.locator("#cb-bo-tao").click()
    page.wait_for_selector("#cb-bo-ket-qua")
    sau_ko = len(zipfile.ZipFile(os.path.join(api.thu_muc_xuat, _zip(api)[0])).namelist())
    page.locator("#cb-bo-bien-the").check()
    page.locator("#cb-bo-tao").click()
    page.wait_for_function("() => document.querySelector('#cb-bo-ket-qua') && "
                           "document.querySelector('#cb-bo-ket-qua').textContent.includes('(2)')")
    mang = [len(zipfile.ZipFile(os.path.join(api.thu_muc_xuat, z)).namelist()) for z in _zip(api)]
    assert max(mang) > sau_ko
    assert not loi, loi


def test_duong_a_tao_duoc_bo(mo, api):
    page, loi = mo(duong="A", de=True)
    assert page.locator("#cb-bo-mot").is_disabled()          # đường A dùng bộ dựng riêng, không có tuỳ chọn này
    page.locator("#cb-bo-tao").click()
    page.wait_for_selector("#cb-bo-ket-qua")
    zips = _zip(api)
    assert len(zips) == 1
    with zipfile.ZipFile(os.path.join(api.thu_muc_xuat, zips[0])) as z:
        assert any("04_forms" in n for n in z.namelist())
    assert not loi, loi
