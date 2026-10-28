# -*- coding: utf-8 -*-
"""Nhóm 6 — Chạy dài / lặp. CHỈ ĐO, không đặt ngưỡng. Dữ liệu MÔ PHỎNG.

    python du_lieu_test/stress/s6_chay_dai.py [--nhanh] [--so-lan N] [--vong M]

  A  N = 500 lần `run_pipeline(42)` liên tiếp trên 800 em × 20 CLB (3 buổi, Điểm quyết tâm bật).
     Cứ 100 lần có MỘT lần `force_redraw_stb=True` (đường vẽ lại hợp lệ của giao diện, sau xác nhận
     hai bước) để run_history có cả hai loại dòng. Ghi thời gian từng lần, cỡ app.db, số và tổng cỡ
     tệp sao lưu, số dòng run_history, bộ nhớ thường trú (RSS hiện tại, đọc /proc/self/statm).
     Kèm hệ số góc hồi quy tuyến tính thời gian theo số thứ tự lần chạy (chậm dần?).
  B  M = 100 vòng: nạp Sổ → `reset_data("hoc_sinh","XOA")` → nạp lại. Ghi thời gian, cỡ app.db,
     freelist, tệp sao lưu.
"""

import argparse
import os
import sqlite3
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402


def rss_hien_tai_mb():
    with open("/proc/self/statm") as f:
        return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 1048576.0


def hoi_quy(ys):
    n = len(ys)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0


def thong_tin_db(thu_muc):
    db = os.path.join(thu_muc, "app.db")
    k = sqlite3.connect(db)
    try:
        fl = k.execute("PRAGMA freelist_count").fetchone()[0]
        pc = k.execute("PRAGMA page_count").fetchone()[0]
    finally:
        k.close()
    d = c.kich_thuoc_db(thu_muc)
    d.update(freelist=fl, page_count=pc)
    return d


def phan_a(so_lan):
    thu_muc = tempfile.mkdtemp(prefix="s6a_")
    p, _clb, _hs = c.sinh_bo(800, 20, 3, 6006, True, thu_muc)
    api = c.tao_api(thu_muc, True)
    assert c.nap_so(api, p)["ok"]
    db = os.path.join(thu_muc, "app.db")
    giay, mau, loi = [], [], []
    for i in range(so_lan):
        ve_lai = (i % 100 == 99)
        t = time.perf_counter()
        r = api.run_pipeline(42, force_redraw_stb=ve_lai)
        giay.append(time.perf_counter() - t)
        if not r["ok"]:
            loi.append((i, [e.get("code") if isinstance(e, dict) else str(e)[:60] for e in r["errors"]][:3]))
        if i % 25 == 0 or i == so_lan - 1:
            d = thong_tin_db(thu_muc)
            d.update(lan=i + 1, rss_mb=round(rss_hien_tai_mb(), 1),
                     run_history=c.dem_bang(db, "run_history"))
            mau.append(d)
    n10 = max(1, so_lan // 10)
    out = {
        "so_lan": so_lan, "so_lan_that_bai": len(loi), "that_bai": loi[:5],
        "giay_tung_lan": [round(x, 4) for x in giay],
        "trung_vi_giay": round(sorted(giay)[len(giay) // 2], 4),
        "lon_nhat_giay": round(max(giay), 4),
        "trung_vi_10pct_dau": round(sorted(giay[:n10])[n10 // 2], 4),
        "trung_vi_10pct_cuoi": round(sorted(giay[-n10:])[n10 // 2], 4),
        "he_so_goc_giay_moi_lan": hoi_quy(giay),
        "mau": mau,
        "cuoi": thong_tin_db(thu_muc),
        "run_history_cuoi": c.dem_bang(db, "run_history"),
        "integrity": c.toan_ven(db),
    }
    c.xoa(thu_muc)
    return out


def phan_b(so_vong):
    thu_muc = tempfile.mkdtemp(prefix="s6b_")
    p, _clb, _hs = c.sinh_bo(800, 20, 3, 6007, True, thu_muc)
    api = c.tao_api(thu_muc, True)
    db = os.path.join(thu_muc, "app.db")
    nap, xoa, mau, loi = [], [], [], []
    for i in range(so_vong):
        r, d = c.thoi(c.nap_so, api, p)
        nap.append(d)
        if not r["ok"]:
            loi.append((i, "nap", str(r["errors"])[:100]))
        r, d = c.thoi(api.reset_data, "hoc_sinh", "XOA")
        xoa.append(d)
        if not r["ok"]:
            loi.append((i, "reset", str(r["errors"])[:100]))
        if i % 10 == 0 or i == so_vong - 1:
            e = thong_tin_db(thu_muc)
            e.update(vong=i + 1, rss_mb=round(rss_hien_tai_mb(), 1))
            mau.append(e)
    r, d = c.thoi(c.nap_so, api, p)           # nạp lần cuối để chắc dữ liệu còn nạp được
    ok_cuoi = r["ok"]
    out = {"so_vong": so_vong, "that_bai": loi[:5], "nap": c.tom(nap), "reset": c.tom(xoa),
           "nap_giay_tung_vong": [round(x, 3) for x in nap],
           "he_so_goc_nap_giay_moi_vong": hoi_quy(nap), "nap_cuoi_ok": ok_cuoi,
           "mau": mau, "cuoi": thong_tin_db(thu_muc),
           "so_hoc_sinh_cuoi": c.dem_bang(db, "students"), "integrity": c.toan_ven(db)}
    c.xoa(thu_muc)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    ap.add_argument("--so-lan", type=int, default=0)
    ap.add_argument("--vong", type=int, default=0)
    a = ap.parse_args()
    so_lan = a.so_lan or (50 if a.nhanh else 500)
    vong = a.vong or (10 if a.nhanh else 100)
    A = phan_a(so_lan)
    c.in_bang("Nhóm 6A — %d lần run_pipeline liên tiếp" % so_lan, ["chỉ số", "giá trị"], [
        ["thất bại", A["so_lan_that_bai"]], ["trung vị (s)", A["trung_vi_giay"]], ["lớn nhất (s)", A["lon_nhat_giay"]],
        ["trung vị 10% đầu (s)", A["trung_vi_10pct_dau"]], ["trung vị 10% cuối (s)", A["trung_vi_10pct_cuoi"]],
        ["hệ số góc (s/lần)", "%.6f" % A["he_so_goc_giay_moi_lan"]],
        ["run_history cuối", A["run_history_cuoi"]], ["cỡ cuối", A["cuoi"]], ["integrity", A["integrity"]]])
    c.in_bang("mẫu theo thời gian", ["lần", "app.db MB", "sao lưu (tệp/MB)", "run_history", "RSS MB"],
              [[m["lan"], m["app_db_mb"], "%d/%s" % (m["n_sao_luu"], m["sao_luu_mb"]), m["run_history"], m["rss_mb"]]
               for m in A["mau"]])
    B = phan_b(vong)
    c.in_bang("Nhóm 6B — %d vòng nạp → xoá → nạp" % vong, ["chỉ số", "giá trị"], [
        ["thất bại", len(B["that_bai"])], ["nạp (s)", B["nap"]], ["reset (s)", B["reset"]],
        ["hệ số góc nạp (s/vòng)", "%.6f" % B["he_so_goc_nap_giay_moi_vong"]],
        ["cỡ cuối", B["cuoi"]], ["số học sinh cuối", B["so_hoc_sinh_cuoi"]], ["integrity", B["integrity"]]])
    print("\nGhi:", c.ghi_json("s6_chay_dai_nhanh" if a.nhanh else "s6_chay_dai",
                              {"may_do": c.may_do(), "A": A, "B": B}))


if __name__ == "__main__":
    main()
