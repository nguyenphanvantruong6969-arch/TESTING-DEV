# ruff: noqa: F811
"""T3-L3 — giao diện (Playwright + Chromium, qua `browser_host`; dữ liệu MÔ PHỎNG).

  * Thẻ 03 đổi tên "Chi tiết và xuất tệp", thẻ 05 "Quản lý CLB" (T3-L3, quyết định của Truong);
  * T3-19: nút "Tải bảng này (Excel)" ở thẻ 02 xuất đúng lớp / CLB / danh sách đang xem, không điểm;
  * T3-11: tạo workspace từ mẫu bằng MỘT bước ("Tạo" ngay) hoặc "Tuỳ chỉnh" để vào bước 2 đến 4;
  * T3-27: chữ giao diện = chữ Sổ nhập (Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên), không còn "dự trữ".
Tái dùng fixture `mo` của test_giao_dien_a14_lop và `mo_trang` của test_ws_giao_dien."""

import glob
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from openpyxl import load_workbook  # noqa: E402

from test_giao_dien_a14_lop import api, mo  # noqa: E402,F401
from test_ws_giao_dien import mo_trang  # noqa: E402,F401

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _doc(p):
    with open(os.path.join(GOC, p), encoding="utf-8") as f:
        return f.read()


def _mo_ket_qua(page, tang1=None):
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_selector("#view-results.is-active")
    if tang1:
        page.locator('#kqTang1 [data-kq="%s"]' % tang1).click()


def _o(duong):
    ws = load_workbook(duong).active
    return [[c.value for c in r] for r in ws.iter_rows()]


def _ma_trong_tep(duong):
    return sorted(str(r[0]) for r in _o(duong) if r[0] and re.fullmatch(r"HS\d+", str(r[0])))


# ------------------------------------------------------------------ tên thẻ

def test_ten_the_03_va_05_vi_va_en(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    nhan = lambda tab: page.locator('.nav-item[data-tab="%s"]' % tab).inner_text()  # noqa: E731
    assert "Chi tiết và xuất tệp" in nhan("others") and re.sub(r"^\d+\s*", "", nhan("admin")) == "Quản lý"
    assert "dự trữ" not in nhan("admin")
    page.locator('.nav-item[data-tab="admin"]').click()
    assert page.locator("#view-admin h1").inner_text() == "Quản lý"
    page.locator('.nav-item[data-tab="others"]').click()
    assert page.locator("#view-others h1").inner_text() == "Chi tiết và xuất tệp"
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("() => /Details and export/.test(document.querySelector('#view-others h1').textContent)")
    assert page.locator('.nav-item[data-tab="admin"]').inner_text().split("\n")[-1].strip() == "Manage"
    assert not loi, loi


def test_chu_giao_dien_dung_chu_cua_so_nhap_khong_con_du_tru(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    for tab in ("admin", "others"):
        page.locator('.nav-item[data-tab="%s"]' % tab).click()
        page.wait_for_selector("#view-%s.is-active" % tab)
        chu = page.locator("#view-%s" % tab).inner_text()
        assert not re.search(r"dự trữ|Nhãn dự|Tổng chỗ", chu, re.I), (tab, re.findall(r"[^\n]*(?:dự trữ|Tổng chỗ)[^\n]*", chu, re.I))
    assert "Chỉ tiêu" in page.locator("#view-admin").inner_text()
    assert not loi, loi


def test_nguon_chu_khong_con_du_tru_o_i18n_va_index():
    for p in ("i18n.js", "index.html", "i18n_errors.py"):
        chu = _doc(p)
        assert not re.search(r"dự trữ|Dự trữ", chu), (p, re.findall(r"[^\n]*dự trữ[^\n]*", chu)[:2])


# ------------------------------------------------------------------ T3-19 tải bảng đang xem

def _bam_tai(page):
    page.locator("#btnKqTaiBang").click()
    page.wait_for_function("() => document.getElementById('kqXuatPhanHoi').textContent.trim() !== ''")
    return page.locator("#kqXuatPhanHoi").inner_text()


def test_tai_bang_theo_lop_dung_lop_dang_chon_khong_diem(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1", "HS3": "10A2"}, chay=True)
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length === 2")
    page.select_option("#kqChonLop", "10A1")
    page.wait_for_function("() => document.querySelectorAll('#kqThan tr').length === 2")
    chu = _bam_tai(page)
    assert "2 dòng" in chu, chu
    tep = glob.glob(os.path.join(api.thu_muc_xuat, "*.xlsx"))
    assert len(tep) == 1
    assert _ma_trong_tep(tep[0]) == ["HS1", "HS2"]
    tat_ca = " ".join(str(c).lower() for r in _o(tep[0]) for c in r if c)
    assert not re.search(r"điểm|bốc thăm|diện", tat_ca), tat_ca
    assert not loi, loi


def test_tai_bang_theo_clb_va_theo_ma_co_tim(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1", "HS3": "10A2"}, chay=True)
    _mo_ket_qua(page, "clb")
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb option').length === 2")
    page.select_option("#kqChonClb", "A")
    page.wait_for_function("() => !document.getElementById('kqBang').hidden")
    sl = page.evaluate("() => document.querySelectorAll('#kqThan tr').length")
    _bam_tai(page)
    tep = sorted(glob.glob(os.path.join(api.thu_muc_xuat, "*.xlsx")))
    assert len(_ma_trong_tep(tep[-1])) == sl and sl >= 1
    _mo_ket_qua(page, "ma")
    page.fill("#kqTimKiem", "HS3")
    page.wait_for_function("() => document.querySelectorAll('#kqThan tr').length === 1")
    _bam_tai(page)
    tep2 = sorted(set(glob.glob(os.path.join(api.thu_muc_xuat, "*.xlsx"))) - set(tep))
    assert len(tep2) == 1 and _ma_trong_tep(tep2[0]) == ["HS3"]
    assert not loi, loi


def test_tai_bang_theo_thu_tu_dang_sap_tren_man_hinh(mo):
    """T3-L4: bấm tiêu đề cột "Mã" để sắp giảm dần, rồi tải: tệp theo đúng thứ tự trên màn hình."""
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1", "HS3": "10A2"}, chay=True, them=("HS10",))
    _mo_ket_qua(page, "ma")
    page.wait_for_function("() => document.querySelectorAll('#kqThan tr').length === 4")
    page.locator('#kqDau .kq-sx-cot[data-cot="0"]').click()                 # cùng cột mã: đảo chiều
    page.wait_for_function("() => document.querySelector('#kqThan tr td').textContent.trim() === 'HS10'")
    man_hinh = page.locator("#kqThan tr").evaluate_all("rs => rs.map(r => r.cells[0].textContent.trim())")
    assert man_hinh == ["HS10", "HS3", "HS2", "HS1"], man_hinh
    _bam_tai(page)
    tep = glob.glob(os.path.join(api.thu_muc_xuat, "*.xlsx"))
    assert len(tep) == 1
    ma = [str(r[0]) for r in _o(tep[0]) if r[0] and re.fullmatch(r"HS\d+", str(r[0]))]
    assert ma == man_hinh, ma
    assert not loi, loi


def test_nut_tai_bang_khoa_khi_chua_co_ket_qua(mo):
    page, api, loi = mo({"HS1": "10A1"})                      # chưa chạy xếp
    _mo_ket_qua(page, "ma")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    assert page.locator("#btnKqTaiBang").is_disabled()
    assert not loi, loi


# ------------------------------------------------------------------ T3-11 workspace từ mẫu

def test_tao_workspace_tu_mau_chi_hai_cu_bam(mo_trang):
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Nhanh")
    assert page.locator("#wzTao").is_visible() and page.locator("#wzTuyChinh").is_visible()
    assert page.locator("#wzTiep").count() == 0 and page.locator(".ws-buoc").count() == 0
    page.locator("#wzTao").click()
    page.wait_for_function("() => document.querySelector('#wsTenHienTai').textContent === 'Nhanh'", timeout=10000)
    assert [w["name"] for w in api.list_workspaces()["data"]["workspaces"]].count("Nhanh") == 1
    assert not loi, loi


def test_tao_nhanh_van_bat_loi_thieu_ten(mo_trang):
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.locator("#wzTao").click()
    assert page.locator("#wzLoi").is_visible() and page.locator("#wzTen").is_visible()
    assert page.locator(".ws-buoc").count() == 0                 # vẫn ở dạng gọn, không bật tuỳ chỉnh
    page.locator("#wzTuyChinh").click()
    assert page.locator("#wzLoi").is_visible() and page.locator("#wzNhan_slot_vi").count() == 0
    assert not loi, loi


def test_tuy_chinh_mo_buoc_2_den_4_va_chi_co_buoc_xem_lai_khi_tuy_chinh(mo_trang):
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Tuỳ biến")
    page.locator("#wzTuyChinh").click()
    assert page.locator(".ws-buoc li").count() == 4
    assert re.fullmatch(r"Bước 2/4: .+", page.inner_text(".ws-buoc-ten"))
    page.fill("#wzNhan_slot_vi", "Phòng")
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    assert "Phòng" in page.locator("#rvNhan_slot").inner_text()        # bước xem lại có mặt
    page.locator("#wzTao").click()
    page.wait_for_function("() => document.querySelector('#wsTenHienTai').textContent === 'Tuỳ biến'", timeout=10000)
    assert api.get_workspace_config()["data"]["config"]["labels"]["slot"]["vi"] == "Phòng"
    assert not loi, loi


def test_buoc_xem_lai_bo_dong_nhom_thu_tu_trong(mo_trang):
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Không nhóm")
    page.locator("#wzTuyChinh").click()
    page.locator("#wzTiep").click()
    page.fill("#wzTiers", "") if page.locator("#wzTiers").is_enabled() else None
    page.locator("#wzTiep").click()
    if page.locator("#rvTiers").count():
        assert page.locator("#rvTiers").inner_text().strip() not in ("", "—")
    assert not loi, loi


def test_diem_chuan_nut_mot_dong_va_chu_giai_gon_trong_css():
    """T3-L4: "Xem chi tiết" không xuống dòng; chú giải là hàng ngang có ô mẫu (không còn danh sách gạch đầu dòng)."""
    css = _doc("style.css")
    assert re.search(r"\.dc-chi-tiet-nut\s*\{[^}]*white-space:\s*nowrap", css)
    assert re.search(r"\.dc-chu-giai\s*\{[^}]*list-style:\s*none[^}]*display:\s*flex", css)
    assert re.search(r"\.dc-mau\s*\{[^}]*display:\s*inline-block", css)
