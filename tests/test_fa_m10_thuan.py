"""FA-M10-THUAN (TH = chưa thử trên Microsoft thật): ba tập lệnh sau-xếp có HÀM gọi được, trả đường dẫn/dữ liệu, và `main`
vẫn ra y như cũ: ghep_ket_qua_email.ghep, doi_chieu_lists.doi_chieu + ghi_bao_cao, danh_sach_chua_dang_ky.chua_dang_ky.
Dữ liệu MÔ PHỎNG."""
import csv
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import danh_sach_chua_dang_ky as ds  # noqa: E402
import doi_chieu_lists as dc  # noqa: E402
import ghep_ket_qua_email as gk  # noqa: E402


def _csv(p, dau, dong):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(dau)
        w.writerows(dong)
    return str(p)


def _bang(p):
    wb = openpyxl.load_workbook(p, data_only=True)
    return {ws.title: [[c.value for c in r] for r in ws.iter_rows()] for ws in wb}


def _doc_thu_muc(d):
    return {f: open(os.path.join(d, f), "rb").read() for f in sorted(os.listdir(d))}


# ---------------------------------------------------------------- ghep_ket_qua_email.ghep
def _ghep_dau_vao(tmp_path):
    ly_do = _csv(tmp_path / "ly_do.csv", gk.TU_LY_DO,
                 [["HS1", "thu_2", "clb_covua", "A", "R1", "câu", "7", ""], ["HS9", "thu_2", "clb_vanhoc", "B", "R2", "câu", "8", "3"]])
    em = _csv(tmp_path / "email.csv", ["Email", "student_id"], [["A@X.vn", "HS1"]])
    return ly_do, em


def test_ghep_ghi_tep_va_tra_canh_bao_giong_cli(tmp_path, capsys):
    ly_do, em = _ghep_dau_vao(tmp_path)
    ra_ham, ra_cli = str(tmp_path / "ham.csv"), str(tmp_path / "cli.csv")
    cb = gk.ghep(ly_do, em, ra_ham)
    assert cb == ["học sinh HS9 không có trong tệp email — dòng vẫn ghi, cột Email rỗng"]
    assert gk.main([ly_do, em, "--ra", ra_cli]) == 0
    cap = capsys.readouterr()
    assert open(ra_ham, "rb").read() == open(ra_cli, "rb").read()
    assert "CẢNH BÁO: " + cb[0] in cap.err and "Đã ghi %s." % ra_cli in cap.out
    dong = list(csv.DictReader(open(ra_ham, encoding="utf-8-sig")))
    assert dong[0]["Email"] == "a@x.vn" and dong[1]["Email"] == ""


# ---------------------------------------------------------------- doi_chieu_lists.doi_chieu + ghi_bao_cao
def _list_cu_moi(tmp_path):
    dau = ["Email", "HoTen", "Thu", "NV1", "NV2", "Lop", "CoSo"]
    cu = _csv(tmp_path / "cu.csv", dau, [["a@x.vn", "A", "thu_2", "clb_covua", "clb_vanhoc", "10A1", "CS1"],
                                         ["b@x.vn", "B", "thu_2", "clb_covua", "", "10A2", "CS1"]])
    moi = _csv(tmp_path / "moi.csv", dau, [["a@x.vn", "A", "thu_2", "clb_vanhoc", "clb_covua", "10A1", "CS1"],
                                           ["c@x.vn", "C", "thu_2", "clb_covua", "", "10A3", "CS1"]])
    return cu, moi


def test_doi_chieu_ham_tra_du_lieu_va_bao_cao_giong_cli(tmp_path, capsys):
    cu, moi = _list_cu_moi(tmp_path)
    kq = dc.doi_chieu(cu, moi)
    assert [(m["loai"], m["email"]) for m in kq["muc"]] == [("moi", "c@x.vn"), ("rut", "b@x.vn"), ("doi_nv", "a@x.vn")]
    ra_ham, ra_cli = str(tmp_path / "ham.xlsx"), str(tmp_path / "cli.xlsx")
    dc.ghi_bao_cao(kq, ra_ham)
    assert dc.main([cu, moi, "--ra", ra_cli]) == 0
    assert _bang(ra_ham) == _bang(ra_cli)
    out = capsys.readouterr().out
    assert "1 em mới, 1 em rút, 1 dòng đổi nguyện vọng" in out


def test_doi_chieu_thieu_cot_bat_buoc_la_loi_khong_ghi_gi(tmp_path, capsys):
    cu, _ = _list_cu_moi(tmp_path)
    xau = _csv(tmp_path / "xau.csv", ["Email", "Thu"], [["a@x.vn", "thu_2"]])
    with pytest.raises(dc.cv.LoiTepXuat):
        dc.doi_chieu(cu, xau)
    ra = tmp_path / "x.xlsx"
    assert dc.main([cu, xau, "--ra", str(ra)]) == 1 and not ra.exists()
    assert "KHÔNG GHI TỆP NÀO" in capsys.readouterr().err


# ---------------------------------------------------------------- danh_sach_chua_dang_ky.chua_dang_ky
def _lop_dau_vao(tmp_path, ten_dk="dk.xlsx"):
    roster = _csv(tmp_path / "ds.csv", ["student_id", "class_id", "homeroom_email"],
                  [["HS1", "10A1", "g@x.vn"], ["HS2", "10A1", ""], ["HS3", "10A2", ""], ["HS4", "10A3", ""],
                   ["HS5", "10/A3", ""]])                                   # 10/A3: tên lớp có ký tự cấm trong tên tệp
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Email", "[student_id] Mã học sinh"])
    for sid in ("HS1", "HS3", "HS4", "HS4", "LA"):
        ws.append(["e@x.vn", sid])
    dk = str(tmp_path / ten_dk)
    wb.save(dk)
    return roster, dk


def test_chua_dang_ky_ham_giong_cli_tung_tep_va_dong_in(tmp_path, capsys):
    roster, dk = _lop_dau_vao(tmp_path)
    ham, cli = tmp_path / "ham", tmp_path / "cli"
    kq = ds.chua_dang_ky(roster, dk, str(ham))
    assert ds.main([roster, dk, "--ra", str(cli)]) == 0
    assert _doc_thu_muc(str(ham)) == _doc_thu_muc(str(cli))                  # cùng tên tệp, cùng từng byte
    assert sorted(os.listdir(ham)) == ["chua_dang_ky_10A1.csv", "chua_dang_ky_10_A3.csv", "tong_hop.csv"]   # lớp đủ: không có tệp
    assert sorted(os.path.basename(p) for p in kq["tep"]) == sorted(os.listdir(ham))
    assert (ham / "chua_dang_ky_10A1.csv").read_text(encoding="utf-8-sig").split() == ["student_id,class_id", "HS2,10A1"]
    assert all(os.path.isabs(p) == os.path.isabs(str(ham)) and os.path.exists(p) for p in kq["tep"])
    assert [r["class_id"] for r in kq["lop"]] == ["10/A3", "10A1", "10A2", "10A3"]
    assert kq["n_email"] == 2 and kq["n_duoi"] == 1 and kq["vuot_gioi_han"] is False
    assert "4 lớp, 1 lớp dưới 50 %%; gửi GVCN cần 2 email -> %s" % cli in capsys.readouterr().out


def test_chua_dang_ky_vuot_gioi_han_power_automate(tmp_path, capsys, monkeypatch):
    roster, dk = _lop_dau_vao(tmp_path)
    monkeypatch.setattr(ds, "GIOI_HAN_YEU_CAU_NGAY", 1)
    assert ds.chua_dang_ky(roster, dk, str(tmp_path / "ra"))["vuot_gioi_han"] is True
    assert ds.main([roster, dk, "--ra", str(tmp_path / "ra2")]) == 0
    assert "CẢNH BÁO: VƯỢT 1 yêu cầu/người/ngày" in capsys.readouterr().out


def test_chua_dang_ky_loi_danh_sach_va_tep_dang_ky(tmp_path, capsys):
    roster, dk = _lop_dau_vao(tmp_path)
    thieu = _csv(tmp_path / "thieu.csv", ["student_id"], [["HS1"]])
    ra = tmp_path / "ra"
    with pytest.raises(ds.LoiDanhSach):
        ds.chua_dang_ky(thieu, dk, str(ra))
    assert ds.main([thieu, dk, "--ra", str(ra)]) == 1
    assert capsys.readouterr().err.strip() == "danh sách phải có cột student_id, class_id"
    khong_cot = _csv(tmp_path / "khong_cot.csv", ["Email"], [["a@x.vn"]])
    with pytest.raises(ValueError):
        ds.chua_dang_ky(roster, khong_cot, str(ra))
    assert ds.main([roster, khong_cot, "--ra", str(ra)]) == 1
    assert capsys.readouterr().err.startswith("tệp đăng ký: ")
    with pytest.raises(ValueError):                                                  # tệp đăng ký không có
        ds.chua_dang_ky(roster, str(tmp_path / "khong_co.xlsx"), str(ra))
    assert not ra.exists()                                                           # lỗi thì chưa ghi gì


def test_chua_dang_ky_danh_sach_khong_co_thi_van_la_loi_nhu_cu(tmp_path):
    with pytest.raises(FileNotFoundError):                                           # như CLI cũ: không bọc lỗi này
        ds.chua_dang_ky(str(tmp_path / "khong_co.csv"), str(tmp_path / "dk.xlsx"), str(tmp_path / "ra"))
