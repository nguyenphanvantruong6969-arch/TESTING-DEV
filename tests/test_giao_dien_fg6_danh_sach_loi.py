"""FG-6 (STEP0, spec §3), phần giao diện (Playwright + Chromium): thông báo nạp tệp Forms là MỘT câu; khung dưới nút
hiện danh sách `<ul>` theo lý do, có mã không khớp; bước "Kiểm tra dữ liệu" gom lỗi theo mã, tối đa 5 dòng mỗi mã,
"và N lỗi nữa". Dữ liệu MÔ PHỎNG; mọi việc Forms là TH.
"""
import datetime

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

import openpyxl  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
from _fa import dung_fa_clb, dung_hs_fa  # noqa: E402
from test_fa_m6b_sau_ket_qua import _dung, _hang_gop, _hs_kn, _run_at, _tl, de  # noqa: E402,F401
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import GOC, mo  # noqa: E402,F401 (fixture)


def _tep_hon_hop(tmp_path, de_, api):
    r0 = _run_at(api)
    dong = [_tl(de_, "s1", 4, 1, "huy_chuong"),
            _hs_kn(de_, api, "s2", luc=r0 + datetime.timedelta(hours=3)),
            _tl(de_, "khong_ai", 3, 1, "chon_clb"),
            _tl(de_, "ma_la_2", 3, 1, "chon_clb")]
    p = tmp_path / "hon_hop.xlsx"
    wb = openpyxl.Workbook()
    for h in _hang_gop(de_, dong):
        wb.active.append(h)
    wb.save(str(p))
    return str(p)


def test_thong_bao_mot_cau_va_khung_co_danh_sach(mo, tmp_path, de):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")
    page.set_input_files("#phTepSauKetQua", _tep_hon_hop(tmp_path, de, api))
    page.wait_for_function("() => document.querySelector('#toastStack').textContent.trim() !== ''")
    toast = page.locator("#toastStack").inner_text().strip()
    assert toast.count(".") == 1 and toast.endswith("."), toast         # MỘT câu, không tường chữ
    assert "khong_ai" not in toast                                      # mã không khớp nằm ở danh sách, không ở thông báo
    page.wait_for_selector("#phNhapKetQua ul li")
    muc = page.locator("#phNhapKetQua ul li").all_inner_texts()
    assert len(muc) >= 1
    chu = page.locator("#phNhapKetQua").inner_text()
    assert "khong_ai" in chu and "ma_la_2" in chu                       # mã không khớp được liệt kê
    assert not loi, loi


def _du_lieu_nhieu_clb_thieu_loai(api):
    """FA bật nhưng 9 CLB không có Loại: chạy xếp phải báo MỘT nhóm lỗi, không phải 9 dòng giống nhau."""
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
    dung_fa_clb(api, T=(9, "TU_DO"))
    for i in range(9):
        assert api.create_or_update_club("X%d" % i, "CLB X%d" % i, 5, 0, "", "")["ok"]
    dung_hs_fa(api, "s1", "s2", nv={"s1": ["T", "X0"], "s2": ["T", "X1"]})


@pytest.fixture
def mo_dau(api):
    """Như `mo` nhưng dừng ở thẻ Xếp CLB (chưa có kết quả nào để đợi)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    from playwright.sync_api import sync_playwright
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
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def test_buoc_kiem_tra_du_lieu_gom_loi_theo_ma(mo_dau):
    page, api, loi = mo_dau(_du_lieu_nhieu_clb_thieu_loai)
    page.locator("#btnRun").click()
    page.wait_for_selector("#logPanel:not([hidden])")
    hop = page.locator("#logBox")
    dong = hop.locator(".log-dong")
    assert dong.count() <= 7, dong.count()                              # 5 dòng của nhóm + dòng "và N lỗi nữa" + dự phòng
    assert "và 4 lỗi nữa" in hop.inner_text()
    assert not loi, loi
