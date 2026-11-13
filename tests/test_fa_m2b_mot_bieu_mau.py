"""FA-M2b (TH = chưa thử trên Microsoft thật): MỘT biểu mẫu đăng ký cho mọi ngày (`--fa-daa --mot-bieu-mau`).

Đường B giữ nguyên chữ của từng câu so với biểu mẫu từng ngày; bộ chuyển đổi đọc được cả hai. Dữ liệu MÔ PHỎNG.
Không đổi hành vi khi không có cờ.
"""
import filecmp
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402

TU_DO = set()


@pytest.fixture
def de():
    return bm.doc_de_thi()


def _tep(thu_muc):
    """Tên tệp trong thư mục, bỏ thư mục giả `TaiXuong_gia` do conftest tạo sẵn."""
    return sorted(t for t in os.listdir(thu_muc) if t != "TaiXuong_gia")


def _cau(phan):
    return [c for _, cs in phan for c in cs]


def _ma(phan):
    return [bm.ma_cua_cau(c[0]) for c in _cau(phan)]


# ---------------------------------------------------------------- 1. bố cục
def test_cac_phan_fa_gop_mot_phan_thong_tin_va_hai_phan_moi_ngay(de):
    phan = bm.cac_phan_fa_gop(de)
    assert len(phan) == 1 + 2 * len(de["buoi"])
    ma = _ma(phan)
    assert ma.count("student_id") == 1 and ma.count("name") == 1
    assert phan[0][0] == "Thông tin học sinh"
    for b in de["buoi"]:
        m = b["ma"]
        so_nv = min(bm.SO_NGUYEN_VONG_FA, len(bm.clb_cua_buoi(de, m)))
        for k in range(1, so_nv + 1):
            assert ma.count("%s-nv%d" % (m, k)) == 1
        assert ma.count(m + "-vang") == 1 and ma.count(m + "-doi") == 1


def test_thu_tu_ngay_theo_de_thi(de):
    ma = _ma(bm.cac_phan_fa_gop(de))
    thu_tu = [ma.index(b["ma"] + "-nv1") for b in de["buoi"]]
    assert thu_tu == sorted(thu_tu)


# ---------------------------------------------------------------- 2. chữ giống hệt biểu mẫu từng ngày
def test_tung_cau_giong_het_bieu_mau_tung_ngay(de):
    gop = bm.cac_phan_fa_gop(de)
    dong_gop = {c[0]: c for c in _cau(gop)}
    for b in de["buoi"]:
        for ten_phan, cs in bm.cac_phan_fa(de, b["ma"])[1:]:
            assert ten_phan in [p[0] for p in gop]
            for c in cs:
                assert dong_gop[c[0]] == c            # tiêu đề, loại, lựa chọn, bắt buộc: bằng nhau
    # phần thông tin giống từng ngày
    assert gop[0] == bm.cac_phan_fa(de, de["buoi"][0]["ma"])[0]


# ---------------------------------------------------------------- 3-4. sinh tệp
def test_mot_bieu_mau_ghi_huong_dan_va_dung_mot_docx(de, tmp_path):
    ra = tmf.sinh_dang_ky(de, str(tmp_path), mot_bieu_mau=True)
    ten = sorted(os.path.basename(p) for p in ra)
    assert ten == sorted([tmf.TEN_CAI_DAT_DANG_KY, tmf.TEN_DOCX_DANG_KY_TAT_CA])
    assert _tep(tmp_path) == ten
    md = (tmp_path / tmf.TEN_CAI_DAT_DANG_KY).read_text(encoding="utf-8")
    assert "Một biểu mẫu cho mọi buổi" in md and "CHƯA thử" in md
    assert "đề xuất" not in md.lower() and "khuyến nghị" not in md.lower()      # D8 còn mở


def test_xoa_tep_cu_khi_doi_che_do(de, tmp_path):
    tmf.sinh_dang_ky(de, str(tmp_path))                                  # từng ngày
    tmf.sinh_dang_ky(de, str(tmp_path), mot_bieu_mau=True)
    ten = _tep(tmp_path)
    assert ten == sorted([tmf.TEN_CAI_DAT_DANG_KY, tmf.TEN_DOCX_DANG_KY_TAT_CA])      # docx từng ngày bị xoá
    tmf.sinh_dang_ky(de, str(tmp_path))                                  # đổi ngược
    ten = _tep(tmp_path)
    assert tmf.TEN_DOCX_DANG_KY_TAT_CA not in ten                         # docx gộp bị xoá
    assert sum(t.startswith(tmf.TIEN_TO_DOCX_DANG_KY) for t in ten) == len(de["buoi"])


def test_mac_dinh_giu_nguyen_danh_sach_tep(de, tmp_path):
    ra = tmf.sinh_dang_ky(de, str(tmp_path))
    ten = sorted(os.path.basename(p) for p in ra)
    assert ten == sorted([tmf.TEN_CAI_DAT_DANG_KY] +
                         ["%s%s.docx" % (tmf.TIEN_TO_DOCX_DANG_KY, b["ma"]) for b in de["buoi"]])
    assert tmf.ghi_cai_dat_dang_ky(de) == tmf.ghi_cai_dat_dang_ky(de, mot_bieu_mau=False)
    assert "Một biểu mẫu cho mọi buổi" not in tmf.ghi_cai_dat_dang_ky(de)


def test_mot_bieu_mau_sinh_hai_lan_giong_het(de, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    tmf.sinh_dang_ky(de, str(a), mot_bieu_mau=True)
    tmf.sinh_dang_ky(de, str(b), mot_bieu_mau=True)
    ten = sorted(os.listdir(a))
    assert filecmp.cmpfiles(a, b, ten, shallow=False)[0] == ten


# ---------------------------------------------------------------- 5-6. bộ chuyển đổi
def _lc(de, club_id):
    return bm.lua_chon_clb(next(c for c in de["cau_lac_bo"] if c["club_id"] == club_id))


def _xuat(tmp_path, ten, phan, dong):
    """Tệp xuất Forms MÔ PHỎNG: tiêu đề = ID, Start/Completion time, Email, Name + tiêu đề câu."""
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [c[0] for _, cs in phan for c in cs]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for r in dong:
        o = {"Email": r["email"], "Name": r["email"]}
        o[bm.cau_ma_hoc_sinh()] = r["sid"]
        o[bm.cau_ho_ten()] = r["email"]
        o.update(r["cau"])
        ws.append([o.get(h, "") for h in tieu])
    p = str(tmp_path / ten)
    wb.save(p)
    return p


def _tra_loi(de, ma_buoi, ds):
    """ds = ['clb_a', 'clb_b', 'clb_c'] -> câu trả lời của ngày đó (huy chương mặc định)."""
    o = {bm.cau_vang_fa(de, ma_buoi): bm.GIU_MAC_DINH_VANG, bm.cau_doi_fa(de, ma_buoi): bm.DOI_KHONG}
    for k, c in enumerate(ds, 1):
        o[bm.cau_nguyen_vong_fa(de, ma_buoi, k)] = _lc(de, c)
    return o


def _clb_ngay(de, ma_buoi):
    return [c["club_id"] for c in bm.clb_cua_buoi(de, ma_buoi)]


def _phan_hai_ngay(de, n1, n2):
    """Bố cục gộp chỉ giữ thông tin học sinh + hai ngày n1, n2 (lọc theo MÃ câu, không theo tên phần)."""
    out = []
    for ten, cs in bm.cac_phan_fa_gop(de):
        ma = {bm.ma_cua_cau(c[0]) for c in cs}
        if ma & {"student_id"} or any(m and m.startswith((n1 + "-", n2 + "-")) for m in ma):
            out.append((ten, cs))
    return out


def _hai_ngay(de):
    """Ngày ĐẦU và ngày CUỐI: bỏ bất kỳ ngày nào khỏi bố cục gộp đều làm bài so khớp đỏ."""
    return de["buoi"][0]["ma"], de["buoi"][-1]["ma"]


def _hoc_sinh(de, lan=0):
    """3 học sinh x 2 ngày; `lan` đảo thứ tự NV để tạo phiếu nộp lần nữa."""
    n1, n2 = _hai_ngay(de)
    c1, c2 = _clb_ngay(de, n1), _clb_ngay(de, n2)
    out = []
    for i in range(3):
        a = c1[i % len(c1):] + c1[:i % len(c1)]
        b = c2[(i + 1) % len(c2):] + c2[:(i + 1) % len(c2)]
        if lan:
            a, b = a[::-1], b[::-1]
        out.append((i, "hs%d@x.vn" % i, "HS%d" % i, a[:3], b[:3]))
    return out


def test_bo_chuyen_doi_gop_bang_hai_tep_tung_ngay(de, tmp_path):
    n1, n2 = _hai_ngay(de)
    hs = _hoc_sinh(de)
    gop = [dict(email=e, sid=s, cau={**_tra_loi(de, n1, a), **_tra_loi(de, n2, b)}) for _, e, s, a, b in hs]
    d1 = [dict(email=e, sid=s, cau=_tra_loi(de, n1, a)) for _, e, s, a, b in hs]
    d2 = [dict(email=e, sid=s, cau=_tra_loi(de, n2, b)) for _, e, s, a, b in hs]

    phan_gop = _phan_hai_ngay(de, n1, n2)
    p_gop = _xuat(tmp_path, "gop.xlsx", phan_gop, gop)
    tieu, cac = cv.doc_tep_xuat(p_gop)
    ds_gop, cb_gop = cv.doc_dang_ky_fa_forms(de, tieu, cac, TU_DO)

    ds_tn = {}
    for ten, ma, dong in (("n1.xlsx", n1, d1), ("n2.xlsx", n2, d2)):
        t, c = cv.doc_tep_xuat(_xuat(tmp_path, ten, bm.cac_phan_fa(de, ma), dong))
        _, cb = cv.doc_dang_ky_fa_forms(de, t, c, TU_DO, danh_sach=ds_tn)
        assert cb == []
    assert cb_gop == []
    assert set(ds_gop) == set(ds_tn) == {e for _, e, _, _, _ in hs}
    for k in ds_gop:
        assert ds_gop[k]["nguyen_vong"] == ds_tn[k]["nguyen_vong"]
        assert ds_gop[k]["wp"] == ds_tn[k]["wp"]
        assert set(ds_gop[k]["nguyen_vong"]) == {n1, n2}


def test_nop_lai_phieu_cuoi_thang_moi_ngay_va_bao_moi_ngay_mot_lan(de, tmp_path):
    n1, n2 = _hai_ngay(de)
    lan1, lan2 = _hoc_sinh(de, 0), _hoc_sinh(de, 1)
    dong = [dict(email=e, sid=s, cau={**_tra_loi(de, n1, a), **_tra_loi(de, n2, b)}) for _, e, s, a, b in lan1]
    dong += [dict(email=e, sid=s, cau={**_tra_loi(de, n1, a), **_tra_loi(de, n2, b)}) for _, e, s, a, b in lan2]
    phan = _phan_hai_ngay(de, n1, n2)
    tieu, cac = cv.doc_tep_xuat(_xuat(tmp_path, "gop2.xlsx", phan, dong))
    ds, cb = cv.doc_dang_ky_fa_forms(de, tieu, cac, TU_DO)
    for _, e, _, a, b in lan2:                                           # phiếu CUỐI thắng ở cả hai ngày
        assert ds[e]["nguyen_vong"][n1] == a
        assert ds[e]["nguyen_vong"][n2] == b
    for _, e, _, _, _ in lan2:
        nop_lai = [x for x in cb if x[1] == e and "nộp lần nữa" in x[2]]
        assert len(nop_lai) == 2                                          # mỗi ngày một cảnh báo
        assert {n1, n2} == {x[2].split(":")[0] for x in nop_lai}


# ---------------------------------------------------------------- 7. vượt trần
def test_vuot_tran_cau_bao_loi_va_khong_ghi_tep(de, tmp_path, monkeypatch):
    monkeypatch.setattr(bm, "TRAN_CAU_MOI_BIEU_MAU", bm.dem_cau_fa_gop(de) - 1)
    with pytest.raises(bm.LoiDeThi):
        tmf.sinh_dang_ky(de, str(tmp_path), mot_bieu_mau=True)
    assert _tep(tmp_path) == []
    assert tmf.main(["--fa-daa", "--mot-bieu-mau", "--ra", str(tmp_path)]) == 1
    assert _tep(tmp_path) == []


def test_vua_dung_tran_van_ghi(de, tmp_path, monkeypatch):
    monkeypatch.setattr(bm, "TRAN_CAU_MOI_BIEU_MAU", bm.dem_cau_fa_gop(de))
    assert len(tmf.sinh_dang_ky(de, str(tmp_path), mot_bieu_mau=True)) == 2


# ---------------------------------------------------------------- 8. dòng lệnh
def test_main_mot_bieu_mau_chi_dung_cung_fa_daa(tmp_path):
    with pytest.raises(SystemExit) as e:
        tmf.main(["--mot-bieu-mau", "--ra", str(tmp_path)])
    assert e.value.code == 2
    for khac in ("--phan-hoi", "--tuan-3", "--chi-thi", "--moi-clb", "--bien-the"):
        with pytest.raises(SystemExit) as e:
            tmf.main(["--mot-bieu-mau", khac, "--ra", str(tmp_path)])
        assert e.value.code == 2
    assert _tep(tmp_path) == []


def test_main_fa_daa_mot_bieu_mau_in_mot_bieu_mau(tmp_path, capsys):
    assert tmf.main(["--fa-daa", "--mot-bieu-mau", "--ra", str(tmp_path)]) == 0
    assert "1 biểu mẫu" in capsys.readouterr().out
    assert (tmp_path / tmf.TEN_DOCX_DANG_KY_TAT_CA).exists()
    assert tmf.main(["--fa-daa", "--ra", str(tmp_path)]) == 0
    assert not (tmp_path / tmf.TEN_DOCX_DANG_KY_TAT_CA).exists()
