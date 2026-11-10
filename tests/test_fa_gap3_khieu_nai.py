"""GAP-3: khiếu nại (chỉ lỗi dữ liệu, trong 3 ngày từ lúc công bố). Chấp nhận -> người quản trị sửa dữ liệu rồi chạy
lại với hạt giống đã khoá; không sửa tay kết quả. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import csv
import datetime

import pytest

import cau_hinh_ws as ch
import fa_sau_xep as sx
from _fa import dung_fa_clb, dung_hs_fa, ma
from test_fa_gap1_diem_danh import _thanh_vien, api_ws  # noqa: F401 (fixture)

DD = "%Y-%m-%d %H:%M:%S"


def _bat(api, kn=True, dd=True, **them):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_diem_danh": dd, "fa_khieu_nai": kn, **them}})


def _dung(api, kn=True):
    _bat(api, kn)
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})
    assert api.run_pipeline(seed=5)["ok"]


def _buoi(api):
    with api._ket_noi_doc() as cur:
        return next(iter(sx.run_goc_theo_buoi(cur)))


def _run_at(api):
    with api._ket_noi_doc() as cur:
        return datetime.datetime.strptime(
            cur.execute("SELECT run_at FROM run_history ORDER BY run_id DESC").fetchone()[0][:19].replace("T", " "), DD)


@pytest.fixture
def gio(monkeypatch):
    """Đặt "bây giờ" = lúc chạy + `delta`."""
    def _dat(api, **delta):
        moc = _run_at(api) + datetime.timedelta(**delta)
        monkeypatch.setattr(sx, "bay_gio", lambda: moc)
    return _dat


# ----------------------------------------------------------------------------- cờ

def test_co_mac_dinh_va_rang_buoc(api_ws):  # noqa: F811
    r = ch.MAC_DINH_TRUONG_HOC["rules"]
    assert r["fa_khieu_nai"] is False and r["fa_khieu_nai_so_ngay"] == 3
    assert ma(api_ws.update_workspace_config({"rules": {"fa_khieu_nai": True}})["errors"]) == ["fa_tinh_nang_can_fa"]
    for sai in (0, 15, "3", True, 2.5):
        ra = api_ws.update_workspace_config({"rules": {"fa_khieu_nai_so_ngay": sai}})
        assert ma(ra["errors"]) == ["ws_du_lieu_sai"], sai
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True, "fa_khieu_nai": True,
                                                     "fa_khieu_nai_so_ngay": 5}})["ok"]


def test_co_tat(api):
    _dung(api, kn=False)
    assert api.get_khieu_nai() == {"ok": True, "data": {"bat": False}, "errors": []}
    assert ma(api.gui_khieu_nai("s1", _buoi(api), "x")["errors"]) == ["fa_khieu_nai_chua_bat"]


# ----------------------------------------------------------------------------- hạn

def test_trong_han_bien():
    t0 = "2026-11-01 08:00:00"
    g = datetime.datetime(2026, 11, 1, 8, 0, 0)
    assert sx.trong_han_khieu_nai(t0, g + datetime.timedelta(days=2, hours=23), 3)
    assert sx.trong_han_khieu_nai(t0, g + datetime.timedelta(days=3), 3)
    assert not sx.trong_han_khieu_nai(t0, g + datetime.timedelta(days=3, minutes=1), 3)
    assert sx.trong_han_khieu_nai("2026-11-01T08:00:00.123456", g + datetime.timedelta(days=3), 3)


def test_gui_trong_han_qua_han_trung_va_la(api, gio):
    _dung(api)
    b = _buoi(api)
    gio(api, days=1)
    ra = api.gui_khieu_nai("s1", b, "Điểm thi nhập sai")
    assert ra["ok"] and isinstance(ra["data"]["id"], int)
    assert ma(api.gui_khieu_nai("s1", b, "lần hai")["errors"]) == ["khieu_nai_trung"]
    assert ma(api.gui_khieu_nai("s9", b, "x")["errors"]) == ["khieu_nai_khong_hop_le"]
    assert ma(api.gui_khieu_nai("s2", "khong_co", "x")["errors"]) == ["khieu_nai_khong_hop_le"]
    gio(api, days=4)
    ra = api.gui_khieu_nai("s2", b, "x")
    assert ma(ra["errors"]) == ["khieu_nai_qua_han"] and ra["errors"][0]["params"]["so_ngay"] == 3


def test_so_ngay_doi_duoc(api, gio):
    _dung(api)
    _bat(api, fa_khieu_nai_so_ngay=5)
    gio(api, days=4)
    assert api.gui_khieu_nai("s1", _buoi(api), "x")["ok"]


# ----------------------------------------------------------------------------- xử lý + chạy lại

def test_chap_nhan_ghi_dau_vet_va_khong_xu_ly_hai_lan(api, gio):
    _dung(api)
    gio(api, hours=1)
    i = api.gui_khieu_nai("s1", _buoi(api), "x")["data"]["id"]
    assert api.xu_ly_khieu_nai(i, True, "đúng là nhập sai")["ok"]
    assert ma(api.xu_ly_khieu_nai(i, False)["errors"]) == ["khieu_nai_da_xu_ly"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh WHERE kind='appeal_rerun'").fetchone()[0] == 1
    k = api.get_khieu_nai()["data"]
    assert k["bat"] and k["so_ngay"] == 3
    assert k["khieu_nai"][0]["trang_thai"] == "CHAP_NHAN" and k["khieu_nai"][0]["da_chay_lai"] is False


def test_chay_lai_sau_chap_nhan_liet_ke_dieu_chinh_cu(api, gio):
    _dung(api)
    b = _buoi(api)
    em = _thanh_vien(api, "G")[0]
    api.luu_diem_danh("G", em, 1, "VANG_KHONG_PHEP")
    api.luu_diem_danh("G", em, 2, "VANG_KHONG_PHEP")
    with api._ket_noi_doc() as cur:
        id_release = cur.execute("SELECT id FROM fa_dieu_chinh WHERE kind='release'").fetchone()[0]
        n_run = cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
        seed = cur.execute("SELECT seed FROM stb_lock WHERE id = 1").fetchone()[0]
    gio(api, hours=1)
    i = api.gui_khieu_nai("s1", b, "x")["data"]["id"]
    api.xu_ly_khieu_nai(i, True)
    assert api.run_pipeline(seed=seed)["ok"]                          # quản trị sửa dữ liệu rồi chạy lại
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == n_run + 1
        assert cur.execute("SELECT seed FROM stb_lock WHERE id = 1").fetchone()[0] == seed
    k = next(x for x in api.get_khieu_nai()["data"]["khieu_nai"] if x["id"] == i)
    assert k["da_chay_lai"] is True and id_release in k["dieu_chinh_cu"]


def test_anh_huong_thuan():
    kn = [{"id": 1, "student_id": "s1", "buoi": "b", "run_id_base": 1, "trang_thai": "CHAP_NHAN"},
          {"id": 2, "student_id": "s2", "buoi": "b", "run_id_base": 1, "trang_thai": "TU_CHOI"}]
    dc = [{"id": 7, "run_id_base": 1, "buoi": "b", "kind": "release"},
          {"id": 8, "run_id_base": 2, "buoi": "b", "kind": "release"}]
    assert sx.anh_huong_sau_chay_lai(kn, {"b": 2}, dc) == {1: {"da_chay_lai": True, "dieu_chinh_cu": [7]}}
    assert sx.anh_huong_sau_chay_lai(kn, {"b": 1}, dc) == {1: {"da_chay_lai": False, "dieu_chinh_cu": []}}


def test_xuat_csv_chan_cong_thuc(api, gio, tmp_path):
    _dung(api)
    gio(api, hours=1)
    api.gui_khieu_nai("s1", _buoi(api), "=1+1")
    ra = api.export_khieu_nai(str(tmp_path / "kn.csv"))
    assert ra["ok"], ra
    with open(ra["data"]["path"], encoding="utf-8-sig", newline="") as f:
        dong = list(csv.reader(f))
    assert dong[0] == ["id", "student_id", "buoi", "trang_thai", "created_at", "ghi_chu", "xu_ly_ghi_chu",
                       "da_chay_lai", "dieu_chinh_cu"]
    assert dong[1][5] != "=1+1" and dong[1][5].endswith("=1+1")
