"""FA-N3: bật FA-DAA mà tắt điểm quyết tâm -> mã lỗi RIÊNG `fa_can_diem_quyet_tam` (không phải lỗi chung
`ws_du_lieu_sai`), ở mọi đường ghi luật: tạo, sửa cấu hình. Dữ liệu MÔ PHỎNG."""
import pytest

import workspace as ws
from api import PipelineAPI
from i18n_errors import MESSAGES


@pytest.fixture
def api(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Trường học", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                       thu_muc_goc_ws=str(goc))


def _ma(res):
    assert res["ok"] is False
    return [e["code"] for e in res["errors"]]


def test_ma_loi_co_hai_ngon_ngu():
    assert MESSAGES["fa_can_diem_quyet_tam"]["vi"] and MESSAGES["fa_can_diem_quyet_tam"]["en"]
    assert "điểm quyết tâm" in MESSAGES["fa_can_diem_quyet_tam"]["vi"].lower() or \
        "huy chương" in MESSAGES["fa_can_diem_quyet_tam"]["vi"].lower()


def test_tao_workspace_bat_fa_tat_wharton(api):
    ra = api.create_workspace("Đợt sai", {"rules": {"wharton": False, "fa_daa": True}})
    assert _ma(ra) == ["fa_can_diem_quyet_tam"]


def test_sua_cau_hinh_bat_fa_tat_wharton(api):
    ra = api.update_workspace_config({"rules": {"wharton": False, "fa_daa": True}})
    assert _ma(ra) == ["fa_can_diem_quyet_tam"]


def test_loi_khac_van_la_loi_chung(api):
    ra = api.update_workspace_config({"rules": {"fa_daa": "co"}})
    assert _ma(ra) == ["ws_du_lieu_sai"]


def test_bat_ca_hai_van_duoc(api):
    assert api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})["ok"]
