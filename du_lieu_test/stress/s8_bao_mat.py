# -*- coding: utf-8 -*-
"""Nhóm 8 — Bảo mật / tấn công vào `browser_host.py`. CHỈ ĐO, không sửa gì. Dữ liệu MÔ PHỎNG.

    python du_lieu_test/stress/s8_bao_mat.py [--nhanh]

Máy chủ chạy trong MỘT TIẾN TRÌNH CON (để tải của máy khách không tranh GIL với máy chủ), trên
thư mục cát riêng. Mọi tệp ghi ra được so với ảnh chụp cây thư mục cát trước / sau.

  T1  tải dồn dập: 1.000 yêu cầu/giây trong 10 giây (4 tiến trình máy khách);
  T2  token sai / thiếu / rỗng / không ASCII / quá dài / trùng tiêu đề / đặt trong URL;
  T3  thân yêu cầu: 50 MB, Content-Length lạ, JSON hỏng, args sai kiểu, lồng sâu, kết nối treo;
  T4  tên phương thức: `_...`, dunder, không có, thuộc tính không gọi được, đường dẫn, rất dài;
  T5  workspace .zip độc: zip bomb, zip slip, đường tuyệt đối, symlink, mã hoá, tệp quá nhiều, tiêu đề nói dối;
  T6  đường xuất có `..`, tuyệt đối, NUL, quá dài — tệp rơi ở đâu;
  T7  rò rỉ: lỗi có chứa vết ngăn xếp / đường dẫn máy; kích thước nhật ký lỗi sau N yêu cầu lỗi.
"""

import argparse
import base64
import io
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import urllib.parse
import time
import zipfile
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _chung as c  # noqa: E402

CHA_SERVER = r'''
import os, sys, time
sys.path.insert(0, %(goc)r); sys.path.insert(0, %(ay)r)
os.environ["RBDA_THU_MUC_TAI_VE"] = %(tai_ve)r
import _chung as c
import workspace as ws
from api import PipelineAPI
import browser_host
root = %(root)r
slug = ws.tao(root, "Thu stress")
api = PipelineAPI(ws.duong_dan_db(root, slug), thu_muc_xuat=%(tai_ve)r, thu_muc_goc_ws=root)
r = c.nap_so(api, %(so)r); assert r["ok"], r
assert api.run_pipeline(42)["ok"]
url = browser_host.serve(api, %(goc)r, "index.html", open_browser=False)
print("URL " + url, flush=True)
while True:
    time.sleep(3600)
'''


def http(cong, duong, than=b"", tieu_de=None, phuong_thuc="POST", doc_het=True, timeout=30, gui_tho=None):
    """Gửi một yêu cầu bằng socket thô. Trả (mã, tiêu đề dict, thân bytes, giây) hoặc (None, ..., lỗi)."""
    t = time.perf_counter()
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", cong))
        if gui_tho is not None:
            s.sendall(gui_tho)
        else:
            th = {"Host": "127.0.0.1:%d" % cong, "Content-Type": "application/json",
                  "Content-Length": str(len(than))}
            th.update(tieu_de or {})
            dau = ("%s %s HTTP/1.1\r\n" % (phuong_thuc, duong)).encode("latin-1", "replace")
            for k, v in th.items():
                if v is None:
                    continue
                dau += k.encode() + b": " + (v if isinstance(v, bytes) else str(v).encode("latin-1", "replace")) + b"\r\n"
            try:
                s.sendall(dau + b"\r\n")
                if than:
                    for i in range(0, len(than), 1 << 20):
                        s.sendall(than[i:i + (1 << 20)])
            except (BrokenPipeError, ConnectionResetError):
                pass          # máy chủ đã trả lời và đóng trước khi nhận hết thân: vẫn đọc phản hồi
        buf = b""
        while doc_het:
            try:
                d = s.recv(1 << 16)
            except socket.timeout:
                break
            if not d:
                break
            buf += d
        if not buf:
            return None, {}, b"", time.perf_counter() - t, "dong_ket_noi_khong_tra_loi"
        dau_tra, _, thanr = buf.partition(b"\r\n\r\n")
        dong = dau_tra.split(b"\r\n")
        ma = int(dong[0].split()[1])
        h = {}
        for l in dong[1:]:
            if b":" in l:
                k, v = l.split(b":", 1)
                h[k.decode("latin-1").lower()] = v.strip().decode("latin-1")
        return ma, h, thanr, time.perf_counter() - t, ""
    except (OSError, ValueError) as e:
        return None, {}, b"", time.perf_counter() - t, repr(e)[:100]
    finally:
        s.close()


def goi_api(cong, token, ten, args=(), **kw):
    body = json.dumps({"args": list(args)}).encode()
    return http(cong, "/__api__/" + ten, body, {"X-Kiosk-Token": token}, **kw)


def song(cong, token):
    ma, _h, th, _g, _e = goi_api(cong, token, "get_dashboard_status", timeout=10)
    return ma == 200 and b'"ok"' in th


def rss_kb(pid):
    try:
        for l in open("/proc/%d/status" % pid):
            if l.startswith("VmRSS"):
                return int(l.split()[1])
    except OSError:
        return None


def so_luong(pid):
    try:
        for l in open("/proc/%d/status" % pid):
            if l.startswith("Threads"):
                return int(l.split()[1])
    except OSError:
        return None


def chup(thu_muc):
    ra = {}
    for g, ds, fs in os.walk(thu_muc, followlinks=False):
        for f in fs + ds:
            p = os.path.join(g, f)
            try:
                st = os.lstat(p)
                ra[p] = (st.st_size, int(st.st_mtime_ns))
            except OSError:
                pass
    return ra


def moi_sau(truoc, sau):
    return sorted(p for p in sau if p not in truoc or truoc[p] != sau[p])


def tai_dan_dap(cong, token, giay, rps_moi_tien_trinh, hang):
    sys.stdout = open(os.devnull, "w")
    xong = time.perf_counter() + giay
    gian = 1.0 / rps_moi_tien_trinh
    ok = loi = 0
    do = []
    mo = time.perf_counter()
    n = 0
    body = json.dumps({"args": []}).encode()
    while time.perf_counter() < xong:
        muc_tieu = mo + n * gian
        d = muc_tieu - time.perf_counter()
        if d > 0:
            time.sleep(d)
        ma, _h, _t, g, _e = http(cong, "/__api__/get_dashboard_status", body,
                                 {"X-Kiosk-Token": token}, timeout=15)
        n += 1
        if ma == 200:
            ok += 1
        else:
            loi += 1
        do.append(g)
    hang.put((n, ok, loi, do))


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))] if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true")
    ap.add_argument("--cho-treo", type=int, default=0, help="giây chờ khi có kết nối treo (mặc định 60; --nhanh: 3)")
    a = ap.parse_args()
    gay_t1 = 3 if a.nhanh else 10

    cat = tempfile.mkdtemp(prefix="s8_")
    root = os.path.join(cat, "ws_goc")
    tai_ve = os.path.join(cat, "tai_ve")
    ngoai = os.path.join(cat, "ngoai")
    for d in (root, tai_ve, ngoai):
        os.makedirs(d)
    p_so, _c, _h = c.sinh_bo(120, 8, 2, 8008, False, cat)
    ma = CHA_SERVER % {"goc": c.GOC, "ay": c.AY, "tai_ve": tai_ve, "root": root, "so": p_so}
    sv = subprocess.Popen([sys.executable, "-c", ma], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    import atexit
    atexit.register(sv.kill)
    dong = sv.stdout.readline().strip()
    if not dong.startswith("URL "):
        print("Máy chủ không lên:", sv.stderr.read()[-500:])
        return
    url = dong[4:]
    cong = int(re.search(r":(\d+)/", url).group(1))
    token = re.search(r"t=([^&]+)", url).group(1)
    pid = sv.pid
    KQ = {"may_do": c.may_do(), "cong": cong}
    bang = []   # (nhóm, kiểm gì, quan sát, dấu hiệu)

    def ghi(nhom, kiem, quan_sat, dau_hieu):
        bang.append([nhom, kiem, str(quan_sat)[:110], dau_hieu])

    assert song(cong, token)
    chup(cat)
    rss0 = rss_kb(pid)
    thr0 = so_luong(pid)

    # ---------------------------------------------------------------- T1
    ctx = mp.get_context("fork")
    hang = ctx.Queue()
    n_tt = 4
    t0 = time.perf_counter()
    ps = [ctx.Process(target=tai_dan_dap, args=(cong, token, gay_t1, 1000 // n_tt, hang)) for _ in range(n_tt)]
    [p.start() for p in ps]
    kq_tt = [hang.get() for _ in ps]
    [p.join() for p in ps]
    dt = time.perf_counter() - t0
    n = sum(k[0] for k in kq_tt)
    ok = sum(k[1] for k in kq_tt)
    lat = [x for k in kq_tt for x in k[3]]
    T1 = {"giay": round(dt, 2), "gui": n, "rps_thuc": round(n / dt, 1), "ok_200": ok, "khong_200": n - ok,
          "do_tre_ms": {"p50": round(pct(lat, .5) * 1000, 1), "p95": round(pct(lat, .95) * 1000, 1),
                        "p99": round(pct(lat, .99) * 1000, 1), "max": round(max(lat) * 1000, 1)},
          "rss_truoc_kb": rss0, "rss_sau_kb": rss_kb(pid), "luong_truoc": thr0, "luong_sau": so_luong(pid)}
    KQ["T1_tai_dan_dap"] = T1
    ghi("T1", "1000 yêu cầu/s × %d s: máy chủ còn sống" % gay_t1, song(cong, token), "OK" if song(cong, token) else "LỆCH")
    ghi("T1", "đạt tải / số 200", "%.0f rps thực, %d/%d 200, p99 %.0f ms" % (T1["rps_thuc"], ok, n, T1["do_tre_ms"]["p99"]), "ghi nhận")

    # ---------------------------------------------------------------- T2 token
    def thu_token(ten, tieu_de=None, duong="/__api__/get_dashboard_status", gui_tho=None):
        r = http(cong, duong, b'{"args": []}', tieu_de, gui_tho=gui_tho, timeout=10)
        return r
    t2 = {}
    cac = {
        "thieu": {}, "rong": {"X-Kiosk-Token": ""}, "sai": {"X-Kiosk-Token": "x" * 32},
        "dai_1MB": {"X-Kiosk-Token": "A" * (1 << 20)},
        "khac_do_dai": {"X-Kiosk-Token": token[:-1]},
        "token_dung_them_ky_tu": {"X-Kiosk-Token": token + "x"},
        "ten_khac": {"X-Token": token},
    }
    for ten, th in cac.items():
        r = thu_token(ten, th)
        t2[ten] = r[0] if r[0] else r[4]
    # không ASCII (UTF-8 thô) — cần socket thô
    raw = ("POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Length: 2\r\n"
           "X-Kiosk-Token: " % cong).encode() + "tôkén-é".encode("utf-8") + b"\r\n\r\n{}"
    r = http(cong, "", gui_tho=raw, timeout=10)
    t2["khong_ascii_utf8"] = r[0] if r[0] else r[4]
    raw2 = raw.replace("tôkén-é".encode(), b"\xff\xfe\x80")
    r = http(cong, "", gui_tho=raw2, timeout=10)
    t2["byte_ngoai_ascii"] = r[0] if r[0] else r[4]
    raw3 = ("POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Length: 2\r\n"
            "X-Kiosk-Token: sai\r\nX-Kiosk-Token: %s\r\n\r\n{}" % (cong, token)).encode()
    r = http(cong, "", gui_tho=raw3, timeout=10)
    t2["hai_tieu_de_token(sai roi dung)"] = r[0] if r[0] else r[4]
    r = http(cong, "/__api__/get_dashboard_status?t=" + token, b"{}", {}, timeout=10)
    t2["token_chi_o_url_khi_goi_api"] = r[0] if r[0] else r[4]
    r = http(cong, "/__api__/get_dashboard_status", b"{}", {"X-Kiosk-Token": token, "Host": "evil.example.com"}, timeout=10)
    t2["host_la(token_dung)"] = r[0] if r[0] else r[4]
    r = http(cong, "/__api__/get_dashboard_status", b"{}", {"X-Kiosk-Token": token, "Host": "localhost:%d" % cong}, timeout=10)
    t2["host_localhost_dung"] = r[0] if r[0] else r[4]
    # GET trang HTML không token / token sai / token không ASCII
    t2["GET_index_khong_token"] = http(cong, "/index.html", phuong_thuc="GET", timeout=10)[0]
    t2["GET_index_token_sai"] = http(cong, "/index.html?t=sai", phuong_thuc="GET", timeout=10)[0]
    raw4 = ("GET /index.html?t=%%C3%%A9 HTTP/1.1\r\nHost: 127.0.0.1:%d\r\n\r\n" % cong).encode()
    r = http(cong, "", gui_tho=raw4, timeout=10)
    t2["GET_index_token_khong_ascii_url"] = r[0] if r[0] else r[4]
    raw5 = ("GET /__alive__?t=\u00e9 HTTP/1.1\r\nHost: 127.0.0.1:%d\r\n\r\n" % cong).encode("utf-8")
    r = http(cong, "", gui_tho=raw5, timeout=5)
    t2["GET_alive_token_khong_ascii"] = r[0] if r[0] else r[4]
    for tep in ("/app.db", "/../app.db", "/%2e%2e/app.db", "/loi_ung_dung.txt", "/workspaces/", "/.git/config",
                "/..%2f..%2fetc/passwd", "/rbda_priority_pipeline.py", "/api.py", "/CLAUDE.md"):
        r = http(cong, tep + ("?t=" + token), phuong_thuc="GET", timeout=10)
        t2["GET " + tep] = r[0] if r[0] else r[4]
    KQ["T2_token"] = t2
    for k, v in t2.items():
        mong_doi = {"thieu": 403, "rong": 403, "sai": 403, "khac_do_dai": 403, "token_dung_them_ky_tu": 403,
                    "ten_khac": 403, "token_chi_o_url_khi_goi_api": 403, "host_la(token_dung)": 403,
                    "host_localhost_dung": 200, "hai_tieu_de_token(sai roi dung)": 403,
                    "GET_index_khong_token": 403, "GET_index_token_sai": 403}.get(k)
        if k.startswith("GET /"):
            dh = "OK" if v in (403, 404) else "XEM"
        elif mong_doi is None:
            dh = "OK" if v in (403, 400, 431) else "XEM"
        else:
            dh = "OK" if v == mong_doi else "LỆCH"
        if k in ("khong_ascii_utf8", "byte_ngoai_ascii", "GET_index_token_khong_ascii_url",
                 "GET_alive_token_khong_ascii", "dai_1MB"):
            dh = "OK" if isinstance(v, int) and v in (400, 403, 431) else "LỆCH"
        ghi("T2", "token: " + k, v, dh)
    ghi("T2", "còn sống sau cả nhóm token", song(cong, token), "OK" if song(cong, token) else "LỆCH")

    # ---------------------------------------------------------------- T3 thân yêu cầu
    t3 = {}
    r = goi_api(cong, token, "get_dashboard_status", timeout=10)
    t3["bình thường"] = r[0]
    big = b'{"args": ["' + b"A" * (50 * 1024 * 1024) + b'"]}'
    t = time.perf_counter()
    r = http(cong, "/__api__/get_dashboard_status", big, {"X-Kiosk-Token": token}, timeout=60)
    t3["50MB_body"] = {"ma": r[0] or r[4], "giay": round(time.perf_counter() - t, 2)}
    del big
    for ten, cl in (("CL_khong_so", "abc"), ("CL_am", "-5"), ("CL_khong_lo", str(10 ** 12)), ("CL_32MB+1", str(32 * 1024 * 1024 + 1))):
        raw = ("POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Length: %s\r\n"
               "X-Kiosk-Token: %s\r\n\r\n" % (cong, cl, token)).encode()
        r = http(cong, "", gui_tho=raw, timeout=10)
        t3[ten] = r[0] or r[4]
    # CL nhỏ hơn thân thật
    raw = ("POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Length: 3\r\n"
           "X-Kiosk-Token: %s\r\n\r\n{\"args\": []}" % (cong, token)).encode()
    t3["CL_ngắn_hơn_thân"] = (http(cong, "", gui_tho=raw, timeout=10)[0])
    # CL lớn hơn thân thật, không gửi đủ → treo tới timeout phía máy chủ?
    raw = ("POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Length: 1000\r\n"
           "X-Kiosk-Token: %s\r\n\r\n{}" % (cong, token)).encode()
    t = time.perf_counter()
    r = http(cong, "", gui_tho=raw, timeout=(a.cho_treo or 60) if not a.nhanh or a.cho_treo else 8)
    t3["CL_lớn_hơn_thân(không gửi đủ)"] = {"ma": r[0] or r[4], "giay_treo": round(time.perf_counter() - t, 1)}
    for ten, body in (("json_hong_{", b"{"), ("json_hong_rac", b"\xff\xfe\x00"), ("json_la_list", b"[1,2]"),
                      ("json_null", b"null"), ("json_so", b"5"), ("args_so", b'{"args": 5}'),
                      ("args_chuoi", b'{"args": "abc"}'), ("args_doi_tuong", b'{"args": {"a": 1}}'),
                      ("args_thua", b'{"args": [1,2,3,4,5,6,7,8]}'),
                      ("NaN", b'{"args": [NaN]}'), ("so_khong_lo", b'{"args": [' + b"9" * 5000 + b"]}"),
                      ("long_sau_100k", b'{"args": ' + b"[" * 100000 + b"]" * 100000 + b"}")):
        r = http(cong, "/__api__/get_run_history", body, {"X-Kiosk-Token": token}, timeout=15)
        thanr = r[2].decode("utf-8", "replace")
        t3[ten] = {"ma": r[0] or r[4], "than": thanr[:160]}
    KQ["T3_than_yeu_cau"] = t3
    ghi("T3", "50 MB trong thân", t3["50MB_body"], "OK" if t3["50MB_body"]["ma"] == 413 else "LỆCH")
    for k in ("CL_khong_so", "CL_am", "CL_khong_lo", "CL_32MB+1"):
        ghi("T3", k, t3[k], "OK" if t3[k] == 413 else "LỆCH")
    ghi("T3", "Content-Length ngắn hơn thân", t3["CL_ngắn_hơn_thân"], "ghi nhận")
    ghi("T3", "Content-Length lớn hơn thân thật (kết nối treo)", t3["CL_lớn_hơn_thân(không gửi đủ)"], "XEM")
    for k in ("json_hong_{", "json_hong_rac", "json_la_list", "json_null", "json_so", "args_so", "args_chuoi",
              "args_doi_tuong", "args_thua", "NaN", "so_khong_lo", "long_sau_100k"):
        v = t3[k]
        ghi("T3", k, v["ma"], "OK" if v["ma"] in (200, 400, 413) else "LỆCH")
    ghi("T3", "còn sống sau nhóm thân yêu cầu", song(cong, token), "OK" if song(cong, token) else "LỆCH")

    # Kết nối treo (slowloris)
    n_treo = 100 if a.nhanh else 400
    thr_truoc = so_luong(pid)
    treo = []
    for _ in range(n_treo):
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect(("127.0.0.1", cong))
            s.sendall(b"POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nContent-Length: 100\r\n" % cong)
            treo.append(s)
        except OSError:
            break
    time.sleep(1)
    thr_giua = so_luong(pid)
    t = time.perf_counter()
    song_giua = song(cong, token)
    g_song = time.perf_counter() - t
    cho_treo = a.cho_treo or (3 if a.nhanh else 60)
    time.sleep(cho_treo)
    thr_sau30 = so_luong(pid)
    [s.close() for s in treo]
    time.sleep(2)
    KQ["T3_ket_noi_treo"] = {"so_ket_noi": len(treo), "luong_truoc": thr_truoc, "luong_khi_treo": thr_giua,
                             "luong_sau_30s_van_treo": thr_sau30, "luong_sau_dong": so_luong(pid),
                             "phuc_vu_duoc_khi_treo": song_giua, "do_tre_khi_treo_s": round(g_song, 3)}
    ghi("T3", "%d kết nối treo (tiêu đề dở)" % len(treo), "luồng %s→%s→%s sau %d s; còn phục vụ: %s" % (
        thr_truoc, thr_giua, thr_sau30, cho_treo, song_giua), "XEM" if (thr_sau30 or 0) > (thr_truoc or 0) + len(treo) * 0.5 else "ghi nhận")

    # ---------------------------------------------------------------- T4 tên phương thức
    t4 = {}
    ten_la = ["_backup_db", "__init__", "__class__", "__dict__", "_khoa_ghi", "__reduce__", "db_path", "_goc_ws",
              "khong_ton_tai", "", "..", "../x", "%2e%2e%2f", "a" * 100000, "get_dashboard_status%00x",
              "get_dashboard_status ", "GET_DASHBOARD_STATUS", "get_dashboard_status/..", "\u0443\u043a\u0440",
              "_set_window", "run_pipeline;ls", "__getattribute__", "thu_muc_xuat", "_window"]
    for ten in ten_la:
        duong = "/__api__/" + (ten if "%" in ten else urllib.parse.quote(ten, safe="_.-"))
        r = http(cong, duong, b'{"args": []}', {"X-Kiosk-Token": token}, timeout=15)
        t4[ten[:40]] = {"ma": r[0] or r[4], "than": r[2].decode("utf-8", "replace")[:140]}
    KQ["T4_ten_phuong_thuc"] = t4
    for k, v in t4.items():
        ghi("T4", "phương thức «%s»" % k, "%s %s" % (v["ma"], v["than"][:60]),
            "OK" if v["ma"] in (404, 400, 403, 431, 414) else "LỆCH")
    ghi("T4", "còn sống", song(cong, token), "OK" if song(cong, token) else "LỆCH")

    # Duyệt slug workspace
    t4b = {}
    for ten, args in (("open_workspace", ["../x"]), ("open_workspace", ["../../etc"]), ("delete_workspace", [".."]),
                      ("export_workspace", ["../x", ""]), ("rename_workspace", ["../x", "y"]),
                      ("duplicate_workspace", ["../x", "y", True]), ("get_workspace_config", ["../x"])):
        r = goi_api(cong, token, ten, args, timeout=20)
        t4b["%s%s" % (ten, args)] = {"ma": r[0] or r[4], "than": r[2].decode("utf-8", "replace")[:140]}
    KQ["T4_slug_workspace"] = t4b
    for k, v in t4b.items():
        ghi("T4", "slug «%s»" % k, v["than"][:70], "OK" if '"ok": false' in v["than"] else "XEM")

    # ---------------------------------------------------------------- T5 zip độc
    snap5 = chup(cat)

    def zip_bytes(muc, nen=zipfile.ZIP_DEFLATED):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w", nen) as z:
            for ten, noi_dung in muc:
                if isinstance(noi_dung, zipfile.ZipInfo):
                    z.writestr(noi_dung, b"x")
                else:
                    z.writestr(ten, noi_dung)
        return b.getvalue()

    # CSDL hợp lệ làm "app.db" trong zip
    db_hop_le = open(os.path.join(root, "workspaces", os.listdir(os.path.join(root, "workspaces"))[0], "app.db"), "rb").read()
    def zi(ten, kieu=0, ngoai=None):
        zi_ = zipfile.ZipInfo(ten)
        zi_.external_attr = (kieu << 16)
        return zi_
    cac_zip = {}
    cac_zip["tot(đối chứng)"] = zip_bytes([("app.db", db_hop_le)])
    cac_zip["zip_slip_../"] = zip_bytes([("app.db", db_hop_le), ("../ZIPSLIP.txt", b"x")])
    cac_zip["zip_slip_..\\"] = zip_bytes([("app.db", db_hop_le), ("..\\..\\ZIPSLIP2.txt", b"x")])
    cac_zip["tuyet_doi_/tmp"] = zip_bytes([("app.db", db_hop_le), ("/tmp/ZIPABS.txt", b"x")])
    cac_zip["o_dia_C:"] = zip_bytes([("app.db", db_hop_le), ("C:\\x\\ZIPDRIVE.txt", b"x")])
    cac_zip["symlink"] = zip_bytes([("app.db", db_hop_le), (None, zi("link", stat.S_IFLNK | 0o777))])
    cac_zip["symlink_ten_app.db"] = zip_bytes([(None, zi("app.db", stat.S_IFLNK | 0o777))])
    cac_zip["ma_hoa_co"] = None
    cac_zip["khong_co_app.db"] = zip_bytes([("x.txt", b"x")])
    cac_zip["app.db_rac"] = zip_bytes([("app.db", b"khong phai sqlite" * 100)])
    cac_zip["nhieu_tep_50k"] = zip_bytes([("app.db", db_hop_le)] + [("f/%d.txt" % i, b"") for i in range(50000)])
    cac_zip["thu_muc_long_sau"] = zip_bytes([("app.db", db_hop_le), ("/".join(["d"] * 2000) + "/x.txt", b"x")])
    cac_zip["ten_NUL"] = zip_bytes([("app.db", db_hop_le), ("a\x00b.txt", b"x")])
    cac_zip["tep_trung_ten"] = zip_bytes([("app.db", db_hop_le), ("app.db", db_hop_le)])
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("app.db", db_hop_le)
        with z.open("bomb.bin", "w", force_zip64=True) as f:
            blk = b"\x00" * (1 << 20)
            for _ in range(700 if not a.nhanh else 100):
                f.write(blk)
    cac_zip["zip_bomb_700MB(→~700KB)"] = b.getvalue()
    # tiêu đề nói dối: khai file_size nhỏ, thực tế lớn → vá sau khi ghi
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("app.db", db_hop_le)
        z.writestr("noi_doi.bin", b"\x00" * (60 << 20))
    raw = bytearray(b.getvalue())
    cac_zip["tieu_de_noi_doi(60MB khai 10 byte)"] = bytes(raw)   # (đối chứng: không vá, chỉ để đo 60MB)
    # tệp ghi chú ZIP64 giả: không làm
    del cac_zip["ma_hoa_co"]
    hang_ws = {}
    for ten, zb in cac_zip.items():
        t = time.perf_counter()
        r = goi_api(cong, token, "import_workspace", [base64.b64encode(zb).decode(), "x.zip"], timeout=120)
        ds = time.perf_counter() - t
        than = r[2].decode("utf-8", "replace")
        hang_ws[ten] = {"kich_thuoc_zip": len(zb), "ma_http": r[0] or r[4], "giay": round(ds, 2),
                        "than": than[:200], "rss_may_chu_kb": rss_kb(pid), "luong": so_luong(pid)}
    KQ["T5_zip"] = hang_ws
    sau5 = chup(cat)
    la = [p for p in moi_sau(snap5, sau5) if "/ws_goc/workspaces/" not in p or "ZIP" in p or "_nhap-" in p]
    la_ngoai = [p for p in la if not p.startswith(os.path.join(root, "workspaces"))]
    KQ["T5_tep_moi_ngoai_thu_muc_workspaces"] = la_ngoai[:10]
    for ten, v in hang_ws.items():
        nhan = v["than"].count('"ok": true') > 0
        doc_hai = ten.startswith(("zip_slip", "tuyet_doi", "o_dia", "symlink", "khong_co_app", "app.db_rac", "thu_muc_long"))
        if ten.startswith("tot"):
            dh = "ghi nhận (đối chứng)"
        elif doc_hai:
            dh = "OK" if not nhan else "LỆCH"
        else:
            dh = "XEM" if nhan else "OK"          # bom / nhiều tệp / tên lạ: ghi nhận tài nguyên đã dùng
        ghi("T5", "zip «%s» (%d KB)" % (ten, v["kich_thuoc_zip"] // 1024),
            ("nhận" if nhan else "từ chối") + "; %.1f s; RSS máy chủ %d MB" % (v["giay"], (v["rss_may_chu_kb"] or 0) // 1024), dh)
    ghi("T5", "tệp mới ngoài thư mục workspaces/ sau mọi zip", la_ngoai[:3] or "không", "OK" if not la_ngoai else "LỆCH")
    for dd in ("/tmp/ZIPABS.txt", os.path.join(os.path.dirname(root), "ZIPSLIP.txt"), os.path.join(root, "ZIPSLIP.txt"),
               os.path.join(os.path.dirname(os.path.dirname(root)), "ZIPSLIP.txt")):
        if os.path.exists(dd):
            ghi("T5", "tệp thoát khỏi thư mục tạm: " + dd, "TỒN TẠI", "LỆCH")
    ghi("T5", "còn sống sau nhóm zip", song(cong, token), "OK" if song(cong, token) else "LỆCH")

    # ---------------------------------------------------------------- T6 đường xuất
    t6 = {}
    snap6 = chup(cat)
    nan_hai = os.path.join(ngoai, "NAN_NHAN.xlsx")
    open(nan_hai, "w").write("TEP_CO_SAN_CUA_NAN_NHAN")
    cac_path = {
        "..\\..": "../../ESC1.xlsx", "..\\ kiểu Windows": "..\\..\\ESC2.xlsx", "thu_muc_con/../..": "sub/../../ESC3.xlsx",
        "tuyệt đối ra ngoài": os.path.join(ngoai, "ABS.xlsx"), "tuyệt đối ghi đè tệp có sẵn": nan_hai,
        "NUL": "a\x00b.xlsx", "rất dài 5000": "x" * 5000 + ".xlsx", "thư mục": ngoai, "dấu ~": "~/ESC4.xlsx",
        "tên đặc biệt": "con.xlsx", "chỉ dấu chấm": "..", "rỗng": "",
    }
    for ten, pth in cac_path.items():
        r = goi_api(cong, token, "export_ket_qua", [pth, False], timeout=60)
        t6[ten] = {"ma": r[0] or r[4], "than": r[2].decode("utf-8", "replace")[:220]}
    for ham in ("export_csv", "export_du_lieu_dau_vao", "export_thay_doi_ket_qua", "export_hoc_sinh_csv", "tao_so_nhap_mau"):
        r = goi_api(cong, token, ham, ["../../ESC5_%s" % ham], timeout=60)
        t6[ham + "(../..)"] = {"ma": r[0] or r[4], "than": r[2].decode("utf-8", "replace")[:160]}
    KQ["T6_duong_xuat"] = t6
    sau6 = chup(cat)
    moi = moi_sau(snap6, sau6)
    cho_phep = (tai_ve, os.path.join(root, "workspaces"))
    ngoai_cho_phep = [p for p in moi if not p.startswith(cho_phep)]
    KQ["T6_tep_moi"] = {"tat_ca": [os.path.relpath(p, cat) for p in moi][:30],
                        "ngoai_thu_muc_cho_phep": [os.path.relpath(p, cat) for p in ngoai_cho_phep][:30],
                        "tep_nan_nhan_sau": open(nan_hai, "rb").read()[:40].decode("latin-1")}
    for ten in t6:
        ghi("T6", "xuất «%s»" % ten, "%s %s" % (t6[ten]["ma"], t6[ten]["than"][:60]), "ghi nhận")
    for p in ngoai_cho_phep:
        ghi("T6", "tệp ghi NGOÀI thư mục cho phép", os.path.relpath(p, cat), "XEM (đường tuyệt đối do người dùng chọn là thiết kế)"
            if p.startswith(ngoai) else "LỆCH")
    ghi("T6", "tệp có sẵn bị ghi đè qua đường tuyệt đối", "bị ghi đè" if open(nan_hai, "rb").read()[:4] != b"TEP_" else "nguyên vẹn",
        "XEM" if open(nan_hai, "rb").read()[:4] != b"TEP_" else "OK")
    ghi("T6", "tệp thoát ra trên cây thư mục chứa cát (../../ESC*)",
        [p for p in ("ESC1.xlsx", "ESC2.xlsx", "ESC3.xlsx", "ESC4.xlsx") if any(x.endswith(p) and not x.startswith(cho_phep) for x in moi)] or "không",
        "OK")

    # ---------------------------------------------------------------- T7 rò rỉ
    log_files = [os.path.join(g, f) for g, _d, fs in os.walk(cat) for f in fs if f.startswith("loi_ung_dung")]
    kich_truoc = sum(os.path.getsize(p) for p in log_files)
    n_loi = 200 if a.nhanh else 2000
    for i in range(n_loi):
        http(cong, "/__api__/get_run_history", b"{", {"X-Kiosk-Token": token}, timeout=10)
    log_files2 = [os.path.join(g, f) for g, _d, fs in os.walk(cat) for f in fs if f.startswith("loi_ung_dung")]
    kich_sau = sum(os.path.getsize(p) for p in log_files2)
    ro = []

    def quet(nhom, k, than):
        """Chỉ quét phần LỖI (errors) của phản hồi ok=false; đường dẫn trong dữ liệu thành công là đường xuất."""
        try:
            j = json.loads(than)
        except Exception:
            j = None
        if isinstance(j, dict) and j.get("ok") is False:
            blob = json.dumps(j.get("errors"), ensure_ascii=False)
        elif j is None:
            if '"ok": false' not in than:
                return            # thân bị cắt của phản hồi thành công (đường xuất): không phải lỗi
            blob = than
        else:
            return
        for mau in ("Traceback", 'File "', "/home/", cat, "C:\\\\Users", '.py", line'):
            if mau in blob:
                ro.append((nhom, k, mau))
    for k, v in KQ["T3_than_yeu_cau"].items():
        if isinstance(v, dict) and "than" in v:
            quet("T3", k, v["than"])
    for k, v in KQ["T4_ten_phuong_thuc"].items():
        quet("T4", k, v["than"])
    for k, v in hang_ws.items():
        quet("T5", k, v["than"])
    for k, v in t6.items():
        quet("T6", k, v["than"])
    rieng_detail = [(k, v["than"]) for k, v in KQ["T3_than_yeu_cau"].items()
                    if isinstance(v, dict) and "loi_ngoai_du_kien" in v.get("than", "")]
    KQ["T7_chi_tiet_ngoai_le_python_trong_phan_hoi"] = [(k, t[:240]) for k, t in rieng_detail]
    KQ["T7_ro_ri"] = {"mau_ro_ri": ro[:20], "so_yeu_cau_loi": n_loi, "nhat_ky_loi_truoc_byte": kich_truoc,
                      "nhat_ky_loi_sau_byte": kich_sau, "so_tep_nhat_ky": len(log_files2),
                      "byte_moi_yeu_cau_loi": round((kich_sau - kich_truoc) / n_loi, 1)}
    ghi("T7", "vết ngăn xếp / đường dẫn máy trong phần LỖI của phản hồi", ro[:3] or "không thấy", "OK" if not ro else "LỆCH")
    ghi("T7", "thông điệp ngoại lệ Python nguyên văn (detail=str(e)) trong phản hồi lỗi",
        "%d/%d phản hồi lỗi thân yêu cầu" % (len(rieng_detail), sum(1 for v in KQ["T3_than_yeu_cau"].values() if isinstance(v, dict))),
        "XEM" if rieng_detail else "OK")
    ghi("T7", "nhật ký lỗi tăng sau %d yêu cầu lỗi" % n_loi, "%d → %d byte (%.0f B/yêu cầu)" % (
        kich_truoc, kich_sau, (kich_sau - kich_truoc) / n_loi), "XEM" if kich_sau - kich_truoc > 0 else "OK")
    ghi("T7", "còn sống cuối cùng", song(cong, token), "OK" if song(cong, token) else "LỆCH")
    KQ["rss_cuoi_kb"] = rss_kb(pid)
    KQ["bang"] = bang

    sv.terminate()
    try:
        sv.wait(10)
    except Exception:
        sv.kill()
    loi_sv = (sv.stderr.read() or "")[-1500:]
    KQ["stderr_may_chu_cuoi"] = loi_sv
    c.in_bang("Nhóm 8 — bảo mật / tấn công browser_host", ["nhóm", "kiểm gì", "quan sát", "dấu hiệu"], bang)
    print("\nstderr máy chủ (cuối): %s" % (loi_sv[-600:] or "(trống)"))
    p = c.ghi_json("s8_bao_mat_nhanh" if a.nhanh else "s8_bao_mat", KQ)
    print("\nGhi:", p)
    shutil.rmtree(cat, ignore_errors=True)


if __name__ == "__main__":
    main()
