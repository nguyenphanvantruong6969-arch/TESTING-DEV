# -*- coding: utf-8 -*-
"""FA-SC (sự cố do con người): phần dùng chung của các kịch bản diễn tập. Dữ liệu hoàn toàn MÔ PHỎNG.

Dựng một đợt FA-DAA giả theo đường B (đăng ký bằng Forms, mỗi ngày một tệp; một tệp bài thi), chạy bộ chuyển đổi
THẬT (`chuyen_fa_daa`) và kiosk THẬT (`PipelineAPI`) trên một thư mục tạm. Chỉ ĐỌC mã sản phẩm; không sửa gì trong kho.

Mỗi ngày của `de_thi.json` có ba CLB: CLB thứ nhất có đề -> Tuyển chọn (điểm sàn 5), CLB thứ hai -> Giới hạn (bỏ đề),
CLB không đề -> Tự do. Một "đợt" là một dict:
    {"hs": [ {sid, email, ten, nv: {buoi: [club_id x3]}, vang: {buoi: club_id}, thi: {club_id: (số câu đúng, giây)}} ],
     "cho": {club_id: chỉ tiêu}}
Kịch bản sửa dict này (gài lỗi) rồi gọi `chay(dot, thu_muc)`.
"""
import base64
import copy
import datetime
import os
import random
import sqlite3
import sys

import openpyxl

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (GOC, os.path.join(GOC, "mau_forms_thi_clb")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bieu_mau as bm  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402
from api import PipelineAPI  # noqa: E402

SO_HS = 120
SEED = 42
CHO_TUYEN_CHON = 20
CHO_GIOI_HAN = 30
DIEM_SAN = 5
GIO_MO = datetime.datetime(2026, 11, 9, 8, 0, 0)


def de_fa():
    """(de, loai): bản sao de_thi.json với CLB thứ hai mỗi ngày bỏ đề; loai {club_id: loại FA}."""
    de = copy.deepcopy(bm.doc_de_thi())
    loai = {}
    for b in de["buoi"]:
        co_de = [c for c in de["cau_lac_bo"] if c["buoi"] == b["ma"] and c["de_thi"]]
        for c in de["cau_lac_bo"]:
            if c["buoi"] != b["ma"]:
                continue
            if co_de and c is co_de[0]:
                loai[c["club_id"]] = so_nhap.TUYEN_CHON
            elif c["de_thi"]:
                c["de_thi"] = []
                loai[c["club_id"]] = so_nhap.GIOI_HAN
            else:
                loai[c["club_id"]] = so_nhap.TU_DO
    return de, loai


def sinh_dot(so_hs=SO_HS, seed=SEED):
    """Đợt SẠCH: mỗi em xếp đủ ba CLB mỗi ngày (thích CLB Tuyển chọn hơn), thi mọi CLB Tuyển chọn em xếp."""
    de, loai = de_fa()
    rng = random.Random(seed)
    hs = []
    for i in range(1, so_hs + 1):
        em = {"sid": "HS%03d" % i, "email": "hs%03d@truong.example" % i, "ten": "Em %03d" % i, "nv": {}, "vang": {},
              "thi": {}}
        for b in de["buoi"]:
            clb = [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == b["ma"]]
            trong_so = {c: {so_nhap.TUYEN_CHON: 3.0, so_nhap.GIOI_HAN: 2.0, so_nhap.TU_DO: 1.0}[loai[c]] for c in clb}
            thu_tu = sorted(clb, key=lambda c: -trong_so[c] * rng.random())
            em["nv"][b["ma"]] = thu_tu
            for c in thu_tu:
                if loai[c] == so_nhap.TUYEN_CHON:
                    em["thi"][c] = (rng.choice([1, 2, 3, 3, 4, 4, 5, 5]), rng.randint(420, 780))
        hs.append(em)
    cho = {c: {so_nhap.TUYEN_CHON: CHO_TUYEN_CHON, so_nhap.GIOI_HAN: CHO_GIOI_HAN, so_nhap.TU_DO: so_hs}[k]
           for c, k in loai.items()}
    return {"hs": hs, "cho": cho}


def _lc(de, club_id):
    return bm.lua_chon_clb(next(c for c in de["cau_lac_bo"] if c["club_id"] == club_id))


def ghi_tep(dot, thu_muc, de, loai, phieu_dang_ky_them=(), phieu_thi_them=(), an_email_thi=False):
    """Ghi Sổ nhập CLB, các tệp đăng ký (mỗi ngày một tệp) và một tệp bài thi. Trả (so_clb, [tệp đăng ký], tệp thi).

    `phieu_dang_ky_them`: [(buoi, dict như một em)] phiếu nộp THÊM, ghi SAU các phiếu thường (phiếu cuối được tính).
    `phieu_thi_them`: [(email, {club_id: (đúng, giây)})] phiếu thi thêm, ghi sau. `an_email_thi`: Record name TẮT."""
    os.makedirs(thu_muc, exist_ok=True)
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": dot["cho"][c["club_id"]], "reserve_capacity": 0,
              "reserve_group": "", "buoi": c["buoi"], "loai": loai[c["club_id"]],
              **({"diem_san": DIEM_SAN} if loai[c["club_id"]] == so_nhap.TUYEN_CHON else {})}
             for c in de["cau_lac_bo"]]
    so_clb = os.path.join(thu_muc, "SO_NHAP_CLB_FA.xlsx")
    so_nhap.ghi_so_nhap(so_clb, clubs=clubs)
    tep_dk = []
    for b in de["buoi"]:
        buoi = b["ma"]
        phan = bm.cac_phan_fa(de, buoi)
        tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [c[0] for _, cs in phan for c in cs]
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(tieu)
        ds = [(em, em["nv"].get(buoi)) for em in dot["hs"]] + [(em, em["nv"].get(buoi))
                                                              for bb, em in phieu_dang_ky_them if bb == buoi]
        for em, xep in ds:
            if not xep:
                continue
            o = {"Email": em["email"], "Name": em["ten"], bm.cau_ma_hoc_sinh(): em["sid"], bm.cau_ho_ten(): em["ten"]}
            for k, c in enumerate(xep, 1):
                o[bm.cau_nguyen_vong_fa(de, buoi, k)] = _lc(de, c)
            vang = em.get("vang", {}).get(buoi)
            o[bm.cau_vang_fa(de, buoi)] = _lc(de, vang) if vang else bm.GIU_MAC_DINH_VANG
            o[bm.cau_doi_fa(de, buoi)] = bm.DOI_KHONG
            ws.append([o.get(h, "") for h in tieu])
        p = os.path.join(thu_muc, "dang_ky_%s.xlsx" % buoi)
        wb.save(p)
        tep_dk.append(p)
    clb_thi = bm.clb_co_thi(de)
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"]
    for clb in clb_thi:
        tieu.append(bm.cau_cong_thi(de, clb, chi_thi=True))
        tieu += [bm.cau_de_thi(clb, i) for i in range(1, len(clb["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for email, cac in [(em["email"], em["thi"]) for em in dot["hs"]] + list(phieu_thi_them):
        if not cac:
            continue
        giay = max(g for _, g in cac.values())
        o = {"Email": "anonymous" if an_email_thi else email, "Name": email,
             "Start time": GIO_MO.strftime("%Y-%m-%d %H:%M:%S"),
             "Completion time": (GIO_MO + datetime.timedelta(seconds=giay)).strftime("%Y-%m-%d %H:%M:%S")}
        for clb in clb_thi:
            td = bm.cau_cong_thi(de, clb, chi_thi=True)
            if clb["club_id"] not in cac:
                o[td] = bm.KHONG
                continue
            o[td] = bm.CO
            dung_n = cac[clb["club_id"]][0]
            for i, cau in enumerate(clb["de_thi"], 1):
                dung = i <= dung_n
                o[bm.cau_de_thi(clb, i)] = cau["lua_chon"][cau["dap_an"] if dung
                                                           else (cau["dap_an"] + 1) % len(cau["lua_chon"])]
        ws.append([o.get(h, "") for h in tieu])
    tep_thi = os.path.join(thu_muc, "bai_thi.xlsx")
    wb.save(tep_thi)
    return so_clb, tep_dk, tep_thi


def mo_kiosk(thu_muc, **luat):
    """Kiosk trên CSDL tạm, FA-DAA bật (cần wharton bật)."""
    db = os.path.join(thu_muc, "app.db")
    api = PipelineAPI(db)
    ch.ghi_cau_hinh(db, {"rules": dict({"wharton": True, "fa_daa": True}, **luat)})
    return api, db


def nap(api, duong_so):
    with open(duong_so, "rb") as f:
        return api.import_so_nhap(base64.b64encode(f.read()).decode())


def ket_qua(db):
    """{(student_id, buoi): club_id} của lần chạy mới nhất."""
    con = sqlite3.connect(db)
    try:
        return {(r[0], r[1]): r[2] for r in con.execute("SELECT student_id, buoi, club_id FROM match_results")}
    finally:
        con.close()


def sql(db, cau, tham=()):
    con = sqlite3.connect(db)
    try:
        return con.execute(cau, tham).fetchall()
    finally:
        con.close()


SO_LOP = 6


def danh_sach_that(dot, co_email=True):
    """Danh sách của trường theo SỰ THẬT của đợt (mã và email đúng, 6 lớp 10A1..10A6): [(mã, lớp, email)].
    Dùng cho tuỳ chọn `danh_sach_truong` của `chay` (mặc định TẮT)."""
    return [(h["sid"], "10A%d" % (i % SO_LOP + 1), h["email"] if co_email else "") for i, h in enumerate(dot["hs"], 1)]


def ghi_danh_sach(duong, hang):
    import csv
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "class_id", "email"])
        w.writerows(hang)
    return duong


def chay(dot, thu_muc, seed=SEED, luat=None, danh_sach_truong=None, **ghi):
    """Trọn chuỗi: ghi tệp -> chuyển đổi -> nạp -> chạy. Trả dict; không ném lỗi khi bị chặn (ghi vào `loi`).
    `luat`: thêm khoá vào `rules` của workspace tạm (ví dụ {"fa_diem_danh": True}).
    `danh_sach_truong` (FA-SC L1, mặc định None = TẮT, số liệu cũ không đổi): [(mã, lớp, email)] ghi thành CSV rồi
    đưa cho bộ chuyển đổi; kết quả `bao_cao_danh_sach` có trong dict trả về."""
    de, loai = de_fa()
    so_clb, tep_dk, tep_thi = ghi_tep(dot, thu_muc, de, loai, **ghi)
    ra = {"thu_muc": thu_muc, "loai": loai, "de": de, "canh_bao": [], "loi": [], "ket_qua": {}, "buoc_chan": None}
    kw = {}
    if danh_sach_truong is not None:
        kw["danh_sach_truong"] = ghi_danh_sach(os.path.join(thu_muc, "danh_sach_truong.csv"), danh_sach_truong)
    try:
        kq = cv.chuyen_fa_daa(os.path.join(thu_muc, "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi], **kw)
    except cv.LoiTepXuat as e:
        ra["buoc_chan"], ra["loi"] = "chuyen_doi", [str(e)]
        return ra
    ra["canh_bao"] = [x[2] for x in kq["canh_bao"]]
    ra["canh_bao_day_du"] = kq["canh_bao"]
    ra["bao_cao_danh_sach"] = kq.get("bao_cao_danh_sach")
    api, db = mo_kiosk(thu_muc, **(luat or {}))
    ra["api"], ra["db"] = api, db
    r = nap(api, os.path.join(thu_muc, "nap", cv.TEN_SO))
    if not r["ok"]:
        ra["buoc_chan"], ra["loi"] = "nap_so", [e["code"] for e in r["errors"]]
        return ra
    r = api.run_pipeline(seed=seed)
    if not r["ok"]:
        ra["buoc_chan"], ra["loi"] = "chay_xep", [e["code"] for e in r["errors"]]
        return ra
    ra["ket_qua"] = ket_qua(db)
    return ra


def so_sanh(sach, loi, bo_qua=()):
    """Số (học sinh, ngày) đổi CLB giữa hai lần chạy, không tính các mã trong `bo_qua`. Trả (số ô đổi, số em đổi)."""
    khac = [k for k in set(sach) | set(loi) if k[0] not in bo_qua and sach.get(k) != loi.get(k)]
    return len(khac), len({k[0] for k in khac})


def dem(canh_bao, chuoi):
    return sum(1 for x in canh_bao if chuoi in x)


def in_bang(ten, dong):
    """In một kết quả diễn tập dạng `khoá: giá trị`, đầu ra ổn định để so sánh giữa các lần chạy."""
    print("== %s  [SỐ LIỆU MÔ PHỎNG] ==" % ten)
    for k, v in dong:
        print("  %-46s %s" % (k, v))
    return {"ten": ten, "so_lieu": [[k, v] for k, v in dong]}


def chuyen_va_nap_them(api, dot, thu_muc, de, loai):
    """Xuất lại + chuyển đổi lại + nạp thêm vào kiosk đang có dữ liệu (nạp chỉ CỘNG THÊM). Trả kết quả nạp."""
    so_clb, tep_dk, tep_thi = ghi_tep(dot, thu_muc, de, loai)
    cv.chuyen_fa_daa(os.path.join(thu_muc, "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi])
    return nap(api, os.path.join(thu_muc, "nap", cv.TEN_SO))


def em(dot, sid):
    return next(h for h in dot["hs"] if h["sid"] == sid)


def chon_em_trung_tuyen(dot, sach, loai, buoi="thu_2", hang=1):
    """Em đầu tiên (theo mã) được xếp vào CLB Tuyển chọn của `buoi` và xếp CLB đó ở nguyện vọng thứ `hang`."""
    for h in dot["hs"]:
        c = sach["ket_qua"].get((h["sid"], buoi))
        if c and loai[c] == so_nhap.TUYEN_CHON and h["nv"][buoi][hang - 1] == c:
            return h["sid"], c
    raise ValueError("không có em nào phù hợp; đổi --seed")


def main(dien_tap, mo_ta):
    """Điểm vào chung: `python dXX_....py --ra THU_MUC [--seed N] [--so-hs N]`. Tất định theo seed."""
    import argparse
    import shutil
    ap = argparse.ArgumentParser(description=mo_ta)
    ap.add_argument("--ra", required=True, help="thư mục tạm để ghi tệp giả (KHÔNG dùng thư mục có app.db thật)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--so-hs", type=int, default=SO_HS)
    a = ap.parse_args()
    ra = os.path.abspath(a.ra)
    if os.path.isdir(ra):
        shutil.rmtree(ra)
    os.makedirs(ra)
    return dien_tap(ra, a.seed, a.so_hs)
