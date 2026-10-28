# -*- coding: utf-8 -*-
"""Nhóm 3 — Đồng thời / sập giữa chừng. CHỈ ĐO, không đặt ngưỡng. Dữ liệu MÔ PHỎNG.

    python du_lieu_test/stress/s3_dong_thoi.py [--nhanh]

Các phép thử (mỗi phép trên CSDL riêng, seed cố định):
  A  N = 4 / 16 / 64 luồng gọi `submit_preferences` cùng lúc — em KHÁC nhau và CÙNG một em;
     tương tự `submit_wharton`. Kiểm: không ngoại lệ, không lỗi khoá CSDL, em cùng một lúc ghi
     thì kết quả cuối đúng MỘT trong các danh sách đã gửi (không trộn), integrity_check.
  B  `run_pipeline` hai lần song song: (B1) cùng một đối tượng API (hai luồng), (B2) hai đối tượng
     API / hai tiến trình trên cùng app.db (khoá ghi của PipelineAPI chỉ có trong một tiến trình).
  C  Tiến trình con chạy `run_pipeline` lặp rồi bị SIGKILL ở nhiều thời điểm; mở lại → kiểm toàn
     vẹn, khoá STB, run_history chỉ tăng, match_results trọn vẹn, chạy lại được.
  D  CSDL bị khoá bởi kết nối khác (BEGIN EXCLUSIVE): thời gian tới lỗi, hình dạng lỗi, không ghi nửa chừng.
  E  Đĩa đầy giả lập bằng RLIMIT_FSIZE trong tiến trình con (ghi vượt giới hạn → SQLite báo lỗi ghi).
"""

import argparse
import json
import multiprocessing as mp
import os
import random
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402


def _dung(n_hs=300, n_clb=10, n_buoi=2, dqt=True, seed=31):
    thu_muc = tempfile.mkdtemp(prefix="s3_")
    p, clb, hs = c.sinh_bo(n_hs, n_clb, n_buoi, seed, dqt, thu_muc)
    api = c.tao_api(thu_muc, dqt)
    r = c.nap_so(api, p)
    assert r["ok"], r
    return thu_muc, api, clb, hs, p


def _co_loi_khoa(r):
    s = repr(r).lower()
    return "locked" in s or "busy" in s


def _hop_dong_ok(r):
    return isinstance(r, dict) and {"ok", "data", "errors"} <= set(r)


# ------------------------------------------------------------------ A
def phep_a(n_luong, cung_mot_em, wharton):
    thu_muc, api, clb, hs, _p = _dung(200, 8, 1, dqt=True)
    db = os.path.join(thu_muc, "app.db")
    clubs = [x["club_id"] for x in clb]
    rnd = random.Random(1000 + n_luong)
    em = [h["student_id"] for h in hs]
    muc_tieu = [em[0]] * n_luong if cung_mot_em else rnd.sample(em, n_luong)
    ds_gui = []
    for i in range(n_luong):
        k = rnd.randint(1, min(5, len(clubs)))
        ds_gui.append(rnd.sample(clubs, k))
    kq = [None] * n_luong
    ngoai_le = []
    rao = threading.Barrier(n_luong)

    def chay(i):
        try:
            rao.wait()
            if wharton:
                # Ghi điểm quyết tâm: giữ nguyên NV hiện có của em, đổi cách chia → hai quỹ 100.
                sid = muc_tieu[i]
                st = api.get_student_entry_state(sid)
                kq[i] = st
                return
            kq[i] = api.submit_preferences(muc_tieu[i], ds_gui[i])
        except BaseException as e:
            ngoai_le.append(repr(e)[:200])

    if wharton:
        return _phep_a_wharton(n_luong, cung_mot_em, thu_muc, api, clb, hs, db)
    t0 = time.perf_counter()
    th = [threading.Thread(target=chay, args=(i,)) for i in range(n_luong)]
    [t.start() for t in th]
    [t.join() for t in th]
    dt = time.perf_counter() - t0
    n_ok = sum(1 for r in kq if r and r.get("ok"))
    n_khoa = sum(1 for r in kq if r and _co_loi_khoa(r))
    n_sai_hd = sum(1 for r in kq if not _hop_dong_ok(r))
    # Kiểm nội dung cuối
    conn = sqlite3.connect(db)
    van_de = []
    try:
        if cung_mot_em:
            sid = muc_tieu[0]
            cuoi = [r[0] for r in conn.execute(
                "SELECT club_id FROM preferences WHERE student_id=? ORDER BY rank", (sid,))]
            # Chỉ so trong buổi duy nhất: danh sách cuối phải bằng đúng một danh sách đã gửi
            if cuoi not in ds_gui:
                van_de.append("em_cung_luc_ket_qua_tron:%s" % cuoi)
        else:
            for sid, gui in zip(muc_tieu, ds_gui):
                cuoi = [r[0] for r in conn.execute(
                    "SELECT club_id FROM preferences WHERE student_id=? ORDER BY rank", (sid,))]
                if cuoi != gui:
                    van_de.append("em_khac_nhau_sai:%s" % sid)
    finally:
        conn.close()
    if c.toan_ven(db) != "ok":
        van_de.append("integrity_check")
    out = {"n_luong": n_luong, "cung_mot_em": cung_mot_em, "ham": "submit_preferences",
           "giay": round(dt, 3), "n_ok": n_ok, "n_loi_khoa": n_khoa, "n_sai_hop_dong": n_sai_hd,
           "ngoai_le": ngoai_le[:3], "van_de": van_de[:5]}
    c.xoa(thu_muc)
    return out


def _chia(ds, rnd, tong=100):
    """Chia `tong` điểm nguyên cho các CLB trong `ds` (mỗi CLB >= 0)."""
    if not ds:
        return {}
    if len(ds) == 1:
        return {ds[0]: tong}
    cat = sorted(rnd.randint(0, tong) for _ in range(len(ds) - 1))
    phan = [b - a_ for a_, b in zip([0] + cat, cat + [tong])]
    return dict(zip(ds, phan))


def _phep_a_wharton(n_luong, cung_mot_em, thu_muc, api, clb, hs, db):
    """N luồng gọi submit_wharton với cách chia KHÁC NHAU. Cùng một em: kết quả cuối phải đúng MỘT
    cách chia đã gửi (không trộn hai bản); khác em: mỗi em đúng cách chia của mình."""
    rnd = random.Random(2000 + n_luong)
    conn = sqlite3.connect(db)
    thi = {}
    for sid, cid in conn.execute("SELECT student_id, club_id FROM club_test_selection"):
        thi.setdefault(sid, set()).add(cid)
    prefs = {}
    for sid, cid in conn.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
        prefs.setdefault(sid, []).append(cid)
    conn.close()
    ung = [h["student_id"] for h in hs if len(prefs.get(h["student_id"], [])) >= 3]
    muc = [ung[0]] * n_luong if cung_mot_em else rnd.sample(ung, min(n_luong, len(ung)))
    n_luong = len(muc)
    cac_goi = []
    for sid in muc:
        ds1 = [c_ for c_ in prefs[sid] if c_ in thi.get(sid, set())]
        ds2 = [c_ for c_ in prefs[sid] if c_ not in thi.get(sid, set())]
        cac_goi.append((sid, _chia(ds1, rnd), _chia(ds2, rnd)))
    kq = [None] * n_luong
    ngoai_le = []
    rao = threading.Barrier(n_luong)

    def chay(i):
        try:
            rao.wait()
            sid, w1, w2 = cac_goi[i]
            kq[i] = api.submit_wharton(sid, w1, w2)
        except BaseException as e:
            ngoai_le.append(repr(e)[:200])

    t0 = time.perf_counter()
    th = [threading.Thread(target=chay, args=(i,)) for i in range(n_luong)]
    [t.start() for t in th]
    [t.join() for t in th]
    dt = time.perf_counter() - t0
    van_de = []
    if c.toan_ven(db) != "ok":
        van_de.append("integrity_check")
    conn = sqlite3.connect(db)
    cuoi = {}
    for sid, cid, pts in conn.execute("SELECT student_id, club_id, points FROM wharton_bids"):
        cuoi.setdefault(sid, {})[cid] = pts
    conn.close()
    if cung_mot_em:
        sid = muc[0]
        cac_ban = [dict(list(w1.items()) + list(w2.items())) for _s, w1, w2 in cac_goi]
        # bỏ qua quỹ chỉ có một CLB (tự điền 100, không ghi) khi so
        if cuoi.get(sid) not in [{k: v for k, v in b.items()} for b in cac_ban] and \
                cuoi.get(sid) not in [{k: v for k, v in b.items() if len([1 for x in b if (x in thi.get(sid, set())) == (k in thi.get(sid, set()))]) > 1} for b in cac_ban]:
            van_de.append("cung_mot_em_ket_qua_tron:%s" % cuoi.get(sid))
    else:
        for sid, w1, w2 in cac_goi:
            mong = dict(list(w1.items()) + list(w2.items()))
            thuc = cuoi.get(sid)
            if thuc != mong and thuc != {k: v for k, v in mong.items() if len([1 for x in mong if (x in thi.get(sid, set())) == (k in thi.get(sid, set()))]) > 1}:
                van_de.append("khac_em_sai:%s" % sid)
    out = {"n_luong": n_luong, "cung_mot_em": cung_mot_em, "ham": "submit_wharton",
           "giay": round(dt, 3), "n_ok": sum(1 for r in kq if r and r.get("ok")),
           "n_loi_khoa": sum(1 for r in kq if r and _co_loi_khoa(r)),
           "n_sai_hop_dong": sum(1 for r in kq if not _hop_dong_ok(r)),
           "ngoai_le": ngoai_le[:3], "van_de": van_de[:5],
           "ma_loi_khac_nhau": sorted({e["code"] for r in kq if r for e in r.get("errors", [])
                                       if isinstance(e, dict)})[:6]}
    c.xoa(thu_muc)
    return out


# ------------------------------------------------------------------ B
def _chay_pipeline_tien_trinh(thu_muc, seed, hang_doi):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _chung as cc
    api = cc.tao_api(thu_muc, True)
    t = time.perf_counter()
    try:
        r = api.run_pipeline(seed)
        hang_doi.put({"ok": r.get("ok"), "giay": time.perf_counter() - t,
                      "ma": [e.get("code") for e in r.get("errors", []) if isinstance(e, dict)][:3]})
    except BaseException as e:
        hang_doi.put({"ngoai_le": repr(e)[:200]})


def phep_b():
    out = {}
    # B1: hai luồng, cùng một đối tượng API
    thu_muc, api, *_ = _dung(500, 12, 2)
    db = os.path.join(thu_muc, "app.db")
    kq, ngoai_le = [None, None], []
    rao = threading.Barrier(2)

    def chay(i):
        try:
            rao.wait()
            t = time.perf_counter()
            r = api.run_pipeline(42)
            kq[i] = (r, time.perf_counter() - t)
        except BaseException as e:
            ngoai_le.append(repr(e)[:200])
    th = [threading.Thread(target=chay, args=(i,)) for i in range(2)]
    [t.start() for t in th]
    [t.join() for t in th]
    out["B1_cung_doi_tuong"] = {
        "ngoai_le": ngoai_le, "ok": [bool(k and k[0].get("ok")) for k in kq],
        "giay": [round(k[1], 3) if k else None for k in kq],
        "run_history": c.dem_bang(db, "run_history"), "integrity": c.toan_ven(db),
        "stb_lock_so_dong": c.dem_bang(db, "stb_lock"),
    }
    c.xoa(thu_muc)

    # B2: hai tiến trình, hai đối tượng API, cùng app.db
    thu_muc, api, *_ = _dung(500, 12, 2)
    db = os.path.join(thu_muc, "app.db")
    ctx = mp.get_context("fork")
    hd = ctx.Queue()
    ps = [ctx.Process(target=_chay_pipeline_tien_trinh, args=(thu_muc, 42, hd)) for _ in range(2)]
    [p.start() for p in ps]
    [p.join(180) for p in ps]
    ket = []
    while not hd.empty():
        ket.append(hd.get())
    stb = sqlite3.connect(db).execute("SELECT COUNT(*) FROM students WHERE stb_number IS NULL").fetchone()[0] \
        if "stb_number" in [r[1] for r in sqlite3.connect(db).execute("PRAGMA table_info(students)")] else None
    out["B2_hai_tien_trinh"] = {
        "ket_qua": ket, "run_history": c.dem_bang(db, "run_history"), "integrity": c.toan_ven(db),
        "em_chua_co_stb": stb,
        "match_results": c.dem_bang(db, "match_results")}
    c.xoa(thu_muc)
    return out


# ------------------------------------------------------------------ C
def _tien_trinh_lap_pipeline(thu_muc, tin_hieu):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _chung as cc
    api = cc.tao_api(thu_muc, True)
    tin_hieu.set()
    seed = 100
    while True:
        api.run_pipeline(seed)
        seed += 1


def phep_c(so_lan, n_hs=800, n_clb=20):
    thu_muc, api, clb, hs, _p = _dung(n_hs, n_clb, 2, seed=77)
    db = os.path.join(thu_muc, "app.db")
    # Một lần chạy sạch trước, để có "trạng thái tốt" và đo thời gian một lần chạy
    t = time.perf_counter()
    r = api.run_pipeline(42)
    mot_lan = time.perf_counter() - t
    assert r["ok"], r
    rnd = random.Random(5150)
    kqs = []
    rh_truoc = c.dem_bang(db, "run_history")
    for lan in range(so_lan):
        # Chụp trạng thái tốt (để so)
        tt_truoc = c.dem_bang(db, "match_results")
        rh_truoc = c.dem_bang(db, "run_history")
        ctx = mp.get_context("fork")
        tin = ctx.Event()
        p = ctx.Process(target=_tien_trinh_lap_pipeline, args=(thu_muc, tin))
        p.start()
        tin.wait(30)
        cho = rnd.uniform(0.0, 1.6 * mot_lan)         # kill ở các pha khác nhau của một lần chạy
        time.sleep(cho)
        os.kill(p.pid, signal.SIGKILL)
        p.join()
        mot = {"lan": lan, "kill_sau_giay": round(cho, 4)}
        van_de = []
        try:
            ic = c.toan_ven(db)
            mot["integrity"] = ic
            if ic != "ok":
                van_de.append("integrity_check:%s" % ic)
            rh = c.dem_bang(db, "run_history")
            mot["run_history_truoc_sau"] = [rh_truoc, rh]
            if rh < rh_truoc:
                van_de.append("run_history_giam")
            # kết quả không nửa vời: số dòng match_results hoặc bằng trạng thái trước hoặc là một lần chạy trọn
            mr = c.dem_bang(db, "match_results")
            mot["match_results"] = mr
            conn = sqlite3.connect(db)
            n_hs_db = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
            # em chưa có STB mà khoá STB đang bật = khoá mồ côi
            khoa = conn.execute("SELECT * FROM stb_lock").fetchall()
            chua_stb = conn.execute("SELECT COUNT(*) FROM students WHERE stb_number IS NULL").fetchone()[0]
            conn.close()
            mot["khoa_stb"] = [list(k)[:3] for k in khoa][:2]
            mot["em_chua_co_stb"] = chua_stb
            if khoa and chua_stb == n_hs_db and any(k[1] for k in khoa if k):
                van_de.append("khoa_stb_mo_coi")
            if mr not in (tt_truoc, 0) and mr != tt_truoc:
                mot["ghi_chu_match_results"] = "đổi số dòng so với trạng thái tốt: %d → %d" % (tt_truoc, mr)
            # mở lại + chạy lại
            api2 = c.tao_api(thu_muc, True)
            r2 = api2.run_pipeline(42)
            mot["chay_lai_ok"] = bool(r2.get("ok"))
            if not r2.get("ok"):
                van_de.append("khong_chay_lai_duoc:%s" % [e.get("code") for e in r2.get("errors", [])
                                                         if isinstance(e, dict)][:3])
            rh2 = c.dem_bang(db, "run_history")
            if rh2 != rh + 1 and r2.get("ok"):
                van_de.append("run_history_khong_tang_1:%d->%d" % (rh, rh2))
        except Exception as e:
            van_de.append("ngoai_le_khi_kiem:%r" % (e,))
        mot["van_de"] = van_de
        kqs.append(mot)
    out = {"mot_lan_chay_giay": round(mot_lan, 3), "so_lan_kill": so_lan,
           "tong_van_de": sum(len(k["van_de"]) for k in kqs), "chi_tiet": kqs}
    c.xoa(thu_muc)
    return out


# ------------------------------------------------------------------ D
def phep_d():
    out = {}
    thu_muc, api, clb, hs, p = _dung(300, 10, 2)
    db = os.path.join(thu_muc, "app.db")
    sid = hs[0]["student_id"]
    cid = [x["club_id"] for x in clb][:2]
    truoc = c.dau_vet_db(db)
    khoa = sqlite3.connect(db, timeout=0, isolation_level=None)
    khoa.execute("BEGIN EXCLUSIVE")
    phep = {
        "submit_preferences": lambda: api.submit_preferences(sid, cid),
        "run_pipeline": lambda: api.run_pipeline(42),
        "import_so_nhap": lambda: c.nap_so(api, p),
        "reset_data": lambda: api.reset_data("hoc_sinh", "XOA"),
        "list_students_admin(đọc)": lambda: api.list_students_admin("", 1, 50),
    }
    ket = {}
    # Đặt busy timeout ngắn qua biến môi trường nếu có; mặc định phần mềm chờ 15 giây.
    for ten, fn in phep.items():
        t = time.perf_counter()
        try:
            r = fn()
            ket[ten] = {"giay": round(time.perf_counter() - t, 2), "ok": r.get("ok"),
                        "ma": [e.get("code") if isinstance(e, dict) else str(e)[:60] for e in r.get("errors", [])][:3]}
        except BaseException as e:
            ket[ten] = {"giay": round(time.perf_counter() - t, 2), "ngoai_le": repr(e)[:200]}
    khoa.execute("ROLLBACK")
    khoa.close()
    sau = c.dau_vet_db(db)
    out["ket_qua"] = ket
    out["csdl_doi_khi_loi"] = (sau != truoc)
    out["integrity"] = c.toan_ven(db)
    # sau khi mở khoá, mọi thứ chạy lại bình thường
    out["sau_mo_khoa_submit_ok"] = bool(api.submit_preferences(sid, cid).get("ok"))
    out["sau_mo_khoa_pipeline_ok"] = bool(api.run_pipeline(42).get("ok"))
    c.xoa(thu_muc)
    return out


# ------------------------------------------------------------------ E
_MA_E = r'''
import json, os, resource, signal, sys
sys.path.insert(0, %(ay)r)
import _chung as c
thu_muc, gioi_han, hanh_dong = sys.argv[1], int(sys.argv[2]), sys.argv[3]
api = c.tao_api(thu_muc, True)
signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
resource.setrlimit(resource.RLIMIT_FSIZE, (gioi_han, gioi_han))
out = {}
try:
    if hanh_dong == "run_pipeline":
        r = api.run_pipeline(42)
    elif hanh_dong == "submit_preferences":
        r = api.submit_preferences(sys.argv[4], sys.argv[5].split(","))
    elif hanh_dong == "import_so_nhap":
        r = c.nap_so(api, sys.argv[4])
    elif hanh_dong == "export_ket_qua":
        r = api.export_ket_qua(os.path.join(thu_muc, "ra.xlsx"))
    else:
        r = {}
    out = {"ok": r.get("ok"), "ma": [e.get("code") if isinstance(e, dict) else str(e)[:80]
                                      for e in r.get("errors", [])][:4],
           "ket_buoc": [(s.get("step"), s.get("status")) for s in (r.get("data") or {}).get("steps", [])]
           if isinstance(r.get("data"), dict) else None}
except BaseException as e:
    out = {"ngoai_le": repr(e)[:300]}
print("KQ" + json.dumps(out, ensure_ascii=False, default=str))
'''


def phep_e():
    out = {}
    for hanh_dong in ("run_pipeline", "submit_preferences", "import_so_nhap", "export_ket_qua"):
        for gioi_han_them in (0, 4096, 65536):
            thu_muc, api, clb, hs, p = _dung(300, 10, 2)
            db = os.path.join(thu_muc, "app.db")
            if hanh_dong == "import_so_nhap":
                api.reset_data("tat_ca", "XOA")
            elif hanh_dong in ("export_ket_qua",):
                api.run_pipeline(42)
            kich_co = max(os.path.getsize(f) for f in
                          [os.path.join(thu_muc, x) for x in os.listdir(thu_muc)] if os.path.isfile(f))
            if hanh_dong == "export_ket_qua":
                kich_co = 0          # tệp xuất (.xlsx) nhỏ hơn CSDL: giới hạn tuyệt đối thấp mới làm nó hỏng
                gioi_han_them = (0, 20000, 60000)[(0, 4096, 65536).index(gioi_han_them)]
            truoc = c.dau_vet_db(db)
            hs0 = hs[0]["student_id"]
            cid = ",".join(x["club_id"] for x in clb[:2])
            tham = [thu_muc, str(kich_co + gioi_han_them), hanh_dong]
            if hanh_dong == "submit_preferences":
                tham += [hs0, cid]
            if hanh_dong == "import_so_nhap":
                tham += [p]
            ma = _MA_E % {"ay": os.path.dirname(os.path.abspath(__file__))}
            r = subprocess.run([sys.executable, "-c", ma] + tham, capture_output=True, text=True, timeout=300)
            kq_dong = [l for l in r.stdout.splitlines() if l.startswith("KQ")]
            ket = json.loads(kq_dong[-1][2:]) if kq_dong else {"tien_trinh_chet": r.returncode, "stderr": r.stderr[-300:]}
            sau = c.dau_vet_db(db)
            ket["integrity"] = c.toan_ven(db)
            ket["csdl_doi"] = sau != truoc
            ket["tep_sao_luu_do_dang"] = [f for f in os.listdir(thu_muc) if ".bak-" in f
                                         and os.path.getsize(os.path.join(thu_muc, f)) < 1024]
            ket["gioi_han_byte"] = kich_co + gioi_han_them
            ket["tep_xuat_con_lai"] = [f for f in os.listdir(thu_muc) if f.startswith("ra") and f.endswith(".xlsx")
                                       and os.path.getsize(os.path.join(thu_muc, f)) > 0]
            out["%s/+%dB" % (hanh_dong, gioi_han_them)] = ket
            c.xoa(thu_muc)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    a = ap.parse_args()
    tat_ca = {"may_do": c.may_do()}

    luong = (4, 16) if a.nhanh else (4, 16, 64)
    dong = []
    tat_ca["A"] = []
    for ham_w in (False, True):
        for n in luong:
            for cung in (False, True):
                r = phep_a(n, cung, ham_w)
                tat_ca["A"].append(r)
                dong.append([r["ham"], n, "cùng 1 em" if cung else "khác em", r["giay"], r["n_ok"],
                             r["n_loi_khoa"], r["n_sai_hop_dong"], len(r["ngoai_le"]), len(r["van_de"])])
    c.in_bang("A — luồng đồng thời (giây, số lời gọi ok, lỗi khoá CSDL, sai hợp đồng, ngoại lệ, vấn đề)",
              ["hàm", "N", "đối tượng", "giây", "ok", "khoá", "sai HĐ", "ngoại lệ", "vấn đề"], dong)

    tat_ca["B"] = phep_b()
    print("\n== B — run_pipeline song song ==")
    print(json.dumps(tat_ca["B"], ensure_ascii=False, indent=1, default=str))

    tat_ca["C"] = phep_c(6 if a.nhanh else 30)
    print("\n== C — SIGKILL giữa run_pipeline: %d lần, %d vấn đề ==" % (
        tat_ca["C"]["so_lan_kill"], tat_ca["C"]["tong_van_de"]))
    for k in tat_ca["C"]["chi_tiet"]:
        if k["van_de"]:
            print("  ", k)

    tat_ca["D"] = phep_d()
    print("\n== D — CSDL bị khoá bởi kết nối khác ==")
    print(json.dumps(tat_ca["D"], ensure_ascii=False, indent=1, default=str))

    tat_ca["E"] = phep_e()
    print("\n== E — đĩa đầy giả lập (RLIMIT_FSIZE) ==")
    print(json.dumps(tat_ca["E"], ensure_ascii=False, indent=1, default=str))

    p = c.ghi_json("s3_dong_thoi_nhanh" if a.nhanh else "s3_dong_thoi", tat_ca)
    print("\nGhi:", p)


if __name__ == "__main__":
    main()
