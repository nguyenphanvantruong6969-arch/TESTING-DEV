"""GAP-5: ba câu phản hồi một chạm (hài lòng 1–5; hiểu vì sao có/không; phần khó nhất) — màn hình kiosk, mẫu Forms
(TH — chưa thử trên Microsoft thật), bộ nhập tệp xuất Forms, tổng hợp và tệp xuất. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import base64
import io
import os
import sys

import cau_hinh_ws as ch
import fa_sau_xep as sx
from _fa import dung_fa_clb, dung_hs_fa, ma
from test_fa_gap1_diem_danh import api_ws  # noqa: F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
import bieu_mau as bm  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402


def _dung(api, ph=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_phan_hoi": ph}})
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", nv={s: ["G", "T"] for s in ("s1", "s2", "s3")})
    assert api.run_pipeline(seed=5)["ok"]


def test_co_mac_dinh_va_can_fa(api_ws):  # noqa: F811
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["fa_phan_hoi"] is False
    assert ma(api_ws.update_workspace_config({"rules": {"fa_phan_hoi": True}})["errors"]) == ["fa_tinh_nang_can_fa"]
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True, "fa_phan_hoi": True}})["ok"]


def test_co_tat(api):
    _dung(api, ph=False)
    assert api.get_phan_hoi_tong_hop() == {"ok": True, "data": {"bat": False}, "errors": []}
    assert ma(api.gui_phan_hoi("s1", 5, True, "khong_co")["errors"]) == ["fa_phan_hoi_chua_bat"]


def test_gui_luu_va_lan_sau_thay_lan_truoc(api):
    _dung(api)
    assert api.gui_phan_hoi("s1", 2, False, "huy_chuong")["ok"]
    assert api.gui_phan_hoi("s1", 4, True, "thu_thach")["ok"]
    assert api.gui_phan_hoi("s2", 5, True, "khong_co")["ok"]
    t = api.get_phan_hoi_tong_hop()["data"]["ket_qua"]
    assert t["n"] == 2 and t["hai_long_tb"] == 4.5 and t["hieu_ly_do_ty_le"] == 1.0
    assert t["kho_nhat_dem"]["thu_thach"] == 1 and t["kho_nhat_dem"]["huy_chuong"] == 0
    for sai in ((0, True, "khong_co"), (6, True, "khong_co"), (3, "co", "khong_co"), (3, True, "la"),
                (True, True, "khong_co")):
        assert ma(api.gui_phan_hoi("s1", *sai)["errors"]) == ["phan_hoi_gia_tri_sai"], sai
    assert ma(api.gui_phan_hoi("s9", 3, True, "khong_co")["errors"]) == ["student_not_found"]


def _dong(sid, loai, nguon="kiosk", **kw):
    d = {"id": kw.pop("id", 1), "student_id": sid, "loai": loai, "nguon": nguon, "hai_long": None,
         "hieu_ly_do": None, "kho_nhat": None, "con_di": None, "muon_doi": None, "created_at": ""}
    d.update(kw)
    return d


def test_tong_hop_thuan_lay_lan_cuoi_moi_em():
    rows = [_dong("a", "ket_qua", id=1, hai_long=1, hieu_ly_do=0, kho_nhat="chon_clb"),
            _dong("a", "ket_qua", id=2, hai_long=3, hieu_ly_do=1, kho_nhat="chon_clb"),
            _dong("b", "ket_qua", id=3, hai_long=5, hieu_ly_do=0, kho_nhat="xep_thu_tu")]
    t = sx.tong_hop_phan_hoi(rows, "ket_qua")
    assert t["n"] == 2 and t["hai_long_tb"] == 4.0 and t["hai_long_dem"] == {1: 0, 2: 0, 3: 1, 4: 0, 5: 1}
    assert t["hieu_ly_do_ty_le"] == 0.5 and t["kho_nhat_dem"]["chon_clb"] == 1
    assert sx.tong_hop_phan_hoi([], "ket_qua")["n"] == 0 and sx.tong_hop_phan_hoi([], "ket_qua")["hai_long_tb"] is None


# ----------------------------------------------------------------------------- Forms (TH)

def test_sinh_mau_forms_phan_hoi_va_sinh_lai_giong_het(tmp_path):
    assert tmf.main(["--phan-hoi", "--ra", str(tmp_path)]) == 0
    md = tmp_path / "CAI_DAT_FORMS_PHAN_HOI.md"
    dx = tmp_path / "NHAP_FORMS_PHAN_HOI.docx"
    assert md.exists() and dx.exists()
    assert "TH" in md.read_text(encoding="utf-8")
    truoc = (md.read_bytes(), dx.read_bytes())
    assert tmf.main(["--phan-hoi", "--ra", str(tmp_path)]) == 0
    assert (md.read_bytes(), dx.read_bytes()) == truoc
    from docx import Document
    chu = "\n".join(p.text for p in Document(str(dx)).paragraphs)
    for tieu_de in (bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT):
        assert tieu_de in chu


def _xlsx_forms(hang):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for h in hang:
        ws.append(h)
    b = io.BytesIO()
    wb.save(b)
    return base64.b64encode(b.getvalue()).decode("ascii")


def _lc(cau, ma_):
    """Lựa chọn có mã `ma_` của câu `cau` (tiêu đề) trong mẫu."""
    for _ten, cac in bm.cac_phan_phan_hoi() + getattr(bm, "cac_phan_tuan_3", list)():
        for tieu_de, _l, lua_chon, _b in cac:
            if tieu_de == cau:
                return next(x for x in lua_chon if bm.ma_trong_lua_chon(x) == ma_)
    raise KeyError(cau)


def test_nhap_tep_xuat_forms(api):
    _dung(api)
    dau = ["ID", "Start time", bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT]
    tep = _xlsx_forms([dau,
                       [1, "", "s1", _lc(bm.CAU_HAI_LONG, "4"), _lc(bm.CAU_HIEU_LY_DO, "1"),
                        _lc(bm.CAU_KHO_NHAT, "huy_chuong")],
                       [2, "", "s2", _lc(bm.CAU_HAI_LONG, "2"), _lc(bm.CAU_HIEU_LY_DO, "0"),
                        _lc(bm.CAU_KHO_NHAT, "khong_co")],
                       [3, "", "s9", _lc(bm.CAU_HAI_LONG, "5"), _lc(bm.CAU_HIEU_LY_DO, "1"),
                        _lc(bm.CAU_KHO_NHAT, "khong_co")]])
    ra = api.nhap_phan_hoi_forms(tep)
    assert ra["ok"], ra
    assert ra["data"] == {"n_ket_qua": 2, "n_tuan_3": 0, "bo_qua": 1,
                          "dong_moi": 2, "dong_trung": 0}
    t = api.get_phan_hoi_tong_hop()["data"]["ket_qua"]
    assert t["n"] == 2 and t["hai_long_tb"] == 3.0
    assert ma(api.nhap_phan_hoi_forms(_xlsx_forms([["a", "b"], [1, 2]]))["errors"]) == ["phan_hoi_tep_sai"]
    assert ma(api.nhap_phan_hoi_forms("khong-phai-base64")["errors"]) == ["phan_hoi_tep_sai"]


def test_xuat_hai_trang_khong_co_ten(api, tmp_path):
    from openpyxl import load_workbook
    _dung(api)
    api.gui_phan_hoi("s1", 4, True, "huy_chuong")
    ra = api.export_phan_hoi(str(tmp_path / "ph.xlsx"))
    assert ra["ok"], ra
    wb = load_workbook(ra["data"]["path"])
    assert wb.sheetnames[:2] == ["Tổng hợp", "Chi tiết"]
    chu = " ".join(str(c.value) for w in wb.worksheets for r in w.iter_rows() for c in r if c.value is not None)
    assert "Em s1" not in chu and "s1" in " ".join(
        str(c.value) for r in wb["Chi tiết"].iter_rows() for c in r if c.value is not None)
    assert "s1" not in " ".join(str(c.value) for r in wb["Tổng hợp"].iter_rows() for c in r if c.value is not None)


def test_doc_tep_forms_bo_gia_tri_ngoai_mien():
    """Tệp Forms bị sửa tay: mã ngoài miền (hài lòng 7, có/không 5, khó nhất lạ) thành None, không ghi số sai."""
    from fa_sau_xep import doc_tep_forms_phan_hoi
    dau = [bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT, bm.CAU_CON_DI, bm.CAU_MUON_DOI]
    ra = doc_tep_forms_phan_hoi([dau, ["s1", "7 (7)", "x (5)", "Khác (abc)", "x (2)", "Có (1)"],
                                 ["s2", "0 (0)", "Có (1)", "(khong_co)", "Không (0)", "x (9)"]])
    kq = {(d["student_id"], d["loai"]): d for d in ra}
    a, b = kq[("s1", "ket_qua")], kq[("s1", "tuan_3")]
    assert (a["hai_long"], a["hieu_ly_do"], a["kho_nhat"]) == (None, None, None)
    assert (b["con_di"], b["muon_doi"]) == (None, 1)
    c, d = kq[("s2", "ket_qua")], kq[("s2", "tuan_3")]
    assert (c["hai_long"], c["hieu_ly_do"], c["kho_nhat"]) == (None, 1, "khong_co")
    assert (d["con_di"], d["muon_doi"]) == (0, None)
