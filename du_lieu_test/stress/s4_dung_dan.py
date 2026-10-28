# -*- coding: utf-8 -*-
"""Nhóm 4 — Đúng đắn của thuật toán trên nhiều bộ ngẫu nhiên. CHỈ ĐO. Dữ liệu MÔ PHỎNG.

    python du_lieu_test/stress/s4_dung_dan.py [--nhanh] [--so-bo N] [--khong-trung-khit]

Mỗi bộ: sinh bằng `sinh_ngau_nhien` (5–200 em, 2–15 CLB, 1–3 buổi, dự trữ có/không, Điểm quyết
tâm có/không), nạp qua Sổ nhập thật, chạy `run_pipeline`, rồi kiểm ĐỘC LẬP trên kết quả trong CSDL:

  K1  pipeline tự báo cặp phá vỡ / lỗi gì không (rollback)?
  K2  không CLB nào vượt chỉ tiêu; mỗi (em, buổi) nhiều nhất một dòng; CLB trúng nằm trong danh
      sách nguyện vọng của em và đúng buổi.
  K3  dự trữ: dòng `reserve` chỉ thuộc em đúng nhóm của CLB và không quá `reserve_capacity`.
  K4  ổn định: tự cài lại hàm lựa chọn (dự trữ rồi chung) và duyệt MỌI cặp (em, CLB) em ưa hơn chỗ
      hiện tại; bộ ≤ 8 em × 4 CLB (mỗi buổi): vét cạn mọi ghép (có ràng buộc chỉ tiêu) → kết quả
      phải ổn định VÀ không có ghép ổn định nào khiến một em tốt hơn (tối ưu phía học sinh).
  K5  cấu trúc khoá ưu tiên: thứ tự mà thuật toán thực sự dùng (chặn `compute_club_priority` /
      `uu_tien_*` bằng một lớp bọc đo) có Tầng 1 (có điểm thi) trước Tầng 2, điểm giảm dần.
  K6  khoá ưu tiên không đọc thứ hạng nguyện vọng: hoán vị thứ tự nguyện vọng của mọi em (giữ tập)
      thì danh sách ưu tiên của mọi CLB y nguyên.
  K7  STB: sau lần đầu khoá; đổi seed → số không đổi; thêm em đến muộn (chỉ bộ không Điểm quyết
      tâm) → thứ tự tương đối của em cũ giữ nguyên, số vẫn là hoán vị 0..n-1.
  K8  tất định: cùng dữ liệu + cùng seed trên CSDL mới → match_results y nguyên.
  K9  run_history chỉ tăng đúng 1 mỗi lần chạy thành công.
Cuối cùng: tắt Điểm quyết tâm (cấu hình mặc định) so với commit e08af78 trên 3 bộ × 20 seed.
"""

import argparse
import collections
import itertools
import json
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402

import rbda_priority_pipeline as rp  # noqa: E402


# ---------------------------------------------------------------- đo thứ tự ưu tiên thật sự được dùng
class Do:
    def __init__(self):
        self.ds = {}
        self.sau = 0

    def boc(self, ten):
        goc = getattr(rp, ten)
        me = self

        def w(*a, **k):
            me.sau += 1
            try:
                r = goc(*a, **k)
            finally:
                me.sau -= 1
            if me.sau == 0 and isinstance(r, list):
                cid = a[0] if a else k.get("club_id")
                me.ds[cid] = list(r)
            return r
        w._goc = goc
        return w

    def cai(self):
        self._cu = {}
        for ten in ("compute_club_priority", "uu_tien_theo_nhom", "uu_tien_wharton"):
            if hasattr(rp, ten):
                self._cu[ten] = getattr(rp, ten)
                setattr(rp, ten, self.boc(ten))
        return self

    def go(self):
        for ten, f in self._cu.items():
            setattr(rp, ten, f)


# ---------------------------------------------------------------- đọc CSDL
def doc(db):
    k = sqlite3.connect(db)
    try:
        clubs = {r[0]: {"capacity": r[1], "reserve_capacity": r[2], "reserve_group": r[3] or "", "buoi": r[4]}
                 for r in k.execute("SELECT club_id, capacity, reserve_capacity, reserve_group, buoi FROM clubs")}
        hs = {r[0]: {"reserve_group": r[1] or "", "stb": r[2]}
              for r in k.execute("SELECT student_id, reserve_group, stb_number FROM students")}
        prefs = collections.defaultdict(list)
        for sid, cid in k.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
            prefs[sid].append(cid)
        diem = collections.defaultdict(dict)
        for sid, cid, sc in k.execute("SELECT student_id, club_id, score FROM club_scores"):
            diem[cid][sid] = sc
        match = {(r[0], r[1]): r[2:] for r in k.execute(
            "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref FROM match_results")}
        return clubs, hs, dict(prefs), diem, match
    finally:
        k.close()


# ---------------------------------------------------------------- hàm lựa chọn tự cài lại
def chon(pool, cap, rc, ok_du_tru, rank):
    """Dự trữ rồi chung (Kominers & Sönmez), cài lại độc lập với mã sản phẩm."""
    uu = sorted(pool, key=lambda s: rank[s])
    du_tru = [s for s in uu if ok_du_tru(s)][:rc]
    con = [s for s in uu if s not in set(du_tru)][:cap - len(du_tru)]
    return set(du_tru) | set(con)


def kiem_bo(db, ds_uutien, bo_qua_du_tru=False):
    """Trả danh sách vấn đề (K2–K5)."""
    clubs, hs, prefs, diem, match = doc(db)
    vd = []
    buoi_cua = {cid: (c_["buoi"] or "") for cid, c_ in clubs.items()}
    # K2 / K3
    dem = collections.Counter()
    dem_dt = collections.Counter()
    for (sid, buoi), (cid, tier, _r) in match.items():
        if cid is None:
            continue
        dem[cid] += 1
        if cid not in prefs.get(sid, []):
            vd.append("K2:trung_clb_ngoai_nguyen_vong:%s->%s" % (sid, cid))
        if (buoi_cua.get(cid) or buoi) != buoi:
            vd.append("K2:sai_buoi:%s,%s" % (sid, cid))
        if tier == "reserve":
            dem_dt[cid] += 1
            cg = clubs[cid]["reserve_group"]
            if not cg or hs[sid]["reserve_group"] != cg:
                vd.append("K3:du_tru_sai_nhom:%s,%s" % (sid, cid))
    for cid, n in dem.items():
        if n > clubs[cid]["capacity"]:
            vd.append("K2:vuot_chi_tieu:%s %d>%d" % (cid, n, clubs[cid]["capacity"]))
    for cid, n in dem_dt.items():
        if n > clubs[cid]["reserve_capacity"]:
            vd.append("K3:vuot_suat_du_tru:%s" % cid)
    # K5: cấu trúc khoá
    for cid, ds in ds_uutien.items():
        diem_c = diem.get(cid, {})
        thay_tang2, truoc = False, None
        for sid in ds:
            if sid in diem_c:
                if thay_tang2:
                    vd.append("K5:tang1_sau_tang2:%s" % cid)
                    break
                # điểm giảm dần chỉ kiểm khi cùng nhóm hạng (không có nhóm hạng ở bộ này)
                if truoc is not None and diem_c[sid] > truoc + 1e-12:
                    vd.append("K5:diem_tang:%s" % cid)
                    break
                truoc = diem_c[sid]
            else:
                thay_tang2 = True
    # K4: ổn định theo từng buổi
    theo_buoi = collections.defaultdict(list)
    for cid, c_ in clubs.items():
        theo_buoi[c_["buoi"] or ""].append(cid)
    for buoi, ds_clb in theo_buoi.items():
        tap = set(ds_clb)
        nv = {sid: [x for x in ds if x in tap] for sid, ds in prefs.items()}
        nv = {s: v for s, v in nv.items() if v}
        giu = {cid: set() for cid in ds_clb}
        hien = {}
        for (sid, b), (cid, _t, _r) in match.items():
            if (b == buoi or (not buoi and b)) and cid in tap:
                giu[cid].add(sid)
                hien[sid] = cid
        rank = {cid: {s: i for i, s in enumerate(ds_uutien.get(cid, []))} for cid in ds_clb}

        def co_chap(cid, s, giu_c):
            c_ = clubs[cid]
            rc = 0 if bo_qua_du_tru else c_["reserve_capacity"]
            return s in chon(giu_c | {s}, c_["capacity"], rc,
                             lambda x: bool(c_["reserve_group"]) and hs[x]["reserve_group"] == c_["reserve_group"],
                             rank[cid])
        for sid, ds in nv.items():
            cur = hien.get(sid)
            gioi = ds.index(cur) if cur in ds else len(ds)
            for cid in ds[:gioi]:
                if sid in rank[cid] and co_chap(cid, sid, giu[cid] - {sid}):
                    vd.append("K4:cap_pha_vo:%s,%s" % (sid, cid))
        # vét cạn tối ưu phía học sinh cho bộ rất nhỏ
        if len(nv) <= 8 and len(ds_clb) <= 4:
            vd += _vet_can(buoi, ds_clb, nv, clubs, hs, rank, hien, bo_qua_du_tru)
    return vd


def _vet_can(buoi, ds_clb, nv, clubs, hs, rank, hien, bo_qua_du_tru):
    """Duyệt mọi ghép khả thi; mọi ghép ổn định phải KHÔNG tốt hơn kết quả cho bất kỳ em nào."""
    sids = sorted(nv)
    lua = [[None] + nv[s] for s in sids]
    if len(sids) > 8:
        return []
    tot = 1
    for l in lua:
        tot *= len(l)
    if tot > 400000:
        return []

    def chap(cid, s, giu_c):
        c_ = clubs[cid]
        rc = 0 if bo_qua_du_tru else c_["reserve_capacity"]
        return chon(giu_c | {s}, c_["capacity"], rc,
                    lambda x: bool(c_["reserve_group"]) and hs[x]["reserve_group"] == c_["reserve_group"],
                    rank[cid])

    vd = []
    kq_pm = {s: hien.get(s) for s in sids}

    def vi_tri(s, cid):
        return nv[s].index(cid) if cid in nv[s] else len(nv[s])

    for tuple_ in itertools.product(*lua):
        gan = dict(zip(sids, tuple_))
        giu = {cid: set() for cid in ds_clb}
        for s, cid in gan.items():
            if cid:
                giu[cid].add(s)
        if any(len(giu[cid]) > clubs[cid]["capacity"] for cid in ds_clb):
            continue
        ok = True
        for cid in ds_clb:
            if not giu[cid]:
                continue
            # tập giữ phải bằng Ch(giu) (CLB không muốn bỏ ai)
            ch = chon(set(giu[cid]), clubs[cid]["capacity"],
                      0 if bo_qua_du_tru else clubs[cid]["reserve_capacity"],
                      lambda x, c_=clubs[cid]: bool(c_["reserve_group"]) and hs[x]["reserve_group"] == c_["reserve_group"],
                      rank[cid])
            if ch != giu[cid]:
                ok = False
                break
        if not ok:
            continue
        for s in sids:
            cur = gan[s]
            for cid in nv[s][:(nv[s].index(cur) if cur else len(nv[s]))]:
                if s in rank[cid] and s in chap(cid, s, giu[cid] - {s}):
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        # ghép ổn định: kết quả pipeline phải tốt hơn hoặc bằng với MỌI em
        for s in sids:
            a = vi_tri(s, kq_pm[s]) if kq_pm[s] else len(nv[s])
            b = vi_tri(s, gan[s]) if gan[s] else len(nv[s])
            if b < a:
                vd.append("K4:khong_toi_uu_phia_hoc_sinh:%s %s>%s" % (s, kq_pm[s], gan[s]))
                return vd
    return vd


# ---------------------------------------------------------------- dựng bộ ngẫu nhiên
def tham_so_bo(i, nhanh):
    rnd = random.Random(900000 + i)
    n_hs = rnd.randint(5, 200)
    t = rnd.randint(2, 15)
    n_buoi = min(rnd.randint(1, 3), t)
    if i % 7 == 0:                      # một phần bộ rất nhỏ để vét cạn được
        n_hs, t, n_buoi = rnd.randint(5, 8), rnd.randint(2, 4), 1
    dqt = rnd.random() < 0.4
    du_tru = rnd.choice([0.0, 0.35, 0.8])
    choi = rnd.choice([0.6, 0.9, 1.15, 1.4])
    return dict(n_hs=n_hs, t=t, n_buoi=n_buoi, dqt=dqt, du_tru=du_tru, choi=choi, seed=100000 + i)


def dung_bo(p, thu_muc):
    ds_buoi = c.BUOI[:p["n_buoi"]]
    moi = max(1, p["t"] // p["n_buoi"])
    c.mo_rong_chu_de(moi * p["n_buoi"])
    clb, hs = c.sk.sinh_ngau_nhien(p["n_hs"], ds_buoi, moi, p["seed"], do_choi=p["choi"],
                                    ti_le_du_tru=p["du_tru"])
    cfg = None
    if p["dqt"]:
        c.sk.ap_diem_quyet_tam(clb, hs, p["seed"] + 1, "hop_le", "tron", 3)
        cfg = c.sk.CFG_DQT
    loi = c.sk.soat(clb, hs) + (c.sk.soat_diem_quyet_tam(clb, hs) if p["dqt"] else [])
    if loi:
        return None, "sinh_khong_hop_le:%s" % loi[0]
    xl = c.sk.ghi_bo(thu_muc, clb, hs, cfg, "SO.xlsx")[0]
    return xl, None


def chay_mot_bo(i, nhanh):
    p = tham_so_bo(i, nhanh)
    kq = {"i": i, "tham_so": p, "van_de": []}
    thu_muc = tempfile.mkdtemp(prefix="s4_")
    do = Do().cai()
    try:
        xl, loi = dung_bo(p, thu_muc)
        if loi:
            kq["van_de"].append(loi)
            return kq
        api = c.tao_api(thu_muc, p["dqt"])
        r = c.nap_so(api, xl)
        if not r["ok"]:
            kq["van_de"].append("K0:nap_that_bai:%s" % str([e.get("code") if isinstance(e, dict) else e
                                                          for e in r["errors"]][:3]))
            return kq
        db = os.path.join(thu_muc, "app.db")
        rh0 = c.dem_bang(db, "run_history")
        do.ds.clear()
        r = api.run_pipeline(42)
        if not r["ok"]:
            ma = [e.get("code") if isinstance(e, dict) else str(e)[:50] for e in r["errors"]][:3]
            kq["van_de"].append("K1:pipeline_tu_choi:%s" % ma)
            return kq
        ds_uu = dict(do.ds)
        kq["van_de"] += kiem_bo(db, ds_uu)
        if c.dem_bang(db, "run_history") != rh0 + 1:
            kq["van_de"].append("K9:run_history_khong_tang_1")
        # K7 STB
        k = sqlite3.connect(db)
        stb = dict(k.execute("SELECT student_id, stb_number FROM students"))
        khoa = k.execute("SELECT is_locked FROM stb_lock").fetchone()
        k.close()
        n = len(stb)
        if sorted(stb.values()) != list(range(n)):
            kq["van_de"].append("K7:stb_khong_la_hoan_vi")
        if not khoa or not khoa[0]:
            kq["van_de"].append("K7:stb_chua_khoa")
        mr1 = sorted((s, b) + tuple(v) for (s, b), v in doc(db)[4].items())
        # Đổi seed sau khi khoá: phần mềm PHẢI từ chối (bất biến 3), số bốc thăm giữ nguyên.
        r2 = api.run_pipeline(7)
        ma2 = [e.get("code") for e in r2.get("errors", []) if isinstance(e, dict)]
        if r2["ok"] or "hat_giong_da_khoa" not in ma2:
            kq["van_de"].append("K7:doi_seed_sau_khoa_khong_bi_chan:%s" % ma2[:2])
        k = sqlite3.connect(db)
        stb2 = dict(k.execute("SELECT student_id, stb_number FROM students"))
        k.close()
        if stb2 != stb:
            kq["van_de"].append("K7:stb_doi_khi_doi_seed")
        if c.dem_bang(db, "run_history") != rh0 + 1:
            kq["van_de"].append("K9:run_history_doi_khi_chay_bi_tu_choi")
        r_lai = api.run_pipeline(42)
        if not r_lai["ok"]:
            kq["van_de"].append("K8:chay_lai_cung_seed_that_bai")
        else:
            mr_lai = sorted((s_, b) + tuple(v) for (s_, b), v in doc(db)[4].items())
            if mr_lai != mr1:
                kq["van_de"].append("K8:khong_tat_dinh_cung_seed")
            if c.dem_bang(db, "run_history") != rh0 + 2:
                kq["van_de"].append("K9:run_history_lan2")
        # K8 trên CSDL mới
        if i % 5 == 0:
            t2 = tempfile.mkdtemp(prefix="s4b_")
            api2 = c.tao_api(t2, p["dqt"])
            c.nap_so(api2, xl)
            api2.run_pipeline(42)
            if sorted((s, b) + tuple(v) for (s, b), v in doc(os.path.join(t2, "app.db"))[4].items()) != mr1:
                kq["van_de"].append("K8:khong_tat_dinh_csdl_moi")
            c.xoa(t2)
        # K6: hoán vị thứ tự nguyện vọng, giữ tập
        if i % 5 == 1:
            t3 = tempfile.mkdtemp(prefix="s4c_")
            api3 = c.tao_api(t3, p["dqt"])
            c.nap_so(api3, xl)
            k = sqlite3.connect(os.path.join(t3, "app.db"))
            rnd = random.Random(i)
            by = collections.defaultdict(list)
            for sid, cid, rk in k.execute("SELECT student_id, club_id, rank FROM preferences"):
                by[sid].append((rk, cid))
            for sid, lst in by.items():
                ranks = [r_ for r_, _ in lst]
                cids = [c_ for _, c_ in lst]
                rnd.shuffle(cids)
                for rk, cid in zip(ranks, cids):
                    k.execute("UPDATE preferences SET rank=? WHERE student_id=? AND club_id=?", (rk + 1000, sid, cid))
                for rk, cid in zip(ranks, cids):
                    k.execute("UPDATE preferences SET rank=? WHERE student_id=? AND club_id=?", (rk, sid, cid))
            k.commit()
            k.close()
            do.ds.clear()
            r3 = api3.run_pipeline(42)
            if r3["ok"]:
                if {cid: l for cid, l in do.ds.items()} != ds_uu:
                    kq["van_de"].append("K6:uu_tien_doi_khi_hoan_vi_nguyen_vong")
            else:
                ma3 = [e.get("code") if isinstance(e, dict) else "?" for e in r3["errors"]][:2]
                if "blocking_pair" in ma3:
                    kq["van_de"].append("K1:cap_pha_vo_sau_hoan_vi")
            c.xoa(t3)
        # K7 chèn em muộn (bộ không Điểm quyết tâm)
        if not p["dqt"] and i % 4 == 0:
            k = sqlite3.connect(db)
            clb0 = [r_[0] for r_ in k.execute("SELECT club_id FROM clubs ORDER BY club_id LIMIT 1")]
            k.close()
            moi = ["MUON%02d" % j for j in range(3)]
            for m in moi:
                api.create_student_if_missing(m, "Em muộn " + m)
                api.submit_preferences(m, clb0)
            r4 = api.run_pipeline(42)
            if not r4["ok"]:
                kq["van_de"].append("K7:chay_sau_khi_them_em_muon_that_bai:%s" % [
                    e.get("code") if isinstance(e, dict) else "?" for e in r4["errors"]][:2])
            else:
                k = sqlite3.connect(db)
                stb3 = dict(k.execute("SELECT student_id, stb_number FROM students"))
                k.close()
                cu = sorted((s for s in stb if True), key=lambda s: stb[s])
                cu3 = sorted(cu, key=lambda s: stb3[s])
                if cu != cu3:
                    kq["van_de"].append("K7:thu_tu_tuong_doi_em_cu_doi")
                if sorted(stb3.values()) != list(range(n + 3)):
                    kq["van_de"].append("K7:stb_sau_chen_khong_la_hoan_vi")
        return kq
    except Exception as e:
        kq["van_de"].append("SAP:%r" % (e,))
        return kq
    finally:
        do.go()
        c.xoa(thu_muc)


# ---------------------------------------------------------------- tự kiểm bộ kiểm
def tu_kiem():
    """Phá cố ý KẾT QUẢ trong một CSDL tạm (không đụng mã sản phẩm) để chắc bộ kiểm có bắt được."""
    kq = {}
    p = dict(n_hs=40, t=4, n_buoi=1, dqt=False, du_tru=0.8, choi=0.9, seed=424242)
    thu_muc = tempfile.mkdtemp(prefix="s4_tk_")
    do = Do().cai()
    try:
        xl, _ = dung_bo(p, thu_muc)
        api = c.tao_api(thu_muc, False)
        c.nap_so(api, xl)
        do.ds.clear()
        api.run_pipeline(42)
        ds = dict(do.ds)
        db = os.path.join(thu_muc, "app.db")
        kq["sach"] = kiem_bo(db, ds)
        clubs, hs, prefs, diem, match = doc(db)
        k = sqlite3.connect(db)
        # (a) cho một em trúng CLB khác trong nguyện vọng làm CLB đó vượt chỉ tiêu / tạo cặp phá vỡ
        da = False
        for (sid, buoi), (cid, tier, _r) in list(match.items()):
            for cid2 in prefs.get(sid, []):
                if cid2 != cid:
                    k.execute("UPDATE match_results SET club_id=? WHERE student_id=? AND buoi=?", (cid2, sid, buoi))
                    da = True
                    break
            if da:
                break
        k.commit()
        kq["a_doi_clb_mot_em"] = sorted(set(x.split(":")[0] for x in kiem_bo(db, ds)))
        # (b) gán 'reserve' cho em không đúng nhóm
        k.execute("UPDATE match_results SET matched_tier='reserve' WHERE rowid IN "
                  "(SELECT rowid FROM match_results WHERE club_id IS NOT NULL LIMIT 3)")
        k.commit()
        kq["b_gan_du_tru_bua"] = sorted(set(x.split(":")[0] for x in kiem_bo(db, ds)))
        # (c) bỏ trống chỗ của mọi em (xoá kết quả) → mọi em có cặp phá vỡ
        k.execute("UPDATE match_results SET club_id=NULL")
        k.commit()
        kq["c_bo_trong_het"] = sorted(set(x.split(":")[0] for x in kiem_bo(db, ds)))
        k.close()
    finally:
        do.go()
        c.xoa(thu_muc)
    return kq


# ---------------------------------------------------------------- trùng khít e08af78
def trung_khit(so_seed):
    sys.path.insert(0, os.path.join(c.GOC, ".claude", "skills", "soat-ma", "scripts"))
    import kiem_nhanh as kn
    tam = tempfile.mkdtemp(prefix="s4_cu_")
    try:
        loi = kn._giai_nen_nhanh(c.GOC, "e08af78", tam)
        if loi:
            return {"loi": loi}
        seeds = tuple(range(1, so_seed + 1))
        ok, ds = kn.kiem_trung_khit(c.GOC, tam, seeds, 3)
        return {"ok": ok, "chi_tiet": ds, "so_seed": so_seed, "so_bo": 3}
    finally:
        shutil.rmtree(tam, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    ap.add_argument("--so-bo", type=int, default=0)
    ap.add_argument("--khong-trung-khit", action="store_true")
    ap.add_argument("--lai", type=int, default=-1, help="chạy lại đúng bộ thứ i")
    a = ap.parse_args()
    if a.lai >= 0:
        print(json.dumps(chay_mot_bo(a.lai, False), ensure_ascii=False, indent=1))
        return
    n = a.so_bo or (60 if a.nhanh else 2000)
    tat_ca = []
    for i in range(n):
        tat_ca.append(chay_mot_bo(i, a.nhanh))
        if (i + 1) % 100 == 0:
            print("  ... %d/%d" % (i + 1, n), flush=True)
    dem = collections.Counter()
    for k in tat_ca:
        dem["bo"] += 1
        if k["tham_so"]["dqt"]:
            dem["bo_co_dqt"] += 1
        if k["tham_so"]["du_tru"] > 0:
            dem["bo_co_du_tru"] += 1
        if k["tham_so"]["n_buoi"] > 1:
            dem["bo_nhieu_buoi"] += 1
        if k["van_de"]:
            dem["bo_co_van_de"] += 1
        for v in set(x.split(":")[0] for x in k["van_de"]):
            dem[v] += 1
    c.in_bang("Nhóm 4 — %d bộ ngẫu nhiên" % n, ["chỉ số", "số bộ"], sorted(dem.items()))
    xau = [k for k in tat_ca if k["van_de"]]
    print("\nBộ có vấn đề (%d) — tái hiện: python %s --lai I" % (len(xau), os.path.relpath(__file__)))
    for k in xau[:40]:
        print("  i=%d %s -> %s" % (k["i"], json.dumps(k["tham_so"], ensure_ascii=False), k["van_de"][:3]))
    out = {"may_do": c.may_do(), "so_bo": n, "tong": dict(dem), "bo_co_van_de": xau}
    out["tu_kiem_bo_kiem"] = tu_kiem()
    print("\nTự kiểm bộ kiểm (phá cố ý CSDL tạm):", json.dumps(out["tu_kiem_bo_kiem"], ensure_ascii=False))
    if not a.khong_trung_khit:
        print("\nTrùng khít với e08af78 (tắt Điểm quyết tâm) ...", flush=True)
        out["trung_khit_e08af78"] = trung_khit(3 if a.nhanh else 20)
        print(json.dumps(out["trung_khit_e08af78"], ensure_ascii=False, indent=1))
    print("\nGhi:", c.ghi_json("s4_dung_dan_nhanh" if a.nhanh else "s4_dung_dan", out))


if __name__ == "__main__":
    main()
