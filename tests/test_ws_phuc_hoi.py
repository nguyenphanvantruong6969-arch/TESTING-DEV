"""Màn phục hồi khi lúc khởi động KHÔNG workspace nào mở được (main.main -> recovery.html).

Chạy `main.main()` thật (chỉ thay `_show_ui` để bắt trang và `js_api` được chọn), rồi:
  * kiểm màn phục hồi trỏ ĐÚNG tệp hỏng trong thư mục workspace (không phải `app.db` cạnh chương
    trình đã được di trú đi);
  * khôi phục từ bản sao lưu nằm cạnh tệp đó, bằng API và bằng bấm nút trong Chromium thật.
"""

import os
import sys

import pytest

import workspace as ws
from api import PipelineAPI
from recovery import RecoveryAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAK = ".bak-20260101_000000_000000"


@pytest.fixture
def main_mod(tmp_path, monkeypatch):
    import main
    g = tmp_path / "goc_main"
    g.mkdir()
    monkeypatch.setattr(main, "BASE_DIR", str(g))
    monkeypatch.setattr(sys, "argv", ["main.py"])
    return main


def _bat_man_hinh(main_mod, monkeypatch):
    """Thay `_show_ui` để lấy (trang, js_api) mà main() định mở."""
    da_mo = []
    monkeypatch.setattr(main_mod, "_show_ui",
                        lambda title, page, js_api, *a, **k: da_mo.append((page, js_api)))
    return da_mo


def _workspace_hong_co_sao_luu(root):
    """Một workspace có dữ liệu, một bản sao lưu lành, rồi app.db bị phá hỏng."""
    slug = ws.tao(root, "Trường A")
    db = ws.duong_dan_db(root, slug)
    api = PipelineAPI(db, thu_muc_goc_ws=root)
    assert api.create_or_update_club("clb1", "Cờ vua", 5, 0, "")["ok"]
    ws._chep_db(db, db + BAK)
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite " * 200)
    return db


def _clb(db):
    import sqlite3
    conn = sqlite3.connect(db)
    try:
        return [r[0] for r in conn.execute("SELECT club_id FROM clubs")]
    finally:
        conn.close()


def test_moi_workspace_hong_main_mo_man_phuc_hoi_dung_tep(main_mod, monkeypatch):
    db = _workspace_hong_co_sao_luu(main_mod.BASE_DIR)
    da_mo = _bat_man_hinh(main_mod, monkeypatch)
    main_mod.main()
    assert len(da_mo) == 1
    trang, rec = da_mo[0]
    assert trang == "recovery.html" and isinstance(rec, RecoveryAPI)
    assert os.path.realpath(rec.db_path) == os.path.realpath(db)
    # tệp hỏng nằm trong workspace nên bản sao lưu cạnh nó được thấy
    assert [b["name"] for b in rec.get_status()["data"]["backups"]] == ["app.db" + BAK]
    # và không đẻ ra app.db mồ côi cạnh chương trình
    assert not os.path.exists(os.path.join(main_mod.BASE_DIR, "app.db"))


def test_khoi_phuc_bang_api_dua_workspace_ve_dung_du_lieu(main_mod, monkeypatch):
    db = _workspace_hong_co_sao_luu(main_mod.BASE_DIR)
    da_mo = _bat_man_hinh(main_mod, monkeypatch)
    main_mod.main()
    _, rec = da_mo[0]
    res = rec.restore_from_backup()
    assert res["ok"], res
    assert _clb(db) == ["clb1"]
    # lần khởi động sau mở bình thường, vào giao diện chính
    da_mo.clear()
    main_mod.main()
    assert da_mo[0][0] == "index.html"


def test_loi_khoi_dong_khong_neu_tep_thi_dung_workspace_gan_nhat_khong_dung_app_db_cu(
        main_mod, monkeypatch):
    root = main_mod.BASE_DIR
    slug = ws.tao(root, "Còn đó")
    db = ws.duong_dan_db(root, slug)
    assert not os.path.exists(os.path.join(root, "app.db"))       # đã di trú từ lâu

    def hong(*a, **k):
        raise RuntimeError("lỗi không nêu tệp")
    monkeypatch.setattr(main_mod, "khoi_dong_workspace", hong)
    da_mo = _bat_man_hinh(main_mod, monkeypatch)
    main_mod.main()
    trang, rec = da_mo[0]
    assert trang == "recovery.html"
    assert os.path.realpath(rec.db_path) == os.path.realpath(db)


def test_loi_khoi_dong_khi_app_db_cu_con_thi_van_dung_app_db_cu(main_mod, monkeypatch):
    cu = os.path.join(main_mod.BASE_DIR, "app.db")
    open(cu, "wb").write(b"x")

    def hong(*a, **k):
        raise RuntimeError("lỗi không nêu tệp")
    monkeypatch.setattr(main_mod, "khoi_dong_workspace", hong)
    da_mo = _bat_man_hinh(main_mod, monkeypatch)
    main_mod.main()
    assert da_mo[0][1].db_path == cu


# ------------------------------------------------------------------ Chromium thật

pw = pytest.importorskip("playwright.sync_api", reason="chưa cài playwright")

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402


def test_man_phuc_hoi_trong_trinh_duyet_liet_ke_sao_luu_va_khoi_phuc_workspace_hong(
        main_mod, monkeypatch):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    db = _workspace_hong_co_sao_luu(main_mod.BASE_DIR)
    da_mo = _bat_man_hinh(main_mod, monkeypatch)
    main_mod.main()
    _, rec = da_mo[0]
    url = browser_host.serve(rec, GOC, "recovery.html", open_browser=False)

    with pw.sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        try:
            page = br.new_page(bypass_csp=True)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("body[data-app-init='1']")
            page.wait_for_timeout(300)
            assert page.locator("#btnRestoreBackup").is_visible()
            assert "app.db" + BAK in page.locator("#backupsTableBody").inner_text()
            assert page.locator("#initErrorDetail").text_content().strip()
            page.locator("#btnRestoreBackup").click()
            page.wait_for_function(
                "document.querySelector('#recoveryStatus').textContent.trim() !== ''",
                timeout=10000)
            assert loi == []
        finally:
            br.close()
    assert _clb(db) == ["clb1"]
