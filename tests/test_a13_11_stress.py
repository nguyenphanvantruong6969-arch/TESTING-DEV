"""A13.11 — sửa phát hiện N1–N4 của đợt stress test trên đỉnh A13.9 (`VAN_DE_STRESS_TEST.md`).

  N1. Đường xuất là một THƯ MỤC có sẵn → từ chối bằng lỗi có tên, không đẻ tệp `x (2)` cạnh nó.
  N2. wharton_nhat_ky: mỗi lần nạp Sổ / CSV ghi MỘT dòng tóm tắt (nap_tep), không một dòng mỗi em.
  N3. Mọi hàm gặp CSDL bận dùng `csdl_dang_ban`, chờ ≤ 3 s (giữ sao lưu trước khi chạy).
  N4. Giao diện: thẻ Kết quả / lật trang ở quy mô lớn (xem `test_giao_dien_a13_11_*.py`).
"""

import json
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
