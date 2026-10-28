"""A13.9 — sửa các vấn đề của đợt stress test. Mỗi test khoá MỘT mục (số mục = số trong lệnh giao).

  1. CSDL đang bận ≠ cấu hình hỏng; đọc cấu hình chờ khoá ngắn (2–3 s).
  2. browser_host: kết nối treo (gửi dở yêu cầu) bị cắt sau 30–60 s, không giữ luồng mãi.
  3. Token không ASCII (tiêu đề / ?t=) → 403, không ném TypeError.
  9. Skill sinh-du-lieu-clb: > 20 CLB tự sinh tên; ≤ 20 đầu ra giữ nguyên từng byte.
  8. Sổ nhập 0 học sinh / 0 CLB: ok + cảnh báo mới (xem trước và nhập); chạy xếp sau đó không sập.
  7. Nhập .zip workspace: ≤ 1.000 tệp, giải nén ≤ 200 MB, từ chối tên trùng / có NUL.
  6. Xuất ra đường TUYỆT ĐỐI không ghi đè tệp đã có: "x (2).xlsx", mọi hàm xuất.
  4. loi_ung_dung.txt: trần ~1 MB giữ phần cuối; bỏ mục trùng liên tiếp.
  5. loi_ngoai_du_kien chỉ mang TÊN KIỂU ngoại lệ; thông điệp thật chỉ nằm trong nhật ký.
"""

import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import socket
import sqlite3
import time
import warnings
import zipfile

import pytest

import browser_host
import cau_hinh_ws as ch
import chan_doan
import so_nhap
import workspace as ws
from api import PipelineAPI


def _ma(res):
    return [e["code"] for e in res["errors"]]


# ------------------------------------------------------------------ 1. CSDL đang bận

@pytest.fixture
def api_ws(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Thử", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                       thu_muc_goc_ws=str(goc), ws_da_chon=True)


@contextlib.contextmanager
def _khoa_csdl(db):
    """Một kết nối khác giữ khoá ghi độc quyền — mô phỏng tiến trình khác đang ghi."""
    conn = sqlite3.connect(db, isolation_level=None)
    conn.execute("BEGIN EXCLUSIVE")
    try:
        yield
    finally:
        conn.execute("ROLLBACK")
        conn.close()


def test_1_csdl_ban_bao_ma_rieng_va_khong_cho_lau(api_ws):
    with _khoa_csdl(api_ws.db_path):
        t0 = time.monotonic()
        res = api_ws.check_data_integrity()
        dt = time.monotonic() - t0
    assert not res["ok"]
    assert _ma(res) == ["csdl_dang_ban"], _ma(res)
    assert dt < 6, dt   # đọc cấu hình chờ 2,5 s; trước đây 15 s


def test_1_chay_xep_gap_csdl_ban_cung_bao_csdl_dang_ban(api_ws):
    # (run_pipeline còn chờ tới 15 s ở bước sao lưu — cố ý giữ, xem báo cáo A13.9.)
    with _khoa_csdl(api_ws.db_path):
        res = api_ws.run_pipeline()
    assert "csdl_dang_ban" in _ma(res), _ma(res)
    assert "ws_cau_hinh_hong" not in _ma(res)


def test_1_cau_hinh_hong_that_van_la_ws_cau_hinh_hong(api_ws):
    conn = sqlite3.connect(api_ws.db_path)
    conn.execute("UPDATE workspace_settings SET value = '{khong phai json' WHERE key = 'config'")
    conn.commit()
    conn.close()
    assert _ma(api_ws.check_data_integrity()) == ["ws_cau_hinh_hong"]


def test_1_hang_so_cho_khoa_doc_cau_hinh_trong_2_3_giay():
    assert 2000 <= ch.CHO_KHOA_DOC_CAU_HINH_MS <= 3000


# ------------------------------------------------------------------ 2, 3, 5. browser_host

RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def hosted(api):
    url = browser_host.serve(api, RESOURCE_DIR, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")
    return base, token


def _tho(base, du_lieu: bytes, doc_toi=5.0):
    """Gửi BYTE THÔ tới máy chủ; trả dòng trạng thái đầu tiên (b"" nếu máy chủ cắt kết nối)."""
    cong = int(base.rsplit(":", 1)[1])
    with socket.create_connection(("127.0.0.1", cong), timeout=doc_toi) as s:
        s.sendall(du_lieu)
        try:
            return s.recv(4096).split(b"\r\n", 1)[0]
        except socket.timeout:
            return None   # máy chủ im lặng, không cắt


def test_2_handler_co_timeout_30_den_60_giay():
    assert 30 <= browser_host._Handler.timeout <= 60


def test_2_ket_noi_gui_do_bi_cat(api, monkeypatch):
    monkeypatch.setattr(browser_host._Handler, "timeout", 1)
    url = browser_host.serve(api, RESOURCE_DIR, "index.html", open_browser=False)
    base = url.split("/index.html?t=")[0]
    t0 = time.monotonic()
    # Mới gửi nửa dòng yêu cầu rồi im lặng — luồng của máy chủ phải tự giải phóng.
    assert _tho(base, b"POST /__api__/get_dashboard_status HTTP/1.1\r\nHo", 6) == b""
    assert time.monotonic() - t0 < 5


@pytest.mark.parametrize("token_xau", ["tok\u00e9n", "\u0111\u1ed7"])
def test_3_token_khong_ascii_trong_tieu_de_bi_403(hosted, token_xau):
    base, _ = hosted
    cong = base.rsplit(":", 1)[1]
    yc = ("POST /__api__/get_dashboard_status HTTP/1.1\r\nHost: 127.0.0.1:%s\r\n"
          "X-Kiosk-Token: %s\r\nContent-Length: 2\r\n\r\n{}" % (cong, token_xau))
    dong = _tho(base, yc.encode("utf-8"))
    assert dong is not None and b" 403 " in dong, dong


@pytest.mark.parametrize("duong", [
    "POST /__closed__?t=%C3%A9%E1%BB%97 HTTP/1.1",
    "GET /index.html?t=%C3%A9%E1%BB%97 HTTP/1.1",
])
def test_3_token_khong_ascii_trong_url_bi_403(hosted, duong):
    base, _ = hosted
    cong = base.rsplit(":", 1)[1]
    yc = "%s\r\nHost: 127.0.0.1:%s\r\nContent-Length: 0\r\n\r\n" % (duong, cong)
    dong = _tho(base, yc.encode("ascii"))
    assert dong is not None and b" 403" in dong, dong


def test_5_loi_ngoai_du_kien_chi_tra_ten_kieu(hosted, api):
    bi_mat = r"C:\Users\hs\app.db không mở được; mật khẩu=abc123"

    def hong():
        raise PermissionError(bi_mat)
    api.get_dashboard_status = hong

    base, token = hosted
    req_ = __import__("urllib.request").request
    req = req_.Request(f"{base}/__api__/get_dashboard_status", data=b"{}", method="POST",
                       headers={"X-Kiosk-Token": token, "Content-Type": "application/json"})
    with req_.urlopen(req) as r:
        res = json.loads(r.read())
    assert res["errors"][0]["code"] == "loi_ngoai_du_kien"
    assert res["errors"][0]["params"]["detail"] == "PermissionError"
    assert "abc123" not in json.dumps(res, ensure_ascii=False)
    log = os.path.join(os.path.dirname(api.db_path), chan_doan.TEN_LOG_UNG_DUNG)
    with open(log, encoding="utf-8") as f:
        assert "abc123" in f.read()   # chi tiết thật vẫn có ở nhật ký


# ------------------------------------------------------------------ 4. nhật ký lỗi có trần

def _doc_log(thu_muc, ten=chan_doan.TEN_LOG_UNG_DUNG):
    with open(os.path.join(thu_muc, ten), encoding="utf-8") as f:
        return f.read()


def test_4_tran_mac_dinh_khoang_1_mb():
    assert 900_000 <= chan_doan.TRAN_LOG_UNG_DUNG_BYTE <= 1_200_000


def test_4_log_vuot_tran_giu_phan_cuoi(tmp_path, monkeypatch):
    monkeypatch.setattr(chan_doan, "TRAN_LOG_UNG_DUNG_BYTE", 20_000)
    for i in range(400):
        chan_doan.ghi(str(tmp_path), "Loi so %04d: " % i + "x" * 80, ten=chan_doan.TEN_LOG_UNG_DUNG)
    noi_dung = _doc_log(tmp_path)
    assert len(noi_dung.encode("utf-8")) <= 20_000
    assert "Loi so 0399" in noi_dung            # phần cuối còn
    assert "Loi so 0000" not in noi_dung        # phần đầu bị cắt
    # cắt ở ranh giới mục: không để nửa dòng
    dong_dau = noi_dung.split("\n", 1)[0]
    assert dong_dau.startswith("[") and "Loi so" in dong_dau or "cắt" in dong_dau


def test_4_bo_muc_trung_lien_tiep(tmp_path):
    for _ in range(50):
        chan_doan.ghi(str(tmp_path), "Loi: cung mot loi", ten=chan_doan.TEN_LOG_UNG_DUNG)
    assert _doc_log(tmp_path).count("cung mot loi") == 1
    # khác thì ghi; trùng nhưng KHÔNG liên tiếp thì vẫn ghi
    chan_doan.ghi(str(tmp_path), "Loi: loi khac", ten=chan_doan.TEN_LOG_UNG_DUNG)
    chan_doan.ghi(str(tmp_path), "Loi: cung mot loi", ten=chan_doan.TEN_LOG_UNG_DUNG)
    nd = _doc_log(tmp_path)
    assert nd.count("cung mot loi") == 2 and nd.count("loi khac") == 1


def test_4_ngoai_le_giong_het_chi_ghi_mot_lan(tmp_path):
    db = str(tmp_path / "app.db")
    for _ in range(5):
        try:
            raise ValueError("nhu nhau")
        except ValueError:
            chan_doan.ghi_ngoai_le_canh_db(db, "Loi: thu")
    assert _doc_log(tmp_path).count("ValueError: nhu nhau") == 1


def test_4_log_khoi_dong_khong_doi_hanh_vi(tmp_path):
    for _ in range(3):
        chan_doan.ghi(str(tmp_path), "lap lai")
    assert _doc_log(tmp_path, chan_doan.TEN_LOG).count("lap lai") == 3


# ------------------------------------------------------------------ 6. xuất đường tuyệt đối

@pytest.fixture
def api_co_ket_qua(api):
    api.create_or_update_club("a", "A", 1, 0, "")
    api.create_or_update_club("b", "B", 5, 0, "")
    for sid, nv in (("N1", ["a", "b"]), ("N2", ["a", "b"])):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, nv)["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    return api


_CU = "NOI DUNG CU - KHONG DUOC MAT"


def _xuat_tep_don(api, ten, ham):
    """Gọi `ham(api, duong_tuyet_doi)`; trả (res, duong_da_co, noi_dung_cu_truoc)."""
    thu_muc = os.path.dirname(api.db_path)
    duong = os.path.join(thu_muc, "ra_ngoai", ten)
    os.makedirs(os.path.dirname(duong))
    with open(duong, "w", encoding="utf-8") as f:
        f.write(_CU)
    return ham(api, duong), duong


@pytest.mark.parametrize("ten,ham,khoa", [
    ("kq.xlsx", lambda a, d: a.export_ket_qua(d), "path"),
    ("kq.xlsx", lambda a, d: a.export_ket_qua(d, True), "path"),
    ("kq.csv", lambda a, d: a.export_csv(d), "path"),
    ("so.xlsx", lambda a, d: a.tao_so_nhap_mau(d), "path"),
    ("vao.xlsx", lambda a, d: a.export_du_lieu_dau_vao(d), "path"),
    ("hs.csv", lambda a, d: a.export_hoc_sinh_csv(["N1", "N2"], d), "path"),
])
def test_6_duong_tuyet_doi_khong_ghi_de(api_co_ket_qua, ten, ham, khoa):
    res, duong = _xuat_tep_don(api_co_ket_qua, ten, ham)
    assert res["ok"], res["errors"]
    with open(duong, encoding="utf-8") as f:
        assert f.read() == _CU                      # tệp có sẵn còn nguyên
    goc, duoi = os.path.splitext(duong)
    assert res["data"][khoa] == "%s (2)%s" % (goc, duoi), res["data"][khoa]
    assert os.path.isfile(res["data"][khoa])


def test_6_xuat_lan_hai_len_ba_so_tang(api_co_ket_qua):
    thu_muc = os.path.join(os.path.dirname(api_co_ket_qua.db_path), "ngoai")
    os.makedirs(thu_muc)
    duong = os.path.join(thu_muc, "kq.csv")
    ra = [api_co_ket_qua.export_csv(duong)["data"]["path"] for _ in range(3)]
    assert [os.path.basename(p) for p in ra] == ["kq.csv", "kq (2).csv", "kq (3).csv"]


def test_6_kem_csv_khong_de_csv_cu_di_kem(api_co_ket_qua):
    thu_muc = os.path.join(os.path.dirname(api_co_ket_qua.db_path), "ngoai")
    os.makedirs(thu_muc)
    with open(os.path.join(thu_muc, "kq.csv"), "w", encoding="utf-8") as f:
        f.write(_CU)    # chỉ có .csv cũ; xuất Excel kèm CSV phải tránh cả hai đuôi
    res = api_co_ket_qua.export_ket_qua(os.path.join(thu_muc, "kq.xlsx"), True)
    assert res["ok"], res["errors"]
    assert os.path.basename(res["data"]["path"]) == "kq (2).xlsx"
    with open(os.path.join(thu_muc, "kq.csv"), encoding="utf-8") as f:
        assert f.read() == _CU


def test_6_export_workspace_tuyet_doi_khong_ghi_de(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Thử", None)
    api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / "x"),
                      thu_muc_goc_ws=str(goc), ws_da_chon=True)
    (tmp_path / "ra").mkdir()
    dich = tmp_path / "ra" / "ws.zip"
    dich.write_text(_CU, encoding="utf-8")
    res = api.export_workspace(slug, str(dich))
    assert res["ok"], res["errors"]
    assert dich.read_text(encoding="utf-8") == _CU
    assert os.path.basename(res["data"]["path"]) == "ws (2).zip"


