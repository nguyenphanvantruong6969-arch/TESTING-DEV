"""GAP-4: vòng 2 — học sinh chưa có CLB mong muốn chọn trong các chỗ còn trống, theo thứ tự bốc thăm của buổi, MỘT
lượt; mỗi lần xếp là một dòng `round2` trong `fa_dieu_chinh`. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import cau_hinh_ws as ch
import fa_sau_xep as sx
from _fa import dung_fa_clb, dung_hs_fa, ma
from test_fa_gap1_diem_danh import _anh_chup, _thanh_vien, api_ws  # noqa: F401 (fixture)


def _dung(api, v2=True):
    """H Giới hạn 1 chỗ: s1, s2 chỉ xếp H -> một em trượt, vào T (Tự do) do dự phòng. G Giới hạn 3 chỗ: trống."""
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_vong_2": v2}})
    dung_fa_clb(api, H=(1, "GIOI_HAN"), G=(3, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", nv={"s1": ["H"], "s2": ["H"], "s3": ["T"]})
    assert api.run_pipeline(seed=5)["ok"]


def test_co_mac_dinh_va_can_fa(api_ws):  # noqa: F811
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["fa_vong_2"] is False
    assert ma(api_ws.update_workspace_config({"rules": {"fa_vong_2": True}})["errors"]) == ["fa_tinh_nang_can_fa"]
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True, "fa_vong_2": True}})["ok"]


def test_co_tat(api):
    _dung(api, v2=False)
    assert api.get_vong_2() == {"ok": True, "data": {"bat": False}, "errors": []}
    assert ma(api.chay_vong_2_api("x", {})["errors"]) == ["fa_vong_2_chua_bat"]


# ----------------------------------------------------------------------------- hàm thuần

def test_chay_vong_2_theo_thu_tu_va_so_cho():
    con = {"G": 1, "K": 2}
    chon = {"a": ["G", "K"], "b": ["G", "K"], "c": ["G"], "d": ["X"]}
    assert sx.chay_vong_2(["b", "a", "c", "d"], chon, con) == [("b", "G"), ("a", "K")]
    assert con == {"G": 1, "K": 2}                                    # không sửa đầu vào


def test_can_vong_2_chi_em_khong_co_clb_mong_muon():
    vt = {("a", "x"): "T", ("b", "x"): "H", ("c", "x"): None, ("d", "y"): None}
    nv = {"a": ["H"], "b": ["H"], "c": ["H"]}
    assert sx.can_vong_2(vt, nv, "x") == ["a", "c"]


def test_cho_con_lai():
    vt = {("a", "x"): "G", ("b", "x"): "T"}
    assert sx.cho_con_lai(vt, {"G": 3, "T": 9, "H": 1}, {"H": 1}, "x", {"G", "T", "H"}) == {"G": 2, "T": 8}


# ----------------------------------------------------------------------------- API

def test_vong_2_xep_em_truot_vao_cho_trong(api):
    _dung(api)
    truoc = _anh_chup(api)
    d = api.get_vong_2()["data"]
    assert d["bat"] is True and d["da_chay"] is False
    em = [h["student_id"] for h in d["hoc_sinh"]]
    assert len(em) == 1 and em[0] in ("s1", "s2")
    con = {c["club_id"]: c["con"] for c in d["cho_con_lai"]}
    assert con["G"] == 3 and "H" not in con
    ra = api.chay_vong_2_api(d["buoi"], {em[0]: ["H", "G"]})            # H hết chỗ -> G
    assert ra["ok"], ra
    assert ra["data"]["xep"] == [{"student_id": em[0], "club_id": "G"}] and ra["data"]["bo_qua"] == []
    assert _thanh_vien(api, "G") == [em[0]]
    assert ma(api.chay_vong_2_api(d["buoi"], {em[0]: ["G"]})["errors"]) == ["vong_2_da_chay"]
    assert api.get_vong_2()["data"]["da_chay"] is True
    assert _anh_chup(api) == truoc
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh WHERE kind='round2'").fetchone()[0] == 1


def test_vong_2_lua_chon_sai_va_bo_qua(api):
    _dung(api)
    d = api.get_vong_2()["data"]
    em = d["hoc_sinh"][0]["student_id"]
    assert ma(api.chay_vong_2_api(d["buoi"], {em: ["KHONG_CO"]})["errors"]) == ["vong_2_lua_chon_sai"]
    assert ma(api.chay_vong_2_api(d["buoi"], {"s3": ["G"]})["errors"]) == ["vong_2_lua_chon_sai"]   # s3 không cần
    ra = api.chay_vong_2_api(d["buoi"], {em: ["H"]})                    # H không còn chỗ
    assert ra["ok"] and ra["data"]["xep"] == [] and ra["data"]["bo_qua"] == [em]
