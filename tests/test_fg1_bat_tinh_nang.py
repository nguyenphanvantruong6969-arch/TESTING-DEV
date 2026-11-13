"""FG-1 (STEP0, spec §3), phần API: bật/tắt tính năng sau khi xếp cho không gian đang mở bằng cấu hình MỘT PHẦN.
Dữ liệu MÔ PHỎNG. Phần giao diện: `test_giao_dien_fg1_bat_tinh_nang.py`.
"""
import cau_hinh_ws as ch
from _fa import ma
from test_fa_gap1_diem_danh import api_ws  # noqa: F401 (fixture)


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def test_cau_hinh_mot_phan_giu_nguyen_cac_khoa_khac(api_ws):  # noqa: F811
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    truoc = _luat(api_ws)
    ra = api_ws.update_workspace_config({"rules": {"fa_khieu_nai": True, "fa_khieu_nai_so_ngay": 5}})
    assert ra["ok"], ra
    sau = _luat(api_ws)
    assert sau["fa_khieu_nai"] is True and sau["fa_khieu_nai_so_ngay"] == 5
    assert {k: v for k, v in sau.items() if k not in ("fa_khieu_nai", "fa_khieu_nai_so_ngay")} == \
        {k: v for k, v in truoc.items() if k not in ("fa_khieu_nai", "fa_khieu_nai_so_ngay")}


def test_tat_lai_tung_co(api_ws):  # noqa: F811
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True, **{k: True for k in ch.CO_SAU_XEP}}})["ok"]
    assert api_ws.update_workspace_config({"rules": {"fa_phan_hoi": False}})["ok"]
    sau = _luat(api_ws)
    assert sau["fa_phan_hoi"] is False and all(sau[k] is True for k in ch.CO_SAU_XEP if k != "fa_phan_hoi")


def test_khong_fa_thi_tu_choi_moi_co_sau_xep(api_ws):  # noqa: F811
    for khoa in ch.CO_SAU_XEP:
        ra = api_ws.update_workspace_config({"rules": {khoa: True}})
        assert ma(ra["errors"]) == ["fa_tinh_nang_can_fa"] and ra["errors"][0]["params"]["khoa"] == khoa
    assert all(_luat(api_ws)[k] is False for k in ch.CO_SAU_XEP)


def test_so_ngay_khieu_nai_ngoai_khoang_1_den_14_bi_tu_choi(api_ws):  # noqa: F811
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    for xau in (0, 15, -1, 2.5, "3", True):
        ra = api_ws.update_workspace_config({"rules": {"fa_khieu_nai_so_ngay": xau}})
        assert not ra["ok"] and ra["errors"], xau
    assert _luat(api_ws)["fa_khieu_nai_so_ngay"] == 3                           # không bị ghi dở
    for tot in (1, 14):
        assert api_ws.update_workspace_config({"rules": {"fa_khieu_nai_so_ngay": tot}})["ok"]
