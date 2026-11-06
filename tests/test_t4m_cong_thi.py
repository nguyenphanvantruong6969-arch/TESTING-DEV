"""T4M-Q4a/b/c: cổng thi — mỗi CLB một biểu mẫu Forms.

  Q4a  tao_mau_forms.py --moi-clb: một tệp Quick Import mỗi CLB có đề (không câu cổng) + CLB.csv.
  Q4b  bộ chuyển đổi --chi-thi nhận N tệp xuất, mỗi tệp MỘT CLB (nhận diện theo thẻ [clb_x-k]).
  Q4c  --bai-thi BaiThi.csv: đối chiếu list trạng thái với các tệp xuất; không đổi điểm.

Dữ liệu hoàn toàn MÔ PHỎNG. Chế độ cũ (một biểu mẫu chung có câu cổng) không được đổi.
"""

import csv
import os
import sys
import time

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC = os.path.join(GOC, "mau_forms_thi_clb")
sys.path.insert(0, THU_MUC)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

MIEN = "@truong-gia.example.test"


@pytest.fixture
def de():
    return bm.doc_de_thi()


# ------------------------------------------------------------------ dựng tệp giả

def _ghi_lists(duong, hs, de):
    """hs: [(email, họ tên, {buổi: [club_id]})] -> CSV Lists rộng (cùng khuôn test_t4m_chi_thi)."""
    ten_thu = {b["ma"]: "Thứ " + b["ma"][-1] for b in de["buoi"]}
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["Email", "HoTen", "CoSo", "Khoi", "Lop", "Thu", "NV1", "NV2", "NV3",
                    "GhiChu", "NguoiSua", "TrangThai", "ThoiGian"])
        for email, ten, nv in hs:
            for b in de["buoi"]:
                ds = (nv.get(b["ma"], []) + ["", "", ""])[:3]
                w.writerow([email, ten, "CS1", 9, "9A1", ten_thu[b["ma"]], *ds,
                            "", "", "Đã khóa", "2026-11-02T07:00:00Z"])


def _tra_loi(clb, so_dung):
    """{số câu: nội dung chọn}: `so_dung` câu đầu đúng, còn lại sai."""
    return {i: clb["de_thi"][i - 1]["lua_chon"][
        cau["dap_an"] if i <= so_dung else (cau["dap_an"] + 1) % len(cau["lua_chon"])]
        for i, cau in enumerate(clb["de_thi"], 1)}


def _ghi_xuat_chung(de, duong, phieu):
    """Một biểu mẫu chung CÓ câu cổng (chế độ cũ). phieu: [(email, {club_id: số câu đúng})]."""
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"]
    for clb in bm.clb_co_thi(de):
        tieu.append(bm.cau_cong_thi(de, clb, chi_thi=True))
        tieu += [bm.cau_de_thi(clb, i) for i in range(1, len(clb["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for n, (email, thi) in enumerate(phieu, 1):
        o = {}
        for clb in bm.clb_co_thi(de):
            g = bm.cau_cong_thi(de, clb, chi_thi=True)
            if clb["club_id"] not in thi:
                o[g] = bm.KHONG
                continue
            o[g] = bm.CO
            for i, nd in _tra_loi(clb, thi[clb["club_id"]]).items():
                o[bm.cau_de_thi(clb, i)] = nd
        ws.append([n, None, None, email, "Tên Forms " + str(n)] + [o.get(c) for c in tieu[5:]])
    wb.save(duong)


def _ghi_xuat_clb(de, duong, ma_clb, phieu, them_cot=(), dong_trong=0):
    """MỘT biểu mẫu của một CLB, KHÔNG câu cổng. phieu: [(email, số câu đúng)]."""
    clb = next(c for c in de["cau_lac_bo"] if c["club_id"] == ma_clb)
    cot = [bm.cau_de_thi(clb, i) for i in range(1, len(clb["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Start time", "Completion time", "Email", "Name"] + cot + list(them_cot))
    for n, (email, dung) in enumerate(phieu, 1):
        tl = _tra_loi(clb, dung)
        ws.append([n, None, None, email, "Tên " + str(n)] + [tl[i] for i in sorted(tl)]
                  + [None] * len(them_cot))
    for n in range(dong_trong):
        ws.append([100 + n, None, None, "trong%d%s" % (n, MIEN), "x"] + [None] * (len(cot) + len(them_cot)))
    wb.save(duong)


def _doc_so(ra):
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True)
    du = so_nhap.doc_so_nhap(wb)
    wb.close()
    assert du["loi"] == [], du["loi"]
    return du


def _diem(du):
    return {s["student_id"]: {x["club_id"]: x["diem"] for x in s["nv"] if x["thi"]}
            for s in du["students"]}


HS = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua", "clb_vanhoc"], "thu_3": ["clb_tienganh"]}),
      ("hs0002" + MIEN, "Bình", {"thu_2": ["clb_vanhoc"], "thu_4": ["clb_robotics"]}),
      ("hs0003" + MIEN, "Chi", {"thu_2": ["clb_covua"]})]


def _ban_chung_va_rieng(tmp_path, de):
    """Cùng dữ liệu giả, hai cách nộp: MỘT biểu mẫu chung / mỗi CLB một tệp."""
    d = {"clb_covua": {"hs0001": 4, "hs0003": 2}, "clb_vanhoc": {"hs0001": 5, "hs0002": 1},
         "clb_tienganh": {"hs0001": 3}, "clb_robotics": {"hs0002": 5}}
    _ghi_lists(str(tmp_path / "lists.csv"), HS, de)
    chung = {}
    for ma, ds in d.items():
        for hs, dung in ds.items():
            chung.setdefault(hs + MIEN, {})[ma] = dung
    _ghi_xuat_chung(de, str(tmp_path / "chung.xlsx"), list(chung.items()))
    rieng = []
    for ma, ds in d.items():
        duong = str(tmp_path / ("rieng_%s.xlsx" % ma))
        _ghi_xuat_clb(de, duong, ma, [(hs + MIEN, dung) for hs, dung in ds.items()])
        rieng.append(duong)
    return rieng


# ------------------------------------------------------------------ Q4a

def test_q4a_bieu_mau_mot_clb_khong_co_cau_cong(de):
    clb = bm.clb_co_thi(de)[0]
    phan = bm.cac_phan_moi_clb(de, clb)
    cau = [c for _ten, cs in phan for c in cs]
    assert [bm.ma_cua_cau(c[0]) for c in cau] == ["%s-%d" % (clb["club_id"], i)
                                                  for i in range(1, len(clb["de_thi"]) + 1)]
    assert all(c[1] == "choice" and c[3] for c in cau)         # mọi câu: lựa chọn, bắt buộc
    assert not any("[thi-" in c[0] for c in cau)


def test_q4a_mot_tep_moi_clb_co_de_va_clb_csv(tmp_path, de):
    pytest.importorskip("docx")
    ra = tm.sinh_moi_clb(de, str(tmp_path))
    ten = sorted(os.path.basename(x) for x in ra)
    mong = sorted(["NHAP_FORMS_MOI_CLB_%s.docx" % c["club_id"] for c in bm.clb_co_thi(de)]
                  + ["CLB.csv", "CAI_DAT_FORMS_MOI_CLB.md"])
    assert ten == mong
    assert len([t for t in ten if t.endswith(".docx")]) == len(bm.clb_co_thi(de)) == 10
    with open(str(tmp_path / "CLB.csv"), encoding="utf-8-sig", newline="") as f:
        dong = list(csv.reader(f))
    assert dong[0] == ["ClubId", "Ten", "Buoi", "FormUrl"]
    assert [r[0] for r in dong[1:]] == [c["club_id"] for c in de["cau_lac_bo"]]   # cả CLB không thi
    assert all(r[3] == "" for r in dong[1:])
    covua = next(r for r in dong if r[0] == "clb_covua")
    assert covua[1] == next(c["name"] for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    assert covua[2] == bm.ten_buoi(de, "thu_2")


def test_q4a_docx_khong_cau_cong_giu_the_ma(tmp_path, de):
    docx = pytest.importorskip("docx")
    tm.sinh_moi_clb(de, str(tmp_path))
    clb = bm.clb_co_thi(de)[0]
    d = docx.Document(str(tmp_path / ("NHAP_FORMS_MOI_CLB_%s.docx" % clb["club_id"])))
    chu = "\n".join(p.text for p in d.paragraphs)
    assert "[thi-" not in chu and "[student_id]" not in chu
    for i in range(1, len(clb["de_thi"]) + 1):
        assert "[%s-%d]" % (clb["club_id"], i) in chu
    khac = next(c for c in bm.clb_co_thi(de) if c is not clb)
    assert "[%s-1]" % khac["club_id"] not in chu               # chỉ đề của CLB này


def test_q4a_cai_dat_ghi_dung_thiet_lap_va_dap_an(de):
    nd = tm.ghi_cai_dat_moi_clb(de)
    for can in ("Record name", "One response per person", "Show results", "TẮT", "Only people in my organization"):
        assert can in nd
    for clb in bm.clb_co_thi(de):
        assert "`%s`" % clb["club_id"] in nd


def test_q4a_sinh_lai_giong_het(tmp_path, de, monkeypatch):
    pytest.importorskip("docx")
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    tm.sinh_moi_clb(de, str(a))
    that = time.localtime
    monkeypatch.setattr(time, "localtime", lambda s=None: that((s if s is not None else time.time()) + 86400 * 400))
    tm.sinh_moi_clb(de, str(b))
    assert sorted(os.listdir(str(a))) == sorted(os.listdir(str(b)))
    for ten in os.listdir(str(a)):
        assert (a / ten).read_bytes() == (b / ten).read_bytes(), ten


def test_q4a_don_tep_cu_cua_clb_khong_con_de(tmp_path, de):
    pytest.importorskip("docx")
    (tmp_path / "NHAP_FORMS_MOI_CLB_clb_da_bo.docx").write_bytes(b"cu")
    (tmp_path / "NHAP_FORMS_CHI_THI.docx").write_bytes(b"giu")      # tệp của chế độ khác: không đụng
    tm.sinh_moi_clb(de, str(tmp_path))
    assert not (tmp_path / "NHAP_FORMS_MOI_CLB_clb_da_bo.docx").exists()
    assert (tmp_path / "NHAP_FORMS_CHI_THI.docx").read_bytes() == b"giu"


def test_q4a_dong_lenh_va_che_do_khac_khong_doi(tmp_path):
    pytest.importorskip("docx")
    assert tm.main(["--moi-clb", "--ra", str(tmp_path)]) == 0
    assert (tmp_path / "CLB.csv").exists()
    assert not (tmp_path / "CAI_DAT_FORMS.md").exists()
    assert not (tmp_path / "CAI_DAT_FORMS_CHI_THI.md").exists()
    with pytest.raises(SystemExit):
        tm.main(["--moi-clb", "--chi-thi", "--ra", str(tmp_path)])


def test_q4a_khong_clb_nao_co_de_khong_ghi_tep(tmp_path, de):
    import copy
    het = copy.deepcopy(de)
    for c in het["cau_lac_bo"]:
        c["de_thi"] = []
    truoc = sorted(os.listdir(str(tmp_path)))           # conftest có thể đã đặt sẵn thư mục giả
    with pytest.raises(bm.LoiDeThi):
        tm.sinh_moi_clb(het, str(tmp_path))
    assert sorted(os.listdir(str(tmp_path))) == truoc


def test_q4a_mot_clb_vuot_200_cau_bao_loi(tmp_path, de):
    import copy
    lon = copy.deepcopy(de)
    c = bm.clb_co_thi(lon)[0]
    c["de_thi"] = c["de_thi"] * 41                                  # 5 x 41 = 205 câu
    with pytest.raises(bm.LoiDeThi, match=c["club_id"]):
        tm.sinh_moi_clb(lon, str(tmp_path))


def test_q4a_chi_thi_va_mac_dinh_van_sinh_giong_tep_trong_kho(de):
    with open(os.path.join(THU_MUC, "CAI_DAT_FORMS.md"), encoding="utf-8") as f:
        assert tm.ghi_cai_dat(de) == f.read()
    nhom = bm.chia_theo_buoi(de, chi_thi=True)
    assert len(nhom) == 1 and bm.dem_cau(de, chi_thi=True) == 60


# ------------------------------------------------------------------ Q4b

def test_q4b_n_tep_mot_clb_cho_cung_so_nhap_nhu_mot_bieu_mau_chung(tmp_path, de):
    rieng = _ban_chung_va_rieng(tmp_path, de)
    ra1, ra2 = tmp_path / "ra_chung", tmp_path / "ra_rieng"
    k1 = cv.chuyen_chi_thi([str(tmp_path / "chung.xlsx")], str(tmp_path / "lists.csv"), str(ra1), de)
    k2 = cv.chuyen_chi_thi(rieng, str(tmp_path / "lists.csv"), str(ra2), de)
    a, b = _doc_so(ra1), _doc_so(ra2)
    assert a["clubs"] == b["clubs"] and a["students"] == b["students"]
    assert k1["n_bai_thi"] == k2["n_bai_thi"] == 6
    assert _diem(b)["hs0001" + MIEN] == {"clb_covua": "8", "clb_vanhoc": "10", "clb_tienganh": "6"}
    # các CLB còn lại có đề nhưng chưa có tệp: được báo, KHÔNG có cảnh báo nào khác
    chua = {c["club_id"] for c in bm.clb_co_thi(de)} - {"clb_covua", "clb_vanhoc", "clb_tienganh", "clb_robotics"}
    assert len(k2["canh_bao"]) == len(chua)
    assert all(any(m in nd for _d, _s, nd in k2["canh_bao"]) for m in chua)


def test_q4b_em_vang_trong_tep_mot_clb_chi_khong_co_diem_clb_do(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:2], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 5)])
    _ghi_xuat_clb(de, str(tmp_path / "b.xlsx"), "clb_vanhoc", [("hs0002" + MIEN, 3)])
    kq = cv.chuyen_chi_thi([str(tmp_path / "a.xlsx"), str(tmp_path / "b.xlsx")],
                           str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert _diem(_doc_so(tmp_path / "nap")) == {"hs0001" + MIEN: {"clb_covua": "10"},
                                                "hs0002" + MIEN: {"clb_vanhoc": "6"}}
    assert not any("hs0001" in s and "clb_vanhoc" in nd for _d, s, nd in kq["canh_bao"])


def test_q4b_phieu_trong_khong_tinh_la_da_thi(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 3)])
    wb = openpyxl.load_workbook(str(tmp_path / "a.xlsx"))
    ws = wb.active
    ws.append([9, None, None, "hs0001" + MIEN.upper(), "x"] + [None] * 5)   # phiếu thứ hai, trống
    wb.save(str(tmp_path / "a.xlsx"))
    kq = cv.chuyen_chi_thi([str(tmp_path / "a.xlsx")], str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert _diem(_doc_so(tmp_path / "nap")) == {"hs0001" + MIEN: {"clb_covua": "6"}}
    assert sum("nộp lần nữa" in nd for _d, _s, nd in kq["canh_bao"]) == 1


def test_q4b_phieu_bo_trong_vai_cau_van_tinh_la_da_thi(tmp_path, de):
    """Soát vòng 3 (gây hỏng `any` -> `all` trong _da_thi không đỏ test nào): em làm dở vẫn có điểm."""
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 5)])
    wb = openpyxl.load_workbook(str(tmp_path / "a.xlsx"))
    ws = wb.active
    for c in range(8, ws.max_column + 1):            # cột 6, 7 = câu 1, 2 (đúng); bỏ trống câu 3 trở đi
        ws.cell(2, c).value = None
    wb.save(str(tmp_path / "a.xlsx"))
    kq = cv.chuyen_chi_thi([str(tmp_path / "a.xlsx")], str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert _diem(_doc_so(tmp_path / "nap")) == {"hs0001" + MIEN: {"clb_covua": "4"}}
    assert kq["n_bai_thi"] == 1


def test_q4b_tep_tron_nhieu_clb_dung_lai_khong_ghi_gi(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 3)])
    wb = openpyxl.load_workbook(str(tmp_path / "a.xlsx"))
    ws = wb.active
    them = next(c for c in bm.clb_co_thi(de) if c["club_id"] == "clb_vanhoc")
    ws.cell(1, ws.max_column + 1).value = bm.cau_de_thi(them, 1)
    wb.save(str(tmp_path / "a.xlsx"))
    with pytest.raises(cv.LoiTepXuat, match="clb_covua.*clb_vanhoc|clb_vanhoc.*clb_covua"):
        cv.chuyen_chi_thi([str(tmp_path / "a.xlsx")], str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert not (tmp_path / "nap").exists() or not os.listdir(str(tmp_path / "nap"))


def test_q4b_the_la_dung_lai_khong_ghi_gi(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 3)],
                  them_cot=["[clb_khongco-1] Câu của CLB lạ"])
    with pytest.raises(cv.LoiTepXuat, match="clb_khongco-1"):
        cv.chuyen_chi_thi([str(tmp_path / "a.xlsx")], str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert not (tmp_path / "nap").exists() or not os.listdir(str(tmp_path / "nap"))


def test_q4b_thieu_cau_cua_clb_dung_lai(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 3)])
    wb = openpyxl.load_workbook(str(tmp_path / "a.xlsx"))
    wb.active.delete_cols(wb.active.max_column)
    wb.save(str(tmp_path / "a.xlsx"))
    with pytest.raises(cv.LoiTepXuat, match="thiếu"):
        cv.chuyen_chi_thi([str(tmp_path / "a.xlsx")], str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)


def test_q4b_chi_co_hai_tep_cung_clb_giu_bai_dau(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_clb(de, str(tmp_path / "a.xlsx"), "clb_covua", [("hs0001" + MIEN, 5)])
    _ghi_xuat_clb(de, str(tmp_path / "b.xlsx"), "clb_covua", [("hs0001" + MIEN, 1)])
    kq = cv.chuyen_chi_thi([str(tmp_path / "a.xlsx"), str(tmp_path / "b.xlsx")],
                           str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert _diem(_doc_so(tmp_path / "nap")) == {"hs0001" + MIEN: {"clb_covua": "10"}}
    assert any("đã có bài từ tệp khác" in nd for _d, _s, nd in kq["canh_bao"])


def test_q4b_tep_chung_co_cau_cong_van_chay_nhu_cu(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_chung(de, str(tmp_path / "chung.xlsx"), [("hs0001" + MIEN, {"clb_covua": 3})])
    kq = cv.chuyen_chi_thi([str(tmp_path / "chung.xlsx")], str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert kq["n_bai_thi"] == 1 and "doi_chieu_bai_thi" not in kq
    assert _diem(_doc_so(tmp_path / "nap")) == {"hs0001" + MIEN: {"clb_covua": "6"}}


# ------------------------------------------------------------------ Q4c

def _ghi_bai_thi(duong, dong, tieu=("Email", "ClubId", "ResponseId", "NopLuc")):
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(tieu)
        for d in dong:
            w.writerow(d)


def _bai_thi_dung(ra_rieng_dong):
    return [(e, c, str(i), "2026-09-07T08:00:00Z") for i, (e, c) in enumerate(ra_rieng_dong, 1)]


CAP = [("hs0001" + MIEN, "clb_covua"), ("hs0003" + MIEN, "clb_covua"),
       ("hs0001" + MIEN, "clb_vanhoc"), ("hs0002" + MIEN, "clb_vanhoc"),
       ("hs0001" + MIEN, "clb_tienganh"), ("hs0002" + MIEN, "clb_robotics")]


def test_q4c_khop_het_thi_phan_doi_chieu_rong(tmp_path, de):
    rieng = _ban_chung_va_rieng(tmp_path, de)
    # khác hoa thường, khoảng trắng, dòng trùng: vẫn khớp
    dong = _bai_thi_dung(CAP) + [("  HS0001" + MIEN.upper(), "clb_covua", "99", "")]
    _ghi_bai_thi(str(tmp_path / "bt.csv"), dong)
    kq = cv.chuyen_chi_thi(rieng, str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de,
                           bai_thi=str(tmp_path / "bt.csv"))
    assert kq["doi_chieu_bai_thi"] == []


def test_q4c_thieu_o_tep_xuat_va_thua_o_tep_xuat(tmp_path, de):
    rieng = _ban_chung_va_rieng(tmp_path, de)
    dong = _bai_thi_dung([x for x in CAP if x != ("hs0002" + MIEN, "clb_robotics")]
                         + [("hs0003" + MIEN, "clb_vanhoc")])
    _ghi_bai_thi(str(tmp_path / "bt.csv"), dong)
    kq = cv.chuyen_chi_thi(rieng, str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de,
                           bai_thi=str(tmp_path / "bt.csv"))
    r = kq["doi_chieu_bai_thi"]
    assert sorted((x[0], x[1], x[2]) for x in r) == [
        ("chi_co_o_bai_thi", "hs0003" + MIEN, "clb_vanhoc"),
        ("chi_co_o_tep_xuat", "hs0002" + MIEN, "clb_robotics")]


def test_q4c_khong_doi_diem_va_so_nhap(tmp_path, de):
    rieng = _ban_chung_va_rieng(tmp_path, de)
    ra1, ra2 = tmp_path / "ra1", tmp_path / "ra2"
    cv.chuyen_chi_thi(rieng, str(tmp_path / "lists.csv"), str(ra1), de)
    _ghi_bai_thi(str(tmp_path / "bt.csv"), _bai_thi_dung(CAP[:2]) + [("la@x.test", "clb_toan", "1", "")])
    cv.chuyen_chi_thi(rieng, str(tmp_path / "lists.csv"), str(ra2), de, bai_thi=str(tmp_path / "bt.csv"))
    a, b = _doc_so(ra1), _doc_so(ra2)
    assert a["clubs"] == b["clubs"] and a["students"] == b["students"]
    ws1 = openpyxl.load_workbook(str(ra1 / "BANG_DIEM.xlsx"))
    ws2 = openpyxl.load_workbook(str(ra2 / "BANG_DIEM.xlsx"))
    assert ws1.sheetnames == ["Bảng điểm", "Chi tiết", "Thống kê đề", "Cảnh báo"]       # không --bai-thi: như cũ
    assert ws2.sheetnames == ws1.sheetnames + ["Đối chiếu BaiThi"]
    assert list(ws1["Bảng điểm"].values) == list(ws2["Bảng điểm"].values)


def test_q4c_thieu_cot_bao_loi_khong_ghi_tep(tmp_path, de):
    rieng = _ban_chung_va_rieng(tmp_path, de)
    _ghi_bai_thi(str(tmp_path / "bt.csv"), [], tieu=("Email", "Club"))
    with pytest.raises(cv.LoiTepXuat, match="ClubId"):
        cv.chuyen_chi_thi(rieng, str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de,
                          bai_thi=str(tmp_path / "bt.csv"))
    assert not (tmp_path / "nap").exists() or not os.listdir(str(tmp_path / "nap"))


def test_q4c_gate_khong_thi_khong_tinh_la_bai_o_tep_xuat(tmp_path, de):
    # chế độ biểu mẫu chung: em chọn "Không" ở câu cổng thì không có bài của CLB đó
    _ghi_lists(str(tmp_path / "lists.csv"), HS[:1], de)
    _ghi_xuat_chung(de, str(tmp_path / "chung.xlsx"), [("hs0001" + MIEN, {"clb_covua": 3})])
    _ghi_bai_thi(str(tmp_path / "bt.csv"), _bai_thi_dung([("hs0001" + MIEN, "clb_covua")]))
    kq = cv.chuyen_chi_thi([str(tmp_path / "chung.xlsx")], str(tmp_path / "lists.csv"),
                           str(tmp_path / "nap"), de, bai_thi=str(tmp_path / "bt.csv"))
    assert kq["doi_chieu_bai_thi"] == []


def test_q4c_dong_lenh(tmp_path, de, capsys):
    rieng = _ban_chung_va_rieng(tmp_path, de)
    _ghi_bai_thi(str(tmp_path / "bt.csv"), _bai_thi_dung(CAP[:3]))
    ra = str(tmp_path / "nap")
    assert cv.main(rieng + ["--chi-thi", "--lists", str(tmp_path / "lists.csv"), "--ra", ra,
                            "--bai-thi", str(tmp_path / "bt.csv")]) == 0
    nd = capsys.readouterr().out
    assert "Đối chiếu BaiThi" in nd and "chi_co_o_tep_xuat" in nd
    with pytest.raises(SystemExit):
        cv.main(rieng[:1] + ["--ra", ra, "--bai-thi", str(tmp_path / "bt.csv")])      # thiếu --chi-thi
