"""T4M-DEMO: bộ sinh tệp Forms chỉ-thi giả + lệnh demo một dòng (dữ liệu hoàn toàn MÔ PHỎNG).

Khoá: tệp Forms giả có đúng hình dạng bộ chuyển đổi --chi-thi cần (Email, cột câu hỏi, cột Points),
nhất quán với tệp Lists giả và de_thi.json, có sẵn các cảnh báo cố ý; demo chạy trọn chuỗi trong
thư mục tạm, xác định (cùng seed cùng kết quả) và không đụng app.db thật.
"""

import os
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("mau_forms_thi_clb", "du_lieu_test"):
    sys.path.insert(0, os.path.join(GOC, p))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import demo_t4m  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

TEP_RA = ["SO_NHAP_CLB.xlsx", "BANG_DIEM.xlsx"]


@pytest.fixture
def de():
    return bm.doc_de_thi()


def _lists(tmp_path, de, so_hs=40, seed=3):
    duong = str(tmp_path / "lists.csv")
    demo_t4m.sinh_lists(de, duong, so_hs, seed)
    ds, cb = cv.doc_lists(duong, de)
    assert cb == []
    return duong, ds


# ------------------------------------------------------------ bộ sinh Forms giả

def test_forms_gia_dung_hinh_dang_va_bo_chuyen_doi_nhan(tmp_path, de):
    duong_l, ds = _lists(tmp_path, de)
    x = str(tmp_path / "forms.xlsx")
    ghi = tm.ghi_mau_xuat_chi_thi(de, x, ds, hat_giong=7)
    tieu, dong = cv.doc_tep_xuat(x)
    assert tieu[:5] == ["ID", "Start time", "Completion time", "Email", "Name"]
    # Không Ranking, không ô mã HS; có cột Points cho từng câu đề thi.
    assert not any(bm.ma_cua_cau(h) in ("student_id",) for h in tieu)
    cac_cau = [bm.cau_de_thi(c, i) for c in bm.clb_co_thi(de) for i in range(1, len(c["de_thi"]) + 1)]
    assert all(c in tieu and "Points - " + c in tieu for c in cac_cau)
    assert all(bm.cau_cong_thi(de, c, chi_thi=True) in tieu for c in bm.clb_co_thi(de))
    kq = cv.chuyen_chi_thi([x], duong_l, str(tmp_path / "nap"), de)
    assert kq["n_bai_thi"] > 0
    # Một số em không nộp phiếu (cố ý), cộng phiếu trùng và email lạ.
    assert len(dong) == ghi["n_phieu"] and 2 < ghi["n_phieu"] <= len(ds) + 2


def test_forms_gia_xac_dinh_cung_seed_cung_o(tmp_path, de):
    _, ds = _lists(tmp_path, de)
    a, b, c = (str(tmp_path / n) for n in ("a.xlsx", "b.xlsx", "c.xlsx"))
    tm.ghi_mau_xuat_chi_thi(de, a, ds, hat_giong=7)
    tm.ghi_mau_xuat_chi_thi(de, b, ds, hat_giong=7)
    tm.ghi_mau_xuat_chi_thi(de, c, ds, hat_giong=8)
    assert cv.doc_tep_xuat(a) == cv.doc_tep_xuat(b)
    assert cv.doc_tep_xuat(a) != cv.doc_tep_xuat(c)


def test_forms_gia_co_du_bon_loai_canh_bao_va_email_hoa(tmp_path, de):
    duong_l, ds = _lists(tmp_path, de, so_hs=60)
    x = str(tmp_path / "forms.xlsx")
    ghi = tm.ghi_mau_xuat_chi_thi(de, x, ds, hat_giong=7)
    kq = cv.chuyen_chi_thi([x], duong_l, str(tmp_path / "nap"), de)
    nd = [(s, n) for _d, s, n in kq["canh_bao"]]
    assert sum("nộp lần nữa" in n for _s, n in nd) == 1
    assert [s for s, n in nd if "nộp lần nữa" in n] == [ghi["email_trung"].lower()]
    assert sum("không có trong danh sách đăng ký" in n for _s, n in nd) == 1
    assert ghi["email_la"].lower() in [s for s, n in nd if "không có trong" in n]
    ko_xep = [(s, n) for s, n in nd if "KHÔNG xếp CLB này" in n]
    assert len(ko_xep) == 1 and ko_xep[0][0] == ghi["khong_xep"][0].lower()
    assert ghi["khong_xep"][1] in ko_xep[0][1]
    # Có email viết hoa trong tệp Forms (bộ chuyển đổi hạ chữ thường, không cảnh báo).
    _, dong = cv.doc_tep_xuat(x)
    assert any(r[3] != r[3].lower() for r in dong[:-2])      # hai dòng cuối là phiếu trùng và email lạ


def test_forms_gia_chi_dung_email_va_clb_cua_lists(tmp_path, de):
    _, ds = _lists(tmp_path, de)
    x = str(tmp_path / "forms.xlsx")
    ghi = tm.ghi_mau_xuat_chi_thi(de, x, ds, hat_giong=7)
    _, dong = cv.doc_tep_xuat(x)
    emails = {r[3].strip().lower() for r in dong}
    assert emails - set(ds) == {ghi["email_la"].lower()}


# ------------------------------------------------------------------ demo trọn chuỗi

def test_demo_chay_tron_chuoi_va_du_tep(tmp_path):
    ra = tmp_path / "ra"
    kq = demo_t4m.chay_demo(str(ra), so_hs=40, seed=11)
    for ten in TEP_RA + ["lists_gia.csv", "forms_chi_thi_gia.xlsx"]:
        assert (ra / ten).is_file(), ten
    thu_muc = ra / "ket_qua_theo_lop"
    assert thu_muc.is_dir() and kq["n_tep_lop"] == len(list(thu_muc.glob("*.xlsx"))) > 0
    assert kq["n_hoc_sinh"] == 40
    assert 0 < kq["n_nv1"] <= kq["n_luot"]
    assert 0 < kq["n_tang1"] <= kq["n_clb"]
    # Không để lại CSDL tạm trong thư mục ra.
    assert not list(ra.rglob("*.db"))


def test_demo_xac_dinh_cung_seed_cung_ket_qua(tmp_path):
    a = demo_t4m.chay_demo(str(tmp_path / "a"), so_hs=40, seed=11)
    b = demo_t4m.chay_demo(str(tmp_path / "b"), so_hs=40, seed=11)
    c = demo_t4m.chay_demo(str(tmp_path / "c"), so_hs=40, seed=12)
    assert a["ket_qua"] and a["ket_qua"] == b["ket_qua"]
    assert a["canh_bao"] == b["canh_bao"]
    assert a["ket_qua"] != c["ket_qua"]


def test_demo_hien_canh_bao_mong_doi(tmp_path):
    kq = demo_t4m.chay_demo(str(tmp_path / "ra"), so_hs=60, seed=11)
    van_ban = "\n".join(n for _d, _s, n in kq["canh_bao"])
    assert "nộp lần nữa" in van_ban
    assert "không có trong danh sách đăng ký" in van_ban
    assert "KHÔNG xếp CLB này" in van_ban


def test_demo_khong_dung_app_db_that(tmp_path, monkeypatch):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    demo_t4m.chay_demo(str(tmp_path / "ra"), so_hs=30, seed=11)
    assert not list(cwd.rglob("*.db"))


def test_demo_main_in_tom_tat_tieng_viet(tmp_path, capsys):
    assert demo_t4m.main(["--ra", str(tmp_path / "ra"), "--so-hs", "40", "--seed", "11"]) == 0
    ra = capsys.readouterr().out
    assert "40 học sinh" in ra and "nguyện vọng 1" in ra and "Tầng 1" in ra and "cảnh báo" in ra


def test_demo_he_so_cho_va_so_lieu_nhat_quan(tmp_path):
    de = bm.doc_de_thi()
    assert demo_t4m.he_so_cho_tu_dong(de, 10) == 1.0       # ít em thì giữ chỉ tiêu mẫu
    assert demo_t4m.he_so_cho_tu_dong(de, 120) > 1.0
    mot = demo_t4m.chay_demo(str(tmp_path / "a"), so_hs=40, seed=11, he_so_cho=1)
    nhieu = demo_t4m.chay_demo(str(tmp_path / "b"), so_hs=40, seed=11, he_so_cho=3)
    for kq in (mot, nhieu):
        assert 0 <= kq["n_nv1"] <= kq["n_dat_nv"] <= kq["n_luot"]
    assert nhieu["n_nv1"] >= mot["n_nv1"]                   # thêm chỗ không làm ai mất nguyện vọng 1
    # tệp de_thi.json không bị đổi bởi việc nhân chỉ tiêu
    assert bm.doc_de_thi()["cau_lac_bo"][0]["capacity"] == de["cau_lac_bo"][0]["capacity"]


def test_demo_chay_lai_cung_thu_muc_khong_de_ban_sao(tmp_path):
    ra = tmp_path / "ra"
    a = demo_t4m.chay_demo(str(ra), so_hs=30, seed=11)
    b = demo_t4m.chay_demo(str(ra), so_hs=30, seed=11)
    assert a["ket_qua"] == b["ket_qua"]
    assert sorted(p.name for p in ra.iterdir() if p.is_dir()) == ["ket_qua_theo_lop"]


# ------------------------------------------- cách B: mỗi CLB một biểu mẫu (T4M-DEMO-B)

def test_demo_moi_clb_cung_ket_qua_nhu_bieu_mau_chung(tmp_path):
    chung = demo_t4m.chay_demo(str(tmp_path / "a"), so_hs=40, seed=11)
    rieng = demo_t4m.chay_demo(str(tmp_path / "b"), so_hs=40, seed=11, moi_clb=True)
    assert rieng["ket_qua"] and rieng["ket_qua"] == chung["ket_qua"]
    assert rieng["n_bai_thi"] == chung["n_bai_thi"]
    # Cùng các em bị cảnh báo; em nộp hai lần được báo một lần MỖI biểu mẫu em thi, nên có thể nhiều dòng hơn.
    assert {s for _d, s, _n in rieng["canh_bao"]} == {s for _d, s, _n in chung["canh_bao"]}
    assert len(rieng["canh_bao"]) >= len(chung["canh_bao"])


@pytest.mark.giu_ma
def test_demo_moi_clb_mot_tep_moi_clb_khong_cau_cong(tmp_path, de):
    ra = tmp_path / "ra"
    kq = demo_t4m.chay_demo(str(ra), so_hs=40, seed=11, moi_clb=True)
    thu_muc = ra / "forms_moi_clb"
    tep = sorted(p.name for p in thu_muc.glob("*.xlsx"))
    assert tep == sorted("%s.xlsx" % c["club_id"] for c in bm.clb_co_thi(de))
    assert kq["n_bieu_mau"] == len(tep)
    assert not (ra / "forms_chi_thi_gia.xlsx").exists()
    for p in thu_muc.glob("*.xlsx"):
        tieu, _dong = cv.doc_tep_xuat(str(p))
        ma = {bm.ma_cua_cau(h) for h in tieu} - {None}
        assert not any(m.startswith("thi-") for m in ma), p.name
        assert {m.rsplit("-", 1)[0] for m in ma if not m.startswith("thi-")} == {p.stem}


def test_demo_moi_clb_doi_chieu_bai_thi_dung_mot_cho_gai(tmp_path):
    ra = tmp_path / "ra"
    kq = demo_t4m.chay_demo(str(ra), so_hs=40, seed=11, moi_clb=True)
    assert (ra / "BaiThi.csv").is_file()
    assert [(x[0], x[1], x[2]) for x in kq["doi_chieu"]] == [
        (cv.CHI_CO_O_TEP_XUAT,) + kq["gai"]["bai_thi_thieu"]]
    wb = openpyxl.load_workbook(str(ra / "BANG_DIEM.xlsx"), read_only=True)
    assert "Đối chiếu BaiThi" in wb.sheetnames
    wb.close()


def test_demo_mac_dinh_khong_co_doi_chieu_va_khong_tep_moi_clb(tmp_path):
    ra = tmp_path / "ra"
    kq = demo_t4m.chay_demo(str(ra), so_hs=30, seed=11)
    assert "doi_chieu" not in kq and not (ra / "forms_moi_clb").exists()
    assert not (ra / "BaiThi.csv").exists()


def test_demo_main_moi_clb_in_doi_chieu(tmp_path, capsys):
    assert demo_t4m.main(["--ra", str(tmp_path / "ra"), "--so-hs", "40", "--seed", "11", "--moi-clb"]) == 0
    ra = capsys.readouterr().out
    assert "mỗi CLB một biểu mẫu" in ra and "Đối chiếu BaiThi" in ra and "1 chỗ lệch" in ra
