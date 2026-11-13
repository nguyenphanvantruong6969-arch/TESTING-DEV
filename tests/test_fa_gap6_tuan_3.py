"""GAP-6: khảo sát tuần 3 (hai câu: còn đi CLB không? muốn đổi không?) — mẫu Forms (TH — chưa thử trên Microsoft
thật), nạp tệp xuất qua cùng bộ nhập của GAP-5, tổng hợp và trang "Tuần 3" trong tệp xuất. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
from test_fa_gap5_phan_hoi import _dung, _lc, _xlsx_forms, bm, tmf


def test_sinh_mau_forms_tuan_3_va_sinh_lai_giong_het(tmp_path):
    assert tmf.main(["--tuan-3", "--ra", str(tmp_path)]) == 0
    md = tmp_path / "CAI_DAT_FORMS_TUAN_3.md"
    dx = tmp_path / "NHAP_FORMS_TUAN_3.docx"
    assert md.exists() and dx.exists() and "TH" in md.read_text(encoding="utf-8")
    truoc = (md.read_bytes(), dx.read_bytes())
    assert tmf.main(["--tuan-3", "--ra", str(tmp_path)]) == 0
    assert (md.read_bytes(), dx.read_bytes()) == truoc
    from docx import Document
    chu = "\n".join(p.text for p in Document(str(dx)).paragraphs)
    assert bm.CAU_CON_DI in chu and bm.CAU_MUON_DOI in chu


def test_nhap_tuan_3_va_tong_hop(api):
    _dung(api)
    dau = ["ID", bm.cau_ma_hoc_sinh(), bm.CAU_CON_DI, bm.CAU_MUON_DOI]
    tep = _xlsx_forms([dau,
                       [1, "s1", _lc(bm.CAU_CON_DI, "1"), _lc(bm.CAU_MUON_DOI, "0")],
                       [2, "s2", _lc(bm.CAU_CON_DI, "0"), _lc(bm.CAU_MUON_DOI, "1")],
                       [3, "s3", _lc(bm.CAU_CON_DI, "1"), _lc(bm.CAU_MUON_DOI, "1")]])
    ra = api.nhap_phan_hoi_forms(tep)
    assert ra["ok"] and ra["data"] == {"n_ket_qua": 0, "n_tuan_3": 3, "bo_qua": 0, "hoc_sinh": 3,
                                "ma_khong_khop": [], "dong_moi": 3, "dong_trung": 0, "dong_bo_qua": []}, ra
    w = api.get_phan_hoi_tong_hop()["data"]["tuan_3"]
    assert w["n"] == 3 and abs(w["con_di_ty_le"] - 2 / 3) < 1e-9 and abs(w["muon_doi_ty_le"] - 2 / 3) < 1e-9
    with api._ket_noi_doc() as cur:
        assert [tuple(r) for r in cur.execute(
            "SELECT con_di, muon_doi FROM fa_phan_hoi WHERE student_id='s1'")] == [(1, 0)]


def test_tep_co_ca_hai_loai_cau(api):
    _dung(api)
    dau = [bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT, bm.CAU_CON_DI, bm.CAU_MUON_DOI]
    tep = _xlsx_forms([dau, ["s1", _lc(bm.CAU_HAI_LONG, "3"), _lc(bm.CAU_HIEU_LY_DO, "1"),
                             _lc(bm.CAU_KHO_NHAT, "khong_co"), _lc(bm.CAU_CON_DI, "1"), _lc(bm.CAU_MUON_DOI, "0")]])
    assert api.nhap_phan_hoi_forms(tep)["data"] == {
        "n_ket_qua": 1, "n_tuan_3": 1, "bo_qua": 0, "hoc_sinh": 1,
        "ma_khong_khop": [], "dong_moi": 2, "dong_trung": 0, "dong_bo_qua": []}


def test_xuat_co_trang_tuan_3(api, tmp_path):
    from openpyxl import load_workbook
    _dung(api)
    tep = _xlsx_forms([[bm.cau_ma_hoc_sinh(), bm.CAU_CON_DI, bm.CAU_MUON_DOI],
                       ["s1", _lc(bm.CAU_CON_DI, "1"), _lc(bm.CAU_MUON_DOI, "0")]])
    api.nhap_phan_hoi_forms(tep)
    ra = api.export_phan_hoi(str(tmp_path / "ph.xlsx"))
    wb = load_workbook(ra["data"]["path"])
    assert "Tuần 3" in wb.sheetnames
    chu = [str(c.value) for r in wb["Tuần 3"].iter_rows() for c in r if c.value is not None]
    assert "Tỉ lệ còn đi CLB" in chu and "s1" not in chu
