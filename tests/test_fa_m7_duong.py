"""FA-M7 G0: chọn đường A / B (`rules.fa_duong`) qua `get_fa_duong` / `dat_fa_duong`.

Không ảnh hưởng kết quả xếp: bảng `match_results` y nguyên. Dữ liệu MÔ PHỎNG.
"""
import cau_hinh_ws as ch
from _fa import dung_fa_clb, dung_hs_fa


def _bat(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})


def test_mac_dinh_chua_chon(api):
    r = api.get_fa_duong()
    assert r["ok"] and r["data"] == {"duong": None}


def test_dat_a_roi_b_ok_va_doc_lai(api):
    for d in ("A", "B"):
        r = api.dat_fa_duong(d)
        assert r["ok"] and r["data"] == {"duong": d}
        assert api.get_fa_duong()["data"] == {"duong": d}
        assert api._luat_nghiem().get("fa_duong") == d


def test_gia_tri_khac_bi_tu_choi(api):
    for xau in ("C", "a", "", None, 1, "AB"):
        r = api.dat_fa_duong(xau)
        assert not r["ok"] and r["errors"][0]["code"] == "forms_duong_chua_chon", xau
    assert api.get_fa_duong()["data"] == {"duong": None}


def test_luu_trong_rules_khong_doi_cac_khoa_khac(api):
    truoc = dict(api._luat_nghiem())
    assert api.dat_fa_duong("A")["ok"]
    sau = dict(api._luat_nghiem())
    assert sau.pop("fa_duong") == "A"
    truoc.pop("fa_duong", None)
    assert sau == truoc


def test_fa_duong_khong_vao_luat_xep(api):
    from rbda_priority_pipeline import luat_xep_de_ghi
    _bat(api)
    truoc = luat_xep_de_ghi(api._luat_nghiem())
    assert api.dat_fa_duong("B")["ok"]
    assert luat_xep_de_ghi(api._luat_nghiem()) == truoc


def test_ket_qua_xep_khong_doi(api):
    _bat(api)
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})

    def _anh_chup():
        with api._ket_noi_doc() as cur:
            return cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi").fetchall()

    assert api.run_pipeline(seed=5)["ok"]
    truoc = _anh_chup()
    assert api.dat_fa_duong("A")["ok"] and api.run_pipeline(seed=5)["ok"]
    assert _anh_chup() == truoc
