"""A13.11 — sửa phát hiện N1–N4 của đợt stress test trên đỉnh A13.9 (`VAN_DE_STRESS_TEST.md`).

  N1. Đường xuất là một THƯ MỤC có sẵn → từ chối bằng lỗi có tên, không đẻ tệp `x (2)` cạnh nó.
  N2. wharton_nhat_ky: mỗi lần nạp Sổ / CSV ghi MỘT dòng tóm tắt (nap_tep), không một dòng mỗi em.
  N3. Mọi hàm gặp CSDL bận dùng `csdl_dang_ban`, chờ ≤ 3 s (giữ sao lưu trước khi chạy).
  N4. Giao diện: thẻ Kết quả / lật trang ở quy mô lớn (xem `test_giao_dien_a13_11_*.py`).
"""

import os

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
    assert res["errors"][0]["params"]["path"] == str(thu_muc)
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
