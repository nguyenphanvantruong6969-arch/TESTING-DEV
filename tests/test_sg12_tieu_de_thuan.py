"""SG-12 (H2, D2 = b): học sinh không còn thấy mã `[thu_2-nv1]`, `(clb_bong_ro)` trong biểu mẫu.

Bộ sinh ghi tiêu đề THUẦN + `MAP_<biểu mẫu>.json`; mọi bộ đọc nhận tiêu đề thuần bằng bản đồ dựng từ đề thi (cùng một hàm
`bieu_mau.ban_do_chung`), và vẫn đọc được tệp xuất CŨ có mã. Cờ `--giu-ma` giữ tiêu đề có mã như trước.

Module này chạy ở chế độ mặc định (thuần); các test cũ chạy ở chế độ giữ mã (xem `tests/conftest.py`) — đó là bằng chứng
"tệp cũ có mã vẫn nạp được". Dữ liệu hoàn toàn MÔ PHỎNG.
"""
import base64
import copy
import io
import json
import os
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import fa_sau_xep as sx  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

MA_THE = "["            # dấu hiệu của thẻ mã ở đầu tiêu đề


@pytest.fixture
def de():
    return bm.doc_de_thi()


def _cau(phan):
    return [c for _, cs in phan for c in cs]


def _moi_tieu_de(de):
    return [c[0] for c in bm._moi_cau_hoi(de)]


# ------------------------------------------------------------------ 1. tiêu đề thuần và chế độ giữ mã

def test_mac_dinh_la_thuan_khong_the_ma_khong_ma_cuoi_lua_chon(de):
    for td in _moi_tieu_de(de):
        assert not str(td).lstrip().startswith(MA_THE), td
    for _t, _l, lcs, *_ in bm._moi_cau_hoi(de):
        for lc in lcs:
            if isinstance(lc, bm.LuaChon):
                assert str(lc) == lc.thuan and not str(lc).rstrip().endswith(")") or "(" not in lc.thuan, lc


def test_giu_ma_tra_dung_chu_cu_tung_chu(de):
    with bm.che_do_giu_ma(True):
        assert bm.cau_ma_hoc_sinh() == "[student_id] Mã học sinh của em (ghi đúng như trên thẻ học sinh)"
        assert bm.cau_nguyen_vong_fa(de, "thu_2", 1) == "[thu_2-nv1] Thứ Hai — Nguyện vọng 1"
        clb = de["cau_lac_bo"][0]
        assert bm.lua_chon_clb(clb) == "%s (%s)" % (clb["name"], clb["club_id"])
        assert bm.CAU_HAI_LONG == "[hai_long] Em hài lòng với kết quả xếp CLB đến mức nào?"
        assert bm.LUA_CHON_KHO_NHAT[0] == "Chọn CLB (chon_clb)"
        assert bm.cau_de_thi(clb, 1, de) == "[%s-1] %s" % (clb["club_id"], clb["de_thi"][0]["cau"])
    assert bm.cau_nguyen_vong_fa(de, "thu_2", 1) == "Thứ Hai — Nguyện vọng 1"      # ra khỏi `with` là về thuần


def test_che_do_giu_ma_khong_ro_ri_sang_luong_khac(de):
    with bm.che_do_giu_ma(True):
        assert bm.dang_giu_ma()
    assert not bm.dang_giu_ma()


def test_main_giu_ma_khong_de_lai_che_do_giu_ma_sau_khi_chay(tmp_path):
    assert tm.main(["--tuan-3", "--giu-ma", "--ra", str(tmp_path)]) == 0
    assert not bm.dang_giu_ma()


def test_ma_cua_cau_va_ma_trong_lua_chon_van_doc_chu_co_ma():
    assert bm.ma_cua_cau("[thu_2] Thứ Hai — …") == "thu_2"
    assert bm.ma_cua_cau("3. [thu_2-nv1] Thứ Hai — Nguyện vọng 1") == "thu_2-nv1"
    assert bm.ma_cua_cau("Thứ Hai — Nguyện vọng 1") is None              # không bản đồ: không đoán
    assert bm.ma_trong_lua_chon("CLB Cờ vua (clb_covua)") == "clb_covua"
    assert bm.ma_trong_lua_chon("CLB Cờ vua") is None


# ------------------------------------------------------------------ 2. bản đồ: một hàm, duy nhất, xác định

def test_ban_do_chung_moi_tieu_de_tro_ve_dung_ma(de):
    bd = bm.ban_do_chung(de)
    for td, _l, lcs, *_ in bm._moi_cau_hoi(de):
        assert bm.ma_cua_cau(str(td), bd) == td.ma
        for lc in lcs:
            if isinstance(lc, bm.LuaChon) and lc.ma is not None:
                assert bm.ma_trong_lua_chon(str(lc), bd, td.ma) == lc.ma
    assert bm.ma_cua_cau("3. " + str(bm.cau_ho_ten()), bd) == "name"        # Forms đôi khi giữ số thứ tự


def test_ban_do_xac_dinh_khoa_sap_va_khong_gio(de):
    a, b = bm.ban_do_ra_json(bm.ban_do_chung(de)), bm.ban_do_ra_json(copy.deepcopy(bm.ban_do_chung(de)))
    assert a == b and a.endswith("}\n")
    d = json.loads(a)
    assert list(d["cau"]) == sorted(d["cau"]) and list(d) == sorted(d)
    assert "kn_buoi" in d["lua_chon"] and d["lua_chon"]["kn_buoi"]["Thứ Hai"] == "thu_2"
    assert d["lua_chon"]["thu_2"]["CLB Cờ vua"] == "clb_covua"


def test_hai_cau_khac_ma_cung_chu_thi_them_ten_clb_va_so_cau(de):
    de2 = copy.deepcopy(de)
    a, b = bm.clb_co_thi(de2)[0], bm.clb_co_thi(de2)[1]
    b["de_thi"][0]["cau"] = a["de_thi"][0]["cau"]
    ta, tb = bm.cau_de_thi(a, 1, de2), bm.cau_de_thi(b, 1, de2)
    assert str(ta) != str(tb) and a["name"] in str(ta) and b["name"] in str(tb) and "câu 1" in str(ta)
    bd = bm.ban_do_chung(de2)                                   # không ném: đã tách
    assert bm.ma_cua_cau(str(ta), bd) == "%s-1" % a["club_id"] and bm.ma_cua_cau(str(tb), bd) == "%s-1" % b["club_id"]
    # không truyền de = không xét trùng (hàm cũ gọi hai tham số vẫn cho chữ câu)
    assert str(bm.cau_de_thi(a, 1)) == a["de_thi"][0]["cau"]
    assert [str(x) for x in (bm.cau_de_thi(c, 2, de2) for c in (a, b))] == [a["de_thi"][1]["cau"], b["de_thi"][1]["cau"]]


def test_hai_clb_cung_ten_trong_mot_ngay_la_loi_ro(de):
    de2 = copy.deepcopy(de)
    c0, c1 = bm.clb_cua_buoi(de2, "thu_2")[:2]
    c1["name"] = c0["name"]
    with pytest.raises(bm.LoiDeThi) as e:
        bm.ban_do_chung(de2)
    assert "cùng chữ" in str(e.value) and c0["name"] in str(e.value)


def test_tieu_de_thuan_mo_dau_bang_ngoac_vuong_bi_tu_choi(de):
    de2 = copy.deepcopy(de)
    bm.clb_co_thi(de2)[0]["de_thi"][0]["cau"] = "[x] câu hỏi mở đầu bằng ngoặc"
    with pytest.raises(bm.LoiDeThi):
        bm.ban_do_chung(de2)


def test_gop_ban_do_va_doc_ban_do_tu_tep(de, tmp_path):
    p = tmp_path / "m.json"
    p.write_text(bm.ban_do_ra_json(bm.ban_do_chung(de)), encoding="utf-8")
    assert bm.doc_ban_do(str(p)) == bm.ban_do_chung(de)
    (tmp_path / "hong.json").write_text("{}", encoding="utf-8")
    with pytest.raises(bm.LoiDeThi):
        bm.doc_ban_do(str(tmp_path / "hong.json"))
    x = {"cau": {"A": "a"}, "lua_chon": {}}
    with pytest.raises(bm.LoiDeThi):
        bm.gop_ban_do(x, {"cau": {"A": "b"}, "lua_chon": {}})
    assert bm.gop_ban_do(x, {"cau": {"B": "b"}, "lua_chon": {}})["cau"] == {"A": "a", "B": "b"}


# ------------------------------------------------------------------ 3. bộ sinh: tiêu đề thuần + MAP_*.json

def _docx_chu(duong):
    from docx import Document
    return "\n".join(p.text for p in Document(duong).paragraphs)


def _che_do(tmp_path, *co):
    ra = tmp_path / "_".join(c.strip("-") for c in co) or "mac_dinh"
    tm.main(list(co) + ["--ra", str(ra)])
    return ra


@pytest.mark.parametrize("co", [("--fa-daa",), ("--fa-daa", "--mot-bieu-mau"), ("--chi-thi",), ("--moi-clb",),
                                ("--phan-hoi",), ("--sau-ket-qua",), ("--tuan-3",)])
def test_moi_che_do_ghi_map_canh_moi_docx_va_khong_ma_trong_docx(co, tmp_path):
    ra = _che_do(tmp_path, *co)
    docx = sorted(f for f in os.listdir(ra) if f.endswith(".docx"))
    assert docx
    for f in docx:
        m = ra / ("MAP_%s.json" % f[:-5])
        assert m.exists(), f
        bd = json.loads(m.read_text(encoding="utf-8"))
        assert bd["cau"] and bd["phien_ban"] == bm.BAN_DO_PHIEN_BAN
        chu = _docx_chu(str(ra / f))
        assert not any(ln.split(". ", 1)[-1].startswith(MA_THE) for ln in chu.splitlines() if ln[:1].isdigit()), f
        for k in bd["cau"]:                                      # mọi tiêu đề trong map có mặt đúng chữ trong docx
            assert k in chu, (f, k)
        assert "(clb_" not in chu


@pytest.mark.parametrize("co", [("--fa-daa",), ("--chi-thi",), ("--moi-clb",), ("--phan-hoi",), ("--sau-ket-qua",)])
def test_giu_ma_giong_cu_va_khong_ghi_map(co, tmp_path):
    ra = _che_do(tmp_path, *co, "--giu-ma")
    assert not [f for f in os.listdir(ra) if f.startswith("MAP_")]
    docx = sorted(f for f in os.listdir(ra) if f.endswith(".docx"))
    assert any("[student_id]" in _docx_chu(str(ra / f)) or "[thi-" in _docx_chu(str(ra / f))
               or "[clb_" in _docx_chu(str(ra / f)) for f in docx)


def test_sinh_hai_lan_map_giong_het_tung_byte(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    tm.main(["--fa-daa", "--ra", str(a)])
    tm.main(["--fa-daa", "--ra", str(b)])
    ten = sorted(f for f in os.listdir(a) if f.startswith("MAP_"))
    assert ten and ten == sorted(f for f in os.listdir(b) if f.startswith("MAP_"))
    assert all((a / t).read_bytes() == (b / t).read_bytes() for t in ten)


def test_doi_che_do_xoa_map_cu(tmp_path):
    tm.main(["--fa-daa", "--ra", str(tmp_path)])
    assert [f for f in os.listdir(tmp_path) if f.startswith("MAP_NHAP_FORMS_DANG_KY_thu")]
    tm.main(["--fa-daa", "--mot-bieu-mau", "--ra", str(tmp_path)])
    assert not [f for f in os.listdir(tmp_path) if f.startswith("MAP_NHAP_FORMS_DANG_KY_thu")]
    assert (tmp_path / "MAP_NHAP_FORMS_DANG_KY_TAT_CA.json").exists()


def test_mac_dinh_md_khong_dan_giu_phan_ma(tmp_path):
    tm.main(["--sau-ket-qua", "--ra", str(tmp_path)])
    md = (tmp_path / tm.TEN_CAI_DAT_SAU_KET_QUA).read_text(encoding="utf-8")
    assert "đừng sửa chữ" in md.lower() or "giữ nguyên chữ" in md.lower()
    assert "Giữ nguyên phần `[mã]`" not in md


def test_bien_the_ghi_map_va_giu_ma_giong_cu(tmp_path):
    de = _de_bien_the()
    dem = {}
    for giu in (False, True):
        ra = tmp_path / ("g%d" % giu)
        with bm.che_do_giu_ma(giu):
            tm.sinh_bien_the(de, str(ra))
        dem[giu] = (len([f for f in os.listdir(ra) if f.startswith("MAP_")]),
                    len([f for f in os.listdir(ra) if f.endswith(".docx")]))
    assert dem[False] == (2, 2) and dem[True] == (0, 2)          # mỗi (CLB, đề) một docx và một MAP; giữ mã thì không MAP
    chu_a = _docx_chu(str(tmp_path / "g0" / "NHAP_FORMS_BIEN_THE_clb_covua_B.docx"))
    assert "(đề B)" in chu_a and "[clb_covua-1]" not in chu_a


def _de_bien_the():
    """de_thi.json + đề B cho CLB Cờ vua (cùng số câu, cùng độ khó)."""
    de = bm.doc_de_thi()
    c = next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    c["de_thi_bien_the"] = [[dict(q, cau=q["cau"] + " (đề B)") for q in c["de_thi"]]]
    return de


# ------------------------------------------------------------------ 4. bộ đọc: tệp thuần = tệp cũ có mã

def _chay_hai_che_do(f):
    """Chạy `f()` ở chế độ thuần rồi chế độ giữ mã; trả (kết quả thuần, kết quả cũ)."""
    with bm.che_do_giu_ma(False):
        thuan = f()
    with bm.che_do_giu_ma(True):
        cu = f()
    return thuan, cu


def _doc_so_nhap(duong):
    wb = openpyxl.load_workbook(duong, data_only=True)
    return {ws.title: [[c for c in r] for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}


def _tieu_cua(duong):
    tieu, cac = cv.doc_tep_xuat(duong)
    return tieu, cac


def test_doc_chuyen_thuong_thuan_giong_cu(de, tmp_path):
    def chay():
        ten = "gm" if bm.dang_giu_ma() else "gt"
        x = str(tmp_path / (ten + ".xlsx"))
        tm.ghi_mau_xuat(de, x, so_hoc_sinh=20)
        tieu, _ = _tieu_cua(x)
        assert any(h.startswith(MA_THE) for h in tieu) == bm.dang_giu_ma()
        kq = cv.chuyen(x, str(tmp_path / ("ra_" + ten)), de)
        return kq["n_hoc_sinh"], kq["n_bai_thi"], [c[2] for c in kq["canh_bao"]], \
            _doc_so_nhap(str(tmp_path / ("ra_" + ten) / cv.TEN_SO))
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu and thuan[0] == 20 and thuan[1] > 0


def test_doc_chi_thi_thuan_giong_cu(de, tmp_path):
    from test_t4m_chi_thi import _ghi_lists
    hs = [("a%d@truong-gia.example.test" % i, "HS %d" % i, {"thu_2": ["clb_covua", "clb_vanhoc"]}) for i in range(5)]

    def chay():
        ten = "gm" if bm.dang_giu_ma() else "gt"
        lists = str(tmp_path / (ten + "_lists.csv"))
        _ghi_lists(lists, hs, de)
        ds, _cb = cv.doc_lists(lists, de)
        x = str(tmp_path / (ten + "_f.xlsx"))
        tm.ghi_mau_xuat_chi_thi(de, x, ds)
        tieu, _ = _tieu_cua(x)
        assert any(h.startswith(MA_THE) for h in tieu) == bm.dang_giu_ma()
        ra = tmp_path / ("ra_" + ten)
        kq = cv.chuyen_chi_thi([x], lists, str(ra), de)
        return kq["n_hoc_sinh"], kq["n_bai_thi"], [c[2] for c in kq["canh_bao"]], _doc_so_nhap(str(ra / cv.TEN_SO))
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu and thuan[1] > 0


def _tep_dang_ky_gop(tmp_path, de, ten):
    phan = bm.cac_phan_fa_gop(de)
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [str(c[0]) for _, cs in phan for c in cs]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    clb = lambda cid: bm.lua_chon_clb(next(c for c in de["cau_lac_bo"] if c["club_id"] == cid))      # noqa: E731
    o = {"Email": "a@x.vn", bm.cau_ma_hoc_sinh(): "HS1", bm.cau_ho_ten(): "An"}
    for k, cid in enumerate(["clb_covua", "clb_vanhoc", "clb_nhiepanh"], 1):
        o[bm.cau_nguyen_vong_fa(de, "thu_2", k)] = clb(cid)
    o[bm.cau_vang_fa(de, "thu_2")] = clb("clb_nhiepanh")
    o[bm.cau_doi_fa(de, "thu_2")] = bm.DOI_CO
    ws.append([o.get(h, "") for h in tieu])
    p = str(tmp_path / ten)
    wb.save(p)
    return p


def test_doc_dang_ky_duong_b_gop_thuan_giong_cu_va_vang_doi_dung(de, tmp_path):
    def chay():
        ten = ("gm" if bm.dang_giu_ma() else "gt") + ".xlsx"
        tieu, cac = _tieu_cua(_tep_dang_ky_gop(tmp_path, de, ten))
        ds, cb = cv.doc_dang_ky_fa_forms(de, tieu, cac, set())
        return ds, cb
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu
    hs = thuan[0]["a@x.vn"]
    assert hs["nguyen_vong"]["thu_2"] == ["clb_covua", "clb_vanhoc", "clb_nhiepanh"]
    assert hs["wp"]["thu_2"]["clb_nhiepanh"] == 60                      # vàng đặt vào CLB nhiếp ảnh


def test_chuyen_fa_daa_duong_b_toan_luong_thuan_giong_cu(de, tmp_path):
    from test_fa_m3_chuyen import _lc, _so_nhap_clb, _tep_dang_ky, _tep_thi

    def chay():
        ten = "gm" if bm.dang_giu_ma() else "gt"
        d = tmp_path / ten
        d.mkdir()
        dk = _tep_dang_ky(d, de, [dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_nhiepanh"), nv2=_lc(de, "clb_covua")),
                                  dict(sid="HS2", email="b@x.vn", nv1=_lc(de, "clb_covua"))])
        thi = _tep_thi(d, de, [("a@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:10:00", {"clb_covua": 4}),
                               ("b@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:09:00", {"clb_covua": 5})])
        ra = d / "ra"
        kq = cv.chuyen_fa_daa(str(ra), de, _so_nhap_clb(d, de), dang_ky_xlsx=[dk], quiz_xlsx=[thi])
        return kq["n_hoc_sinh"], kq["n_bai_thi"], [c[2] for c in kq["canh_bao"]], _doc_so_nhap(str(ra / cv.TEN_SO))
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu and thuan[0] == 2 and thuan[1] == 2


def test_moi_clb_mot_tep_moi_clb_khong_cong_thuan_giong_cu(de, tmp_path):
    clb = bm.clb_co_thi(de)[0]

    def chay():
        ten = "gm" if bm.dang_giu_ma() else "gt"
        phan = bm.cac_phan_moi_clb(de, clb)
        tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [str(c[0]) for _, cs in phan for c in cs]
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(tieu)
        ws.append([1, "", "", "a@x.vn", "A"] + [q["lua_chon"][q["dap_an"]] for q in clb["de_thi"]])
        x = str(tmp_path / (ten + ".xlsx"))
        wb.save(x)
        t, cac = _tieu_cua(x)
        i_email, _n, cot, _cd, phu, la = cv._cot_chi_thi(de, t)
        return [c["club_id"] for c in phu], la, sorted(cot)
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu and thuan[0] == [clb["club_id"]] and thuan[1] == []


def test_tep_thuan_cot_la_duoc_bao_khong_im_lang(de, tmp_path):
    x = str(tmp_path / "x.xlsx")
    tm.ghi_mau_xuat(de, x, so_hoc_sinh=3)
    wb = openpyxl.load_workbook(x)
    ws = wb.active
    ws.cell(1, ws.max_column + 1, "Cột do ai đó thêm vào")
    wb.save(x)
    tieu, cac = _tieu_cua(x)
    _hs, canh_bao = cv.phan_tich(de, tieu, cac)
    nd = " | ".join(c[2] for c in canh_bao)
    assert "Cột do ai đó thêm vào" in nd and "bỏ qua" in nd


def test_tep_thuan_thieu_cau_la_loi_noi_chu_tieu_de(de, tmp_path):
    x = str(tmp_path / "x.xlsx")
    tm.ghi_mau_xuat(de, x, so_hoc_sinh=3)
    wb = openpyxl.load_workbook(x)
    ws = wb.active
    ws.cell(1, 8).value = str(ws.cell(1, 8).value) + " (đã sửa chữ)"       # cột mã học sinh bị sửa chữ trên Forms
    wb.save(x)
    tieu, cac = _tieu_cua(x)
    with pytest.raises(cv.LoiTepXuat) as e:
        cv.phan_tich(de, tieu, cac)
    assert "student_id" in str(e.value) and "chữ tiêu đề" in str(e.value)


def test_nhan_dien_tep_va_doan_bien_the_tieu_de_thuan(tmp_path):
    de = _de_bien_the()
    tieu_dk = [str(c[0]) for _, cs in bm.cac_phan_fa_gop(de) for c in cs]
    tieu_thi = [str(c[0]) for _, cs in bm.cac_phan_moi_clb(de, next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua"))
                for c in cs]
    tieu_sau = [str(c[0]) for _, cs in bm.cac_phan_sau_ket_qua(de) for c in cs]
    assert cv.nhan_dien_tep("a.xlsx", tieu_dk, de) == "dang_ky"
    assert cv.nhan_dien_tep("b.xlsx", ["Email"] + tieu_thi, de) == "bai_thi"
    assert cv.nhan_dien_tep("c.xlsx", tieu_sau, de) == "sau_ket_qua"
    assert cv.nhan_dien_tep("c.xlsx", tieu_sau) == "sau_ket_qua"            # khiếu nại không phụ thuộc đề
    assert cv.nhan_dien_tep("a.xlsx", tieu_dk) == "khong_ro"                # không có đề thì không nhận ra: không đoán
    covua = next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    for k, chu in ((0, "A"), (1, "B")):
        qs = bm._cac_de_cua_clb(covua)[k]
        td = [str(bm.cau_de_thi(dict(covua, de_thi=qs), i, de)) for i in range(1, len(qs) + 1)]
        assert cv.doan_bien_the(de, td) == chu


def test_doan_bien_the_khi_hai_clb_trung_chu_cau_van_dung(de):
    de2 = copy.deepcopy(de)
    a, b = bm.clb_co_thi(de2)[:2]
    b["de_thi"][0]["cau"] = a["de_thi"][0]["cau"]
    td = [str(bm.cau_de_thi(a, i, de2)) for i in range(1, len(a["de_thi"]) + 1)]
    assert "câu 1" in td[0]
    assert cv.doan_bien_the(de2, td) == "A"


# ------------------------------------------------------------------ 5. kiosk: phản hồi, tuần 3, khiếu nại

def _xlsx_b64(hang):
    wb = openpyxl.Workbook()
    ws = wb.active
    for h in hang:
        ws.append(h)
    b = io.BytesIO()
    wb.save(b)
    return base64.b64encode(b.getvalue()).decode("ascii")


def _lc(phan, td, ma):
    for c in _cau(phan):
        if c[0] == td:
            return next(x for x in c[2] if bm.ma_trong_lua_chon(x) == ma)
    raise KeyError(td)


def _hang_sau_ket_qua(de, dong):
    phan = bm.cac_phan_sau_ket_qua(de)
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [str(c[0]) for c in _cau(phan)]
    ra = [tieu]
    for sid, hl, co_sai, buoi, ghi_chu in dong:
        o = {str(bm.cau_ma_hoc_sinh()): sid, str(bm.CAU_HAI_LONG): str(_lc(phan, bm.CAU_HAI_LONG, str(hl))),
             str(bm.CAU_HIEU_LY_DO): str(_lc(phan, bm.CAU_HIEU_LY_DO, "1")),
             str(bm.CAU_KHO_NHAT): str(_lc(phan, bm.CAU_KHO_NHAT, "huy_chuong")),
             str(bm.CAU_CO_SAI): str(_lc(phan, bm.CAU_CO_SAI, str(co_sai))),
             str(bm.CAU_KN_BUOI): buoi, str(bm.CAU_KN_GHI_CHU): ghi_chu}
        ra.append([o.get(h, "") for h in tieu])
    return ra


def test_doc_tep_phan_hoi_thuan_giong_cu_khong_can_de(de):
    def chay():
        h = _hang_sau_ket_qua(de, [("s1", 4, 0, "", ""), ("s2", 2, 0, "", "")])
        assert (not h[0][5].startswith(MA_THE)) == (not bm.dang_giu_ma())
        return sx.doc_tep_forms_phan_hoi(h)
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu and [d["hai_long"] for d in thuan] == [4, 2] and all(d["kho_nhat"] == "huy_chuong" for d in thuan)


def test_doc_tep_khieu_nai_thuan_giong_cu_voi_ban_do_tu_de(de):
    def chay():
        ten = lambda ma: bm.ten_buoi(de, ma)                                    # noqa: E731
        cell = ";".join(str(x) for x in bm.cac_phan_sau_ket_qua(de)[1][1][0][2] if x.ma in ("thu_2", "thu_4"))
        h = _hang_sau_ket_qua(de, [("s1", 4, 1, cell, "sai điểm"), ("s2", 3, 0, "", "")])
        return sx.doc_tep_forms_khieu_nai(h, ["thu_2", "thu_3", "thu_4"], bm.ban_do_chung(de)), ten("thu_2")
    thuan, cu = _chay_hai_che_do(chay)
    assert thuan == cu
    assert [(y["student_id"], y["buoi"]) for y in thuan[0][0]] == [("s1", "thu_2"), ("s1", "thu_4")]


def test_khieu_nai_ten_buoi_thuan_khong_ban_do_la_loi_khong_doan(de):
    cell = ";".join(str(x) for x in bm.cac_phan_sau_ket_qua(de)[1][1][0][2] if x.ma == "thu_2")
    h = _hang_sau_ket_qua(de, [("s1", 4, 1, cell, "sai")])
    assert cell == "Thứ Hai"
    with pytest.raises(sx.ThieuBanDo):
        sx.doc_tep_forms_khieu_nai(h, ["thu_2"])                     # không de, không map: không đoán "Thứ Hai" là buổi nào


def test_api_sau_ket_qua_tieu_de_thuan_can_de_cho_ten_buoi(api):
    import forms_dot
    from test_fa_m6b_sau_ket_qua import _buoi, _dung
    _dung(api)
    ma_buoi = _buoi(api)
    de = {"tieu_de": "x", "diem_moi_cau": 1, "buoi": [{"ma": ma_buoi, "ten": "Ngày chính"}], "cau_lac_bo": []}
    # phản hồi (không phụ thuộc đề): đọc được tiêu đề thuần dù đợt chưa có đề
    ra = api.nhap_sau_ket_qua_forms(_xlsx_b64(_hang_sau_ket_qua(de, [("s1", 4, 0, "", "")])))
    assert ra["ok"] and ra["data"]["n_ket_qua"] == 1 and ra["data"]["n_khieu_nai"] == 0, ra
    # khiếu nại chọn buổi bằng TÊN buổi mà đợt chưa có đề: báo mã lỗi, không đoán
    hang = _hang_sau_ket_qua(de, [("s2", 4, 1, "Ngày chính", "sai điểm")])
    ra = api.nhap_sau_ket_qua_forms(_xlsx_b64(hang))
    assert not ra["ok"] and [e["code"] for e in ra["errors"]] == ["forms_thieu_ban_do"]
    # đợt có đề (kiosk đã dựng biểu mẫu từ đề này): tên buổi đổi ra mã buổi, khiếu nại vào
    with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
        json.dump(de, f, ensure_ascii=False)
    ra = api.nhap_sau_ket_qua_forms(_xlsx_b64(hang))
    assert ra["ok"] and ra["data"]["n_khieu_nai"] == 1, ra
    # cột lạ được báo bằng cảnh báo i18n, không lặng lẽ bỏ
    hang2 = [hang[0] + ["Cột lạ"]] + [r + [""] for r in hang[1:]]
    ra = api.nhap_sau_ket_qua_forms(_xlsx_b64(hang2))
    assert ra["ok"] and "forms_cot_la" in [w["code"] for w in ra["data"]["canh_bao"]], ra


def test_api_phan_hoi_va_tuan_3_tieu_de_thuan(api):
    from test_fa_gap5_phan_hoi import _dung
    _dung(api)
    phan = bm.cac_phan_tuan_3()
    hang = [[str(c[0]) for c in phan[0][1]],
            ["s1", str(phan[0][1][1][2][0]), str(phan[0][1][2][2][1])]]
    ra = api.nhap_phan_hoi_forms(_xlsx_b64(hang))
    assert ra["ok"] and ra["data"]["n_tuan_3"] == 1 and ra["data"]["hoc_sinh"] == 1, ra


def test_danh_sach_chua_dang_ky_nhan_cot_ma_thuan(de, tmp_path):
    import danh_sach_chua_dang_ky as ds
    x = str(tmp_path / "dk.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", str(bm.cau_ma_hoc_sinh())])
    ws.append([1, "HS7"])
    wb.save(x)
    assert ds.doc_da_dang_ky(x) == {"HS7"}
    with bm.che_do_giu_ma(True):
        wb2 = openpyxl.Workbook()
        wb2.active.append(["ID", str(bm.cau_ma_hoc_sinh())])
        wb2.active.append([1, "HS8"])
        wb2.save(x)
        assert ds.doc_da_dang_ky(x) == {"HS8"}


def test_api_nhan_dien_tep_thuan_va_de_trung_la_loi_i18n(api, de):
    import forms_dot
    forms_dot.nap_mau_forms()
    de2 = copy.deepcopy(de)
    c0, c1 = bm.clb_cua_buoi(de2, "thu_2")[:2]
    c1["name"] = c0["name"]
    with pytest.raises(bm.LoiDeThi):
        cv.nhan_dien_tep("a.xlsx", ["x"], de2)
    # ở tầng API: _mot_tep bắt lỗi và trả mã i18n
    d = api._mot_tep("a.xlsx", b"", "B", de2) if hasattr(api, "_mot_tep") else None
    assert d is None or d["loi"]["code"] in ("xlsx_read_failed", "forms_tieu_de_trung")


def test_bo_bieu_mau_mac_dinh_thuan_dung_duoc_va_phieu_clb_khong_co_ban_do(de, tmp_path):
    """Hồi quy: phiếu thiết lập CLB (giáo viên điền, tiêu đề không phải `TieuDe`) làm hỏng cả bộ ở chế độ mặc định."""
    for duong in ("A", "B"):
        thu_muc = tmp_path / duong
        tm.tao_bo_bieu_mau(de, str(thu_muc), duong=duong)
        tep = sorted(p.name for p in thu_muc.rglob("*") if p.is_file())
        assert not [t for t in tep if "PHIEU_CLB" in t and t.startswith("MAP_")]
        assert any(t.startswith("MAP_NHAP_FORMS_") for t in tep)
