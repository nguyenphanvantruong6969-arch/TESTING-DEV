# -*- coding: utf-8 -*-
"""Nhóm 5 — Giao diện dưới tải (Chromium thật, qua browser_host). CHỈ ĐO. Dữ liệu MÔ PHỎNG.

    RBDA_TEST_CHROMIUM=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome | head -1) \
        python du_lieu_test/stress/s5_giao_dien.py [--nhanh] [--em N --clb M --buoi B]

Mặc định 5.000 em × 100 CLB, 1 buổi, Điểm quyết tâm bật, đã chạy xếp. `--nhanh`: 800 × 20 và 20 vòng
đổi tab / ngôn ngữ. Mỗi phép đo lặp 3 lần (trung vị / lớn nhất). Bộ nhớ: `performance.memory`
(Chromium bật --enable-precise-memory-info, gọi gc() trước khi đọc). Lỗi console / pageerror được gom.
"""

import argparse
import glob
import os
import statistics
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

CHROMIUM = os.environ.get("RBDA_TEST_CHROMIUM") or (
    (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux64/chrome") or [None])[0])

RAF2 = "() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))"


def heap(page):
    return page.evaluate("""() => { if (window.gc) window.gc();
        const m = performance.memory; return [m.usedJSHeapSize, document.getElementsByTagName('*').length]; }""")


def do_ms(page, hanh_dong, dieu_kien, lan=3, truoc=None):
    """Đo thời gian từ lúc thao tác tới khi `dieu_kien` (JS) đúng và đã vẽ xong hai khung hình."""
    xs = []
    for _ in range(lan):
        if truoc:
            truoc()
        t = time.perf_counter()
        hanh_dong()
        page.wait_for_function(dieu_kien, timeout=120000)
        page.evaluate(RAF2)
        xs.append((time.perf_counter() - t) * 1000)
    return {"trung_vi_ms": round(statistics.median(xs), 1), "lon_nhat_ms": round(max(xs), 1), "n": lan}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    ap.add_argument("--em", type=int, default=0)
    ap.add_argument("--clb", type=int, default=0)
    ap.add_argument("--buoi", type=int, default=1)
    ap.add_argument("--vong", type=int, default=0)
    a = ap.parse_args()
    if not CHROMIUM:
        print("Không tìm thấy Chromium (đặt RBDA_TEST_CHROMIUM).")
        sys.exit(2)
    n_hs = a.em or (800 if a.nhanh else 5000)
    n_clb = a.clb or (20 if a.nhanh else 100)
    vong = a.vong or (20 if a.nhanh else 100)

    thu_muc = tempfile.mkdtemp(prefix="s5_")
    t0 = time.perf_counter()
    p, _clb, _hs = c.sinh_bo(n_hs, n_clb, a.buoi, 5005, True, thu_muc)
    api = c.tao_api(thu_muc, True)
    r = c.nap_so(api, p)
    assert r["ok"], r["errors"]
    r = api.run_pipeline(42)
    assert r["ok"], r["errors"]
    print("Dựng dữ liệu + nạp + chạy xếp: %.1f s" % (time.perf_counter() - t0), flush=True)

    url = browser_host.serve(api, c.GOC, "index.html", open_browser=False)
    kq = {"em": n_hs, "clb": n_clb, "buoi": a.buoi, "may_do": c.may_do()}
    loi_console, loi_trang = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=[
            "--no-sandbox", "--enable-precise-memory-info", "--js-flags=--expose-gc"])
        page = br.new_page(locale="vi-VN", viewport={"width": 1366, "height": 900}, bypass_csp=True)
        page.set_default_timeout(120000)
        page.on("pageerror", lambda e: loi_trang.append(str(e)[:300]))
        page.on("console", lambda m: loi_console.append(m.text[:300]) if m.type == "error" else None)
        page.add_init_script("""window.__longtask = []; try { new PerformanceObserver(l => {
            for (const e of l.getEntries()) window.__longtask.push(Math.round(e.duration)); })
            .observe({entryTypes: ['longtask']}); } catch (e) {}""")

        t = time.perf_counter()
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.evaluate(RAF2)
        kq["tai_trang_ms"] = round((time.perf_counter() - t) * 1000, 1)
        kq["heap_dau"] = heap(page)

        nav = lambda ten: page.locator('[data-tab="%s"]' % ten).click()   # noqa: E731
        ql = lambda ten: page.locator('#qlTabs [data-ql-tab="%s"]' % ten).click()   # noqa: E731
        do = {}

        # --- Quản lý: danh sách học sinh
        nav("admin")
        page.wait_for_selector("#btnResetAll", state="attached")
        do["ql_clb_tab_dau"] = do_ms(
            page, lambda: (nav("pipeline"), nav("admin"), ql("clb")),
            "() => document.querySelectorAll('#adminClubTableBody tr').length > 0")
        do["ql_hoc_sinh_trang_dau"] = do_ms(
            page, lambda: (ql("clb"), ql("hs")),
            "() => document.querySelectorAll('#adminStudentTableBody tr').length > 0")
        so_dong = page.evaluate("() => document.querySelectorAll('#adminStudentTableBody tr').length")
        nhan = page.locator("#adminPaginationLabel").inner_text()
        # Lật HẾT các trang (cuộn hết danh sách phân trang)
        ms_trang, so_trang = [], 0
        t_tong = time.perf_counter()
        while page.locator("#btnAdminNextPage").is_enabled() and so_trang < 2000:
            cu = page.locator("#adminPaginationLabel").inner_text()
            tt = time.perf_counter()
            page.locator("#btnAdminNextPage").click()
            page.wait_for_function("(cu) => document.getElementById('adminPaginationLabel').textContent !== cu", arg=cu)
            page.evaluate(RAF2)
            ms_trang.append((time.perf_counter() - tt) * 1000)
            so_trang += 1
            if so_trang >= (10 if a.nhanh else 10000) and False:
                break
        kq["lat_het_trang"] = {"so_trang_da_lat": so_trang, "tong_s": round(time.perf_counter() - t_tong, 2),
                               "moi_trang_trung_vi_ms": round(statistics.median(ms_trang), 1) if ms_trang else None,
                               "moi_trang_lon_nhat_ms": round(max(ms_trang), 1) if ms_trang else None,
                               "dong_moi_trang": so_dong, "nhan_trang_dau": nhan}
        # Tìm / lọc
        o_tim = page.locator("#adminStudentSearch")
        for ten, chuoi in (("tim_ma", "HS100"), ("tim_ten", "Nguyễn"), ("tim_khong_co", "zzzzzz")):
            o_tim.fill("")
            page.evaluate(RAF2)
            xs = []
            for _ in range(3):
                o_tim.fill("")
                page.wait_for_timeout(1000)
                cu = page.locator("#adminPaginationLabel").inner_text()
                tt = time.perf_counter()
                o_tim.fill(chuoi)
                try:
                    page.wait_for_function(
                        "(cu) => document.getElementById('adminPaginationLabel').textContent !== cu || "
                        "!document.getElementById('adminStudentEmptyState').hidden", arg=cu,
                        timeout=20000)
                except Exception:
                    pass
                page.evaluate(RAF2)
                xs.append((time.perf_counter() - tt) * 1000)
            do[ten] = {"trung_vi_ms": round(statistics.median(xs), 1), "lon_nhat_ms": round(max(xs), 1), "n": 3,
                       "ghi_chu": "gồm thời gian chờ trễ gõ của giao diện (nếu có)"}
        o_tim.fill("")
        page.wait_for_timeout(800)

        # --- 5 tab con của Quản lý
        for ten, sel in (("clb", "#adminClubTableBody tr"), ("hs", "#adminStudentTableBody tr"),
                         ("wh", "#whQlBody tr"), ("dc", "#dcQlTongQuan *"), ("du_lieu", "#taiBuoiBody tr, #qlPanelDuLieu *")):
            ten_panel = {"clb": "Clb", "hs": "Hs", "wh": "Wh", "dc": "Dc", "du_lieu": "DuLieu"}[ten]
            try:
                do["ql_tab_" + ten] = do_ms(
                    page, lambda ten=ten: (ql("clb") if ten != "clb" else ql("hs"), ql(ten)),
                    "() => { const p = document.querySelector('#qlPanel%s'); return p && !p.hidden && "
                    "document.querySelectorAll(%r).length > 0; }" % (ten_panel, sel))
            except Exception as e:
                do["ql_tab_" + ten] = {"loi": repr(e)[:200]}

        # --- Điểm chuẩn + biểu đồ
        try:
            ql("dc")
            page.wait_for_selector("#dcChonClb option", state="attached")
            ds_opt = page.eval_on_selector_all("#dcChonClb option", "els => els.map(e => e.value)")
            kq["dc_so_clb_trong_hop_chon"] = len(ds_opt)
            idx = [0]

            def doi_clb():
                idx[0] = (idx[0] + 1) % max(2, len(ds_opt))
                page.select_option("#dcChonClb", ds_opt[idx[0]])
            do["diem_chuan_chi_tiet_1_clb"] = do_ms(
                page, doi_clb,
                "() => !document.getElementById('dcChiTiet').hidden && "
                "document.querySelectorAll('#dcCot svg, #dcCot canvas, #dcCot *').length > 0")
        except Exception as e:
            do["diem_chuan_chi_tiet_1_clb"] = {"loi": repr(e)[:200]}

        # --- Kết quả
        try:
            do["tab_ket_qua"] = do_ms(
                page, lambda: (nav("pipeline"), nav("results")),
                "() => document.querySelectorAll('#resultsTableBody tr').length > 0")
            n_kq = page.evaluate("() => document.querySelectorAll('#resultsTableBody tr').length")
            kq["ket_qua_so_dong_ve"] = n_kq
            tt = time.perf_counter()
            page.evaluate("""async () => { const el = document.scrollingElement; let h = -1;
                while (el.scrollTop + el.clientHeight < el.scrollHeight - 2 && h !== el.scrollTop) {
                  h = el.scrollTop; el.scrollTop += 2000; await new Promise(r => requestAnimationFrame(r)); } }""")
            kq["ket_qua_cuon_het_ms"] = round((time.perf_counter() - tt) * 1000, 1)
        except Exception as e:
            do["tab_ket_qua"] = {"loi": repr(e)[:200]}

        kq["do"] = do
        # --- Đổi tab và đổi ngôn ngữ lặp
        heap_truoc = heap(page)
        tt = time.perf_counter()
        cac_tab = ["pipeline", "results", "admin", "scoring", "fallback"]
        mem_mau = []
        for i in range(vong):
            nav(cac_tab[i % len(cac_tab)])
            page.locator("#btnLangToggle").click()
            if i % 10 == 9:
                page.evaluate(RAF2)
                mem_mau.append(heap(page))
        page.evaluate(RAF2)
        kq["doi_tab_ngon_ngu"] = {"so_vong": vong, "tong_s": round(time.perf_counter() - tt, 2),
                                  "moi_vong_ms": round((time.perf_counter() - tt) * 1000 / vong, 1)}
        heap_sau = heap(page)
        kq["heap"] = {"dau_trang": kq["heap_dau"], "truoc_vong_lap": heap_truoc, "sau_vong_lap": heap_sau,
                      "mau_moi_10_vong": mem_mau,
                      "tang_heap_mb": round((heap_sau[0] - heap_truoc[0]) / 1048576, 2),
                      "tang_node_dom": heap_sau[1] - heap_truoc[1]}
        lt = page.evaluate("() => window.__longtask || []")
        kq["tac_vu_dai_ms"] = {"so": len(lt), "lon_nhat": max(lt) if lt else 0,
                               "tong": sum(lt) if lt else 0}
        kq["loi_console"] = loi_console[:10]
        kq["so_loi_console"] = len(loi_console)
        kq["loi_trang"] = loi_trang[:10]
        kq["so_loi_trang"] = len(loi_trang)
        br.close()

    c.in_bang("Nhóm 5 — thời gian (ms): trung vị / lớn nhất", ["phép đo", "trung vị", "lớn nhất"],
              [[k, v.get("trung_vi_ms", "-"), v.get("lon_nhat_ms", v.get("loi", "-"))] for k, v in kq["do"].items()])
    for k in ("tai_trang_ms", "ket_qua_so_dong_ve", "ket_qua_cuon_het_ms", "lat_het_trang", "doi_tab_ngon_ngu", "heap",
              "tac_vu_dai_ms", "so_loi_console", "so_loi_trang", "loi_console", "loi_trang"):
        print("%s: %s" % (k, kq.get(k)))
    print("\nGhi:", c.ghi_json("s5_giao_dien_nhanh" if a.nhanh else "s5_giao_dien", kq))
    c.xoa(thu_muc)


if __name__ == "__main__":
    main()
