"""SG-9 (Playwright + Chromium): MỘT hàm cho mọi lần gọi API bằng nút — khoá nút + "Đang…", lỗi -> thông báo,
`finally` mở lại nút; bấm đúp chỉ gọi API MỘT lần. Mỗi trong 5 tệp js/05, 10, 11, 12, 13 có ít nhất một nút được thử.
Dữ liệu MÔ PHỎNG.

Cách đo: bọc `window.pywebview.api` trong trang: hàm của nút NÉM LỖI (đường lỗi thật của wrapper, không đi qua
`{ok:false}`) hoặc TREO mãi (để quan sát nút khi API còn đang chạy) và đếm số lần gọi.
"""
import csv
import json
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import forms_dot  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_fa_ly_do import _dung as _dung_ql  # noqa: E402
from test_fa_m6b_sau_ket_qua import _dung as _dung_theo_doi  # noqa: E402
from test_fa_m9_thuan import _de_3_de  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _chuan_bi(api, co_xep=False):
    if co_xep:
        _dung_ql(api)
        assert api.run_pipeline(seed=9)["ok"]
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
    assert api.dat_fa_duong("B")["ok"]
    with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
        json.dump(_de_3_de(), f, ensure_ascii=False)
    with open(forms_dot.duong_email_ma_hs(api.db_path), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "student_id"])
        w.writerows([["%s@x.vn" % s, s] for s in ("s1", "s2", "s3")])


def _dien_clb(page):
    page.fill("#clubFormId", "ZZ")
    page.fill("#clubFormName", "CLB thử")
    page.fill("#clubFormCapacity", "5")


# (tệp, thẻ, chờ, nút, tên API, dựng dữ liệu, việc làm trước khi bấm)
CAC_NUT = [
    ("05_quan_ly", '[data-tab="admin"]', "#adminClubTableBody tr", "btnSaveClub", "create_or_update_club",
     _dung_ql, _dien_clb),
    ("10_theo_doi", '[data-tab="others"]', "#phanHoiTongPanel:not([hidden])", "btnGuiKhieuNai", "gui_khieu_nai",
     _dung_theo_doi, None),
    ("11_chuan_bi", '.nav-item[data-tab="chuan_bi"]', "#cb-b2-tai-mau", "cb-b2-tai-mau", "tai_mau_de_thi",
     _chuan_bi, None),
    ("12_chuan_bi_nap", '.nav-item[data-tab="chuan_bi"]', "#cb-nap5-xuat", "cb-nap5-xuat", "xuat_ket_qua_list",
     lambda api: _chuan_bi(api, co_xep=True), None),
    ("13_chuan_bi_bo", '.nav-item[data-tab="chuan_bi"]', "#cb-bo-tao", "cb-bo-tao", "tao_bo_bieu_mau_api",
     _chuan_bi, None),
]
MA_NUT = [x[0] for x in CAC_NUT]


@pytest.fixture
def mo(api, tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []
    tai_ve = tmp_path / "tai_ve"
    tai_ve.mkdir()
    api.thu_muc_xuat = str(tai_ve)

    def _mo(x):
        _, the, cho, _nut, _api, dung, _truoc = x
        dung(api)
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
        if "chuan_bi" in the:
            page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
        page.locator(the).click()
        page.wait_for_selector(cho, state="attached")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _thay_api(page, ten, che_do):
    """Bọc api[ten]: che_do 'nem' -> ném lỗi ngay; 'treo' -> Promise không bao giờ xong. Đếm số lần gọi."""
    page.evaluate(
        """([ten, cheDo]) => {
          window.__goi = 0;
          const goc = window.pywebview.api;
          window.pywebview = { api: new Proxy({}, {
            has: () => true,
            get: (_t, n) => (n === ten
              ? function () {
                  window.__goi += 1;
                  if (cheDo === "nem") throw new Error("API hong");
                  return new Promise(() => {});
                }
              : goc[n]),
          }) };
        }""", [ten, che_do])


def _dem_unhandled(page):
    page.evaluate("() => { window.__unh = 0; window.addEventListener('unhandledrejection', () => { window.__unh += 1; }); }")


def _bam(page, nut):
    """Bấm bằng JS để thử cả khi nút ẩn dưới khung khác; nút đang khoá thì `.click()` của trình duyệt bị bỏ qua."""
    page.evaluate("id => document.getElementById(id).click()", nut)


@pytest.mark.parametrize("x", CAC_NUT, ids=MA_NUT)
def test_api_loi_nut_mo_lai_va_co_thong_bao_loi(mo, x):
    _, _, _, nut, ten_api, _, truoc = x
    page, loi = mo(x)
    if truoc:
        truoc(page)
    chu_goc = page.locator("#" + nut).inner_text()
    _dem_unhandled(page)
    _thay_api(page, ten_api, "nem")
    _bam(page, nut)
    page.wait_for_selector("#toastStack .toast")
    page.wait_for_timeout(300)
    assert page.locator("#toastStack .toast.is-error").count() == 1        # ĐÚNG MỘT thông báo lỗi
    # `.catch` của chayNut bắt lỗi: không có promise bị từ chối nào lọt tới trang (nếu bỏ `.catch` thì =1)
    assert page.evaluate("() => window.__unh") == 0
    assert page.evaluate("() => window.__goi") == 1
    assert page.locator("#" + nut).is_enabled()                            # nút được mở lại
    assert page.locator("#" + nut).inner_text() == chu_goc                 # nhãn được trả lại
    loi_trang = [e for e in loi if "API hong" not in e]
    assert not loi_trang, loi_trang


def test_chay_tai_bat_loi_mot_thong_bao_khong_unhandled(mo):
    page, loi = mo(CAC_NUT[2])
    _dem_unhandled(page)
    page.evaluate("() => { chayTai(Promise.reject(new Error('tai hong')), () => {}); }")
    page.wait_for_selector("#toastStack .toast.is-error")
    page.wait_for_timeout(300)
    assert page.locator("#toastStack .toast.is-error").count() == 1
    assert page.evaluate("() => window.__unh") == 0


def test_api_nem_loi_dong_bo_o_buoc_5_van_bam_lai_duoc(mo):
    """Cờ bận `S5.dang` được đặt TRƯỚC lời gọi: API ném đồng bộ thì cờ phải được trả (sauCung), bấm lần hai gọi lần hai."""
    x = CAC_NUT[3]
    page, loi = mo(x)
    _thay_api(page, x[4], "nem")
    _bam(page, x[3])
    page.wait_for_selector("#toastStack .toast.is-error")
    page.wait_for_function("id => !document.getElementById(id).disabled", arg=x[3])
    _bam(page, x[3])
    page.wait_for_function("() => window.__goi === 2")


def test_chuyen_va_goi_tra_co_ban_trong_sau_cung():
    with open(os.path.join(GOC, "js/12_chuan_bi_nap.js"), encoding="utf-8") as f:
        ma = f.read()
    assert "sauCung: () => { S.dang = false; }" in ma and 'sauCung: () => { S5.dang = ""; }' in ma


@pytest.mark.parametrize("x", CAC_NUT, ids=MA_NUT)
def test_bam_dup_chi_goi_api_mot_lan_va_hien_dang_xu_ly(mo, x):
    _, _, _, nut, ten_api, _, truoc = x
    page, loi = mo(x)
    if truoc:
        truoc(page)
    chu_goc = page.locator("#" + nut).inner_text()
    _thay_api(page, ten_api, "treo")
    _bam(page, nut)
    _bam(page, nut)
    page.locator("#" + nut).click(force=True)
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__goi") == 1
    assert page.locator("#" + nut).is_disabled()
    ban = page.locator("#" + nut).inner_text()
    assert re.search("Đang", ban) and ban != chu_goc
    assert not loi, loi


# ---------- tĩnh: không còn `.then(` trần trong 5 tệp ----------
CAC_TEP_JS = ["js/05_quan_ly.js", "js/10_theo_doi.js", "js/11_chuan_bi.js", "js/12_chuan_bi_nap.js",
              "js/13_chuan_bi_bo.js"]
# Danh sách ngoại lệ có giải thích (tệp, đoạn mã). Hiện RỖNG: mọi chỗ đi qua chayTai / chayNut.
NGOAI_LE = []


def _bo_chu_thich_va_chuoi(ma):
    ma = re.sub(r"/\*.*?\*/", "", ma, flags=re.S)
    ma = re.sub(r"//[^\n]*", "", ma)
    return re.sub(r'"(?:\\.|[^"\\\n])*"', '""', ma)


@pytest.mark.parametrize("tep", CAC_TEP_JS)
def test_khong_con_then_tran(tep):
    with open(os.path.join(GOC, tep), encoding="utf-8") as f:
        ma = _bo_chu_thich_va_chuoi(f.read())
    for m in re.finditer(r"\.then\(", ma):
        doan = ma[max(0, m.start() - 60):m.start() + 60].replace("\n", " ")
        assert any(tep == t and e in doan for t, e in NGOAI_LE), "`.then(` trần trong %s: ...%s..." % (tep, doan)


def test_chay_tai_chay_nut_o_00_nen_va_nap_tep_dung_chung():
    with open(os.path.join(GOC, "js/00_nen.js"), encoding="utf-8") as f:
        nen = f.read()
    assert "function chayNut(" in nen and "function chayTai(" in nen
    with open(os.path.join(GOC, "js/10_theo_doi.js"), encoding="utf-8") as f:
        td = f.read()
    than = td[td.index("function napTepForms("):td.index("function khoiTaoPhanHoi(")]
    assert "chayNut(" in than and "FileReader" in than and ".finally(" not in than
