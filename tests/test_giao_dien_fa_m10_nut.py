"""FA-M10 (Playwright + Chromium; TH = chưa thử trên Microsoft thật): bước 5 "Sau khi xếp" của thẻ "Chuẩn bị đợt".

Ba nút thật sự chạy trong Chromium và ghi tệp vào thư mục Tải xuống:
  * "Xuất KETQUA_NHAP_LIST.csv" (kể cả báo lỗi khi chưa có tệp email);
  * "Ai chưa đăng ký": chọn CSV danh sách lớp -> thư mục chua_dang_ky/;
  * "Đối chiếu" (chỉ đường A): chọn hai CSV -> DOI_CHIEU_LIST.xlsx; đường B không có nút này.
Dữ liệu MÔ PHỎNG.
"""
import csv
import json
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import forms_dot  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_fa_ly_do import _dung  # noqa: E402
from test_fa_m9_thuan import _de_3_de  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api, tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []
    tai_ve = tmp_path / "tai_ve"
    tai_ve.mkdir()
    api.thu_muc_xuat = str(tai_ve)

    def _mo(duong, co_xep=True, co_email=True):
        if co_xep:
            _dung(api)
            assert api.run_pipeline(seed=9)["ok"]
        ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
        assert api.dat_fa_duong(duong)["ok"]
        with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
            json.dump(_de_3_de(), f, ensure_ascii=False)
        if co_email:
            with open(forms_dot.duong_email_ma_hs(api.db_path), "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["Email", "student_id"])
                w.writerows([["%s@x.vn" % s, s] for s in ("s1", "s2", "s3")])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1800}, bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
        page.locator('.nav-item[data-tab="chuan_bi"]').click()
        page.wait_for_function("() => window.ChuanBi.duong() === %s" % json.dumps(duong))
        page.wait_for_selector("#cb-nap5-xuat")
        return page, loi, tai_ve

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _csv(p, dau, dong):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(dau)
        w.writerows(dong)
    return str(p)


def test_nut_xuat_ket_qua_ghi_tep_vao_tai_xuong(mo):
    page, loi, tai_ve = mo("A")
    page.locator("#cb-nap5-xuat").click()
    page.wait_for_selector("#cb-nap5-xuat-kq")
    assert "KETQUA_NHAP_LIST.csv" in page.locator("#cb-nap5-xuat-kq").inner_text()
    assert sorted(os.listdir(tai_ve)) == ["KETQUA_NHAP_LIST.csv"]
    dong = list(csv.DictReader(open(tai_ve / "KETQUA_NHAP_LIST.csv", encoding="utf-8-sig")))
    assert dong and {d["Email"] for d in dong} >= {"s1@x.vn", "s2@x.vn"}
    assert not loi, loi


def test_nut_xuat_ket_qua_thieu_email_bao_loi_khong_ghi_tep(mo):
    page, loi, tai_ve = mo("A", co_email=False)
    page.locator("#cb-nap5-xuat").click()
    page.wait_for_function("() => /email/i.test(document.body.innerText)")
    assert page.locator("#cb-nap5-xuat-kq").count() == 0
    assert os.listdir(tai_ve) == []
    assert not loi, loi


def test_nut_ai_chua_dang_ky_khoa_den_khi_chon_tep_roi_ghi_thu_muc(mo, tmp_path):
    page, loi, tai_ve = mo("A")
    assert page.locator("#cb-nap5-ai").is_disabled()
    lop = _csv(tmp_path / "lop.csv", ["student_id", "class_id"], [["s1", "10A1"], ["s2", "10A1"], ["s9", "10A2"]])
    page.locator("#cb-nap5-lop").set_input_files(lop)
    page.wait_for_function("() => !document.querySelector('#cb-nap5-ai').disabled")
    page.locator("#cb-nap5-ai").click()
    page.wait_for_selector("#cb-nap5-ai-kq")
    thu_muc = tai_ve / "chua_dang_ky"
    assert sorted(os.listdir(thu_muc)) == ["chua_dang_ky_10A2.csv", "tong_hop.csv"]
    assert [r["student_id"] for r in csv.DictReader(open(thu_muc / "chua_dang_ky_10A2.csv", encoding="utf-8-sig"))] == ["s9"]
    assert "2 lớp" in page.locator("#cb-nap5-ai-kq").inner_text()
    assert not loi, loi


def test_nut_doi_chieu_chi_o_duong_a_va_ghi_bao_cao(mo, tmp_path):
    page, loi, tai_ve = mo("A", co_xep=False)
    assert page.locator("#cb-nap5-dc").is_disabled()
    dau = ["Email", "HoTen", "Thu", "NV1", "NV2", "Lop", "CoSo"]
    cu = _csv(tmp_path / "cu.csv", dau, [["a@x.vn", "A", "thu_2", "clb_covua", "clb_vanhoc", "10A1", "CS1"],
                                         ["b@x.vn", "B", "thu_2", "clb_covua", "", "10A2", "CS1"]])
    moi = _csv(tmp_path / "moi.csv", dau, [["a@x.vn", "A", "thu_2", "clb_vanhoc", "clb_covua", "10A1", "CS1"],
                                           ["c@x.vn", "C", "thu_2", "clb_covua", "", "10A3", "CS1"]])
    page.locator("#cb-nap5-cu").set_input_files(cu)
    page.wait_for_timeout(300)
    assert page.locator("#cb-nap5-dc").is_disabled()                 # mới có một tệp
    page.locator("#cb-nap5-moi").set_input_files(moi)
    page.wait_for_function("() => !document.querySelector('#cb-nap5-dc').disabled")
    page.locator("#cb-nap5-dc").click()
    page.wait_for_selector("#cb-nap5-dc-kq")
    kq = page.locator("#cb-nap5-dc-kq").inner_text()
    assert "1 học sinh mới, 1 học sinh rút, 1 dòng đổi nguyện vọng" in kq and "DOI_CHIEU_LIST.xlsx" in kq
    assert os.listdir(tai_ve) == ["DOI_CHIEU_LIST.xlsx"]
    assert not loi, loi


def test_duong_b_khong_co_nut_doi_chieu_nhung_co_hai_nut_kia(mo):
    page, loi, _ = mo("B", co_xep=False)
    assert page.locator("#cb-nap5-dc").count() == 0 and page.locator("#cb-nap5-cu").count() == 0
    assert page.locator("#cb-nap5-xuat").count() == 1 and page.locator("#cb-nap5-ai").count() == 1
    assert not loi, loi
