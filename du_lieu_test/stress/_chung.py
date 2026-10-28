# -*- coding: utf-8 -*-
"""Phần dùng chung của các script stress test (STRESS TEST sau A13.8).

CHỈ ĐO, không sửa mã sản phẩm. Mọi dữ liệu là MÔ PHỎNG, seed cố định, sinh bằng
`sinh_ngau_nhien` của kỹ năng `sinh-du-lieu-clb` và ghi sổ bằng `so_nhap.ghi_so_nhap`.

Ghi chú: `sinh_ngau_nhien` chỉ có 20 chủ đề CLB. Để dựng 50 / 100 CLB, file này NỐI THÊM chủ đề
vào danh sách `_CHU_DE` TRONG BỘ NHỚ của tiến trình đo (không sửa tệp kỹ năng).
"""

import base64
import copy
import json
import os
import platform
import resource
import shutil
import sqlite3
import statistics
import sys
import tempfile
import time
import tracemalloc

AY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(AY))
KQ_DIR = os.path.join(AY, "ket_qua")
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts"))
sys.path.insert(0, AY)

import sinh_du_lieu as sk  # noqa: E402
import so_nhap  # noqa: E402

os.makedirs(KQ_DIR, exist_ok=True)

BUOI = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]
CFG_DQT_RULES = {"rules": {"wharton": True, "max_choices": 10, "max_tests": 5,
                           "score_scope": "per_slot"}}


def mo_rong_chu_de(n):
    """Đảm bảo `sk._CHU_DE` có ít nhất n chủ đề (nối thêm tên máy sinh)."""
    i = 0
    while len(sk._CHU_DE) < n:
        sk._CHU_DE.append(("clb_mr%03d" % i, "CLB Mở rộng %03d" % i))
        i += 1


def may_do():
    ram = ""
    try:
        with open("/proc/meminfo") as f:
            ram = f.readline().split()[1]
            ram = "%.1f GB" % (int(ram) / 1048576)
    except Exception:
        pass
    chromium = ""
    try:
        import glob
        import subprocess
        p = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux64/chrome") or [""])[0]
        if p:
            chromium = subprocess.run([p, "--version"], capture_output=True, text=True).stdout.strip()
    except Exception:
        pass
    return {"cpu": os.cpu_count(), "ram": ram, "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version, "os": platform.platform(), "chromium": chromium}


def sinh_bo(n_hs, n_clb, n_buoi, seed, dqt=False, thu_muc=None, kieu_chia="tron"):
    """Sinh sổ nhập hợp lệ. Trả (đường dẫn xlsx, clb, hs). `dqt` bật điểm quyết tâm hợp lệ."""
    ds_buoi = BUOI[:n_buoi]
    moi = max(1, n_clb // n_buoi)
    mo_rong_chu_de(moi * n_buoi)
    clb, hs = sk.sinh_ngau_nhien(n_hs, ds_buoi, moi, seed)
    cfg = None
    if dqt:
        sk.ap_diem_quyet_tam(clb, hs, seed + 1, "hop_le", kieu_chia, 3)
        cfg = sk.CFG_DQT
    loi = sk.soat(clb, hs) + (sk.soat_diem_quyet_tam(clb, hs) if dqt else [])
    if loi:
        raise RuntimeError("bộ sinh không hợp lệ: %s" % loi[:3])
    thu_muc = thu_muc or tempfile.mkdtemp(prefix="stress_")
    p = sk.ghi_bo(thu_muc, clb, hs, cfg, "SO.xlsx")[0]
    return p, clb, hs


def tao_api(thu_muc, dqt=False, cfg=None):
    from api import PipelineAPI
    import cau_hinh_ws
    db = os.path.join(thu_muc, "app.db")
    api = PipelineAPI(db)
    if dqt or cfg:
        c = copy.deepcopy(cfg) if cfg else copy.deepcopy(CFG_DQT_RULES)
        cau_hinh_ws.ghi_cau_hinh(db, c)
    return api


def b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


def nap_so(api, duong):
    return api.import_so_nhap(b64(duong))


def thoi(fn, *a, **k):
    t = time.perf_counter()
    r = fn(*a, **k)
    return r, (time.perf_counter() - t)


def tom(xs):
    xs = list(xs)
    return {"trung_vi": round(statistics.median(xs), 4), "lon_nhat": round(max(xs), 4),
            "nho_nhat": round(min(xs), 4), "n": len(xs)}


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def do_lap(fn, lan=3):
    """Chạy fn `lan` lần, trả tóm tắt thời gian (giây) và kết quả lần cuối."""
    xs, r = [], None
    for _ in range(lan):
        r, d = thoi(fn)
        xs.append(d)
    return tom(xs), r


def do_ram_tracemalloc(fn):
    """Chạy fn một lần dưới tracemalloc; trả (đỉnh MB do tracemalloc, kết quả)."""
    tracemalloc.start()
    try:
        r = fn()
        _cur, dinh = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return dinh / 1048576.0, r


def kich_thuoc_db(thu_muc):
    db = os.path.join(thu_muc, "app.db")
    sao = [f for f in os.listdir(thu_muc) if ".db.bak-" in f]
    return {"app_db_mb": round(os.path.getsize(db) / 1048576.0, 3) if os.path.exists(db) else 0,
            "n_sao_luu": len(sao),
            "sao_luu_mb": round(sum(os.path.getsize(os.path.join(thu_muc, f)) for f in sao) / 1048576.0, 3)}


def ghi_json(ten, noi_dung):
    p = os.path.join(KQ_DIR, ten + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(noi_dung, f, ensure_ascii=False, indent=1, sort_keys=True, default=str)
    return p


def in_bang(tieu_de, cot, dong):
    print("\n== %s ==" % tieu_de)
    rong = [max(len(str(c)), *(len(str(d[i])) for d in dong)) if dong else len(str(c))
            for i, c in enumerate(cot)]
    print(" | ".join(str(c).ljust(rong[i]) for i, c in enumerate(cot)))
    print("-+-".join("-" * w for w in rong))
    for d in dong:
        print(" | ".join(str(x).ljust(rong[i]) for i, x in enumerate(d)))
    sys.stdout.flush()


def dem_bang(db, bang):
    c = sqlite3.connect(db)
    try:
        return c.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]
    finally:
        c.close()


def toan_ven(db):
    c = sqlite3.connect(db)
    try:
        return c.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        c.close()


def dau_vet_db(db):
    """Ảnh chụp số dòng mọi bảng người dùng + hash nội dung: để so trước/sau khi lỗi."""
    import hashlib
    c = sqlite3.connect(db)
    try:
        h = hashlib.sha256()
        kq = {}
        for (ten,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                                "AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall():
            dong_ = sorted(repr(d) for d in c.execute('SELECT * FROM "%s"' % ten))
            for d in dong_:
                h.update(d.encode())
            n = len(dong_)
            kq[ten] = n
        kq["_hash"] = h.hexdigest()[:16]
        return kq
    finally:
        c.close()


def xoa(thu_muc):
    shutil.rmtree(thu_muc, ignore_errors=True)
