"""FA-M6b (TH = chưa thử trên Microsoft thật): MỘT biểu mẫu "Sau khi xem kết quả" = 3 câu phản hồi + nhánh khiếu nại
lỗi dữ liệu, một nút nạp ở kiosk. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import base64
import datetime
import io
import os
import sys

import pytest

import cau_hinh_ws as ch
import fa_sau_xep as sx
from _fa import dung_fa_clb, dung_hs_fa, ma
from test_fa_gap1_diem_danh import api_ws  # noqa: F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
import bieu_mau as bm  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402

DD = "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def de():
    return bm.doc_de_thi()


def _tep(thu_muc):
    """Tên tệp trong thư mục, bỏ thư mục giả `TaiXuong_gia` do conftest tạo sẵn."""
    return sorted(t for t in os.listdir(thu_muc) if t != "TaiXuong_gia")


def _cau(phan):
    return [c for _, cs in phan for c in cs]


# ---------------------------------------------------------------- 1. bố cục
def test_bo_cuc_hai_phan(de):
    phan = bm.cac_phan_sau_ket_qua(de)
    assert [len(cs) for _, cs in phan] == [5, 2]
    p1 = phan[0][1]
    assert [bm.ma_cua_cau(c[0]) for c in p1] == ["student_id", "hai_long", "hieu_ly_do", "kho_nhat", "co_sai"]
    assert all(c[3] is True for c in p1)                                  # phần 1: mọi câu bắt buộc
    assert p1[1:4] == bm.cac_phan_phan_hoi()[0][1][1:4]                   # ba câu phản hồi giống hệt biểu mẫu cũ
    assert p1[0] == (bm.cau_ma_hoc_sinh(), "text", [], True)
    co_sai = p1[4]
    assert co_sai[0] == bm.CAU_CO_SAI and co_sai[1] == "choice" and co_sai[2] == bm.LUA_CHON_CO_SAI
    assert bm.LUA_CHON_CO_SAI == ["Không (0)", "Có (1)"]
    p2 = phan[1][1]
    assert [bm.ma_cua_cau(c[0]) for c in p2] == ["kn_buoi", "kn_ghi_chu"]
    assert all(c[3] is True for c in p2)
    kn_buoi = p2[0]
    assert kn_buoi[1] == "checkbox"
    assert kn_buoi[2] == ["%s (%s)" % (b["ten"], b["ma"]) for b in de["buoi"]]          # mọi ngày, đủ mã, đúng thứ tự
    assert [bm.ma_trong_lua_chon(x) for x in kn_buoi[2]] == [b["ma"] for b in de["buoi"]]
    assert p2[1][1] == "text"
    assert bm.CAU_KN_BUOI.startswith("[kn_buoi]") and bm.CAU_KN_GHI_CHU.startswith("[kn_ghi_chu]")
    assert bm.CAU_CO_SAI.startswith("[co_sai]")


def test_cac_phan_phan_hoi_khong_doi():
    """So với bản sao nguyên văn của cấu trúc trước FA-M6b."""
    mong = [("Phản hồi sau khi xem kết quả", [
        ("[student_id] Mã học sinh của em (ghi đúng như trên thẻ học sinh)", "text", [], True),
        ("[hai_long] Em hài lòng với kết quả xếp CLB đến mức nào?", "choice",
         ["1 — Rất không hài lòng (1)", "2 (2)", "3 (3)", "4 (4)", "5 — Rất hài lòng (5)"], True),
        ("[hieu_ly_do] Em có hiểu vì sao mình được xếp như vậy không?", "choice", ["Có (1)", "Không (0)"], True),
        ("[kho_nhat] Phần nào khó nhất với em?", "choice",
         ["Chọn CLB (chon_clb)", "Xếp thứ tự nguyện vọng (xep_thu_tu)", "Đặt huy chương (huy_chuong)",
          "Bài thử thách (thu_thach)", "Không có phần nào khó (khong_co)"], True)])]
    assert bm.cac_phan_phan_hoi() == mong


# ---------------------------------------------------------------- 3. bộ đọc phản hồi trên tệp gộp
def _hang_gop(de, dong):
    """Tệp xuất Forms MÔ PHỎNG của biểu mẫu gộp: danh sách dòng (hàng 1 = tiêu đề)."""
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [c[0] for c in _cau(bm.cac_phan_sau_ket_qua(de))]
    return [tieu] + [[o.get(h, "") for h in tieu] for o in dong]


def _lc(de, tieu_de, ma_):
    for c in _cau(bm.cac_phan_sau_ket_qua(de)):
        if c[0] == tieu_de:
            return next(x for x in c[2] if bm.ma_trong_lua_chon(x) == ma_)
    raise KeyError(tieu_de)


def _lc_cu(tieu_de, ma_):
    """Như `_lc` nhưng trên biểu mẫu 3 câu CŨ (cho test hồi quy, không phụ thuộc bố cục mới)."""
    for c in _cau(bm.cac_phan_phan_hoi()):
        if c[0] == tieu_de:
            return next(x for x in c[2] if bm.ma_trong_lua_chon(x) == ma_)
    raise KeyError(tieu_de)


def _tl(de, sid, hai_long=4, hieu=1, kho="huy_chuong", co_sai=0, buoi="", ghi_chu="", luc=None):
    o = {bm.cau_ma_hoc_sinh(): sid, bm.CAU_HAI_LONG: _lc(de, bm.CAU_HAI_LONG, str(hai_long)),
         bm.CAU_HIEU_LY_DO: _lc(de, bm.CAU_HIEU_LY_DO, str(hieu)), bm.CAU_KHO_NHAT: _lc(de, bm.CAU_KHO_NHAT, kho),
         bm.CAU_CO_SAI: _lc(de, bm.CAU_CO_SAI, str(co_sai)), bm.CAU_KN_BUOI: buoi, bm.CAU_KN_GHI_CHU: ghi_chu}
    if luc is not None:
        o["Completion time"] = luc
    return o


def test_doc_phan_hoi_tren_tep_gop_giong_tep_ba_cau(de):
    gop = _hang_gop(de, [_tl(de, "s1", 4, 1, "huy_chuong"), _tl(de, "s2", 2, 0, "khong_co", co_sai=1, buoi="x")])
    cu = [[bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT],
          ["s1", _lc(de, bm.CAU_HAI_LONG, "4"), _lc(de, bm.CAU_HIEU_LY_DO, "1"), _lc(de, bm.CAU_KHO_NHAT, "huy_chuong")],
          ["s2", _lc(de, bm.CAU_HAI_LONG, "2"), _lc(de, bm.CAU_HIEU_LY_DO, "0"), _lc(de, bm.CAU_KHO_NHAT, "khong_co")]]
    assert sx.doc_tep_forms_phan_hoi(gop) == sx.doc_tep_forms_phan_hoi(cu)
    assert len(sx.doc_tep_forms_phan_hoi(gop)) == 2


# ---------------------------------------------------------------- 4. bộ đọc khiếu nại
HOP_LE = ["thu_2", "thu_3", "thu_4"]


def _buoi_cell(*cac):
    return ";".join("Ngày %s (%s)" % (c, c) for c in cac)


def test_khieu_nai_co_sai_khong_thi_khong_yeu_cau(de):
    hang = _hang_gop(de, [_tl(de, "s1", co_sai=0, buoi=_buoi_cell("thu_2"), ghi_chu="bỏ qua vì co_sai = 0")])
    assert sx.doc_tep_forms_khieu_nai(hang, HOP_LE) == ([], [])


def test_khieu_nai_hai_buoi_thanh_hai_yeu_cau_va_giu_thu_tu(de):
    luc = datetime.datetime(2026, 11, 11, 8, 30, 0)
    hang = _hang_gop(de, [_tl(de, "s1", co_sai=1, buoi=_buoi_cell("thu_2", "thu_4"), ghi_chu="Điểm sai", luc=luc)])
    yc, bo = sx.doc_tep_forms_khieu_nai(hang, HOP_LE)
    assert bo == []
    assert yc == [{"student_id": "s1", "buoi": "thu_2", "ghi_chu": "Điểm sai", "luc": luc},
                  {"student_id": "s1", "buoi": "thu_4", "ghi_chu": "Điểm sai", "luc": luc}]


def test_khieu_nai_ma_la_rong_va_thieu_ma_hoc_sinh_vao_bo_qua(de):
    hang = _hang_gop(de, [
        _tl(de, "s1", co_sai=1, buoi=_buoi_cell("thu_2", "thu_9"), ghi_chu="a"),      # dòng 2: thu_9 lạ, thu_2 vẫn nhận
        _tl(de, "s2", co_sai=1, buoi="", ghi_chu="b"),                                 # dòng 3: không chọn buổi
        _tl(de, "", co_sai=1, buoi=_buoi_cell("thu_2"), ghi_chu="c"),                  # dòng 4: thiếu mã học sinh
    ])
    yc, bo = sx.doc_tep_forms_khieu_nai(hang, HOP_LE)
    assert [(y["student_id"], y["buoi"]) for y in yc] == [("s1", "thu_2")]
    assert [(r, s) for r, s, _ in bo] == [(2, "s1"), (3, "s2"), (4, "")]
    assert len({m for _, _, m in bo}) == 3                                            # ba lý do khác nhau


def test_khieu_nai_gio_hoan_thanh_doc_duoc_chuoi_va_dang_du_phong(de):
    hang = _hang_gop(de, [_tl(de, "s1", co_sai=1, buoi=_buoi_cell("thu_2"), ghi_chu="a", luc="2026-11-11 09:15:00")])
    assert sx.doc_tep_forms_khieu_nai(hang, HOP_LE)[0][0]["luc"] == datetime.datetime(2026, 11, 11, 9, 15, 0)
    # không có "Completion time": dùng "Start time" làm dự phòng; không đọc được thì None
    h2 = [list(r) for r in hang]
    h2[0][h2[0].index("Completion time")] = "Thời gian hoàn thành"
    assert sx.doc_tep_forms_khieu_nai(h2, HOP_LE)[0][0]["luc"] == datetime.datetime(2026, 11, 11, 9, 15, 0)
    h3 = [list(r) for r in hang]
    h3[0][h3[0].index("Completion time")] = "x"
    h3[1][h3[0].index("Start time")] = datetime.datetime(2026, 11, 10, 7, 0, 0)
    assert sx.doc_tep_forms_khieu_nai(h3, HOP_LE)[0][0]["luc"] == datetime.datetime(2026, 11, 10, 7, 0, 0)
    h4 = [list(r) for r in hang]
    h4[1][h4[0].index("Completion time")] = "không phải giờ"
    assert sx.doc_tep_forms_khieu_nai(h4, HOP_LE)[0][0]["luc"] is None
    h5 = [list(r) for r in hang]
    h5[1][h5[0].index("Completion time")] = ""
    assert sx.doc_tep_forms_khieu_nai(h5, HOP_LE)[0][0]["luc"] is None


def test_khieu_nai_khong_co_cot_co_sai_la_loi(de):
    cu = [[bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG], ["s1", _lc(de, bm.CAU_HAI_LONG, "4")]]
    with pytest.raises(ValueError):
        sx.doc_tep_forms_khieu_nai(cu, HOP_LE)


# ---------------------------------------------------------------- 5. API
def _dung(api, kn=True, ph=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_khieu_nai": kn, "fa_phan_hoi": ph}})
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})
    assert api.run_pipeline(seed=5)["ok"]


def _buoi(api):
    with api._ket_noi_doc() as cur:
        return next(iter(sx.run_goc_theo_buoi(cur)))


def _run_at(api):
    with api._ket_noi_doc() as cur:
        return datetime.datetime.strptime(
            cur.execute("SELECT run_at FROM run_history ORDER BY run_id DESC").fetchone()[0][:19].replace("T", " "), DD)


@pytest.fixture
def gio(monkeypatch):
    def _dat(api, **delta):
        moc = _run_at(api) + datetime.timedelta(**delta)
        monkeypatch.setattr(sx, "bay_gio", lambda: moc)
    return _dat


def _b64(hang):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for h in hang:
        ws.append(h)
    b = io.BytesIO()
    wb.save(b)
    return base64.b64encode(b.getvalue()).decode("ascii")


def _tep_api(de, api, dong):
    return _b64(_hang_gop(de, dong))


def _hs_kn(de, api, sid, **kw):
    kw.setdefault("co_sai", 1)
    kw.setdefault("ghi_chu", "Điểm thi nhập sai")
    return _tl(de, sid, buoi=_buoi_cell(_buoi(api)), **kw)


def _dem(api, bang):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]


def test_api_gio_forms_trong_han_du_nop_sau_han(api, de, gio):
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=5)                                           # lúc nạp (5 ngày sau) đã quá hạn 3 ngày
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s1", luc=r0 + datetime.timedelta(days=1))]))
    assert ra["ok"], ra
    d = ra["data"]
    assert d["n_ket_qua"] == 1 and d["n_khieu_nai"] == 1 and d["khieu_nai_loi"] == [] and d["canh_bao"] == []
    assert _dem(api, "fa_khieu_nai") == 1 and _dem(api, "fa_phan_hoi") == 1
    kn = api.get_khieu_nai()["data"]["khieu_nai"][0]
    assert (kn["student_id"], kn["buoi"], kn["trang_thai"], kn["ghi_chu"]) == \
        ("s1", _buoi(api), "CHO", "Điểm thi nhập sai")


def test_api_gio_forms_sau_han_bao_qua_han_khong_loi_chung(api, de, gio):
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=5)
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [
        _hs_kn(de, api, "s1", luc=r0 + datetime.timedelta(days=4)),                 # quá hạn theo giờ Forms
        _hs_kn(de, api, "s2", luc=r0 + datetime.timedelta(days=1))]))               # trong hạn
    assert ra["ok"], ra
    d = ra["data"]
    assert d["n_ket_qua"] == 2 and d["n_khieu_nai"] == 1
    assert d["khieu_nai_loi"] == [{"student_id": "s1", "buoi": _buoi(api), "code": "khieu_nai_qua_han"}]
    assert _dem(api, "fa_khieu_nai") == 1


def test_api_trung_cho_xu_ly_va_hoc_sinh_la(api, de, gio):
    _dung(api)
    gio(api, days=1)
    assert api.gui_khieu_nai("s1", _buoi(api), "đã gửi tay")["ok"]
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [
        _hs_kn(de, api, "s1"), _hs_kn(de, api, "s_la"), _hs_kn(de, api, "s2")]))
    assert ra["ok"], ra
    d = ra["data"]
    assert d["khieu_nai_loi"] == [{"student_id": "s1", "buoi": _buoi(api), "code": "khieu_nai_trung"}]
    assert d["n_khieu_nai"] == 1                                    # chỉ s2
    assert d["bo_qua"] >= 1                                         # s_la: mã học sinh lạ
    assert d["n_ket_qua"] == 2                                      # phản hồi của s1, s2; s_la bị bỏ
    assert _dem(api, "fa_khieu_nai") == 2


def test_api_hoc_sinh_chua_co_ket_qua_la_khieu_nai_khong_hop_le(api, de, gio):
    _dung(api)
    dung_hs_fa(api, "s5", nv={"s5": ["G", "T"]})                    # có trong CSDL nhưng chưa có dòng kết quả nào
    gio(api, days=1)
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s5")]))
    assert ra["ok"], ra
    assert ra["data"]["khieu_nai_loi"] == [{"student_id": "s5", "buoi": _buoi(api), "code": "khieu_nai_khong_hop_le"}]
    assert ra["data"]["n_khieu_nai"] == 0 and _dem(api, "fa_khieu_nai") == 0


def test_api_buoi_la_va_dong_thieu_buoi_vao_bo_qua_khong_phai_loi(api, de, gio):
    _dung(api)
    gio(api, days=1)
    la = _tl(de, "s1", co_sai=1, buoi=_buoi_cell("thu_6_khong_co"), ghi_chu="x")
    trong = _tl(de, "s2", co_sai=1, buoi="", ghi_chu="y")
    ra = api.nhap_sau_ket_qua_forms(_b64(_hang_gop(de, [la, trong, _hs_kn(de, api, "s3")])))
    assert ra["ok"], ra
    d = ra["data"]
    assert d["n_khieu_nai"] == 1 and d["khieu_nai_loi"] == []
    assert d["bo_qua"] == 2                                           # hai dòng bị bỏ ở bước đọc tệp


def test_api_khong_co_gio_forms_dung_gio_nap_va_canh_bao(api, de, gio):
    _dung(api)
    gio(api, days=1)
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s1")]))
    assert ra["ok"] and ra["data"]["n_khieu_nai"] == 1
    assert [c["code"] for c in ra["data"]["canh_bao"]] == ["khieu_nai_khong_co_gio_forms"]
    gio(api, days=4)                                                 # không có giờ Forms -> tính giờ nạp -> quá hạn
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s2")]))
    assert ra["data"]["khieu_nai_loi"][0]["code"] == "khieu_nai_qua_han"


def test_api_tat_khieu_nai_van_nap_phan_hoi(api, de, gio):
    _dung(api, kn=False)
    gio(api, days=1)
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s1")]))
    assert ra["ok"], ra
    d = ra["data"]
    assert d["n_ket_qua"] == 1 and d["n_khieu_nai"] == 0
    assert [c["code"] for c in d["canh_bao"]] == ["fa_khieu_nai_chua_bat"]
    assert _dem(api, "fa_khieu_nai") == 0 and _dem(api, "fa_phan_hoi") == 1


def test_api_tat_phan_hoi_van_nhan_khieu_nai(api, de, gio):
    _dung(api, ph=False)
    gio(api, days=1)
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s1")]))
    assert ra["ok"], ra
    d = ra["data"]
    assert d["n_ket_qua"] == 0 and d["n_khieu_nai"] == 1
    assert "fa_phan_hoi_chua_bat" in [c["code"] for c in d["canh_bao"]]
    assert _dem(api, "fa_khieu_nai") == 1 and _dem(api, "fa_phan_hoi") == 0


def test_api_tat_ca_co_tat_va_tep_sai(api, de):
    _dung(api, kn=False, ph=False)
    assert ma(api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s1")]))["errors"]) == \
        ["fa_sau_ket_qua_chua_bat"]
    _dung_lai = ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_khieu_nai": True, "fa_phan_hoi": True}})  # noqa: F841
    assert ma(api.nhap_sau_ket_qua_forms("khong-phai-base64")["errors"]) == ["phan_hoi_tep_sai"]
    assert ma(api.nhap_sau_ket_qua_forms(_b64([["a", "b"], [1, 2]]))["errors"]) == ["phan_hoi_tep_sai"]
    # tệp ba câu cũ (không có [co_sai]) vẫn nạp được phần phản hồi, không báo lỗi khiếu nại
    cu = _b64([[bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT],
               ["s1", _lc(de, bm.CAU_HAI_LONG, "4"), _lc(de, bm.CAU_HIEU_LY_DO, "1"),
                _lc(de, bm.CAU_KHO_NHAT, "huy_chuong")]])
    ra = api.nhap_sau_ket_qua_forms(cu)
    assert ra["ok"], ra
    assert ra["data"]["n_ket_qua"] == 1 and ra["data"]["n_khieu_nai"] == 0


def test_api_loi_bat_ngo_hoan_tac_ca_giao_dich(api, de, gio, monkeypatch):
    _dung(api)
    gio(api, days=1)
    goc = type(api)._them_khieu_nai
    so_lan = {"n": 0}

    def hong(self, *a, **k):
        so_lan["n"] += 1
        if so_lan["n"] == 2:
            raise RuntimeError("hong giua chung")
        return goc(self, *a, **k)

    monkeypatch.setattr(type(api), "_them_khieu_nai", hong)
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, [_hs_kn(de, api, "s1"), _hs_kn(de, api, "s2")]))
    assert ma(ra["errors"]) == ["loi_luu_sau_xep"]
    assert _dem(api, "fa_khieu_nai") == 0 and _dem(api, "fa_phan_hoi") == 0          # hoàn tác cả hai bảng


def test_api_hai_nut_cu_van_cho_ket_qua_cu(api, de, gio):
    """Hồi quy: `nhap_phan_hoi_forms` và `gui_khieu_nai` không đổi đầu ra."""
    _dung(api)
    gio(api, days=1)
    tep = _b64([[bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT],
                ["s1", _lc_cu(bm.CAU_HAI_LONG, "4"), _lc_cu(bm.CAU_HIEU_LY_DO, "1"),
                 _lc_cu(bm.CAU_KHO_NHAT, "huy_chuong")],
                ["s9", _lc_cu(bm.CAU_HAI_LONG, "5"), _lc_cu(bm.CAU_HIEU_LY_DO, "1"),
                 _lc_cu(bm.CAU_KHO_NHAT, "khong_co")]])
    assert api.nhap_phan_hoi_forms(tep)["data"] == {"n_ket_qua": 1, "n_tuan_3": 0, "bo_qua": 1}
    b = _buoi(api)
    assert api.gui_khieu_nai("s1", b, "x")["ok"]
    assert ma(api.gui_khieu_nai("s1", b, "lần hai")["errors"]) == ["khieu_nai_trung"]
    assert ma(api.gui_khieu_nai("s9", b, "x")["errors"]) == ["khieu_nai_khong_hop_le"]


# ---------------------------------------------------------------- 7. bộ sinh
def test_sinh_sau_ket_qua_hai_tep_va_giong_het(de, tmp_path):
    assert tmf.main(["--sau-ket-qua", "--ra", str(tmp_path)]) == 0
    assert _tep(tmp_path) == ["CAI_DAT_FORMS_SAU_KET_QUA.md", "NHAP_FORMS_SAU_KET_QUA.docx"]
    md = (tmp_path / "CAI_DAT_FORMS_SAU_KET_QUA.md").read_text(encoding="utf-8")
    assert "TH" in md and "CHƯA thử" in md
    for can in ("[co_sai]", "End of form", "Không (0)", "Có (1)", "Record name", "One response per person",
                "3 ngày", "chủ nhiệm", "Open in Excel", "Nạp biểu mẫu Sau khi xem kết quả", "Multiple answers"):
        assert can in md, can
    truoc = [(tmp_path / t).read_bytes() for t in _tep(tmp_path)]
    assert tmf.main(["--sau-ket-qua", "--ra", str(tmp_path)]) == 0
    assert [(tmp_path / t).read_bytes() for t in _tep(tmp_path)] == truoc
    from docx import Document
    chu = "\n".join(p.text for p in Document(str(tmp_path / "NHAP_FORMS_SAU_KET_QUA.docx")).paragraphs)
    for c in _cau(bm.cac_phan_sau_ket_qua(de)):
        assert c[0] in chu


def test_sinh_sau_ket_qua_xung_khac_che_do_khac(tmp_path):
    for khac in ("--phan-hoi", "--tuan-3", "--fa-daa", "--chi-thi", "--moi-clb", "--bien-the"):
        with pytest.raises(SystemExit) as e:
            tmf.main(["--sau-ket-qua", khac, "--ra", str(tmp_path)])
        assert e.value.code == 2, khac
    assert _tep(tmp_path) == []


def test_phan_hoi_van_giong_het_nhu_truoc(tmp_path):
    """`--phan-hoi` giữ nguyên: hai tệp cũ, không có câu mới."""
    assert tmf.main(["--phan-hoi", "--ra", str(tmp_path)]) == 0
    assert _tep(tmp_path) == ["CAI_DAT_FORMS_PHAN_HOI.md", "NHAP_FORMS_PHAN_HOI.docx"]
    assert "co_sai" not in (tmp_path / "CAI_DAT_FORMS_PHAN_HOI.md").read_text(encoding="utf-8")
