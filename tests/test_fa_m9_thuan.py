"""FA-M9-THUAN (TH = chưa thử trên Microsoft thật): phần THUẦN của nạp tệp Forms/List — `nhan_dien_tep`, `doan_bien_the`,
`chuyen_fa_daa_du_lieu` trong chuyen_forms_sang_phan_mem.py. Dữ liệu MÔ PHỎNG; không dùng UI/API."""
import copy
import csv
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402


# ---------------------------------------------------------------- dữ liệu dựng
def _de_3_de():
    """clb_covua có đề A, B, C (cùng lựa chọn, chữ câu khác, đáp án xoay); clb_vanhoc chỉ một đề."""
    de = copy.deepcopy(bm.doc_de_thi())
    clb = next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    clb["de_thi_bien_the"] = [
        [dict(c, cau=c["cau"] + " (đề %s)" % chu, dap_an=(c["dap_an"] + k) % len(c["lua_chon"]))
         for c in clb["de_thi"]] for k, chu in ((1, "B"), (2, "C"))]
    return de


def _clb(de, ma):
    return next(c for c in de["cau_lac_bo"] if c["club_id"] == ma)


def _clb_de(de, ma, chu):
    """CLB với đề `chu` làm `de_thi` (cách bộ chuyển đổi dựng)."""
    c = copy.deepcopy(_clb(de, ma))
    c["de_thi"] = ([c["de_thi"]] + list(c.get("de_thi_bien_the") or []))["ABC".index(chu)]
    return c


def _tieu_bai_thi(de, chu="A", cac_clb=("clb_covua",)):
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"]
    for ma in cac_clb:
        c = _clb_de(de, ma, chu if len(cv_cac_de(_clb(de, ma))) > 1 else "A")
        tieu.append(bm.cau_cong_thi(de, c, chi_thi=True))
        tieu += [bm.cau_de_thi(c, i) for i in range(1, len(c["de_thi"]) + 1)]
    return tieu


def cv_cac_de(clb):
    return [clb["de_thi"]] + list(clb.get("de_thi_bien_the") or [])


def _tieu_dang_ky(de, buoi="thu_2"):
    return ["ID", "Start time", "Completion time", "Email", "Name"] + [c[0] for _, cs in bm.cac_phan_fa(de, buoi)
                                                                       for c in cs]


TIEU_LISTS = ["Email", "HoTen", "Thu", "NV1", "NV2", "NV3", "TrangThai", "HC_TuChinh", "WP1", "WP2", "WP3"]


# ---------------------------------------------------------------- nhan_dien_tep
def test_nhan_dien_tep_tung_loai():
    de = _de_3_de()
    assert cv.nhan_dien_tep("dk.xlsx", _tieu_dang_ky(de)) == "dang_ky"
    assert cv.nhan_dien_tep("thi.xlsx", _tieu_bai_thi(de)) == "bai_thi"
    assert cv.nhan_dien_tep("list.csv", TIEU_LISTS) == "lists"
    assert cv.nhan_dien_tep("sau.xlsx", ["ID", "Email", bm.CAU_CO_SAI]) == "sau_ket_qua"
    assert cv.nhan_dien_tep("lung.xlsx", ["ID", "Email", "Name", "Câu hỏi bất kỳ"]) == "khong_ro"


def test_nhan_dien_tep_khong_phan_biet_hoa_thuong_cot_list_va_bo_khoang_trang():
    assert cv.nhan_dien_tep("x.csv", [" email ", "THU", "nv1"]) == "lists"
    assert cv.nhan_dien_tep("x.csv", ["Email", "Thu"]) == "khong_ro"              # thiếu NV1


def test_nhan_dien_tep_sau_ket_qua_thang_moi_thu_khac():
    de = _de_3_de()
    assert cv.nhan_dien_tep("s.xlsx", _tieu_dang_ky(de) + [bm.CAU_CO_SAI]) == "sau_ket_qua"
    assert cv.nhan_dien_tep("s.xlsx", ["[kn_buoi] Buổi nào (mã)"]) == "sau_ket_qua"


def test_nhan_dien_tep_bo_qua_cot_points_va_feedback():
    de = _de_3_de()
    tieu = _tieu_bai_thi(de)
    ca = tieu + ["Points - " + tieu[6]] + ["Feedback - " + tieu[6]] + ["Points - [thu_2-nv1] x"]
    assert cv.nhan_dien_tep("thi.xlsx", ca) == "bai_thi"
    assert cv.nhan_dien_tep("lung.xlsx", ["Points - [thu_2-nv1] x"]) == "khong_ro"


def test_nhan_dien_tep_lan_dang_ky_voi_bai_thi_hoac_csv_la_khong_ro():
    de = _de_3_de()
    assert cv.nhan_dien_tep("trong.xlsx", _tieu_dang_ky(de) + _tieu_bai_thi(de)) == "khong_ro"
    assert cv.nhan_dien_tep("la.csv", _tieu_bai_thi(de)) == "khong_ro"             # CSV không phải List
    assert cv.nhan_dien_tep("trong.xlsx", []) == "khong_ro"
    assert cv.nhan_dien_tep("trong.xlsx", None) == "khong_ro"


def test_nhan_dien_tep_cau_cong_thi_mot_minh_khong_phai_bai_thi():
    assert cv.nhan_dien_tep("x.xlsx", ["[thi-clb_covua] Em có thi không?"]) == "khong_ro"


# ---------------------------------------------------------------- doan_bien_the
@pytest.mark.parametrize("chu", ["A", "B", "C"])
def test_doan_bien_the_tung_de(chu):
    de = _de_3_de()
    assert cv.doan_bien_the(de, _tieu_bai_thi(de, chu)) == chu


def test_doan_bien_the_tep_nhieu_clb_chi_mot_clb_co_nhieu_de():
    de = _de_3_de()
    for chu in "ABC":
        tieu = _tieu_bai_thi(de, chu, cac_clb=("clb_covua", "clb_vanhoc"))
        assert cv.doan_bien_the(de, tieu) == chu


def test_doan_bien_the_lan_hai_de_la_none():
    de = _de_3_de()
    a, b = _tieu_bai_thi(de, "A"), _tieu_bai_thi(de, "B")
    tron = a[:7] + b[7:]                                                      # câu 1 đề A, các câu sau đề B
    assert cv.doan_bien_the(de, tron) is None
    assert cv.doan_bien_the(de, a[:7] + b[7:] + a[7:8]) is None                # trùng mã câu: câu sau ghi đè, vẫn lẫn


def test_doan_bien_the_chi_mot_clb_de_a_va_de_b_cung_chu_la_mo_ho():
    de = copy.deepcopy(_de_3_de())
    clb = _clb(de, "clb_covua")
    clb["de_thi_bien_the"][0] = copy.deepcopy(clb["de_thi"])                  # đề B y hệt chữ đề A
    tieu = _tieu_bai_thi(de, "A")
    assert cv.doan_bien_the(de, tieu) is None


def test_doan_bien_the_khong_khop_de_nao_hoac_khong_co_cau_bai_thi():
    de = _de_3_de()
    tieu = _tieu_bai_thi(de, "A")
    tieu[7] = "[clb_covua-2] một câu lạ hoàn toàn"
    assert cv.doan_bien_the(de, tieu) is None
    assert cv.doan_bien_the(de, _tieu_dang_ky(de)) is None
    assert cv.doan_bien_the(de, []) is None
    assert cv.doan_bien_the(de, ["[clb_la-1] x"]) is None                       # CLB không có trong de_thi.json


def test_doan_bien_the_bo_qua_khoang_trang_thua_va_cot_points():
    de = _de_3_de()
    tieu = _tieu_bai_thi(de, "B")
    tieu = [h.replace(" ", "  ", 3) if h.startswith("[clb_covua-3]") else h for h in tieu]
    tieu += ["Points - " + tieu[8], "Feedback - " + tieu[8]]
    assert cv.doan_bien_the(de, tieu) == "B"


def test_doan_bien_the_mot_cau_vuot_so_cau_cua_de_la_none():
    de = _de_3_de()
    tieu = _tieu_bai_thi(de, "A") + ["[clb_covua-99] không có câu này"]
    assert cv.doan_bien_the(de, tieu) is None


def test_doan_bien_the_chi_co_clb_mot_de_tra_a_neu_khop():
    de = _de_3_de()
    tieu = _tieu_bai_thi(de, "A", cac_clb=("clb_vanhoc",))
    assert cv.doan_bien_the(de, tieu) == "A"
    tieu[6] = "[clb_vanhoc-1] sai chữ"
    assert cv.doan_bien_the(de, tieu) is None


# ---------------------------------------------------------------- CLI: --bien-the-tep vẫn thắng, không tự đoán
def _bo(tmp_path, de, chu_tep, dung=5, nhan="thi.xlsx", so_em=4):
    """List + tệp thi của đề `chu_tep` (mọi em làm đúng `dung` câu theo đề ĐÓ) + Sổ nhập CLB."""
    c = _clb_de(de, "clb_covua", chu_tep)
    tieu = ["ID", "Start time", "Completion time", "Email", "Name", bm.cau_cong_thi(de, c, chi_thi=True)]
    tieu += [bm.cau_de_thi(c, i) for i in range(1, len(c["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    emails = ["e%d@x.vn" % i for i in range(so_em)]
    for e in emails:
        r = {"Email": e, "Name": e, "Start time": "2026-11-09 10:00:00", "Completion time": "2026-11-09 10:10:00",
             tieu[5]: bm.CO}
        for i, cau in enumerate(c["de_thi"], 1):
            r[bm.cau_de_thi(c, i)] = cau["lua_chon"][cau["dap_an"] if i <= dung else (cau["dap_an"] + 1) % len(cau["lua_chon"])]
        ws.append([r.get(h, "") for h in tieu])
    thi = str(tmp_path / nhan)
    wb.save(thi)
    lst = tmp_path / "list.csv"
    with open(lst, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "HoTen", "Thu", "NV1", "TrangThai"])
        for e in emails:
            w.writerow([e, e, "Thứ 2", "clb_covua", "SUBMITTED"])
    clubs = [{"club_id": x["club_id"], "name": x["name"], "capacity": 40, "reserve_capacity": 0, "reserve_group": "",
              "buoi": x["buoi"], "loai": so_nhap.TU_DO if x["club_id"] == "clb_nhiepanh" else so_nhap.GIOI_HAN}
             for x in de["cau_lac_bo"]]
    clubs[0]["loai"], clubs[0]["diem_san"] = so_nhap.TUYEN_CHON, 5
    sn = str(tmp_path / "clb.xlsx")
    so_nhap.ghi_so_nhap(sn, clubs=clubs)
    return str(lst), thi, sn


def _diem_covua(ra):
    du = so_nhap.doc_so_nhap(openpyxl.load_workbook(os.path.join(ra, cv.TEN_SO)))
    return {s["student_id"]: float(next(n for n in s["nv"] if n["club_id"] == "clb_covua")["diem"] or -1)
            for s in du["students"]}


def _de_ra_tep(tmp_path, de):
    p = tmp_path / "de.json"
    import json
    p.write_text(json.dumps(de, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_cli_bien_the_tep_ghi_ro_thang_va_khong_tu_doan(tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "B")
    dj = _de_ra_tep(tmp_path, de)
    ra_b, ra_a = tmp_path / "ra_b", tmp_path / "ra_a"
    base = ["--fa-daa", "--so-nhap-clb", sn, "--lists", lst, "--de", dj]
    assert cv.main(base + ["--bien-the-tep", "thi.xlsx=B", "--ra", str(ra_b), thi]) == 0
    assert set(_diem_covua(str(ra_b)).values()) == {10.0}                      # chấm đúng đề B
    assert cv.main(base + ["--ra", str(ra_a), thi]) == 0                       # không ghi gì = đề A: CLI KHÔNG tự đoán
    assert set(_diem_covua(str(ra_a)).values()) != {10.0}
    assert cv.doan_bien_the(de, cv.doc_tep_xuat(thi)[0]) == "B"


def test_cli_in_ra_nhu_cu_khong_nhac_khoa_moi(tmp_path, capsys):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dj = _de_ra_tep(tmp_path, de)
    assert cv.main(["--fa-daa", "--so-nhap-clb", sn, "--lists", lst, "--de", dj, "--ra", str(tmp_path / "ra"), thi]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Đã chuyển 4 học sinh, chấm 4 bài thi -> ")
    assert "cau_co_co" not in out and "trang_thai" not in out


# ---------------------------------------------------------------- chuyen_fa_daa_du_lieu
def _gia_tri_so_nhap(ra):
    wb = openpyxl.load_workbook(os.path.join(ra, cv.TEN_SO), data_only=True)
    return {ws.title: [[c.value for c in r] for r in ws.iter_rows()] for ws in wb}


def test_du_lieu_giong_het_cli_cung_tep(tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dj = _de_ra_tep(tmp_path, de)
    cli = tmp_path / "cli"
    assert cv.main(["--fa-daa", "--so-nhap-clb", sn, "--lists", lst, "--de", dj, "--ra", str(cli), thi]) == 0
    api = tmp_path / "api"
    kq = cv.chuyen_fa_daa_du_lieu(str(api), de, sn, lists=lst, quiz_xlsx=[thi])
    assert kq["trang_thai"] == "xong" and kq["n_hoc_sinh"] == 4 and kq["n_bai_thi"] == 4
    assert _gia_tri_so_nhap(str(api)) == _gia_tri_so_nhap(str(cli))
    assert (api / cv.TEN_EMAIL_MA_HS).read_bytes() == (cli / cv.TEN_EMAIL_MA_HS).read_bytes()
    assert isinstance(kq["cau_co_co"], list) and kq["ghi_chu"]


def test_du_lieu_loi_tra_loi_va_khong_ghi_gi(tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    ra = tmp_path / "ra"
    kq = cv.chuyen_fa_daa_du_lieu(str(ra), de, None, lists=lst, quiz_xlsx=[thi])              # thiếu Sổ nhập CLB
    assert kq["trang_thai"] == "loi" and "Sổ nhập CLB" in kq["thong_bao"]
    assert not ra.exists()
    kq = cv.chuyen_fa_daa_du_lieu(str(ra), de, sn, lists=lst, quiz_xlsx=[thi], bien_the_tep={"thi.xlsx": "Z"})
    assert kq["trang_thai"] == "loi" and not (ra / cv.TEN_SO).exists()


def _bo_lech(tmp_path, de):
    """10 em đề A đúng 5/5 và 10 em đề B đúng 2/5: lệch ngoài ngưỡng (như tests/test_fa_m4_phan_tich.py)."""
    lst, thi_a, sn = _bo(tmp_path, de, "A", dung=5, nhan="thi_A.xlsx", so_em=10)
    tb = tmp_path / "b"
    tb.mkdir()
    _, thi_b, _ = _bo(tb, de, "B", dung=2, nhan="thi_B.xlsx", so_em=10)
    wb = openpyxl.load_workbook(thi_b)
    ws = wb.active
    for r in ws.iter_rows(min_row=2):
        r[3].value = r[3].value.replace("e", "f")                                          # f0..f9: em khác
        r[4].value = r[3].value
    wb.save(thi_b)
    with open(lst, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        for i in range(10):
            w.writerow(["f%d@x.vn" % i, "f%d" % i, "Thứ 2", "clb_covua", "SUBMITTED"])
    return lst, [thi_a, thi_b], sn


def test_du_lieu_cho_xac_nhan_roi_lua_chon_thi_xong(tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo_lech(tmp_path, de)
    bt = {"thi_A.xlsx": "A", "thi_B.xlsx": "B"}
    ra = tmp_path / "ra"
    kq = cv.chuyen_fa_daa_du_lieu(str(ra), de, sn, lists=lst, quiz_xlsx=thi, bien_the_tep=bt)
    assert kq["trang_thai"] == "cho_xac_nhan" and kq["clb"] == ["clb_covua"]
    assert os.path.exists(kq["bao_cao"]) and not (ra / cv.TEN_SO).exists()
    kq = cv.chuyen_fa_daa_du_lieu(str(ra), de, sn, lists=lst, quiz_xlsx=thi, bien_the_tep=bt,
                                  lua_chon={"dieu_chinh": "giu"})
    assert kq["trang_thai"] == "xong"
    d = _diem_covua(str(ra))
    assert d["e0@x.vn"] == 10.0 and d["f0@x.vn"] == 4.0                                   # giữ điểm đã chấm
    ra2 = tmp_path / "ra2"
    kq = cv.chuyen_fa_daa_du_lieu(str(ra2), de, sn, lists=lst, quiz_xlsx=thi, bien_the_tep=bt,
                                  lua_chon={"dieu_chinh": "ap_dung"})
    assert kq["trang_thai"] == "xong"
    d = _diem_covua(str(ra2))
    assert d["e0@x.vn"] == 7.0 and d["f0@x.vn"] == 7.0                                    # dịch về trung bình chung


def test_du_lieu_bo_cau_cham_lai(tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A", dung=4)
    ra = tmp_path / "ra"
    kq = cv.chuyen_fa_daa_du_lieu(str(ra), de, sn, lists=lst, quiz_xlsx=[thi])
    assert kq["trang_thai"] == "xong" and set(_diem_covua(str(ra)).values()) == {8.0}     # 4/5
    kq = cv.chuyen_fa_daa_du_lieu(str(ra), de, sn, lists=lst, quiz_xlsx=[thi],
                                  lua_chon={"bo_cau": [["clb_covua", "A", 5]]})
    assert kq["trang_thai"] == "xong" and set(_diem_covua(str(ra)).values()) == {10.0}    # bỏ câu 5 (sai) -> 4/4
