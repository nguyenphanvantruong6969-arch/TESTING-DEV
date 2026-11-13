"""FA-D7L (Playwright + Chromium): ô "Ghi điểm lẻ đến 0,1" ở bước 4 "Nạp kết quả từ biểu mẫu".

  * mặc định không tick; tick -> lưu `rules.fa_diem_le` = true, kèm dòng hướng dẫn; mở lại thẻ vẫn tick;
  * bỏ tick -> false.
Dữ liệu MÔ PHỎNG.
"""
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

import cau_hinh_ws as ch  # noqa: E402
from test_fa_m9_thuan import _bo, _de_3_de  # noqa: E402
from test_giao_dien_fa_m9_nap import mo  # noqa: E402,F401


def _co(api):
    return ch.doc_cau_hinh(api.db_path, nghiem=True)["rules"]["fa_diem_le"]


def test_tick_diem_le_luu_co_va_nho_khi_mo_lai(mo, api, tmp_path):  # noqa: F811 (fixture nhập từ test_giao_dien_fa_m9_nap)
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    page, loi = mo("A", de, sn)
    page.locator("#cb-nap-tep").set_input_files([lst, thi])
    page.wait_for_selector("#cb-nap-diem-le")
    assert not page.locator("#cb-nap-diem-le").is_checked() and _co(api) is False
    assert "vẫn xét như điểm làm tròn" in page.locator("#cb-buoc-4").inner_text()
    page.locator("#cb-nap-diem-le").check()
    for _ in range(50):
        if _co(api) is True:
            break
        page.wait_for_timeout(100)
    assert _co(api) is True
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="chuan_bi"]').click()
    page.wait_for_selector("#cb-nap-diem-le")
    assert page.locator("#cb-nap-diem-le").is_checked()
    page.locator("#cb-nap-diem-le").uncheck()
    for _ in range(50):
        if _co(api) is False:
            break
        page.wait_for_timeout(100)
    assert _co(api) is False
    assert not loi, loi
