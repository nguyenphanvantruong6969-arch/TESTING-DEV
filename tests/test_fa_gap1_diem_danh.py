"""GAP-1: điểm danh 3 buổi đầu; vắng 2/3 buổi không phép -> giải phóng chỗ (một dòng `release` trong `fa_dieu_chinh`).

Sau `rules.fa_diem_danh` (mặc định TẮT, chỉ dùng được khi `fa_daa` bật). Kết quả DA (`match_results`) và `run_history`
không đổi. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import pytest

import cau_hinh_ws as ch
import fa_sau_xep as sx
import workspace as ws
from _fa import dung_fa_clb, dung_hs_fa, ma
from api import PipelineAPI


def _bat(api, diem_danh=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_diem_danh": diem_danh}})


def _dung(api, diem_danh=True):
    """G Giới hạn 2 chỗ, T Tự do; s1..s4 đều xếp G rồi T -> 2 em G, 2 em T."""
    _bat(api, diem_danh)
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})
    assert api.run_pipeline(seed=5)["ok"]


def _thanh_vien(api, cid):
    with api._ket_noi_doc() as cur:
        vt, _, _ = sx.doc_vi_tri(cur)
    return sorted(s for (s, _), c in vt.items() if c == cid)


def _anh_chup(api):
    with api._ket_noi_doc() as cur:
        return (cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi").fetchall(),
                cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0])


def _so_release(api):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh WHERE kind='release'").fetchone()[0]


# ----------------------------------------------------------------------------- cờ

@pytest.fixture
def api_ws(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Trường học", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=str(goc))


def test_co_mac_dinh_tat_va_can_fa(api_ws):
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["fa_diem_danh"] is False
    ra = api_ws.update_workspace_config({"rules": {"fa_diem_danh": True}})
    assert ma(ra["errors"]) == ["fa_tinh_nang_can_fa"] and ra["errors"][0]["params"]["khoa"] == "fa_diem_danh"
    ra = api_ws.update_workspace_config({"rules": {"fa_diem_danh": "co"}})
    assert ma(ra["errors"]) == ["ws_du_lieu_sai"]
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True, "fa_diem_danh": True}})["ok"]


def test_co_khong_vao_luat_xep_cua_lan_chay(api):
    _dung(api)
    with api._ket_noi_doc() as cur:
        luat = cur.execute("SELECT luat_xep FROM run_history ORDER BY run_id DESC").fetchone()[0] or ""
    assert "fa_diem_danh" not in luat


def test_co_tat_thi_khong_lam_gi(api):
    _dung(api, diem_danh=False)
    assert api.get_diem_danh() == {"ok": True, "data": {"bat": False}, "errors": []}
    ra = api.luu_diem_danh("G", "s1", 1, "VANG_KHONG_PHEP")
    assert ma(ra["errors"]) == ["fa_diem_danh_chua_bat"]
    assert ma(api.export_diem_danh("")["errors"]) == ["fa_diem_danh_chua_bat"]


# ----------------------------------------------------------------------------- giải phóng

def test_hai_buoi_vang_khong_phep_thi_giai_phong_mot_lan(api):
    _dung(api)
    g = _thanh_vien(api, "G")
    em = g[0]
    truoc = _anh_chup(api)
    ra = api.luu_diem_danh("G", em, 1, "VANG_KHONG_PHEP")
    assert ra["ok"] and ra["data"]["da_giai_phong"] is False
    assert _so_release(api) == 0
    ra = api.luu_diem_danh("G", em, 3, "VANG_KHONG_PHEP")
    assert ra["ok"] and ra["data"]["da_giai_phong"] is True
    assert _so_release(api) == 1
    assert em not in _thanh_vien(api, "G")
    assert api.luu_diem_danh("G", em, 2, "VANG_KHONG_PHEP")["ok"]      # lần lưu sau: không giải phóng lần hai
    assert _so_release(api) == 1
    assert _anh_chup(api) == truoc                                      # match_results + số run_history không đổi


def test_vang_co_phep_va_co_mat_khong_giai_phong(api):
    _dung(api)
    em = _thanh_vien(api, "G")[0]
    for so, tt in ((1, "VANG_KHONG_PHEP"), (2, "VANG_CO_PHEP"), (3, "CO_MAT")):
        assert api.luu_diem_danh("G", em, so, tt)["ok"]
    assert _so_release(api) == 0 and em in _thanh_vien(api, "G")


def test_xoa_dau_bang_chuoi_rong(api):
    _dung(api)
    em = _thanh_vien(api, "G")[0]
    assert api.luu_diem_danh("G", em, 1, "VANG_KHONG_PHEP")["ok"]
    assert api.luu_diem_danh("G", em, 1, "")["ok"]
    assert api.luu_diem_danh("G", em, 2, "VANG_KHONG_PHEP")["data"]["da_giai_phong"] is False


def test_gia_tri_sai_va_hoc_sinh_khong_thuoc_clb(api):
    _dung(api)
    em = _thanh_vien(api, "G")[0]
    assert ma(api.luu_diem_danh("G", em, 4, "CO_MAT")["errors"]) == ["diem_danh_gia_tri_sai"]
    assert ma(api.luu_diem_danh("G", em, 1, "TRE")["errors"]) == ["diem_danh_gia_tri_sai"]
    khac = _thanh_vien(api, "T")[0]
    assert ma(api.luu_diem_danh("G", khac, 1, "CO_MAT")["errors"]) == ["diem_danh_khong_thuoc_clb"]


def test_can_giai_phong_thuan():
    assert sx.NGUONG_VANG == 2
    assert sx.can_giai_phong({1: "VANG_KHONG_PHEP", 2: "VANG_KHONG_PHEP"})
    assert not sx.can_giai_phong({1: "VANG_KHONG_PHEP", 2: "VANG_CO_PHEP", 3: "CO_MAT"})


# ----------------------------------------------------------------------------- màn hình + xuất

def test_get_diem_danh_liet_ke_va_dem(api):
    _dung(api)
    g = _thanh_vien(api, "G")
    api.luu_diem_danh("G", g[0], 1, "VANG_KHONG_PHEP")
    api.luu_diem_danh("G", g[0], 2, "VANG_KHONG_PHEP")
    d = api.get_diem_danh("G")["data"]
    assert d["bat"] is True and d["club_id"] == "G"
    assert {c["club_id"] for c in d["clubs"]} == {"G", "T"}
    hs = {h["student_id"]: h for h in d["hoc_sinh"]}
    assert set(hs) == set(g)
    assert hs[g[0]]["da_giai_phong"] is True and hs[g[0]]["so_vang_khong_phep"] == 2
    assert hs[g[0]]["buoi_1"] == "VANG_KHONG_PHEP" and hs[g[0]]["buoi_3"] == ""
    assert hs[g[1]]["da_giai_phong"] is False


def test_xuat_xlsx_moi_clb_mot_trang_va_an_toan(api, tmp_path):
    from openpyxl import load_workbook
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET name = ? WHERE club_id = 'G'", ("=X\x01",))
    em = _thanh_vien(api, "G")[0]
    api.luu_diem_danh("G", em, 1, "VANG_CO_PHEP")
    ra = api.export_diem_danh(str(tmp_path / "dd.xlsx"))
    assert ra["ok"], ra
    wb = load_workbook(ra["data"]["path"])
    assert len(wb.worksheets) == 2 and ra["data"]["n_clb"] == 2
    chu = [str(c.value) for w in wb.worksheets for row in w.iter_rows() for c in row if c.value is not None]
    assert "Vắng có phép" in chu and "Mã học sinh" in chu
    import zipfile
    with zipfile.ZipFile(ra["data"]["path"]) as z:
        xml = "".join(z.read(n).decode("utf-8") for n in z.namelist() if n.startswith("xl/worksheets/"))
    assert "<f>" not in xml and "<f " not in xml
