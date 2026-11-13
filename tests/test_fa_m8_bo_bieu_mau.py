"""FA-M8 giai đoạn 1 (TH = chưa thử trên Microsoft thật): bộ biểu mẫu một lần bấm — hàm thuần.

R3: không đặt đáp án trên Forms (`dap_an_tren_forms=False`); R8: một thư mục + một zip cho cả đường A / B;
R9: phiếu thiết lập CLB sinh từ PHIEU_THIET_LAP_CLB.md §1. Dữ liệu MÔ PHỎNG (de_thi.json mặc định).
"""
import copy
import os
import re
import sys
import zipfile

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_FORMS = os.path.join(GOC, "mau_forms_thi_clb")
sys.path.insert(0, THU_MUC_FORMS)
sys.path.insert(0, GOC)

import bieu_mau as bm  # noqa: E402
import chuyen_phieu_clb as pc  # noqa: E402
import tao_mau_forms as tm  # noqa: E402


DE = bm.doc_de_thi()
CO_DE = [c["club_id"] for c in bm.clb_co_thi(DE)]
DONG_DU_PHONG = tm.DONG_DU_PHONG_KHONG_DAP_AN


def _de_bien_the():
    de = copy.deepcopy(DE)
    for c in bm.clb_co_thi(de)[:2]:
        c["de_thi_bien_the"] = [[dict(q, cau=q["cau"] + " (đề B)") for q in c["de_thi"]]]
    return de


def _tep_md(thu_muc):
    ds = []
    for goc, _d, tep in os.walk(thu_muc):
        ds += [os.path.relpath(os.path.join(goc, t), thu_muc).replace(os.sep, "/") for t in tep]
    return sorted(ds)


def _doc_tat_ca_md(thu_muc):
    chu = []
    for t in _tep_md(thu_muc):
        if t.endswith(".md"):
            with open(os.path.join(thu_muc, t), encoding="utf-8") as f:
                chu.append(f.read())
    return "\n".join(chu)


def _dong_docx(duong):
    from docx import Document
    return [p.text for p in Document(duong).paragraphs]


def _tieu_de_tu_md():
    """Cột 2 của bảng §1 trong PHIEU_THIET_LAP_CLB.md (mã dòng 1a, 1b, 2, 2a … 5)."""
    with open(os.path.join(THU_MUC_FORMS, "PHIEU_THIET_LAP_CLB.md"), encoding="utf-8") as f:
        dong = f.read().split("## 2.")[0].splitlines()
    kq = []
    for d in dong:
        o = [x.strip() for x in d.strip().strip("|").split("|")]
        if len(o) >= 3 and re.fullmatch(r"\d[a-d]?", o[0]):
            kq.append(o[1])
    return kq


# ----------------------------------------------------------------- R9: phiếu thiết lập CLB

def test_tieu_de_phieu_clb_khop_tai_lieu_va_bo_chuyen_doi():
    tieu_de = _tieu_de_tu_md()
    assert len(tieu_de) == 14
    assert sorted(tieu_de) == sorted(pc.TIEU_DE_PHIEU)
    assert sorted(bm.TIEU_DE_PHIEU_CLB) == sorted(pc.TIEU_DE_PHIEU)


def test_phieu_clb_docx_co_du_tieu_de_nguyen_van(tmp_path):
    ra = tm.sinh_phieu_clb(DE, str(tmp_path))
    ten = sorted(os.path.basename(x) for x in ra)
    assert ten == [tm.TEN_CAI_DAT_PHIEU_CLB, tm.TEN_DOCX_PHIEU_CLB]
    dong = [re.sub(r"^\d+\.\s+", "", d) for d in _dong_docx(str(tmp_path / tm.TEN_DOCX_PHIEU_CLB))]
    for td in _tieu_de_tu_md():
        assert td in dong, td
    md = (tmp_path / tm.TEN_CAI_DAT_PHIEU_CLB).read_text(encoding="utf-8")
    for td in _tieu_de_tu_md():
        assert td in md, td


def test_phieu_clb_huong_dan_neu_hai_re_nhanh_tay(tmp_path):
    tm.sinh_phieu_clb(DE, str(tmp_path))
    md = (tmp_path / tm.TEN_CAI_DAT_PHIEU_CLB).read_text(encoding="utf-8")
    assert md.count("Go to") >= 3
    assert "Add branching" in md
    assert "chuyen_phieu_clb.py" in md


def test_xuat_gia_dung_tieu_de_cua_docx_di_qua_bo_chuyen_phieu_clb(tmp_path):
    """Tệp xuất giả lập mang đúng tiêu đề lấy từ chính .docx đã sinh -> bộ chuyển đổi phiếu CLB đọc được."""
    tm.sinh_phieu_clb(DE, str(tmp_path))
    tieu_de = [re.sub(r"^\d+\.\s+", "", d) for d in _dong_docx(str(tmp_path / tm.TEN_DOCX_PHIEU_CLB))]
    tieu_de = [d for d in tieu_de if d in set(pc.TIEU_DE_PHIEU)]
    assert sorted(tieu_de) == sorted(pc.TIEU_DE_PHIEU)
    gia_tri = {"Tên CLB": "CLB Mô phỏng", "Buổi": "Thứ 2", "Giờ": "15:30", "Địa điểm": "Phòng A",
               "Mở thêm nhóm được nếu đông không? (Có/Không)": "Có", "Sức chứa mỗi nhóm": "30",
               "Số thành viên tối thiểu": "8"}
    p = tmp_path / "xuat.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu_de)
    ws.append([gia_tri.get(h, "") for h in tieu_de])
    wb.save(p)
    kq = pc.doc_phieu_clb(str(p))
    assert not kq["loi"]
    assert [c["name"] for c in kq["clubs"]] == ["CLB Mô phỏng"]


# ----------------------------------------------------------------- R3: không đáp án trên Forms

BO_GHI_CAI_DAT = [
    ("chi_thi", lambda de, **kw: tm.ghi_cai_dat_chi_thi(de, bm.chia_theo_buoi(de, chi_thi=True), **kw)),
    ("moi_clb", lambda de, **kw: tm.ghi_cai_dat_moi_clb(de, **kw)),
    ("bien_the", lambda de, **kw: tm.ghi_cai_dat_bien_the(
        de, [c for c in de["cau_lac_bo"] if c.get("de_thi_bien_the")], **kw)),
    ("mac_dinh", lambda de, **kw: tm.ghi_cai_dat(de, **kw)),
]


@pytest.mark.parametrize("ten,ghi", BO_GHI_CAI_DAT, ids=[t for t, _ in BO_GHI_CAI_DAT])
def test_dap_an_tren_forms_false_khong_dan_tick_va_co_dong_du_phong(ten, ghi):
    de = _de_bien_the()
    mac_dinh = ghi(de)
    assert mac_dinh == ghi(de, dap_an_tren_forms=True)      # mặc định = như cũ
    khong = ghi(de, dap_an_tren_forms=False)
    assert "Correct answer" not in khong
    assert DONG_DU_PHONG in khong
    assert "Time limit" in khong
    assert "Show results" in khong
    assert khong != mac_dinh
    if ten != "bien_the":
        assert "Correct answer" in mac_dinh


def test_dap_an_tren_forms_false_khong_in_bang_dap_an_cho_it():
    de = DE
    khong = tm.ghi_cai_dat_moi_clb(de, dap_an_tren_forms=False)
    clb = bm.clb_co_thi(de)[0]
    cau = clb["de_thi"][0]
    assert "XEM_LAI_DAP_AN.xlsx" in khong
    assert "| `[%s-1]` %s |" % (clb["club_id"], cau["cau"]) not in khong


def test_sinh_chi_thi_moi_clb_bien_the_chuyen_tham_so(tmp_path):
    de = _de_bien_the()
    for sinh, ten in ((tm.sinh_chi_thi, "a"), (tm.sinh_moi_clb, "b"), (tm.sinh_bien_the, "c")):
        d = tmp_path / ten
        sinh(de, str(d), dap_an_tren_forms=False)
        assert "Correct answer" not in _doc_tat_ca_md(str(d))
        d2 = tmp_path / (ten + "2")
        sinh(de, str(d2))
        assert "Correct answer" in _doc_tat_ca_md(str(d2)) or sinh is tm.sinh_bien_the


# ----------------------------------------------------------------- XEM_LAI_DAP_AN.xlsx

def test_xem_lai_dap_an_so_dong_bang_so_cau_ke_ca_bien_the(tmp_path):
    de = _de_bien_the()
    p = tmp_path / "x.xlsx"
    tm.ghi_xem_lai_dap_an(de, str(p))
    ws = openpyxl.load_workbook(p).active
    dong = list(ws.iter_rows(values_only=True))
    assert dong[0] == ("CLB", "Mã CLB", "Đề", "Câu", "Nội dung câu", "Đáp án đúng")
    n_cau = sum(len(d) for c in bm.clb_co_thi(de) for d in [c["de_thi"]] + list(c.get("de_thi_bien_the") or []))
    assert len(dong) - 1 == n_cau
    c0 = bm.clb_co_thi(de)[0]
    mot = [r for r in dong[1:] if r[1] == c0["club_id"] and r[2] == "A" and r[3] == 1][0]
    q = c0["de_thi"][0]
    assert mot[5] == "%s. %s" % ("abcdefghijklmnopqrstuvwxyz"[q["dap_an"]].upper(), q["lua_chon"][q["dap_an"]])
    assert {r[2] for r in dong[1:] if r[1] == c0["club_id"]} == {"A", "B"}


def test_xem_lai_dap_an_de_mac_dinh_khong_bien_the(tmp_path):
    p = tmp_path / "x.xlsx"
    tm.ghi_xem_lai_dap_an(DE, str(p))
    ws = openpyxl.load_workbook(p).active
    assert ws.max_row - 1 == sum(len(c["de_thi"]) for c in bm.clb_co_thi(DE))


# ----------------------------------------------------------------- bộ biểu mẫu

def test_bo_duong_b_danh_sach_tep_dung(tmp_path):
    ra = tm.tao_bo_bieu_mau(DE, str(tmp_path), duong="B")
    mong = ["00_DOC_TRUOC.md",
            "01_phieu_clb/" + tm.TEN_CAI_DAT_PHIEU_CLB, "01_phieu_clb/" + tm.TEN_DOCX_PHIEU_CLB,
            "02_dang_ky/" + tm.TEN_CAI_DAT_DANG_KY, "02_dang_ky/" + tm.TEN_DOCX_DANG_KY_TAT_CA,
            "03_bai_thi/" + tm.TEN_CAI_DAT_MOI_CLB, "03_bai_thi/" + tm.TEN_CLB_CSV,
            "04_sau_ket_qua/" + tm.TEN_CAI_DAT_SAU_KET_QUA, "04_sau_ket_qua/" + tm.TEN_DOCX_SAU_KET_QUA,
            "05_khao_sat_tuan_3/CAI_DAT_FORMS_TUAN_3.md", "05_khao_sat_tuan_3/NHAP_FORMS_TUAN_3.docx",
            "XEM_LAI_DAP_AN.xlsx"]
    mong += ["03_bai_thi/%s%s.docx" % (tm.TIEN_TO_DOCX_MOI_CLB, c) for c in CO_DE]
    if not bm.dang_giu_ma():      # SG-12: mỗi biểu mẫu của học sinh có MAP_<tên>.json cạnh nó (phiếu CLB của giáo viên thì không)
        mong += [os.path.dirname(x) + "/MAP_" + os.path.basename(x)[:-5] + ".json"
                 for x in mong if x.endswith(".docx") and "01_phieu_clb" not in x]
    assert sorted(ra) == sorted(mong)
    assert _tep_md(str(tmp_path)) == sorted(mong)


def test_bo_duong_b_nhieu_bieu_mau_moi_ngay_mot_docx(tmp_path):
    ra = tm.tao_bo_bieu_mau(DE, str(tmp_path), duong="B", mot_bieu_mau=False)
    dk = [x for x in ra if x.startswith("02_dang_ky/") and x.endswith(".docx")]
    assert sorted(dk) == sorted("02_dang_ky/%s%s.docx" % (tm.TIEN_TO_DOCX_DANG_KY, b["ma"]) for b in DE["buoi"])


def test_bo_duong_a_dung_bo_dung_t4m_va_khong_co_dang_ky(tmp_path):
    ra = tm.tao_bo_bieu_mau(DE, str(tmp_path), duong="A")
    assert not any(x.startswith("02_dang_ky/") for x in ra)
    assert "02_bo_dung_t4m/HUONG_DAN_IT.md" in ra
    assert "02_bo_dung_t4m/00_FA_DAA_GHI_CHU.md" in ra          # --fa-daa
    for c in CO_DE:
        assert "02_bo_dung_t4m/04_forms/%s%s.docx" % (tm.TIEN_TO_DOCX_MOI_CLB, c) in ra
    for x in ("00_DOC_TRUOC.md", "XEM_LAI_DAP_AN.xlsx", "01_phieu_clb/" + tm.TEN_DOCX_PHIEU_CLB,
              "04_sau_ket_qua/" + tm.TEN_DOCX_SAU_KET_QUA, "05_khao_sat_tuan_3/NHAP_FORMS_TUAN_3.docx"):
        assert x in ra
    assert sorted(ra) == _tep_md(str(tmp_path))


def test_bo_bien_the_them_thu_muc_de_b(tmp_path):
    de = _de_bien_the()
    ra = tm.tao_bo_bieu_mau(de, str(tmp_path), duong="B", bien_the=True)
    bt = [x for x in ra if x.startswith("03b_bai_thi_bien_the/")]
    assert "03b_bai_thi_bien_the/" + tm.TEN_CAI_DAT_BIEN_THE in bt
    assert len([x for x in bt if x.endswith(".docx")]) == 4          # 2 CLB × (A, B)


def test_bo_bien_the_ma_khong_clb_nao_co_de_bien_the_bao_loi_va_khong_ghi(tmp_path):
    with pytest.raises(bm.LoiDeThi):
        tm.tao_bo_bieu_mau(DE, str(tmp_path / "ra"), duong="B", bien_the=True)
    assert not (tmp_path / "ra").exists() or not _tep_md(str(tmp_path / "ra"))


def test_duong_sai_bao_loi(tmp_path):
    with pytest.raises(ValueError):
        tm.tao_bo_bieu_mau(DE, str(tmp_path), duong="C")


def test_doc_truoc_liet_ke_dung_thu_tu_va_moi_tep_docx(tmp_path):
    for duong in ("A", "B"):
        d = tmp_path / duong
        ra = tm.tao_bo_bieu_mau(DE, str(d), duong=duong)
        md = (d / "00_DOC_TRUOC.md").read_text(encoding="utf-8")
        assert "TH" in md
        vi_tri = [md.index(x) for x in ("01_phieu_clb/", "04_sau_ket_qua/", "05_khao_sat_tuan_3/")]
        assert vi_tri == sorted(vi_tri)
        for x in ra:
            if x.endswith(".docx") and not x.startswith("02_bo_dung_t4m/") and "/NHAP_FORMS_MOI_CLB_" not in x:
                assert x.split("/")[0] in md or os.path.basename(x) in md


def test_bo_khong_co_dap_an_tren_forms_o_moi_huong_dan(tmp_path):
    """R3: mọi hướng dẫn trong bộ (cả bộ dựng T4M của đường A) không dặn tick đáp án đúng."""
    for duong in ("A", "B"):
        d = tmp_path / duong
        tm.tao_bo_bieu_mau(_de_bien_the(), str(d), duong=duong, bien_the=True)
        assert "Correct answer" not in _doc_tat_ca_md(str(d)), duong
        assert DONG_DU_PHONG in _doc_tat_ca_md(str(d)), duong


def test_bo_xem_lai_dap_an_la_noi_duy_nhat_co_dap_an(tmp_path):
    d = tmp_path / "b"
    tm.tao_bo_bieu_mau(DE, str(d), duong="B")
    ws = openpyxl.load_workbook(d / "XEM_LAI_DAP_AN.xlsx").active
    assert ws.max_row - 1 == sum(len(c["de_thi"]) for c in bm.clb_co_thi(DE))


def test_tao_bo_khong_sua_de(tmp_path):
    de = copy.deepcopy(DE)
    tm.tao_bo_bieu_mau(de, str(tmp_path / "a"), duong="A")
    tm.tao_bo_bieu_mau(de, str(tmp_path / "b"), duong="B")
    assert de == DE


def test_sinh_lai_cho_cung_tep_docx(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    tm.tao_bo_bieu_mau(DE, str(a), duong="B")
    tm.tao_bo_bieu_mau(DE, str(b), duong="B")
    for x in _tep_md(str(a)):
        if x.endswith((".docx", ".md", ".csv")):
            assert (a / x).read_bytes() == (b / x).read_bytes(), x


def test_ghi_zip_bo_giong_thu_muc(tmp_path):
    thu = tmp_path / "bo"
    ra = tm.tao_bo_bieu_mau(DE, str(thu), duong="B")
    z = tmp_path / "BO.zip"
    tm.ghi_zip_bo(str(thu), str(z))
    with zipfile.ZipFile(z) as zf:
        assert sorted(zf.namelist()) == sorted(ra)
        for x in ra:
            assert zf.read(x) == (thu / x).read_bytes()


def test_ghi_zip_bo_duong_a_cung_giong_thu_muc(tmp_path):
    thu = tmp_path / "bo"
    ra = tm.tao_bo_bieu_mau(DE, str(thu), duong="A")
    z = tmp_path / "BO.zip"
    tm.ghi_zip_bo(str(thu), str(z))
    with zipfile.ZipFile(z) as zf:
        assert sorted(zf.namelist()) == sorted(ra)


def test_duong_b_voi_so_nhap_clb_doi_loai(tmp_path):
    """`so_nhap_clb` đi vào đăng ký như `--so-nhap-clb` của CLI: CLB Tự do không có trong câu huy chương vàng."""
    c0 = DE["cau_lac_bo"][0]
    tieu_de = list(pc.TIEU_DE_PHIEU)
    dong = dict.fromkeys(tieu_de, "")
    dong.update({"Tên CLB": c0["name"], "Buổi": "Thứ 2", "Mở thêm nhóm được nếu đông không? (Có/Không)": "Có",
                 "Sức chứa mỗi nhóm": "30", "Số thành viên tối thiểu": "8"})
    x = tmp_path / "phieu.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(tieu_de)
    wb.active.append([dong[h] for h in tieu_de])
    wb.save(x)
    so = pc.chuyen_phieu(str(x), str(tmp_path / "ra"))["so_nhap"]
    a = tm.tao_bo_bieu_mau(DE, str(tmp_path / "khong"), duong="B")
    b = tm.tao_bo_bieu_mau(DE, str(tmp_path / "co"), duong="B", so_nhap_clb=so)
    assert a == b
    f = "02_dang_ky/" + tm.TEN_DOCX_DANG_KY_TAT_CA
    assert _dong_docx(str(tmp_path / "khong" / f)) != _dong_docx(str(tmp_path / "co" / f))


def test_so_nhap_clb_hong_bao_loi_va_khong_ghi(tmp_path):
    p = tmp_path / "hong.xlsx"
    openpyxl.Workbook().save(p)
    with pytest.raises(bm.LoiDeThi):
        tm.tao_bo_bieu_mau(DE, str(tmp_path / "bo"), duong="B", so_nhap_clb=str(p))
    assert not (tmp_path / "bo").exists()


def test_huong_dan_it_duong_a_khong_dan_dat_dap_an(tmp_path):
    tm.tao_bo_bieu_mau(DE, str(tmp_path), duong="A")
    md = (tmp_path / "02_bo_dung_t4m" / "HUONG_DAN_IT.md").read_text(encoding="utf-8")
    assert "đáp án đúng và điểm mỗi câu" not in md
    assert "XEM_LAI_DAP_AN.xlsx" in md
