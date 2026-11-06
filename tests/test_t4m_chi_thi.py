"""T4M-Q1..Q3: chế độ "chỉ thi" của mau_forms_thi_clb/ (Forms chỉ có bài thi, nguyện vọng ở app ECA).

  Q1  bộ chuyển đổi: khoá là cột Email (chữ thường), ghép với tệp xuất Lists (mô hình rộng).
  Q2  tao_mau_forms.py: bỏ Ranking và ô gõ mã HS, đếm câu (<= 200), tách theo buổi, sinh lại giống hệt.
  Q3  ghi chú một trang cho giáo viên.

Dữ liệu hoàn toàn MÔ PHỎNG. Chế độ mặc định (có Ranking + mã HS) không được đổi: test cũ ở
tests/test_mau_forms_thi_clb.py giữ nguyên.
"""

import copy
import csv
import os
import sys
import time

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC = os.path.join(GOC, "mau_forms_thi_clb")
sys.path.insert(0, THU_MUC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import sinh_xuat_lists_gia as lists_gia  # noqa: E402
import so_nhap  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

MIEN = "@truong-gia.example.test"


@pytest.fixture
def de():
    return bm.doc_de_thi()


# ------------------------------------------------------------------ dựng tệp giả

def _ghi_lists(duong, hs, de):
    """hs: [(email, họ tên, {buổi: [club_id]})] -> CSV Lists rộng (UTF-8 BOM, CRLF)."""
    ten_thu = {b["ma"]: "Thứ " + b["ma"][-1] for b in de["buoi"]}
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(lists_gia.COT)
        for email, ten, nv in hs:
            for b in de["buoi"]:
                ds = (nv.get(b["ma"], []) + ["", "", ""])[:3]
                w.writerow([email, ten, "CS1", 9, "9A1", ten_thu[b["ma"]], *ds,
                            "", "", "Đã khóa", "2026-11-02T07:00:00Z"])


def _cot_thi(de, buoi=None):
    """Tiêu đề các cột bài thi của chế độ chỉ thi, đúng thứ tự biểu mẫu."""
    tieu = []
    for clb in bm.clb_co_thi(de):
        if buoi is not None and clb["buoi"] not in buoi:
            continue
        tieu.append(bm.cau_cong_thi(de, clb, chi_thi=True))
        tieu += [bm.cau_de_thi(clb, i) for i in range(1, len(clb["de_thi"]) + 1)]
    return tieu


def _ghi_xuat_thi(de, duong, phieu, buoi=None, them=()):
    """phieu: [(email, {club_id: số câu đúng})] -> tệp Forms xuất, KHÔNG có Ranking và mã HS."""
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + _cot_thi(de, buoi) + list(them)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for n, (email, thi) in enumerate(phieu, 1):
        o = {}
        for clb in bm.clb_co_thi(de):
            if buoi is not None and clb["buoi"] not in buoi:
                continue
            g = bm.cau_cong_thi(de, clb, chi_thi=True)
            if clb["club_id"] not in thi:
                o[g] = bm.KHONG
                continue
            o[g] = bm.CO
            for i, cau in enumerate(clb["de_thi"], 1):
                k = cau["dap_an"] if i <= thi[clb["club_id"]] else (cau["dap_an"] + 1) % len(cau["lua_chon"])
                o[bm.cau_de_thi(clb, i)] = cau["lua_chon"][k]
        ws.append([n, None, None, email, "Tên Forms " + str(n)] + [o.get(c) for c in tieu[5:]])
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


def _chay(de, tmp_path, hs, phieu, buoi=None):
    _ghi_lists(str(tmp_path / "lists.csv"), hs, de)
    _ghi_xuat_thi(de, str(tmp_path / "forms.xlsx"), phieu, buoi)
    ra = tmp_path / "nap"
    kq = cv.chuyen_chi_thi([str(tmp_path / "forms.xlsx")], str(tmp_path / "lists.csv"), str(ra), de)
    return kq, ra


# ------------------------------------------------------------------ Q1

def test_q1_email_hoa_thuong_ghep_dung(tmp_path, de):
    hs = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"]}),
          ("hs0002" + MIEN, "Bình", {"thu_2": ["clb_covua"]})]
    kq, ra = _chay(de, tmp_path, hs, [("  HS0001" + MIEN.upper() + " ", {"clb_covua": 4})])
    assert kq["canh_bao"] == [] and kq["n_hoc_sinh"] == 2 and kq["n_bai_thi"] == 1
    du = _doc_so(ra)
    # khoá của học sinh là email CHỮ THƯỜNG (student_id phân biệt hoa thường)
    assert _diem(du) == {"hs0001" + MIEN: {"clb_covua": "8"}, "hs0002" + MIEN: {}}
    assert {s["name"] for s in du["students"]} == {"An", "Bình"}
    assert (ra / "BANG_DIEM.xlsx").exists()


def test_q1_phieu_trung_giu_phieu_dau(tmp_path, de):
    hs = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"]})]
    kq, ra = _chay(de, tmp_path, hs, [("hs0001" + MIEN, {"clb_covua": 2}),
                                      ("HS0001" + MIEN, {"clb_covua": 5})])
    assert _diem(_doc_so(ra)) == {"hs0001" + MIEN: {"clb_covua": "4"}}
    assert sum("nộp lần nữa" in nd for _d, _s, nd in kq["canh_bao"]) == 1


def test_q1_email_la_bi_bao_va_bo(tmp_path, de):
    hs = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"]})]
    kq, ra = _chay(de, tmp_path, hs, [("la@khac.example.test", {"clb_covua": 5})])
    assert any("la@khac.example.test" in s and "không có trong" in nd for _d, s, nd in kq["canh_bao"])
    assert _diem(_doc_so(ra)) == {"hs0001" + MIEN: {}}


def test_q1_thi_ma_khong_xep_nguyen_vong_bo_diem_va_bao(tmp_path, de):
    # em xếp Cờ vua nhưng thi Văn học (cùng thu_2? kiểm bằng dữ liệu) -> điểm Văn học bị bỏ
    khac = next(c for c in bm.clb_co_thi(de) if c["club_id"] != "clb_covua" and c["buoi"] == "thu_2")
    hs = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"]})]
    kq, ra = _chay(de, tmp_path, hs, [("hs0001" + MIEN, {"clb_covua": 3, khac["club_id"]: 5})])
    assert _diem(_doc_so(ra)) == {"hs0001" + MIEN: {"clb_covua": "6"}}
    assert any(khac["club_id"] in nd and "KHÔNG xếp" in nd for _d, _s, nd in kq["canh_bao"])
    # bài vẫn có trong bảng điểm
    wb = openpyxl.load_workbook(str(ra / "BANG_DIEM.xlsx"))
    ct = [r for r in wb["Chi tiết"].iter_rows(min_row=2, values_only=True)]
    assert {r[2] for r in ct} == {"clb_covua", khac["club_id"]}


def test_q1_khong_co_bai_thi_so_nhap_trung_khit_ban_khong_diem(tmp_path, de):
    hs = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"], "thu_3": []}),
          ("hs0002" + MIEN, "Bình", {"thu_2": [], "thu_4": []})]
    kq, ra = _chay(de, tmp_path, hs, [])
    assert kq["n_bai_thi"] == 0
    mong_doi = tmp_path / "mong_doi"
    mong_doi.mkdir()
    cv.ghi_tep_phan_mem(de, [
        {"student_id": "hs0001" + MIEN, "name": "An", "lop": "9A1",     # _ghi_lists đặt lớp 9A1 cho mọi em
         "nguyen_vong": {"thu_2": ["clb_covua"]}, "bai_thi": []},
        {"student_id": "hs0002" + MIEN, "name": "Bình", "lop": "9A1", "nguyen_vong": {}, "bai_thi": []},
    ], str(mong_doi))
    a, b = _doc_so(ra), _doc_so(mong_doi)
    assert a["clubs"] == b["clubs"] and a["students"] == b["students"]


def test_q1_thieu_cau_cua_mau_khong_ghi_tep_nao(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), [("hs0001" + MIEN, "An", {})], de)
    _ghi_xuat_thi(de, str(tmp_path / "forms.xlsx"), [("hs0001" + MIEN, {})])
    wb = openpyxl.load_workbook(str(tmp_path / "forms.xlsx"))
    ws = wb.active
    ws.delete_cols(len(_cot_thi(de)) + 3)          # bỏ cột cuối cùng
    wb.save(str(tmp_path / "forms.xlsx"))
    ra = tmp_path / "nap"
    with pytest.raises(cv.LoiTepXuat):
        cv.chuyen_chi_thi([str(tmp_path / "forms.xlsx")], str(tmp_path / "lists.csv"), str(ra), de)
    assert not ra.exists() or not os.listdir(str(ra))


def test_q1_thieu_cot_email_bao_bat_record_name(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), [("hs0001" + MIEN, "An", {})], de)
    _ghi_xuat_thi(de, str(tmp_path / "forms.xlsx"), [])
    wb = openpyxl.load_workbook(str(tmp_path / "forms.xlsx"))
    wb.active.cell(1, 4).value = "Khác"
    wb.save(str(tmp_path / "forms.xlsx"))
    with pytest.raises(cv.LoiTepXuat, match="Email"):
        cv.chuyen_chi_thi([str(tmp_path / "forms.xlsx")], str(tmp_path / "lists.csv"),
                          str(tmp_path / "nap"), de)


def test_q1_tach_theo_buoi_hai_tep_xuat_gop_lai(tmp_path, de):
    hs = [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"], "thu_3": []})]
    thu3 = next(c for c in bm.clb_co_thi(de) if c["buoi"] == "thu_3")
    hs[0][2]["thu_3"] = [thu3["club_id"]]
    _ghi_lists(str(tmp_path / "lists.csv"), hs, de)
    cac_buoi_1 = {"thu_2"}
    cac_buoi_2 = {b["ma"] for b in de["buoi"]} - cac_buoi_1
    _ghi_xuat_thi(de, str(tmp_path / "f1.xlsx"), [("hs0001" + MIEN, {"clb_covua": 5})], cac_buoi_1)
    _ghi_xuat_thi(de, str(tmp_path / "f2.xlsx"), [("HS0001" + MIEN, {thu3["club_id"]: 1})], cac_buoi_2)
    kq = cv.chuyen_chi_thi([str(tmp_path / "f1.xlsx"), str(tmp_path / "f2.xlsx")],
                           str(tmp_path / "lists.csv"), str(tmp_path / "nap"), de)
    assert kq["canh_bao"] == []                      # hai tệp phủ đủ mọi CLB thi, không trùng
    assert _diem(_doc_so(tmp_path / "nap")) == {
        "hs0001" + MIEN: {"clb_covua": "10", thu3["club_id"]: "2"}}


def test_q1_tep_xuat_chi_phu_mot_phan_bao_clb_khong_co_diem(tmp_path, de):
    _ghi_lists(str(tmp_path / "lists.csv"), [("hs0001" + MIEN, "An", {})], de)
    _ghi_xuat_thi(de, str(tmp_path / "f1.xlsx"), [], {"thu_2"})
    kq = cv.chuyen_chi_thi([str(tmp_path / "f1.xlsx")], str(tmp_path / "lists.csv"),
                           str(tmp_path / "nap"), de)
    ngoai = [c["club_id"] for c in bm.clb_co_thi(de) if c["buoi"] != "thu_2"]
    assert ngoai and all(any(m in nd for _d, _s, nd in kq["canh_bao"]) for m in ngoai)


def test_q1_doc_duoc_tep_lists_do_bo_sinh_gia_tao(tmp_path, de):
    """Tệp giả của GĐ3 (BOM, CRLF, 'Thứ 2', mã CLB riêng): đọc được, email về chữ thường, mã CLB lạ bị báo."""
    csv_gia = str(tmp_path / "lists_gia.csv")
    lists_gia.ghi_csv(csv_gia, so_hs=20, seed=7)
    ds, canh_bao = cv.doc_lists(csv_gia, de)
    assert len(ds) == 20
    assert all(e == e.lower() and e.endswith(MIEN) for e in ds)
    assert any("không phải CLB nào" in nd for _d, _s, nd in canh_bao)
    assert not any("ngày" in nd and "lạ" in nd for _d, _s, nd in canh_bao)     # 'Thứ 2'..'Thứ 6' đều nhận ra


def test_q1_lists_dong_trung_va_email_trong(tmp_path, de):
    duong = str(tmp_path / "lists.csv")
    _ghi_lists(duong, [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"]})], de)
    with open(duong, "a", encoding="utf-8-sig", newline="") as f:     # thêm: dòng trùng (em, buổi) + email trống
        csv.writer(f, lineterminator="\r\n").writerows([
            ["HS0001" + MIEN, "An", "CS1", 9, "9A1", "Thứ 2", "", "", "", "", "", "Đã khóa", ""],
            ["", "Vô danh", "CS1", 9, "9A1", "Thứ 2", "clb_covua", "", "", "", "", "Đã khóa", ""]])
    ds, canh_bao = cv.doc_lists(duong, de)
    assert list(ds) == ["hs0001" + MIEN]
    assert ds["hs0001" + MIEN]["nguyen_vong"] == {"thu_2": ["clb_covua"]}      # giữ dòng ĐẦU
    nd = " | ".join(x[2] for x in canh_bao)
    assert "trùng" in nd and "email" in nd


def test_q1_dong_lenh(tmp_path, de, capsys):
    _ghi_lists(str(tmp_path / "lists.csv"), [("hs0001" + MIEN, "An", {"thu_2": ["clb_covua"]})], de)
    _ghi_xuat_thi(de, str(tmp_path / "forms.xlsx"), [("hs0001" + MIEN, {"clb_covua": 5})])
    assert cv.main([str(tmp_path / "forms.xlsx"), "--chi-thi", "--lists", str(tmp_path / "lists.csv"),
                    "--ra", str(tmp_path / "nap")]) == 0
    assert (tmp_path / "nap" / "SO_NHAP_CLB.xlsx").exists()
    # thiếu --lists, hoặc --lists mà không --chi-thi: lỗi dùng lệnh
    with pytest.raises(SystemExit):
        cv.main([str(tmp_path / "forms.xlsx"), "--chi-thi", "--ra", str(tmp_path / "x")])
    with pytest.raises(SystemExit):
        cv.main([str(tmp_path / "forms.xlsx"), "--lists", str(tmp_path / "lists.csv"),
                 "--ra", str(tmp_path / "x")])


# ------------------------------------------------------------------ Q2

def _de_lon(so_ngay=5, so_clb=5, so_cau=10):
    """de_thi.json giả đủ lớn để vượt 200 câu."""
    de = {"tieu_de": "Thử", "diem_moi_cau": 1,
          "buoi": [{"ma": "b%d" % i, "ten": "Buổi %d" % i} for i in range(1, so_ngay + 1)],
          "cau_lac_bo": []}
    for i in range(1, so_ngay + 1):
        for k in range(1, so_clb + 1):
            de["cau_lac_bo"].append({
                "club_id": "c%d_%d" % (i, k), "name": "CLB %d-%d" % (i, k), "buoi": "b%d" % i,
                "capacity": 10, "reserve_capacity": 0, "reserve_group": "",
                "de_thi": [{"cau": "Câu %d?" % q, "lua_chon": ["a", "b"], "dap_an": 0}
                           for q in range(so_cau)]})
    bm.soat_de_thi(de)
    return de


def test_q2_chi_thi_bo_ranking_va_ma_hs(de):
    phan = bm.cac_phan(de, chi_thi=True)
    cau = [c for _, cs in phan for c in cs]
    assert all(loai != "ranking" for _t, loai, _l, _b in cau)
    ma = {bm.ma_cua_cau(t) for t, *_ in cau}
    assert "student_id" not in ma and "name" not in ma
    assert not ma & {b["ma"] for b in de["buoi"]}
    # còn đúng: mỗi CLB thi một câu cổng + các câu đề
    mong = {"thi-" + c["club_id"] for c in bm.clb_co_thi(de)}
    mong |= {"%s-%d" % (c["club_id"], i) for c in bm.clb_co_thi(de) for i in range(1, len(c["de_thi"]) + 1)}
    assert ma == mong
    assert bm.dem_cau(de, chi_thi=True) == len(mong) == 60


def test_q2_che_do_mac_dinh_khong_doi(de):
    phan = bm.cac_phan(de)
    assert len(phan) == 26 and sum(len(c) for _, c in phan) == 67
    assert phan == bm.cac_phan(de, chi_thi=False)
    assert bm.cau_cong_thi(de, bm.clb_co_thi(de)[0]) == bm.cau_cong_thi(de, bm.clb_co_thi(de)[0], chi_thi=False)


def test_q2_cau_cong_chi_thi_khong_nhac_ranking_trong_form(de):
    g = bm.cau_cong_thi(de, bm.clb_co_thi(de)[0], chi_thi=True)
    assert bm.ma_cua_cau(g) == "thi-clb_covua"
    assert "câu nguyện vọng" not in g


def test_q2_khong_tach_khi_du_200_cau(de):
    assert bm.chia_theo_buoi(de, chi_thi=True) == [[b["ma"] for b in de["buoi"]]]


def test_q2_tach_theo_buoi_khi_vuot_200():
    de = _de_lon()                      # 5 buổi × 5 CLB × (1 cổng + 10 câu) = 55 câu/buổi, 275 tổng
    assert bm.dem_cau(de, chi_thi=True) == 275
    nhom = bm.chia_theo_buoi(de, chi_thi=True)
    assert nhom == [["b1", "b2", "b3"], ["b4", "b5"]]
    assert all(bm.dem_cau(de, chi_thi=True, buoi=g) <= bm.TRAN_CAU_MOI_BIEU_MAU == 200 for g in nhom)
    assert [m for g in nhom for m in g] == [b["ma"] for b in de["buoi"]]


def test_q2_bien_dung_200_cau_van_mot_bieu_mau():
    de = _de_lon(so_ngay=10, so_clb=5, so_cau=3)         # 5 × 4 = 20 câu/buổi × 10 = đúng 200
    assert bm.dem_cau(de, chi_thi=True) == 200
    assert len(bm.chia_theo_buoi(de, chi_thi=True)) == 1
    de = _de_lon(so_ngay=11, so_clb=5, so_cau=3)         # 220: buổi cuối sang biểu mẫu thứ hai
    assert [len(g) for g in bm.chia_theo_buoi(de, chi_thi=True)] == [10, 1]


def test_q2_mot_buoi_vuot_200_bao_loi():
    de = _de_lon(so_ngay=1, so_clb=5, so_cau=40)         # 5 × 41 = 205 câu trong MỘT buổi
    with pytest.raises(bm.LoiDeThi, match="b1"):
        bm.chia_theo_buoi(de, chi_thi=True)


def test_q2_khong_clb_nao_co_de_bao_loi(de):
    d = copy.deepcopy(de)
    for c in d["cau_lac_bo"]:
        c["de_thi"] = []
    with pytest.raises(bm.LoiDeThi):
        bm.chia_theo_buoi(d, chi_thi=True)


def test_q2_sinh_chi_thi_dung_cai_dat_va_docx(tmp_path, de):
    docx = pytest.importorskip("docx")
    files = tm.sinh_chi_thi(de, str(tmp_path))
    ten = sorted(os.path.basename(f) for f in files)
    assert ten == ["CAI_DAT_FORMS_CHI_THI.md", "NHAP_FORMS_CHI_THI.docx"]
    md = (tmp_path / "CAI_DAT_FORMS_CHI_THI.md").read_text(encoding="utf-8")
    assert "Record name" in md and "One response per person" in md
    assert "Only people in my organization" in md
    assert "Show results automatically" in md and "Ranking" not in md.replace("không có câu Ranking", "")
    assert "60 câu" in md
    van_ban = "\n".join(p.text for p in docx.Document(str(tmp_path / "NHAP_FORMS_CHI_THI.docx")).paragraphs)
    assert "Mã học sinh" not in van_ban and "Kéo thả" not in van_ban
    assert "[thi-clb_covua]" in van_ban and "[clb_covua-5]" in van_ban
    assert "[thu_2]" not in van_ban and "[student_id]" not in van_ban


def test_q2_nhieu_bieu_mau_khi_vuot_200(tmp_path):
    pytest.importorskip("docx")
    de = _de_lon()
    files = tm.sinh_chi_thi(de, str(tmp_path))
    ten = sorted(os.path.basename(f) for f in files)
    assert ten == ["CAI_DAT_FORMS_CHI_THI.md", "NHAP_FORMS_CHI_THI_1.docx", "NHAP_FORMS_CHI_THI_2.docx"]
    md = (tmp_path / "CAI_DAT_FORMS_CHI_THI.md").read_text(encoding="utf-8")
    assert "275 câu" in md and "2 biểu mẫu" in md and "165 câu" in md and "110 câu" in md


def test_q2_don_tep_cu_khi_tu_hai_ve_mot_bieu_mau(tmp_path, de):
    pytest.importorskip("docx")
    tm.sinh_chi_thi(_de_lon(), str(tmp_path))
    tm.sinh_chi_thi(de, str(tmp_path))
    assert sorted(f for f in os.listdir(str(tmp_path)) if f.endswith(".docx")) == ["NHAP_FORMS_CHI_THI.docx"]


def test_q2_sinh_lai_giong_het(tmp_path, de, monkeypatch):
    pytest.importorskip("docx")
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    tm.sinh_chi_thi(de, str(a))
    # đồng hồ chạy tới: zip mặc định ghi giờ hiện tại vào từng mục, nên chỉ giống hệt nếu mã cố định giờ
    that = time.localtime
    monkeypatch.setattr(time, "localtime", lambda s=None: that((s if s is not None else time.time()) + 86400 * 400))
    tm.sinh_chi_thi(de, str(b))
    for ten in os.listdir(str(a)):
        assert (a / ten).read_bytes() == (b / ten).read_bytes(), ten


def test_q2_dong_lenh(tmp_path):
    pytest.importorskip("docx")
    assert tm.main(["--chi-thi", "--ra", str(tmp_path)]) == 0
    assert (tmp_path / "CAI_DAT_FORMS_CHI_THI.md").exists()
    assert not (tmp_path / "CAI_DAT_FORMS.md").exists()          # chế độ mặc định không chạy kèm


def test_q2_che_do_mac_dinh_van_sinh_giong_tep_trong_kho(de):
    with open(os.path.join(THU_MUC, "CAI_DAT_FORMS.md"), encoding="utf-8") as f:
        assert tm.ghi_cai_dat(de) == f.read()


# ------------------------------------------------------------------ Q3

GHI_CHU = os.path.join(THU_MUC, "GHI_CHU_GIAO_VIEN.md")


def test_q3_ghi_chu_giao_vien_mot_trang_du_muc():
    with open(GHI_CHU, encoding="utf-8") as f:
        van_ban = f.read()
    assert len(van_ban.splitlines()) <= 60                       # vừa một trang A4 khi in
    for can in ["Quick import", "Correct answer", "Points", "Only people in my organization",
                "Record name", "One response per person", "Show results automatically",
                "Post scores", "200", "10 MB", "Email", "Start date", "de_thi.json"]:
        assert can in van_ban, can
    # Post scores là việc của giáo viên, kiosk không cần
    dong = [d for d in van_ban.splitlines() if "Post scores" in d]
    assert dong and any("không cần" in d.lower() for d in dong)


# ------------------------------------------------------------------ Q1b: Lớp chủ nhiệm từ Lists -> Sổ nhập

def _ghi_lists_lop(duong, de, lop_theo_email, bo_cot_lop=False):
    """CSV Lists rộng; cột `Lop` lấy từ lop_theo_email (mỗi dòng ngày lặp lại cùng lớp). bo_cot_lop: bỏ hẳn cột."""
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        cot = [c for c in lists_gia.COT if not (bo_cot_lop and c == "Lop")]
        w.writerow(cot)
        for email, lop in lop_theo_email.items():
            for b in de["buoi"]:
                dong = {c: "" for c in lists_gia.COT}
                dong.update({"Email": email, "HoTen": email[:6], "Lop": lop,
                             "Thu": "Thứ " + b["ma"][-1],
                             "NV1": "clb_covua" if b["ma"] == "thu_2" else ""})
                w.writerow([dong[c] for c in cot])


def _chuyen_lists(tmp_path, de, lop_theo_email, bo_cot_lop=False):
    _ghi_lists_lop(str(tmp_path / "lists.csv"), de, lop_theo_email, bo_cot_lop)
    _ghi_xuat_thi(de, str(tmp_path / "forms.xlsx"), [])
    ra = tmp_path / "nap"
    kq = cv.chuyen_chi_thi([str(tmp_path / "forms.xlsx")], str(tmp_path / "lists.csv"), str(ra), de)
    return kq, ra


def test_q1b_lop_tu_lists_toi_cot_lop_cua_so_nhap(tmp_path, de):
    """Lớp ở Lists (cả dạng bẩn ' 9a1 ') thành cột Lớp của Sổ nhập; so_nhap đọc và chuẩn hoá qua chuan_hoa_lop."""
    import rbda_priority_pipeline as pl
    lop = {"hs0001" + MIEN: " 9a1 ", "hs0002" + MIEN: "10B2", "hs0003" + MIEN: ""}
    kq, ra = _chuyen_lists(tmp_path, de, lop)
    assert kq["canh_bao"] != [] or kq["n_hoc_sinh"] == 3
    du = _doc_so(ra)
    theo = {s["student_id"]: s["class_id"] for s in du["students"]}
    assert theo == {"hs0001" + MIEN: pl.chuan_hoa_lop(" 9a1 "),
                    "hs0002" + MIEN: pl.chuan_hoa_lop("10B2"),
                    "hs0003" + MIEN: ""}
    assert theo["hs0001" + MIEN] and theo["hs0002" + MIEN]      # không phải hai chuỗi rỗng khớp tình cờ
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True)
    tieu = [o for o in next(wb[so_nhap.SHEET_HS].iter_rows(max_row=1, values_only=True))]
    wb.close()
    assert so_nhap.nhan_lop(None) in tieu


def test_q1b_lists_khong_co_cot_lop_giu_hanh_vi_cu(tmp_path, de):
    """Lists không có cột Lop: Sổ nhập KHÔNG có cột Lớp (giống từng byte hành vi cũ), không lỗi, không cảnh báo mới."""
    lop = {"hs0001" + MIEN: "9A1", "hs0002" + MIEN: "9A2"}
    kq, ra = _chuyen_lists(tmp_path, de, lop, bo_cot_lop=True)
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True)
    tieu = [o for o in next(wb[so_nhap.SHEET_HS].iter_rows(max_row=1, values_only=True))]
    wb.close()
    assert so_nhap.nhan_lop(None) not in tieu
    assert all(not s.get("class_id") for s in _doc_so(ra)["students"])
    assert not any("lớp" in nd.lower() for _d, _s, nd in kq["canh_bao"])


def test_q1b_moi_lists_khong_lop_nao_khong_ghi_cot(tmp_path, de):
    """Có cột Lop nhưng mọi ô trống: coi như không có lớp, không ghi cột Lớp."""
    kq, ra = _chuyen_lists(tmp_path, de, {"hs0001" + MIEN: "", "hs0002" + MIEN: ""})
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True)
    tieu = [o for o in next(wb[so_nhap.SHEET_HS].iter_rows(max_row=1, values_only=True))]
    wb.close()
    assert so_nhap.nhan_lop(None) not in tieu
