"""FA-M4 (TH = chưa thử trên Microsoft thật): đề biến thể, phân tích câu hỏi (V§7.5) và cân bằng điểm giữa các đề (D11).

D11: so sánh trung bình từng đề với phần còn lại trên thang 0-10 chưa làm tròn; ngưỡng z*sqrt(s_v^2/n_v + s_o^2/n_o), z = 1,96 (2 đề)
hoặc 2,39 (3 đề); đề có n < 5 chỉ báo, không bao giờ chỉnh; vượt ngưỡng thì cộng (trung bình chung - trung bình đề). Không bao giờ chặn:
admin chọn --ap-dung-dieu-chinh hoặc --giu-diem-goc. Dữ liệu MÔ PHỎNG.
"""
import copy
import math
import os
import sys
import zlib

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import phan_tich_cau_hoi as pt  # noqa: E402
import so_nhap  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402


# ---------------------------------------------------------------- chia đề
def test_chon_bien_the_la_crc32_khong_phai_hash():
    for e in ("a@x.vn", "nguyen.van.a@truong.edu.vn", "zz@x.vn"):
        for n in (2, 3):
            assert pt.chon_bien_the(e, n) == zlib.crc32(e.encode("utf-8")) % n


def test_chon_bien_the_chuan_hoa_email_va_chia_deu():
    assert pt.chon_bien_the("  A@X.vn ", 2) == pt.chon_bien_the("a@x.vn", 2)
    dem = [0, 0]
    for i in range(2000):
        dem[pt.chon_bien_the("hs%d@truong.vn" % i, 2)] += 1
    assert 850 < dem[0] < 1150
    assert pt.chon_bien_the("a@x.vn", 1) == 0


def test_thi_lai_sang_de_khac():
    for i in range(50):
        e = "hs%d@x.vn" % i
        for n in (2, 3):
            assert pt.chon_bien_the_thi_lai(e, n) != pt.chon_bien_the(e, n)
            assert 0 <= pt.chon_bien_the_thi_lai(e, n) < n


# ---------------------------------------------------------------- kiểm đề biến thể
def _cau(dk="de", **kw):
    return dict({"cau": "c", "lua_chon": ["a", "b"], "dap_an": 0, "do_kho": dk}, **kw)


def test_kiem_bien_the_cung_co_cau_thi_khong_loi():
    clb = {"club_id": "clb_x", "de_thi": [_cau("de"), _cau("kho")],
           "de_thi_bien_the": [[_cau("kho"), _cau("de")]]}
    assert pt.kiem_bien_the(clb) == []


def test_kiem_bien_the_lech_so_cau_hoac_co_cau_do_kho():
    clb = {"club_id": "clb_x", "de_thi": [_cau("de"), _cau("kho")], "de_thi_bien_the": [[_cau("de")]]}
    assert any("số câu" in x for x in pt.kiem_bien_the(clb))
    clb = {"club_id": "clb_x", "de_thi": [_cau("de"), _cau("kho")], "de_thi_bien_the": [[_cau("de"), _cau("de")]]}
    assert any("độ khó" in x for x in pt.kiem_bien_the(clb))
    clb = {"club_id": "clb_x", "de_thi": [_cau("de")], "de_thi_bien_the": [[_cau("de")]] * 3}
    assert any("tối đa 3" in x for x in pt.kiem_bien_the(clb))


# ---------------------------------------------------------------- phân tích câu
def _bai(sid, dung, club="clb_x", bt="A"):
    return {"sid": sid, "club_id": club, "bien_the": bt, "dung": dung}


def test_phan_tich_cau_phan_biet_va_co():
    # 9 em xếp theo (tổng giảm dần, mã): nhóm trên s0-s2 (tổng 3), giữa s3-s5 và dưới s6-s8 (tổng 2).
    mau = {"tren": [True, False, True, False, True], "giua": [True, False, True, False, False],
           "duoi": [False, True, True, False, False]}
    bai = [_bai("s%d" % i, list(mau["tren" if i < 3 else "giua" if i < 6 else "duoi"])) for i in range(9)]
    ra = {r["cau"]: r for r in pt.phan_tich_cau(bai)}
    assert ra[1]["phan_biet"] == 1.0 and not ra[1]["co"]
    assert ra[2]["phan_biet"] == -1.0 and "PHAN_BIET_AM" in ra[2]["co"]
    assert ra[3]["ti_le_dung"] == 1.0 and "QUA_DE" in ra[3]["co"]
    assert ra[4]["ti_le_dung"] == 0.0 and "QUA_KHO" in ra[4]["co"]
    assert ra[1]["so_bai"] == 9 and ra[1]["ti_le_dung"] == pytest.approx(6 / 9)


def test_phan_tich_cau_it_hon_3_em_khong_tinh_phan_biet():
    ra = pt.phan_tich_cau([_bai("a", [True, False]), _bai("b", [False, True])])
    assert all(r["phan_biet"] is None for r in ra)


def test_phan_tich_cau_tach_theo_clb_va_de():
    bai = [_bai("a", [True], "clb_x", "A"), _bai("b", [False], "clb_x", "B"), _bai("c", [True], "clb_y", "A")]
    khoa = {(r["club_id"], r["bien_the"], r["cau"]) for r in pt.phan_tich_cau(bai)}
    assert khoa == {("clb_x", "A", 1), ("clb_x", "B", 1), ("clb_y", "A", 1)}


def test_tinh_lai_bo_cau_chia_deu_cac_cau_con_lai():
    assert pt.diem_10_sau_bo_cau([True, False, True, True], bo=set()) == 7.5
    assert pt.diem_10_sau_bo_cau([True, False, True, True], bo={2}) == 10.0
    assert pt.diem_10_sau_bo_cau([True, False], bo={1, 2}) == 0.0


# ---------------------------------------------------------------- D11
TRONG = [6, 5, 7, 6, 5, 6, 7, 5, 6, 6]


def test_d11_trong_ngưỡng_khong_dieu_chinh():
    a = [6, 7, 5, 6, 7, 6, 5, 7, 6, 5]
    b = [6, 5, 7, 6, 5, 6, 7, 5, 6, 6]
    kq = pt.so_sanh_bien_the({"A": a, "B": b})
    assert kq["co_lech"] is False
    assert all(v["dich"] == 0 for v in kq["bien_the"].values())


def test_d11_vuot_ngưỡng_dich_dung_bang_trung_binh_chung_tru_trung_binh_de():
    a = [8, 9, 7, 8, 9, 8, 7, 9, 8, 7]                              # trung bình 8,0
    b = [4, 5, 3, 4, 5, 4, 3, 5, 4, 3]                              # trung bình 4,0
    kq = pt.so_sanh_bien_the({"A": a, "B": b})
    assert kq["co_lech"] is True
    assert kq["trung_binh_chung"] == pytest.approx(6.0)
    assert kq["bien_the"]["A"]["dich"] == pytest.approx(-2.0)
    assert kq["bien_the"]["B"]["dich"] == pytest.approx(2.0)
    # ngưỡng đúng công thức
    sa, sb = _sd(a), _sd(b)
    assert kq["bien_the"]["A"]["nguong"] == pytest.approx(1.96 * math.sqrt(sa ** 2 / 10 + sb ** 2 / 10))
    assert pt.diem_dieu_chinh(8, -2.0) == 6 and pt.diem_dieu_chinh(5.5, 0) == 6      # nửa lên
    assert pt.diem_dieu_chinh(1, -3.0) == 0 and pt.diem_dieu_chinh(9.8, 2.0) == 10    # kẹp 0-10


def _sd(x):
    m = sum(x) / len(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def test_d11_de_it_hon_5_em_chi_bao_khong_bao_gio_chinh():
    kq = pt.so_sanh_bien_the({"A": [9, 9, 9, 9, 9, 9, 9, 9], "B": [1, 1, 1, 1]})
    assert kq["bien_the"]["B"]["dich"] == 0 and kq["bien_the"]["B"]["ly_do"] == "N_NHO"
    assert kq["bien_the"]["A"]["ly_do"] in ("NGOAI_NGUONG", "TRONG_NGUONG")


def test_d11_ba_de_dung_z_2_39_va_mot_de():
    x = {"A": [5, 6, 7, 6, 5, 6], "B": [5, 6, 7, 6, 5, 6], "C": [6, 7, 8, 7, 6, 7]}
    kq = pt.so_sanh_bien_the(x)
    s = _sd(x["C"])
    so = [v for k, vs in x.items() if k != "C" for v in vs]
    assert kq["bien_the"]["C"]["nguong"] == pytest.approx(2.39 * math.sqrt(s ** 2 / 6 + _sd(so) ** 2 / 12))
    assert pt.so_sanh_bien_the({"A": [1, 2, 3, 4, 5]})["co_lech"] is False
    with pytest.raises(ValueError):
        pt.so_sanh_bien_the({k: [1, 2, 3, 4, 5] for k in "ABCD"})


# ---------------------------------------------------------------- sinh biểu mẫu biến thể
def _de_bien_the():
    de = copy.deepcopy(bm.doc_de_thi())
    clb = next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    clb["de_thi_bien_the"] = [[dict(c, cau=c["cau"] + " (đề B)") for c in clb["de_thi"]]]
    return de


def test_sinh_bien_the_ghi_docx_moi_de_va_huong_dan(tmp_path):
    de = _de_bien_the()
    ra = tmf.sinh_bien_the(de, str(tmp_path))
    ten = sorted(os.path.basename(p) for p in ra)
    assert ten == sorted([tmf.TEN_CAI_DAT_BIEN_THE, "NHAP_FORMS_BIEN_THE_clb_covua_A.docx",
                          "NHAP_FORMS_BIEN_THE_clb_covua_B.docx"])
    md = (tmp_path / tmf.TEN_CAI_DAT_BIEN_THE).read_text(encoding="utf-8")
    for tu in ("CHƯA thử", "crc32", "Time limit", "Shuffle questions", "Shuffle options", "--ap-dung-dieu-chinh",
               "--giu-diem-goc"):
        assert tu in md, tu


def test_sinh_bien_the_khong_co_de_nao_thi_bao_loi(tmp_path):
    with pytest.raises(bm.LoiDeThi):
        tmf.sinh_bien_the(bm.doc_de_thi(), str(tmp_path))


# ---------------------------------------------------------------- bộ chuyển đổi: cổng xác nhận
def _tep_thi(tmp_path, clb_v, dong, ten):
    """dong: [(email, so_cau_dung)]; clb_v: CLB với đề của biến thể này; mọi em thi trong 600 giây."""
    tieu = ["ID", "Start time", "Completion time", "Email", "Name", bm.cau_cong_thi(bm.doc_de_thi(), clb_v, chi_thi=True)]
    tieu += [bm.cau_de_thi(clb_v, i) for i in range(1, len(clb_v["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for email, k in dong:
        r = {"Email": email, "Name": email, "Start time": "2026-11-09 10:00:00", "Completion time": "2026-11-09 10:10:00",
             tieu[5]: bm.CO}
        for i, cau in enumerate(clb_v["de_thi"], 1):
            r[bm.cau_de_thi(clb_v, i)] = cau["lua_chon"][cau["dap_an"] if i <= k else (cau["dap_an"] + 1) % len(cau["lua_chon"])]
        ws.append([r.get(h, "") for h in tieu])
    p = str(tmp_path / ten)
    wb.save(p)
    return p


def _bo(tmp_path, ka, kb, n=10):
    """Dựng: de có 2 đề cho CLB cờ vua, n em mỗi đề, điểm đúng ka (đề A) và kb (đề B); trả (de, ds đăng ký, tệp thi A/B, sổ nhập CLB)."""
    de = _de_bien_the()
    clb = next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    clb_b = dict(clb, de_thi=clb["de_thi_bien_the"][0])
    emails_a = ["a%d@x.vn" % i for i in range(n)]
    emails_b = ["b%d@x.vn" % i for i in range(n)]
    dong_a = [(e, ka[i % len(ka)]) for i, e in enumerate(emails_a)]
    dong_b = [(e, kb[i % len(kb)]) for i, e in enumerate(emails_b)]
    pa = _tep_thi(tmp_path, clb, dong_a, "thi_A.xlsx")
    pb = _tep_thi(tmp_path, clb_b, dong_b, "thi_B.xlsx")
    import csv
    p = tmp_path / "list.csv"
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "HoTen", "Thu", "NV1", "TrangThai"])
        for e in emails_a + emails_b:
            w.writerow([e, e, "Thứ 2", "clb_covua", "SUBMITTED"])
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": 40, "reserve_capacity": 0, "reserve_group": "",
              "buoi": c["buoi"], "loai": so_nhap.TU_DO if c["club_id"] == "clb_nhiepanh" else so_nhap.GIOI_HAN}
             for c in de["cau_lac_bo"]]
    clubs[0]["loai"], clubs[0]["diem_san"] = so_nhap.TUYEN_CHON, 5
    sn = str(tmp_path / "clb.xlsx")
    so_nhap.ghi_so_nhap(sn, clubs=clubs)
    return de, str(p), {"A": pa, "B": pb}, sn


def _chay(tmp_path, de, lists, tep, sn, **kw):
    return cv.chuyen_fa_daa(str(tmp_path / "ra"), de, sn, lists=lists, quiz_xlsx=[tep["A"], tep["B"]],
                            bien_the_tep={"thi_A.xlsx": "A", "thi_B.xlsx": "B"}, **kw)


def _diem(tmp_path):
    du = so_nhap.doc_so_nhap(openpyxl.load_workbook(str(tmp_path / "ra" / cv.TEN_SO)))
    return {s["student_id"]: float(next(n for n in s["nv"] if n["club_id"] == "clb_covua")["diem"] or -1)
            for s in du["students"]}


def test_cong_xac_nhan_khong_co_co_thi_khong_ghi_so_nhap(tmp_path):
    de, lists, tep, sn = _bo(tmp_path, [5, 5, 4, 5, 5, 4, 5, 5, 4, 5], [2, 2, 3, 2, 1, 2, 3, 2, 2, 1])
    with pytest.raises(cv.LoiTepXuat) as e:
        _chay(tmp_path, de, lists, tep, sn)
    assert "--ap-dung-dieu-chinh" in str(e.value) and "--giu-diem-goc" in str(e.value)
    assert not (tmp_path / "ra" / cv.TEN_SO).exists()
    assert (tmp_path / "ra" / "DIEU_CHINH_BAN_DE.xlsx").exists()


def test_giu_diem_goc_ghi_diem_nhu_da_cham(tmp_path):
    de, lists, tep, sn = _bo(tmp_path, [5] * 10, [2] * 10)
    _chay(tmp_path, de, lists, tep, sn, giu_diem_goc=True)
    d = _diem(tmp_path)
    assert {d["a0@x.vn"], d["b0@x.vn"]} == {10.0, 4.0}


def test_ap_dung_dieu_chinh_dich_ve_trung_binh_chung(tmp_path):
    de, lists, tep, sn = _bo(tmp_path, [5] * 10, [2] * 10)
    _chay(tmp_path, de, lists, tep, sn, ap_dung_dieu_chinh=True)
    d = _diem(tmp_path)
    assert d["a0@x.vn"] == 7.0 and d["b0@x.vn"] == 7.0               # trung bình chung 7: A 10-3, B 4+3


def test_hai_co_cung_luc_la_loi(tmp_path):
    de, lists, tep, sn = _bo(tmp_path, [5] * 10, [2] * 10)
    with pytest.raises(cv.LoiTepXuat):
        _chay(tmp_path, de, lists, tep, sn, ap_dung_dieu_chinh=True, giu_diem_goc=True)


def test_khong_lech_thi_khong_can_co_va_ghi_diem_goc(tmp_path):
    de, lists, tep, sn = _bo(tmp_path, [4, 3, 4, 3, 4, 3, 4, 3, 4, 3], [3, 4, 3, 4, 3, 4, 3, 4, 3, 4])
    kq = _chay(tmp_path, de, lists, tep, sn)
    assert (tmp_path / "ra" / cv.TEN_SO).exists()
    assert not any("lệch" in x[2] for x in kq["canh_bao"] if "đề" in x[2])


def test_bo_cau_cham_lai_cho_moi_hoc_sinh(tmp_path):
    de, lists, tep, sn = _bo(tmp_path, [4] * 10, [4] * 10)
    _chay(tmp_path, de, lists, tep, sn, bo_cau={("clb_covua", 5)})
    d = _diem(tmp_path)
    assert d["a0@x.vn"] == 10.0                                          # 4 câu đúng đầu, bỏ câu 5 (sai) -> 4/4
    assert (tmp_path / "ra" / "PHAN_TICH_CAU_HOI.xlsx").exists()


def test_main_ap_dung_va_giu_goc_loai_tru(tmp_path):
    with pytest.raises(SystemExit):
        cv.main(["--fa-daa", "--so-nhap-clb", "c.xlsx", "--lists", "l.csv", "--ap-dung-dieu-chinh", "--giu-diem-goc",
                 "--ra", str(tmp_path)])
    with pytest.raises(SystemExit):
        cv.main(["--ap-dung-dieu-chinh", "x.xlsx", "--ra", str(tmp_path)])        # chỉ với --fa-daa


def test_cli_chia_ghi_de_giao_va_de_thi_lai(tmp_path):
    import csv
    ds = tmp_path / "ds.csv"
    ds.write_text("Email\nA@x.vn\nb@x.vn\n", encoding="utf-8")
    ra = tmp_path / "de.csv"
    assert pt.main(["chia", str(ds), "--so-bien-the", "2", "--ra", str(ra)]) == 0
    dong = list(csv.DictReader(open(ra, encoding="utf-8-sig")))
    assert [r["Email"] for r in dong] == ["a@x.vn", "b@x.vn"]
    for r in dong:
        assert r["DeGiao"] == "AB"[pt.chon_bien_the(r["Email"], 2)] and r["DeThiLai"] != r["DeGiao"]


def test_main_bien_the_loai_tru_voi_che_do_khac(tmp_path):
    with pytest.raises(SystemExit):
        tmf.main(["--bien-the", "--fa-daa", "--ra", str(tmp_path)])
