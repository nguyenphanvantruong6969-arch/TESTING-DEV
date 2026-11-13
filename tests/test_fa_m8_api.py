"""FA-M8 Phase 2 (TH = CHƯA thử trên Microsoft / Google thật): API `tao_bo_bieu_mau_api` / `get_bo_bieu_mau`.

Đề lấy từ `forms/de_thi.json` của đợt, đường từ `rules.fa_duong`; ghi `forms/bieu_mau/` và một tệp zip ở Tải xuống.
R3: bộ KHÔNG dặn đặt đáp án trên Forms. Dữ liệu MÔ PHỎNG.
"""
import copy
import json
import os
import shutil
import zipfile

import pytest

import forms_dot

forms_dot.nap_mau_forms()
import bieu_mau  # noqa: E402



@pytest.fixture
def ap(api, tmp_path):
    api.thu_muc_xuat = str(tmp_path / "tai_ve")
    os.makedirs(api.thu_muc_xuat)
    return api


def _dat_de(api, bien_the=False):
    de = bieu_mau.doc_de_thi()
    if bien_the:
        c = next(x for x in de["cau_lac_bo"] if x["de_thi"])
        c["de_thi_bien_the"] = [copy.deepcopy(c["de_thi"]), copy.deepcopy(c["de_thi"])]
    with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
        json.dump(de, f, ensure_ascii=False)
    return de


def _codes(res):
    return [e["code"] for e in res["errors"]]


def test_chua_co_de(ap):
    ap.dat_fa_duong("B")
    res = ap.tao_bo_bieu_mau_api({})
    assert not res["ok"] and _codes(res) == ["forms_chua_co_de"]


def test_chua_chon_duong(ap):
    _dat_de(ap)
    res = ap.tao_bo_bieu_mau_api({})
    assert not res["ok"] and _codes(res) == ["forms_duong_chua_chon"]


def test_duong_b_ghi_thu_muc_va_zip(ap):
    _dat_de(ap)
    ap.dat_fa_duong("B")
    res = ap.tao_bo_bieu_mau_api({})
    assert res["ok"], res
    d = res["data"]
    assert d["duong"] == "B" and d["n_tep"] > 5
    assert os.path.dirname(d["path"]) == ap.thu_muc_xuat and d["path"].endswith(".zip")
    assert os.path.basename(d["path"]).startswith("BO_BIEU_MAU_")
    thu_muc = forms_dot.thu_muc_bieu_mau(ap.db_path)
    assert os.path.isfile(os.path.join(thu_muc, "00_DOC_TRUOC.md"))
    with zipfile.ZipFile(d["path"]) as z:
        ten = z.namelist()
    assert len(ten) == d["n_tep"] and "00_DOC_TRUOC.md" in ten and "XEM_LAI_DAP_AN.xlsx" in ten


def test_duong_a_co_bo_dung(ap):
    _dat_de(ap)
    ap.dat_fa_duong("A")
    res = ap.tao_bo_bieu_mau_api({})
    assert res["ok"], res
    assert res["data"]["duong"] == "A"
    with zipfile.ZipFile(res["data"]["path"]) as z:
        assert any("04_forms" in n for n in z.namelist())


def test_r3_bo_khong_dan_dat_dap_an_tren_forms(ap):
    """R3 ở tầng API: cả hai đường, mọi hướng dẫn trong zip không dặn tích "Correct answer"."""
    _dat_de(ap)
    for duong in ("A", "B"):
        ap.dat_fa_duong(duong)
        res = ap.tao_bo_bieu_mau_api({})
        assert res["ok"], res
        with zipfile.ZipFile(res["data"]["path"]) as z:
            for n in z.namelist():
                if n.endswith((".md", ".txt")) and "DOC_TRUOC" not in n:
                    chu = z.read(n).decode("utf-8")
                    assert "tích đáp án đúng" not in chu.lower() and "correct answer" not in chu.lower() \
                        or "không" in chu.lower(), (duong, n)
        # Bộ chỉ có đáp án ở tệp xem lại, không ở hướng dẫn đặt trên Forms
        with zipfile.ZipFile(res["data"]["path"]) as z:
            assert "XEM_LAI_DAP_AN.xlsx" in z.namelist()


def test_r3_so_voi_dap_an_tren_forms_true(ap):
    """Gốc rễ R3: bản dựng của API phải TRÙNG bản `dap_an_tren_forms=False` và KHÁC bản `True`."""
    import tao_mau_forms as tm
    de = _dat_de(ap)
    ap.dat_fa_duong("B")
    res = ap.tao_bo_bieu_mau_api({})
    thu_muc = forms_dot.thu_muc_bieu_mau(ap.db_path)
    bai = os.path.join(thu_muc, tm.THU_MUC_BAI_THI)
    tam = os.path.join(os.path.dirname(thu_muc), "_doi_chung")
    tm.sinh_moi_clb(de, tam, dap_an_tren_forms=True)
    khac = [n for n in os.listdir(tam)
            if n.endswith(".md") and open(os.path.join(tam, n), encoding="utf-8").read()
            == open(os.path.join(bai, n), encoding="utf-8").read()]
    shutil.rmtree(tam)
    assert res["ok"] and khac == [], "bộ của API trùng bản có đáp án trên Forms: %s" % khac


def test_mot_bieu_mau_theo_tuy_chon(ap):
    _dat_de(ap)
    ap.dat_fa_duong("B")
    gop = ap.tao_bo_bieu_mau_api({"mot_bieu_mau": True})
    n_gop = gop["data"]["n_tep"]
    rieng = ap.tao_bo_bieu_mau_api({"mot_bieu_mau": False})
    assert gop["ok"] and rieng["ok"]
    assert rieng["data"]["n_tep"] != n_gop        # mỗi buổi một biểu mẫu -> số tệp đăng ký khác


def test_bien_the_khong_co_thi_loi(ap):
    _dat_de(ap)
    ap.dat_fa_duong("B")
    res = ap.tao_bo_bieu_mau_api({"bien_the": True})
    assert not res["ok"] and _codes(res) == ["forms_tao_bo_loi"]


def test_bien_the_co_thi_them_tep(ap):
    _dat_de(ap, bien_the=True)
    ap.dat_fa_duong("B")
    co = ap.tao_bo_bieu_mau_api({"bien_the": True})
    khong = ap.tao_bo_bieu_mau_api({"bien_the": False})
    assert co["ok"] and khong["ok"] and co["data"]["n_tep"] > khong["data"]["n_tep"]


def test_trang_thai(ap):
    t = ap.get_bo_bieu_mau()["data"]
    assert t == {"co_de": False, "duong": None, "co_bien_the": False}
    _dat_de(ap, bien_the=True)
    ap.dat_fa_duong("A")
    t = ap.get_bo_bieu_mau()["data"]
    assert t == {"co_de": True, "duong": "A", "co_bien_the": True}


def test_goi_hai_lan_khong_de_tep_cu(ap):
    _dat_de(ap)
    ap.dat_fa_duong("B")
    a = ap.tao_bo_bieu_mau_api({})
    b = ap.tao_bo_bieu_mau_api({})
    assert a["ok"] and b["ok"] and a["data"]["path"] != b["data"]["path"]   # không ghi đè tệp zip trước
    assert os.path.isfile(a["data"]["path"])


def test_khong_ghi_vao_app_db(ap):
    import sqlite3
    _dat_de(ap)
    ap.dat_fa_duong("B")
    con = sqlite3.connect(ap.db_path)
    truoc = con.execute("select count(*) from run_history").fetchone()[0]
    ap.tao_bo_bieu_mau_api({})
    assert con.execute("select count(*) from run_history").fetchone()[0] == truoc
    con.close()
