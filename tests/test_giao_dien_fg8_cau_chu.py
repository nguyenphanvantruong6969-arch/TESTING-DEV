"""FG-8 (STEP0, spec §3), phần giao diện (Playwright + Chromium): dòng tóm tắt cảnh báo chỉ đỏ khi có mục nghiêm trọng;
bước 3 của trình hướng dẫn khoá bốn ô "Theo dõi sau khi xếp…" khi chưa chọn xếp theo loại CLB và ô nằm cùng dòng nhãn;
khung "Sau khi công bố kết quả" gom khiếu nại + phản hồi; ẩn nhãn "Chưa chia buổi" khi chỉ có một buổi.
Dữ liệu MÔ PHỎNG.
"""
import json

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_fa_m6b_sau_ket_qua import _buoi, _dung, de  # noqa: E402,F401
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)
from test_giao_dien_fg6_danh_sach_loi import mo_dau  # noqa: E402,F401 (fixture)
from test_ws_wharton_giao_dien import _toi_buoc_luat, mo_trang  # noqa: E402,F401 (fixture)

CAC_O_FA = ("wzFaDiemDanh", "wzFaKhieuNai", "wzFaVong2", "wzFaPhanHoi")


def _bao_cao(n_high, n_khac=1):
    ds = [{"code": "health_vi_pham_diem_am", "params": {}, "severity": "high"} for _ in range(n_high)]
    ds += [{"code": "health_scoring_none", "params": {}, "severity": "medium"} for _ in range(n_khac)]
    return {"ok": True, "data": {"warnings": ds, "n_warnings": len(ds), "n_high": n_high}, "errors": []}


@pytest.mark.parametrize("n_high,do", [(0, False), (2, True)])
def test_dong_tom_tat_chi_do_khi_co_muc_nghiem_trong(mo_dau, n_high, do):  # noqa: F811
    page, api, loi = mo_dau(_dung)
    page.route("**/__api__/get_data_health_report", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(_bao_cao(n_high))))
    page.locator("#btnValidate").click()
    page.wait_for_function("() => document.querySelector('#healthList').children.length > 0")
    lop = page.locator("#healthSummary").get_attribute("class")
    assert ("is-warn" in lop) is do, lop
    assert not loi, loi


def test_buoc_3_khoa_bon_o_khi_chua_chon_xep_theo_loai_clb(mo_trang):  # noqa: F811
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt khoá ô")
    assert not page.locator("#wzFaDaa").is_checked()
    for o in CAC_O_FA:
        assert page.locator("#" + o).is_disabled() and not page.locator("#" + o).is_checked(), o
    page.locator("#wzFaDaa").check()
    for o in CAC_O_FA:
        assert page.locator("#" + o).is_enabled(), o
    page.locator("#wzFaPhanHoi").check()
    page.locator("#wzFaDaa").uncheck()                                    # tắt FA: ô con bị khoá VÀ bỏ tick
    assert page.locator("#wzFaPhanHoi").is_disabled() and not page.locator("#wzFaPhanHoi").is_checked()
    assert not loi, loi


def test_o_tick_nam_cung_dong_voi_nhan(mo_trang):  # noqa: F811
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt cùng dòng")
    for o in ("wzFaDaa",) + CAC_O_FA:
        h_o = page.locator("#" + o).bounding_box()
        h_n = page.locator('label[for="%s"]' % o).bounding_box()
        tam = h_o["y"] + h_o["height"] / 2
        assert h_n["y"] - 2 <= tam <= h_n["y"] + h_n["height"] + 2, (o, h_o, h_n)
    assert not loi, loi


def test_tieu_de_nhom_sau_khi_cong_bo_ket_qua_gom_hai_khung(mo):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")
    ok = page.evaluate("""() => {
      const tieu = [...document.querySelectorAll('h2, h3')]
        .find((h) => h.textContent.trim() === 'Sau khi công bố kết quả');
      if (!tieu) return 'khong-co-tieu-de';
      if (tieu.offsetParent === null) return 'tieu-de-an';
      const sau = (x) => !!(tieu.compareDocumentPosition(x) & Node.DOCUMENT_POSITION_FOLLOWING);
      const kn = document.getElementById('khieuNaiPanel'), ph = document.getElementById('phanHoiTongPanel');
      if (!sau(kn) || !sau(ph)) return 'tieu-de-khong-dung-truoc-hai-khung';
      /* giữa tiêu đề nhóm và hai khung không có thẻ nào khác của thẻ Chi tiết xen vào */
      const xen = [...document.querySelectorAll('.panel')].filter((p) => p !== kn && p !== ph && sau(p)
        && !!(p.compareDocumentPosition(ph) & Node.DOCUMENT_POSITION_FOLLOWING)
        && !!(p.compareDocumentPosition(kn) & Node.DOCUMENT_POSITION_FOLLOWING));
      return xen.length ? 'xen-khung-khac:' + xen.map((p) => p.id).join(',') : 'ok';
    }""")
    assert ok == "ok", ok
    chu = page.locator("body").inner_text()
    assert "Nạp từ Forms (Excel)" in chu and "Nạp biểu mẫu Sau khi xem kết quả" in chu
    dong_goi_y = page.evaluate("""() => [...document.querySelectorAll('#phanHoiTongPanel p, #phanHoiTongPanel .hint, .hint-text')]
      .map((p) => p.textContent).filter((s) => s.includes('Nạp từ Forms') && s.includes('Nạp biểu mẫu Sau khi xem kết quả'))""")
    assert dong_goi_y, "thiếu MỘT dòng gợi ý nói nút nào dùng cho biểu mẫu cũ, nút nào cho biểu mẫu mới"
    assert not loi, loi


def test_mot_buoi_thi_an_nhan_chua_chia_buoi(mo, de):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#khieuNaiPanel:not([hidden])")
    nhan = page.evaluate("() => t('buoi_chua_chia', { session_l: 'buổi' })")
    assert nhan.startswith("Chưa chia")
    cac_nhan = page.evaluate("() => [...document.querySelectorAll('#knBuoi option')].map((o) => o.textContent)")
    assert all(not x.startswith("Chưa chia") for x in cac_nhan), cac_nhan
    assert api.gui_khieu_nai("s1", _buoi(api), "x")["ok"]
    page.reload()
    page.locator('[data-tab="others"]').click()
    page.wait_for_selector("#knDanhSach li")
    assert "Chưa chia" not in page.locator("#knDanhSach").inner_text()
    assert not loi, loi
