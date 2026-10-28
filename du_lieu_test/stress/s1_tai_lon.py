# -*- coding: utf-8 -*-
"""Nhóm 1 — Tải lớn / hiệu năng. CHỈ ĐO, không đặt ngưỡng. Dữ liệu MÔ PHỎNG.

    python du_lieu_test/stress/s1_tai_lon.py [--nhanh]

Bậc: 800×20, 2.000×50, 5.000×100; mỗi bậc 1 buổi và 3 buổi; Điểm quyết tâm tắt / bật.
Mỗi cấu hình chạy trong MỘT TIẾN TRÌNH CON riêng (để RAM đỉnh `ru_maxrss` không lẫn giữa các
cấu hình) và lặp `--lan` lần (mặc định 3; mỗi lần dựng CSDL mới). `--nhanh`: chỉ 800×20 và
2.000×50, 1 buổi, Điểm quyết tâm tắt, 3 lần.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402

BAC = [(800, 20), (2000, 50), (5000, 100)]


def _dung_do_buoc(api_mod):
    """Bọc các hàm của api.py để cộng dồn thời gian từng bước (chỉ trong tiến trình đo)."""
    import time
    nhom = {
        "doc_du_lieu": ["load_from_sqlite_kem_dau_van_tay", "load_from_sqlite_kem_dau_van_tay_wharton"],
        "kiem_du_lieu": ["validate_data_integrity", "kiem_ho_so_wharton"],
        "khoa_stb": ["generate_stb_lottery", "chen_stb_cho_hoc_sinh_moi"],
        "giai": ["run_rbda_nhieu_buoi"],
        "sanity": ["sanity_check_result", "soat_vi_pham_rang_buoc"],
        "verify": ["verify_stability"],
    }
    tong = {k: 0.0 for k in nhom}
    for k, ten_ham in nhom.items():
        for ten in ten_ham:
            goc = getattr(api_mod, ten, None)
            if goc is None:
                continue

            def boc(*a, _g=goc, _k=k, **kw):
                t = time.perf_counter()
                try:
                    return _g(*a, **kw)
                finally:
                    tong[_k] += time.perf_counter() - t
            setattr(api_mod, ten, boc)
    goc_sl = api_mod.PipelineAPI._backup_db
    tong["sao_luu"] = 0.0

    def sl(self, *a, **kw):
        t = time.perf_counter()
        try:
            return goc_sl(self, *a, **kw)
        finally:
            tong["sao_luu"] += time.perf_counter() - t
    api_mod.PipelineAPI._backup_db = sl
    return tong


def mot_cau_hinh(n_hs, n_clb, n_buoi, dqt, lan):
    import api as api_mod
    tong = _dung_do_buoc(api_mod)
    nap, chay, xuat, bu = [], [], [], []
    buoc_ds = []
    api_cuoi = thu_muc_cuoi = None
    ram_trace = None
    thoi_gian_sinh = 0.0
    for i in range(lan):
        thu_muc = tempfile.mkdtemp(prefix="s1_")
        p, _clb, _hs = c.sinh_bo(n_hs, n_clb, n_buoi, 1000 + n_hs + n_buoi, dqt, thu_muc)
        api = c.tao_api(thu_muc, dqt)
        r, d = c.thoi(c.nap_so, api, p)
        if not r["ok"]:
            return {"loi": "nạp sổ thất bại: %s" % str(r["errors"])[:300]}
        nap.append(d)
        for k in tong:
            tong[k] = 0.0
        if i == 0:
            ram_trace, r = c.do_ram_tracemalloc(lambda: api.run_pipeline(42))
            chay.append(None)            # lần có tracemalloc không tính vào thời gian
            # Chạy lại một lần nữa trên CSDL sạch để có thời gian không bị tracemalloc làm chậm.
            api.reset_data("hoc_sinh", "XOA")
            c.nap_so(api, p)
            for k in tong:
                tong[k] = 0.0
            chay.pop()
        r, d = c.thoi(api.run_pipeline, 42)
        if not r["ok"]:
            return {"loi": "run_pipeline thất bại: %s" % str(r["errors"])[:300]}
        chay.append(d)
        buoc_ds.append(dict(tong, tong=d))
        bu.append(d - sum(v for k, v in tong.items() if k != "tong"))
        out = os.path.join(thu_muc, "ra.xlsx")
        r, d = c.thoi(api.export_ket_qua, out)
        if not r["ok"]:
            return {"loi": "export_ket_qua thất bại: %s" % str(r["errors"])[:300]}
        xuat.append(d)
        if i < lan - 1:
            c.xoa(thu_muc)
        else:
            api_cuoi, thu_muc_cuoi = api, thu_muc

    # Các API đọc (trên CSDL của lần cuối; mỗi phép đo lặp `lan` lần)
    api = api_cuoi
    clb_dau = api.list_clubs()["data"][0]["club_id"]
    n_trang = api.list_students_admin("", 1, 100)["data"]["total_pages"]
    phep = {
        "list_students_admin(trang1,100)": lambda: api.list_students_admin("", 1, 100),
        "list_students_admin(trang_cuoi,100)": lambda: api.list_students_admin("", n_trang, 100),
        "list_students_admin(tim 'Nguyen')": lambda: api.list_students_admin("Nguyễn", 1, 100),
        "list_clubs_admin": lambda: api.list_clubs_admin(),
        "get_match_results": lambda: api.get_match_results(),
        "get_club_fill_stats": lambda: api.get_club_fill_stats(),
        "get_data_health_report": lambda: api.get_data_health_report(),
    }
    if dqt:
        phep.update({
            "list_wharton_admin(trang1,100)": lambda: api.list_wharton_admin("", None, None, None, False, 1, 100),
            "list_wharton_admin(chi_loi)": lambda: api.list_wharton_admin("", None, None, None, True, 1, 100),
            "get_diem_chuan": lambda: api.get_diem_chuan(),
            "get_diem_chuan_clb(1 CLB)": lambda: api.get_diem_chuan_clb(clb_dau),
            "list_wharton_canh_bao": lambda: api.list_wharton_canh_bao(),
        })
    api_do = {}
    for ten, fn in phep.items():
        try:
            tom, r = c.do_lap(fn, lan)
            tom["ok"] = bool(r.get("ok")) if isinstance(r, dict) else None
            api_do[ten] = tom
        except Exception as e:  # ghi nhận, không dừng
            api_do[ten] = {"ngoai_le": repr(e)[:200]}

    tb = {k: c.tom([b[k] for b in buoc_ds]) for k in buoc_ds[0]}
    tb["con_lai_ghi_xuat_khac"] = c.tom(bu)
    kq = {
        "n_hs": n_hs, "n_clb": n_clb, "n_buoi": n_buoi, "dqt": dqt, "lan": lan,
        "nap_so": c.tom(nap), "run_pipeline": c.tom(chay), "export_ket_qua": c.tom(xuat),
        "run_pipeline_tung_buoc": tb,
        "api_doc": api_do,
        "ram_dinh_rss_mb": round(c.rss_mb(), 1),
        "ram_tracemalloc_run_pipeline_mb": round(ram_trace, 1) if ram_trace is not None else None,
        "csdl": c.kich_thuoc_db(thu_muc_cuoi),
        "run_history": c.dem_bang(os.path.join(thu_muc_cuoi, "app.db"), "run_history"),
    }
    c.xoa(thu_muc_cuoi)
    return kq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    ap.add_argument("--lan", type=int, default=3)
    ap.add_argument("--mot", nargs=5, metavar=("N_HS", "N_CLB", "N_BUOI", "DQT", "LAN"))
    a = ap.parse_args()
    if a.mot:
        n_hs, n_clb, n_buoi, dqt, lan = a.mot
        print(json.dumps(mot_cau_hinh(int(n_hs), int(n_clb), int(n_buoi), dqt == "1", int(lan)),
                         ensure_ascii=False, default=str))
        return

    cau_hinh = []
    for n_hs, n_clb in (BAC[:2] if a.nhanh else BAC):
        for n_buoi in ((1,) if a.nhanh else (1, 3)):
            for dqt in ((0,) if a.nhanh else (0, 1)):
                cau_hinh.append((n_hs, n_clb, n_buoi, dqt))
    tat_ca, dong = [], []
    for (n_hs, n_clb, n_buoi, dqt) in cau_hinh:
        print(">> %d HS × %d CLB × %d buổi, điểm quyết tâm=%d ..." % (n_hs, n_clb, n_buoi, dqt), flush=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mot", str(n_hs), str(n_clb),
                            str(n_buoi), str(dqt), str(a.lan)], capture_output=True, text=True)
        try:
            kq = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            kq = {"n_hs": n_hs, "n_clb": n_clb, "n_buoi": n_buoi, "dqt": bool(dqt),
                  "loi": "tiến trình con lỗi (mã %s): %s" % (r.returncode, (r.stderr or r.stdout)[-400:])}
        tat_ca.append(kq)
        if "loi" in kq:
            dong.append([n_hs, n_clb, n_buoi, dqt, "LỖI", kq["loi"][:60], "", "", "", ""])
            continue
        dong.append([n_hs, n_clb, n_buoi, dqt,
                     "%.2f/%.2f" % (kq["nap_so"]["trung_vi"], kq["nap_so"]["lon_nhat"]),
                     "%.2f/%.2f" % (kq["run_pipeline"]["trung_vi"], kq["run_pipeline"]["lon_nhat"]),
                     "%.2f/%.2f" % (kq["export_ket_qua"]["trung_vi"], kq["export_ket_qua"]["lon_nhat"]),
                     kq["ram_dinh_rss_mb"], kq["ram_tracemalloc_run_pipeline_mb"],
                     "%s (+%s sao lưu, %s tệp)" % (kq["csdl"]["app_db_mb"], kq["csdl"]["sao_luu_mb"],
                                                  kq["csdl"]["n_sao_luu"])])
    c.in_bang("Nhóm 1 — giây (trung vị/lớn nhất), RAM MB, cỡ CSDL MB",
              ["HS", "CLB", "buổi", "DQT", "nạp sổ", "run_pipeline", "xuất", "RSS đỉnh", "tracemalloc", "app.db"], dong)
    for kq in tat_ca:
        if "loi" in kq:
            continue
        print("\n-- %d×%d, %d buổi, DQT=%s: run_pipeline từng bước (trung vị s)" %
              (kq["n_hs"], kq["n_clb"], kq["n_buoi"], kq["dqt"]))
        print("   " + ", ".join("%s=%.3f" % (k, v["trung_vi"]) for k, v in kq["run_pipeline_tung_buoc"].items()))
        print("   API đọc (trung vị s): " + ", ".join(
            "%s=%.3f" % (k, v["trung_vi"]) for k, v in kq["api_doc"].items() if "trung_vi" in v))
    p = c.ghi_json("s1_tai_lon_nhanh" if a.nhanh else "s1_tai_lon",
                   {"may_do": c.may_do(), "ket_qua": tat_ca})
    print("\nGhi:", p)


if __name__ == "__main__":
    main()
