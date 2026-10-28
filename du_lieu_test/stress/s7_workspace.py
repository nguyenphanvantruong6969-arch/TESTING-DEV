# -*- coding: utf-8 -*-
"""Nhóm 7 — Workspace ngành khác. CHỈ ĐO, không đặt ngưỡng. Dữ liệu MÔ PHỎNG.

    python du_lieu_test/stress/s7_workspace.py [--nhanh] [--em N --clb M]

Mọi tổ hợp luật mà `cau_hinh_ws` cho phép (3 `priority` × 2 `tier_mode` × 2 `score_scope` × `wharton`
bật/tắt, bỏ tổ hợp bị từ chối) với nhãn trường học; thêm 3 bộ nhãn ngành khác (công ty — nhãn lấy từ
`du_lieu_test/bo_thu_workspace/cau_hinh_workspace.json`, sự kiện, tuỳ biến) × 2 tổ hợp luật. Cỡ mặc
định 2.000 em × 50 CLB, 2 buổi. Mỗi cấu hình: nạp Sổ (đúng định dạng của workspace đó, ghi bằng
`so_nhap.ghi_so_nhap(cfg=...)`), `run_pipeline`, `export_ket_qua` (mỗi phép lặp 3 lần), rồi kiểm như
nhóm 4: chỉ tiêu, dự trữ, ổn định (cài lại hàm lựa chọn), cấu trúc khoá ưu tiên khi luật là điểm thuần.
"""

import argparse
import collections
import copy
import itertools
import json
import os
import random
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402
import s4_dung_dan as s4  # noqa: E402

import cau_hinh_ws  # noqa: E402
import rbda_priority_pipeline as rp  # noqa: E402

NHAN_CONG_TY = json.load(open(os.path.join(c.GOC, "du_lieu_test", "bo_thu_workspace",
                                           "cau_hinh_workspace.json"), encoding="utf-8"))["labels"]
NHAN_SU_KIEN = {"person": {"vi": "Khách mời", "en": "Guest"}, "slot": {"vi": "Phiên", "en": "Session"},
                "session": {"vi": "Ngày", "en": "Day"}, "group": {"vi": "Diện", "en": "Category"},
                "score": {"vi": "Điểm xét", "en": "Rating"}}
NHAN_TUY_BIEN = {"person": {"vi": "Thí sinh", "en": "Candidate"}, "slot": {"vi": "Nguyện vọng ngành", "en": "Major"},
                 "session": {"vi": "Đợt", "en": "Round"}, "group": {"vi": "Diện ưu tiên", "en": "Priority"},
                 "score": {"vi": "Điểm xét tuyển", "en": "Admission score"}}
NHOM = ["chinh_sach", "khoi_10"]


def tat_ca_cau_hinh():
    ds = []
    for pr, tm, sc, wh in itertools.product(("score", "tier", "score+tier"), ("reserve", "strict"),
                                            ("per_slot", "per_person"), (False, True)):
        luat = {"max_choices": 10, "max_tests": 5, "priority": pr, "tier_mode": tm, "score_scope": sc,
                "tiers": NHOM if pr != "score" or tm == "strict" else [], "wharton": wh}
        cfg = {"name": "stress", "industry": "school", "rules": luat}
        try:
            cau_hinh_ws.chuan_hoa(copy.deepcopy(cfg))
        except ValueError:
            continue
        ten = "%s|%s|%s|W=%d" % (pr, tm, sc, wh)
        ds.append((ten, cfg))
    # nhãn ngành khác × hai luật
    for ten_n, nganh, nhan in (("cong_ty", "company", NHAN_CONG_TY), ("su_kien", "event", NHAN_SU_KIEN),
                               ("tuy_bien", "custom", NHAN_TUY_BIEN)):
        for pr, sc in (("score", "per_slot"), ("tier", "per_slot")):
            luat = {"max_choices": 10, "max_tests": 5, "priority": pr, "tier_mode": "reserve",
                    "score_scope": sc, "tiers": NHOM if pr != "score" else [], "wharton": False}
            ds.append(("nhan:%s|%s|%s" % (ten_n, pr, sc),
                       {"name": ten_n, "industry": nganh, "labels": copy.deepcopy(nhan), "rules": luat}))
    return ds


def sinh_so(cfg, n_hs, n_clb, n_buoi, seed, thu_muc):
    luat = cfg["rules"]
    dqt = bool(luat.get("wharton"))
    ca_nhan = luat.get("score_scope") == "per_person"
    ds_buoi = c.BUOI[:n_buoi]
    moi = max(1, n_clb // n_buoi)
    c.mo_rong_chu_de(moi * n_buoi)
    clb, hs = c.sk.sinh_ngau_nhien(n_hs, ds_buoi, moi, seed)
    if dqt:
        c.sk.ap_diem_quyet_tam(clb, hs, seed + 1, "hop_le", "tron", 3)
    loi = c.sk.soat(clb, hs) + (c.sk.soat_diem_quyet_tam(clb, hs) if dqt else [])
    if loi:
        raise RuntimeError(loi[:2])
    clubs, students = c.sk.thanh_so(clb, hs)
    if ca_nhan:
        rnd = random.Random(seed + 2)
        for st, h in zip(students, hs):
            r = rnd.random()
            st["diem_ca_nhan"] = ("%.1f" % rnd.uniform(4, 10)) if r < 0.6 else ("thi" if r < 0.7 else "")
            for x in st["nv"]:               # sổ điểm theo người không có cột điểm theo CLB
                x["thi"], x["diem"] = False, ""
    p = os.path.join(thu_muc, "SO.xlsx")
    c.so_nhap.ghi_so_nhap(p, clubs, students, cfg=cfg)
    return p


def mot_cau_hinh(ten, cfg, n_hs, n_clb, n_buoi, lan):
    kq = {"cau_hinh": ten, "rules": cfg["rules"], "van_de": []}
    thu_muc = tempfile.mkdtemp(prefix="s7_")
    do = s4.Do().cai()
    try:
        t = time.perf_counter()
        p = sinh_so(cfg, n_hs, n_clb, n_buoi, 7007, thu_muc)
        kq["sinh_so_s"] = round(time.perf_counter() - t, 2)
        api = c.tao_api(thu_muc, cfg=cfg)
        nap = []
        for i in range(lan):
            if i:
                api.reset_data("hoc_sinh", "XOA")
            r, d = c.thoi(c.nap_so, api, p)
            nap.append(d)
            if not r["ok"]:
                kq["van_de"].append("nap_that_bai:%s" % str([e.get("code") if isinstance(e, dict) else str(e)[:40]
                                                          for e in r["errors"]][:3]))
                return kq
        kq["nap_so"] = c.tom(nap)
        kq["canh_bao_nap"] = len(r["data"].get("warnings", []))
        chay = []
        for i in range(lan):
            do.ds.clear()
            r, d = c.thoi(api.run_pipeline, 42)
            chay.append(d)
            if not r["ok"]:
                kq["van_de"].append("run_pipeline_that_bai:%s" % str([e.get("code") if isinstance(e, dict) else str(e)[:40]
                                                                   for e in r["errors"]][:3]))
                return kq
        kq["run_pipeline"] = c.tom(chay)
        xuat = []
        for i in range(lan):
            r, d = c.thoi(api.export_ket_qua, os.path.join(thu_muc, "ra%d.xlsx" % i))
            xuat.append(d)
            if not r["ok"]:
                kq["van_de"].append("xuat_that_bai:%s" % str(r["errors"])[:100])
        kq["export_ket_qua"] = c.tom(xuat)
        db = os.path.join(thu_muc, "app.db")
        # Kiểm
        luat = cfg["rules"]
        clubs, hs_, prefs, diem, match = s4.doc(db)
        tham = rp.tham_so_luat(api._luat_nghiem(), {s: {"reserve_group": v["reserve_group"]} for s, v in hs_.items()})
        bo_qua = bool(tham["bo_qua_du_tru"])
        ds_uu = dict(do.ds)
        vd = s4.kiem_bo(db, ds_uu, bo_qua_du_tru=bo_qua)
        if luat["priority"] != "score" or luat["tier_mode"] != "reserve" or luat["score_scope"] == "per_person":
            vd = [v for v in vd if not v.startswith("K5:")]    # khoá không còn là "điểm thuần"
        if bo_qua:
            # chế độ không dự trữ: dòng 'reserve' không được phép có
            if any(v[1] == "reserve" for v in match.values()):
                vd.append("K3:co_dong_reserve_khi_bo_qua_du_tru")
        kq["bo_qua_du_tru"] = bo_qua
        kq["van_de"] += vd[:10]
        kq["so_van_de_kiem"] = len(vd)
        kq["so_dong_ket_qua"] = len(match)
        kq["so_trung"] = sum(1 for v in match.values() if v[0])
        kq["csdl"] = c.kich_thuoc_db(thu_muc)
        kq["integrity"] = c.toan_ven(db)
        kq["rss_mb"] = round(c.rss_mb(), 1)
        return kq
    except Exception as e:
        kq["van_de"].append("SAP:%r" % (e,))
        return kq
    finally:
        do.go()
        c.xoa(thu_muc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    ap.add_argument("--em", type=int, default=0)
    ap.add_argument("--clb", type=int, default=0)
    ap.add_argument("--buoi", type=int, default=2)
    ap.add_argument("--lan", type=int, default=3)
    ap.add_argument("--chi", default="", help="chỉ chạy cấu hình có tên chứa chuỗi này")
    a = ap.parse_args()
    n_hs = a.em or (300 if a.nhanh else 2000)
    n_clb = a.clb or (10 if a.nhanh else 50)
    ds = [(t, cf) for t, cf in tat_ca_cau_hinh() if a.chi in t]
    if a.nhanh:
        ds = ds[::3]
    tat_ca, dong = [], []
    for ten, cfg in ds:
        print(">> %s ..." % ten, flush=True)
        kq = mot_cau_hinh(ten, cfg, n_hs, n_clb, a.buoi, a.lan)
        tat_ca.append(kq)
        dong.append([ten, "%.2f" % kq["nap_so"]["trung_vi"] if "nap_so" in kq else "-",
                     "%.2f" % kq["run_pipeline"]["trung_vi"] if "run_pipeline" in kq else "-",
                     "%.2f" % kq["export_ket_qua"]["trung_vi"] if "export_ket_qua" in kq else "-",
                     kq.get("so_trung", "-"), len(kq["van_de"]), "; ".join(kq["van_de"])[:70]])
    c.in_bang("Nhóm 7 — %d em × %d CLB × %d buổi: giây (trung vị)" % (n_hs, n_clb, a.buoi),
              ["cấu hình", "nạp", "chạy", "xuất", "số em trúng", "vấn đề", "chi tiết"], dong)
    print("\nGhi:", c.ghi_json("s7_workspace_nhanh" if a.nhanh else "s7_workspace",
                              {"may_do": c.may_do(), "em": n_hs, "clb": n_clb, "buoi": a.buoi, "ket_qua": tat_ca}))


if __name__ == "__main__":
    main()
