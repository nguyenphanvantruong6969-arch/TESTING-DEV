"""A13.11 — sửa phát hiện N1–N4 của đợt stress test trên đỉnh A13.9 (`VAN_DE_STRESS_TEST.md`).

  N1. Đường xuất là một THƯ MỤC có sẵn → từ chối bằng lỗi có tên, không đẻ tệp `x (2)` cạnh nó.
  N2. wharton_nhat_ky: mỗi lần nạp Sổ / CSV ghi MỘT dòng tóm tắt (nap_tep), không một dòng mỗi em.
  N3. Mọi hàm gặp CSDL bận dùng `csdl_dang_ban`, chờ ≤ 3 s (giữ sao lưu trước khi chạy).
  N4. Giao diện: thẻ Kết quả / lật trang ở quy mô lớn (xem `test_giao_dien_a13_11_*.py`).
"""

import contextlib
import json
import os
import base64
import importlib.util
import sqlite3
import threading
import time

import pytest

import workspace as ws
from api import PipelineAPI


def _ma(res):
    return [e["code"] for e in res["errors"]]


@pytest.fixture
def api_co_ket_qua(api):
    api.create_or_update_club("a", "A", 1, 0, "")
    api.create_or_update_club("b", "B", 5, 0, "")
    for sid in ("N1", "N2"):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, ["a", "b"])["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    assert api.run_pipeline(seed=1)["ok"]      # lần thứ hai: có "lần chạy trước" để xuất thay đổi
    return api


# ------------------------------------------------------------------ N1. đường xuất là thư mục

@pytest.mark.parametrize("ham", [
    lambda a, d: a.export_ket_qua(d),
    lambda a, d: a.export_ket_qua(d, True),
    lambda a, d: a.export_csv(d),
    lambda a, d: a.tao_so_nhap_mau(d),
    lambda a, d: a.export_du_lieu_dau_vao(d),
    lambda a, d: a.export_hoc_sinh_csv(["N1", "N2"], d),
    lambda a, d: a.export_thay_doi_ket_qua(d),
], ids=["ket_qua", "ket_qua_kem_csv", "csv", "so_mau", "du_lieu_vao", "hoc_sinh", "thay_doi"])
def test_n1_duong_xuat_la_thu_muc_bi_tu_choi(api_co_ket_qua, tmp_path, ham):
    thu_muc = tmp_path / "ngoai"
    thu_muc.mkdir()
    truoc = sorted(os.listdir(tmp_path))
    res = ham(api_co_ket_qua, str(thu_muc))
    assert not res["ok"]
    assert _ma(res)[0] == "xuat_duong_la_thu_muc", _ma(res)
    assert res["errors"][0]["params"]["path"] == "ngoai"      # chỉ tên, không lộ đường dẫn máy
    assert sorted(os.listdir(tmp_path)) == truoc            # không đẻ "ngoai (2)"
    assert os.listdir(thu_muc) == []


def test_n1_export_workspace_duong_la_thu_muc_bi_tu_choi(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Thử", None)
    api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / "x"),
                      thu_muc_goc_ws=str(goc), ws_da_chon=True)
    ra = tmp_path / "ra"
    ra.mkdir()
    res = api.export_workspace(slug, str(ra))
    assert not res["ok"] and _ma(res)[0] == "xuat_duong_la_thu_muc"
    assert not [x for x in os.listdir(tmp_path) if x.startswith("ra (")]   # không đẻ "ra (2)"
    assert os.listdir(ra) == []


def test_n1_duong_tep_binh_thuong_van_xuat_duoc(api_co_ket_qua, tmp_path):
    res = api_co_ket_qua.export_ket_qua(str(tmp_path / "ok.xlsx"))
    assert res["ok"], res["errors"]
    assert os.path.basename(res["data"]["path"]) == "ok.xlsx"


# ------------------------------------------------------------------ N2. nhật ký Wharton gộp

def _nhat_ky(api):
    with api._ket_noi_doc() as cur:
        return [(r["nguon"], r["hanh_dong"], r["student_id"], r["cu_json"],
                 json.loads(r["moi_json"]) if r["moi_json"] else None)
                for r in cur.execute("SELECT * FROM wharton_nhat_ky ORDER BY id")]


@pytest.fixture
def wh(api):
    from _wharton import bat_wharton, dung_clb
    bat_wharton(api)
    dung_clb(api, A=50, B=50, C=50)
    return api


def _csv_nap(n, diem_a=100):
    dong = ["student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3"]
    dong += ["HS%03d,Em %d,A,%d,B,60,C,40" % (i, i, diem_a) for i in range(n)]
    return "\n".join(dong) + "\n"


def test_n2_nap_nhieu_em_chi_ghi_mot_dong_tom_tat(wh):
    kq = wh.import_preferences_csv(_csv_nap(40))
    assert kq["ok"], kq["errors"]
    nk = _nhat_ky(wh)
    assert len(nk) == 1, len(nk)
    nguon, hanh_dong, sid, cu, moi = nk[0]
    assert (nguon, hanh_dong, sid, cu) == ("nap_tep", "luu_hang_loat", None, None)
    assert moi == {"so_em_doi": 40, "so_dong_nap": 40}


def test_n2_nap_lai_y_nguyen_khong_ghi_them(wh):
    wh.import_preferences_csv(_csv_nap(10))
    wh.import_preferences_csv(_csv_nap(10))
    assert len(_nhat_ky(wh)) == 1


def test_n2_chi_tinh_em_co_diem_doi(wh):
    wh.import_preferences_csv(_csv_nap(10))
    wh.import_preferences_csv(_csv_nap(10, diem_a=90).replace("HS005,Em 5,A,90", "HS005,Em 5,A,100"))
    nk = _nhat_ky(wh)
    assert len(nk) == 2
    assert nk[1][4] == {"so_em_doi": 9, "so_dong_nap": 10}


def test_n2_so_nhap_cung_chi_mot_dong_va_chi_ghi_them(wh):
    wh.import_preferences_csv(_csv_nap(5))
    truoc = _nhat_ky(wh)
    assert wh.reset_data("hoc_sinh", "XOA")["ok"]      # dữ liệu mất đi, nhật ký vẫn còn
    sau = _nhat_ky(wh)
    assert sau[:len(truoc)] == truoc                   # chỉ ghi thêm, không sửa / xoá dòng cũ


# ------------------------------------------------------------------ N3. CSDL bận ở MỌI hàm

@contextlib.contextmanager
def _khoa_csdl(db):
    """Một kết nối khác giữ khoá độc quyền — mô phỏng tiến trình khác đang ghi."""
    conn = sqlite3.connect(db, isolation_level=None)
    conn.execute("BEGIN EXCLUSIVE")
    try:
        yield
    finally:
        conn.execute("ROLLBACK")
        conn.close()


_HAM_BAN = [
    ("list_students_admin", lambda a: a.list_students_admin()),
    ("list_clubs_admin", lambda a: a.list_clubs_admin()),
    ("reset_data", lambda a: a.reset_data("hoc_sinh", "XOA")),
    ("get_dashboard_status", lambda a: a.get_dashboard_status()),
    ("check_data_integrity", lambda a: a.check_data_integrity()),
    ("get_data_health_report", lambda a: a.get_data_health_report()),
    ("get_run_history", lambda a: a.get_run_history()),
    ("get_match_results", lambda a: a.get_match_results()),
    ("get_club_fill_stats", lambda a: a.get_club_fill_stats()),
    ("get_scoring_overview", lambda a: a.get_scoring_overview()),
    ("submit_preferences", lambda a: a.submit_preferences("N1", ["a"])),
    ("create_or_update_club", lambda a: a.create_or_update_club("z", "Z", 3, 0, "")),
    ("run_pipeline", lambda a: a.run_pipeline(seed=1)),
]


@pytest.mark.parametrize("ten,goi", _HAM_BAN, ids=[x[0] for x in _HAM_BAN])
def test_n3_moi_ham_gap_csdl_ban_bao_csdl_dang_ban_nhanh(api_co_ket_qua, ten, goi):
    api = api_co_ket_qua
    with _khoa_csdl(api.db_path):
        t0 = time.monotonic()
        res = goi(api)
        dt = time.monotonic() - t0
    assert not res["ok"], ten
    ma = _ma(res)
    assert "csdl_dang_ban" in ma, (ten, ma)
    assert dt < 7, (ten, dt)           # trước: 15 – 30 s


def test_n3_tren_csdl_khong_khoa_khong_doi_gi(api_co_ket_qua):
    api = api_co_ket_qua
    assert api.list_students_admin()["ok"]
    assert api.run_pipeline(seed=1)["ok"]


def test_n3_chay_xep_gap_csdl_ban_khong_chay_khi_chua_sao_luu_duoc(api_co_ket_qua):
    """CSDL bận thì không có bản sao lưu để làm lưới an toàn: từ chối chạy, không bỏ sao lưu."""
    api = api_co_ket_qua
    thu_muc = os.path.dirname(api.db_path)
    so_bak = lambda: len([f for f in os.listdir(thu_muc) if ".bak-" in f])    # noqa: E731
    truoc = so_bak()
    with _khoa_csdl(api.db_path):
        res = api.run_pipeline(seed=1)
    assert "csdl_dang_ban" in _ma(res)
    assert so_bak() == truoc            # không để lại bản sao lưu dở
    assert api.run_pipeline(seed=1)["ok"]


def test_n3_ma_loi_khoa_trong_detail_duoc_doi_thanh_csdl_dang_ban():
    from i18n_errors import err
    e = err("error_reading_student_list", detail="database is locked")
    assert e["code"] == "csdl_dang_ban"
    assert err("error_reading_student_list", detail="no such table: x")["code"] == \
        "error_reading_student_list"


# ------------------------------------------------------------------ N4. lời gọi đọc đồng thời

RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT_SDL = os.path.join(RESOURCE_DIR, ".claude", "skills", "sinh-du-lieu-clb", "scripts",
                           "sinh_du_lieu.py")

# Mười ba lời gọi đọc mà giao diện bắn CÙNG LÚC khi mở thẻ Kết quả (xem js/03_ket_qua.js).
_DOC_THE_KET_QUA = ["get_thay_doi_ket_qua", "get_match_results", "get_em_chua_co_cho",
                    "get_phan_bo_nguyen_vong", "get_club_fill_stats", "get_suat_du_tru",
                    "get_last_run_info", "get_club_fill_stats", "get_phan_bo_nguyen_vong",
                    "get_suat_du_tru", "get_last_run_info", "get_em_chua_co_cho",
                    "get_thay_doi_ket_qua"]


@pytest.fixture(scope="module")
def api_lon(tmp_path_factory):
    spec = importlib.util.spec_from_file_location("sdl_n4", _SCRIPT_SDL)
    sdl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sdl)
    thu_muc = tmp_path_factory.mktemp("n4")
    clb, hs = sdl.sinh_ngau_nhien(1500, [""], 40, 11)
    sdl.ghi_bo(str(thu_muc), clb, hs)
    api = PipelineAPI(str(thu_muc / "app.db"), thu_muc_xuat=str(thu_muc))
    with open(thu_muc / "SO_NHAP_CLB.xlsx", "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    return api


def test_n4_doc_dong_thoi_khong_cham_hon_doc_lan_luot(api_lon):
    """Nguyên nhân đo được: nhiều luồng đọc tranh GIL (mỗi bước SQLite nhả rồi giành lại GIL), nên
    13 lời gọi chạy CÙNG LÚC chậm gấp 5 – 10 lần chạy NỐI TIẾP. Đọc xếp hàng thì không."""
    api = api_lon

    def goi(ten):
        assert getattr(api, ten)()["ok"]

    for ten in set(_DOC_THE_KET_QUA):       # làm nóng
        goi(ten)
    t0 = time.perf_counter()
    for ten in _DOC_THE_KET_QUA:
        goi(ten)
    noi_tiep = time.perf_counter() - t0

    luong = [threading.Thread(target=goi, args=(ten,)) for ten in _DOC_THE_KET_QUA]
    t0 = time.perf_counter()
    for x in luong:
        x.start()
    for x in luong:
        x.join()
    dong_thoi = time.perf_counter() - t0
    assert dong_thoi < 2.5 * noi_tiep + 0.15, (dong_thoi, noi_tiep)


def test_n4_ham_doc_xep_hang_nhau_va_ham_ghi_khong_bi_chan(api_lon):
    api = api_lon
    dang_chay, tung_thay = [0], []
    khoa = threading.Lock()

    def cham(*a, **k):
        with khoa:
            dang_chay[0] += 1
            tung_thay.append(dang_chay[0])
        time.sleep(0.05)
        with khoa:
            dang_chay[0] -= 1
        return {"ok": True, "data": None, "errors": []}

    # thay phần THÂN bằng hàm chậm nhưng vẫn đi qua lớp xếp hàng của lớp PipelineAPI
    goc = PipelineAPI.get_run_history.__wrapped__ if hasattr(
        PipelineAPI.get_run_history, "__wrapped__") else None
    assert goc is not None, "hàm đọc công khai phải được bọc (có __wrapped__)"
    ham_boc = PipelineAPI.get_run_history
    try:
        PipelineAPI.get_run_history = PipelineAPI._xep_hang_doc(cham)
        luong = [threading.Thread(target=api.get_run_history) for _ in range(6)]
        for x in luong:
            x.start()
        for x in luong:
            x.join()
    finally:
        PipelineAPI.get_run_history = ham_boc
    assert max(tung_thay) == 1            # không bao giờ hai lời gọi đọc chồng lên nhau


def test_n4_moi_ham_doc_cong_khai_duoc_boc_con_ham_ghi_thi_khong():
    doc = [n for n in dir(PipelineAPI)
           if n.startswith(("get_", "list_", "check_", "xem_truoc_"))
           and callable(getattr(PipelineAPI, n))]
    assert len(doc) > 30
    chua_boc = [n for n in doc if not hasattr(getattr(PipelineAPI, n), "__wrapped__")]
    assert chua_boc == [], chua_boc
    for n in ("run_pipeline", "submit_preferences", "import_so_nhap", "reset_data",
              "export_ket_qua"):
        assert not hasattr(getattr(PipelineAPI, n), "__wrapped__"), n


# ------------------------------------------------------------------ N1b. lỗi xuất không lộ đường dẫn máy

DAU_DUONG = "thu_muc_khong_co_zzz"


@pytest.mark.parametrize("ham", [
    lambda a, d: a.export_ket_qua(d),
    lambda a, d: a.export_ket_qua(d, True),
    lambda a, d: a.export_csv(d),
    lambda a, d: a.tao_so_nhap_mau(d),
    lambda a, d: a.export_du_lieu_dau_vao(d),
    lambda a, d: a.export_hoc_sinh_csv(["N1", "N2"], d),
    lambda a, d: a.export_thay_doi_ket_qua(d),
], ids=["ket_qua", "ket_qua_kem_csv", "csv", "so_mau", "du_lieu_vao", "hoc_sinh", "thay_doi"])
def test_n1b_loi_xuat_khong_lo_duong_dan_may(api_co_ket_qua, tmp_path, ham):
    duong = str(tmp_path / DAU_DUONG / "x.xlsx")            # thư mục cha không tồn tại
    res = ham(api_co_ket_qua, duong)
    assert not res["ok"]
    van_ban = json.dumps(res, ensure_ascii=False)
    assert DAU_DUONG not in van_ban and str(tmp_path) not in van_ban, van_ban
    assert "FileNotFoundError" in van_ban or "No such file" in van_ban    # vẫn nói được kiểu lỗi


def test_n1b_export_workspace_khong_lo_duong_dan_may(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Thử", None)
    api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / "x"),
                      thu_muc_goc_ws=str(goc), ws_da_chon=True)
    (tmp_path / DAU_DUONG).write_text("tệp, không phải thư mục", encoding="utf-8")
    res = api.export_workspace(slug, str(tmp_path / DAU_DUONG / "ws.zip"))   # cha là TỆP
    assert not res["ok"]
    assert DAU_DUONG not in json.dumps(res, ensure_ascii=False)


def test_n1b_chi_tiet_that_nam_o_nhat_ky(api_co_ket_qua, tmp_path):
    import chan_doan
    duong = str(tmp_path / DAU_DUONG / "x.xlsx")
    api_co_ket_qua.export_ket_qua(duong)
    log = os.path.join(os.path.dirname(api_co_ket_qua.db_path), chan_doan.TEN_LOG_UNG_DUNG)
    with open(log, encoding="utf-8") as f:
        assert DAU_DUONG in f.read()
