"""Chụp ảnh giao diện THẬT của phần mềm cho poster.

    python poster/chup_giao_dien.py

Dựng CSDL demo BẢN CŨ (`tao_db_demo.py --tat-wharton`: DỮ LIỆU MÔ PHỎNG,
120 học sinh, 10 CLB, bộ ba TEST, Wharton tắt, đã chấm điểm) vào thư mục tạm
rồi chạy sắp xếp với seed 42 — tệp .db trong kho không bị đụng. Ảnh ra ở
poster/hinh/.

VÌ SAO BẢN CŨ: ảnh nằm trên poster cạnh các con số đã công bố (đo trên bộ ba
TEST, Wharton tắt). Chụp bản có điểm quyết tâm thì ảnh và số liệu lệch nhau.
"""

import glob
import os
import shutil
import sys
import tempfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)

from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from api import PipelineAPI  # noqa: E402

RA = os.path.join(GOC, "poster", "hinh")


def chromium():
    for c in ["/opt/pw-browsers/chromium"] + sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")):
        if os.path.isfile(c):
            return c
    return None


def main():
    os.makedirs(RA, exist_ok=True)
    tam = tempfile.mkdtemp()
    os.environ["RBDA_THU_MUC_TAI_VE"] = tam
    db = os.path.join(tam, "app.db")
    sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
    import tao_db_demo
    tao_db_demo.main(["--tat-wharton", "--ra", db])
    api = PipelineAPI(db)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)

    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
        page = br.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(RA, "giao_dien_van_hanh.png"))

        page.locator('[data-tab="results"]').click()
        page.wait_for_timeout(1200)
        page.screenshot(path=os.path.join(RA, "giao_dien_ket_qua.png"))

        page.locator('[data-tab="scoring"]').click()
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(RA, "giao_dien_cham_diem.png"))
        br.close()
    shutil.rmtree(tam, ignore_errors=True)
    print("Đã chụp vào", RA)


if __name__ == "__main__":
    main()
