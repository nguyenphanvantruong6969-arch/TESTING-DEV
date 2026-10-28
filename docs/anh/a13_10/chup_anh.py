"""Chụp ảnh màn Quản lý, Điểm chuẩn (A13.10). Dữ liệu MÔ PHỎNG.

    RBDA_TEST_CHROMIUM=... .venv/bin/python docs/anh/a13_10/chup_anh.py truoc|sau

Nạp du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx vào workspace tạm, bật điểm quyết tâm, chạy xếp
(seed 3), rồi chụp khối Điểm chuẩn ở tiếng Việt và tiếng Anh, sáng và tối.
"""
import base64
import glob
import os
import sys
import tempfile

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path[:0] = [GOC, os.path.join(GOC, "tests")]

from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton  # noqa: E402
from api import PipelineAPI  # noqa: E402

DAU = sys.argv[1] if len(sys.argv) > 1 else "truoc"
RA = os.path.dirname(os.path.abspath(__file__))
CHROMIUM = os.environ.get("RBDA_TEST_CHROMIUM") or sorted(
    glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))[-1]


def main():
    tam = tempfile.mkdtemp()
    api = PipelineAPI(os.path.join(tam, "app.db"))
    bat_wharton(api)
    with open(os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx"), "rb") as f:
        nap = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert nap["ok"], nap
    assert api.run_pipeline(seed=3)["ok"]
    hang = api.get_diem_chuan()["data"]["rows"]
    chon = max(hang, key=lambda r: r["so_don"] / max(1, r["suc_chua"]))["club_id"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        # Một trang duy nhất: máy chủ dự phòng tự tắt khi trang cuối đóng.
        page = br.new_page(viewport={"width": 1280, "height": 1000}, bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.locator('#qlTabs [data-ql-tab="dc"]').click()
        page.wait_for_selector("#adminDiemChuanBlock:not([hidden]) #dcQlTongQuan table")
        page.locator("#dcChonClb").select_option(chon)
        page.wait_for_selector("#dcChiTiet:not([hidden]) svg")
        for ngon in ("vi", "en"):
            for che_do in ("sang", "toi"):
                page.emulate_media(color_scheme="dark" if che_do == "toi" else "light")
                page.evaluate("window.I18N.setLang(%r)" % ngon)
                page.wait_for_timeout(700)
                page.locator("#adminDiemChuanBlock").screenshot(
                    path=os.path.join(RA, "%s_%s_%s.png" % (DAU, ngon, che_do)))
        page.close()
        br.close()


main()
