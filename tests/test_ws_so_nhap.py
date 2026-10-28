"""Sổ nhập CLB theo cấu hình workspace (TASK 5): tên sheet/tiêu đề theo nhãn, điểm theo người,
trần nguyện vọng/thi lấy từ luật, và MẶC ĐỊNH TRƯỜNG HỌC cho ra đúng sổ như trước.

so_nhap.py phải chạy được một mình: nhận `cfg` là dict thô, không import cau_hinh_ws.
"""

import base64
import io
import json
import os

import pytest

openpyxl = pytest.importorskip("openpyxl")

import cau_hinh_ws as ch  # noqa: E402
import rbda_priority_pipeline as rp  # noqa: E402
import so_nhap  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from _so_nhap_dump import chup  # noqa: E402
from i18n_errors import MESSAGES  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANH_CHUP = os.path.join(GOC, "tests", "du_lieu_ws", "so_nhap_truoc_khi_co_cfg.json")

CONG_TY = {
    "labels": {
        "person": {"vi": "Nhân viên", "en": "Employee"},
        "slot": {"vi": "Dự án", "en": "Project"},
        "session": {"vi": "Ca", "en": "Shift"},
        "group": {"vi": "Cấp bậc", "en": "Level"},
        "score": {"vi": "Điểm", "en": "Score"},
    },
    "rules": {"max_choices": 4, "max_tests": 2, "score_scope": "per_slot"},
}


def _clb(cid, ten, cho=5, buoi="", uu_tien=0, nhom=""):
    return {"club_id": cid, "name": ten, "capacity": cho, "reserve_capacity": uu_tien,
            "reserve_group": nhom, "buoi": buoi}


def _hs(sid, ten, nv, nhom=""):
    return {"student_id": sid, "name": ten, "reserve_group": nhom, "nv": nv}


def _bytes(clubs=(), students=(), **kw):
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, clubs, students, **kw)
    return b.getvalue()


def _wb(du_lieu):
    return openpyxl.load_workbook(io.BytesIO(du_lieu))


def _b64(du_lieu):
    return base64.b64encode(du_lieu).decode()


def _doc(du_lieu, cfg=None, **kw):
    wb = openpyxl.load_workbook(io.BytesIO(du_lieu), read_only=True, data_only=True)
    try:
        return so_nhap.doc_so_nhap(wb, cfg=cfg, **kw)
    finally:
        wb.close()


def _ma_loi(du):
    return [e["code"] for e in du["loi"]]


def _chuan(x):
    return json.loads(json.dumps(x, ensure_ascii=False, default=str, sort_keys=True))


# ------------------------------------------------------------------ độc lập

def test_so_nhap_khong_import_cau_hinh_ws():
    """so_nhap.py được đóng gói vào skill: không được kéo cau_hinh_ws (và rbda_priority_pipeline)."""
    nguon = open(os.path.join(GOC, "so_nhap.py"), encoding="utf-8").read()
    dong_import = [d for d in nguon.splitlines() if d.startswith(("import ", "from "))]
    assert not any("cau_hinh_ws" in d for d in dong_import), dong_import
    assert not any("rbda_priority_pipeline" in d for d in dong_import[:15]), dong_import


def test_chay_mot_minh_voi_cfg_la_dict_tho(tmp_path):
    import subprocess
    import sys
    ra = tmp_path / "s.xlsx"
    ma = ("import so_nhap; so_nhap.ghi_so_nhap(%r, [], [], cfg={'labels': {'slot': {'vi': 'Dự án'}}})"
          % str(ra))
    # chạy trong thư mục có đúng ba tệp mà bản đóng gói của skill mang theo
    nho = tmp_path / "goi"
    nho.mkdir()
    for t in ("so_nhap.py", "i18n_errors.py", "nhan_ws.py"):
        (nho / t).write_bytes(open(os.path.join(GOC, t), "rb").read())
    r = subprocess.run([sys.executable, "-c", ma], cwd=str(nho), capture_output=True, text=True,
                       encoding="utf-8", env={**os.environ, "PYTHONPATH": str(nho)})
    assert r.returncode == 0, r.stderr
    assert openpyxl.load_workbook(str(ra)).sheetnames[0] == "1. Dự án"


# ------------------------------------------------------------------ mặc định trường học == trước đây

CLUBS_MAU = [_clb("a", "Cờ vua", 5, "thu_2", 1, "cs"), _clb("b", "Bóng đá", 6, "thu_3")]
HS_MAU = [_hs("H1", "An", [{"club_id": "a", "thi": True, "diem": "9,5"},
                           {"club_id": "b", "thi": False, "diem": ""}], "cs"),
          _hs("H2", "Bình", [{"club_id": "b", "thi": True, "diem": ""}])]


@pytest.mark.parametrize("cfg", [None, {}, ch.MAC_DINH_TRUONG_HOC,
                                 {"rules": {"max_choices": 10, "max_tests": 5}}],
                         ids=["None", "rong", "mac_dinh_truong_hoc", "luat_mac_dinh"])
def test_mac_dinh_truong_hoc_cho_ra_dung_so_nhu_truoc(cfg):
    truoc = json.load(open(ANH_CHUP, encoding="utf-8"))
    assert _chuan(chup(_bytes(CLUBS_MAU, HS_MAU, cfg=cfg))) == truoc["co_du_lieu"]
    assert _chuan(chup(_bytes(cfg=cfg))) == truoc["trong"]


def test_mau_nv_khong_doi_voi_mac_dinh():
    wb = _wb(_bytes(cfg=ch.MAC_DINH_TRUONG_HOC))
    # Hai hàng tiêu đề (A13.4): hàng 1 là ô gộp "Nguyện vọng k", hàng 2 là tên cột trong nhóm.
    tieu_de = [c.value for c in wb["2. Học sinh"][1]]
    hang_2 = [c.value for c in wb["2. Học sinh"][2]]
    assert tieu_de[:3] == ["Mã HS", "Họ tên", "Nhóm ưu tiên"]
    assert tieu_de[3:7] == ["Nguyện vọng 1", None, "Nguyện vọng 2", None]
    assert hang_2[3:7] == ["CLB", "Điểm thi", "CLB", "Điểm thi"]
    assert len(hang_2) == 3 + 2 * 15      # 15 nhóm CLB/Điểm thi như trước


def test_mac_dinh_doc_giong_het_khi_co_va_khong_co_cfg():
    du = _bytes(CLUBS_MAU, HS_MAU)
    a, b = _doc(du), _doc(du, cfg=ch.MAC_DINH_TRUONG_HOC)
    assert a == b and not a["loi"]
    assert [s["nv"] for s in a["students"]][0][0] == {"club_id": "a", "thi": True, "diem": "9.5"}


# ------------------------------------------------------------------ công ty

def test_cong_ty_sinh_mau_roi_doc_lai():
    clubs = [_clb("du_an_a", "Dự án A", 3, "", 0, "")]
    hs = [_hs("NV01", "Lan", [{"club_id": "du_an_a", "thi": True, "diem": "8"}], "Cấp 1")]
    du = _bytes(clubs, hs, cfg=CONG_TY)
    wb = _wb(du)
    assert wb.sheetnames == ["1. Dự án", "2. Nhân viên", "Hướng dẫn"]
    assert [c.value for c in wb["1. Dự án"][1]] == [
        "Tên CLB", "Buổi", "Chỉ tiêu", "Suất ưu tiên", "Cấp bậc", "Mã CLB"]
    tieu_de = [c.value for c in wb["2. Nhân viên"][1]]
    hang_2 = [c.value for c in wb["2. Nhân viên"][2]]
    assert tieu_de[:5] == ["Mã HS", "Họ tên", "Cấp bậc", "Nguyện vọng 1", None]
    assert hang_2[3:5] == ["Dự án", "Điểm thi"]      # cột chỗ xếp theo nhãn của workspace
    assert tieu_de[-2:] == ["Nguyện vọng 4", None]   # đúng 4 = max_choices, không cột thừa
    # đọc lại bằng cfg: ra đúng dữ liệu đã ghi
    doc = _doc(du, cfg=CONG_TY)
    assert not doc["loi"], doc["loi"]
    assert doc["clubs"][0]["name"] == "Dự án A"
    assert doc["students"][0]["student_id"] == "NV01"
    assert doc["students"][0]["reserve_group"] == "Cấp 1"
    assert doc["students"][0]["nv"] == [{"club_id": "du_an_a", "thi": True, "diem": "8"}]
    # còn không có cfg thì sổ này không phải sổ nhập
    assert _ma_loi(_doc(du)) == ["so_nhap_thieu_sheet", "so_nhap_thieu_sheet"]
    assert so_nhap.la_so_nhap(["1. Dự án", "2. Nhân viên"], CONG_TY)
    assert not so_nhap.la_so_nhap(["1. Dự án", "2. Nhân viên"])


def test_cong_ty_huong_dan_dung_nhan():
    chu = " ".join(str(o.value) for o in _wb(_bytes(cfg=CONG_TY))["Hướng dẫn"]["A"] if o.value)
    assert "Dự án" in chu and "Nhân viên" in chu
    for tu in ("học sinh", "câu lạc bộ", "1. CLB", "2. Học sinh"):
        assert tu not in chu, tu


def test_so_cu_cua_truong_hoc_nap_duoc_vao_workspace_nhan_khac():
    """Tiêu đề CŨ vẫn được nhận: chỉ thêm, không bớt."""
    cu = _bytes(CLUBS_MAU, HS_MAU)                      # sổ y như trước, không cfg
    doc = _doc(cu, cfg=CONG_TY)
    assert not doc["loi"], doc["loi"]
    assert [c["name"] for c in doc["clubs"]] == ["Cờ vua", "Bóng đá"]
    assert [s["student_id"] for s in doc["students"]] == ["H1", "H2"]
    # cả hai cột nhóm: "Nhóm ưu tiên" cũ vẫn là cột nhóm dù nhãn mới là "Cấp bậc"
    assert doc["students"][0]["reserve_group"] == "cs"


def test_nhan_viet_hoa_viet_thuong_va_khong_dau_van_khop():
    wb = openpyxl.Workbook()
    a = wb.active
    a.title = "DU AN"
    a.append(["TEN DU AN", "Chi tieu", "Cap bac", "MA DU AN"])
    a.append(["Dự án X", 4, "", "x"])
    h = wb.create_sheet("nhan vien")
    h.append(["Ma nhan vien", "Ten nhan vien", "cap bac", "nv1", "DIEM 1"])
    h.append(["NV1", "Hà", "senior", "Dự án X", "9"])
    b = io.BytesIO()
    wb.save(b)
    doc = _doc(b.getvalue(), cfg=CONG_TY)
    assert not doc["loi"], doc["loi"]
    assert doc["students"][0]["name"] == "Hà" and doc["students"][0]["reserve_group"] == "senior"
    assert doc["students"][0]["nv"][0]["diem"] == "9"
    assert doc["clubs"][0]["club_id"] == "x"


def test_nhan_tieng_anh_cung_duoc_nhan():
    wb = openpyxl.Workbook()
    a = wb.active
    a.title = "1. Project"
    a.append(["Tên CLB", "Chỉ tiêu"])
    a.append(["P1", 3])
    h = wb.create_sheet("2. Employee")
    h.append(["Mã HS", "Họ tên", "NV1", "Score 1"])
    h.append(["E1", "Eve", "P1", 7])
    b = io.BytesIO()
    wb.save(b)
    doc = _doc(b.getvalue(), cfg=CONG_TY)
    assert not doc["loi"], doc["loi"]
    assert doc["students"][0]["nv"] == [{"club_id": "clb_p1", "thi": True, "diem": "7"}]


def test_nhan_co_ky_tu_cam_o_ten_sheet_van_ghi_va_doc_duoc():
    cfg = {"labels": {"slot": {"vi": "Dự án/Phòng: lớn?"}, "person": {"vi": "Nhân viên " * 5}}}
    du = _bytes([_clb("a", "A")], cfg=cfg)
    ten = _wb(du).sheetnames
    assert all(len(t) <= 31 and not any(c in t for c in "[]:*?/\\") for t in ten), ten
    assert not _doc(du, cfg=cfg)["loi"]


def test_so_cot_nv_theo_tran():
    def nv(cfg, **kw):
        return sum(1 for c in _wb(_bytes(cfg=cfg, **kw))[so_nhap.ten_sheet_hs(cfg)][1]
                   if str(c.value or "").startswith("Nguyện vọng"))
    assert nv({"rules": {"max_choices": 3}}) == 3
    assert nv({"rules": {"max_choices": 1}}) == 1
    assert nv({"rules": {"max_choices": 10}}) == 15            # như trước
    assert nv({"rules": {"max_choices": 20}}) == 20
    assert nv({"rules": {"max_choices": 3}},
              clubs=[_clb("a", "A", buoi="thu_2"), _clb("b", "B", buoi="thu_3")]) == 6   # 3 mỗi buổi
    # dữ liệu dài hơn trần thì cột nới theo dữ liệu, không mất nguyện vọng nào
    dai = [_hs("X", "x", [{"club_id": "a", "thi": False, "diem": ""}] * 5)]
    assert nv({"rules": {"max_choices": 3}}, clubs=[_clb("a", "A")], students=dai) == 5


# ------------------------------------------------------------------ điểm theo người

CA_NHAN = {"labels": CONG_TY["labels"], "rules": {"max_choices": 3, "max_tests": 2,
                                                  "score_scope": "per_person"}}


def test_diem_theo_nguoi_mot_cot_sau_cot_nhom():
    hs = [_hs("NV01", "Lan", [{"club_id": "a", "thi": True, "diem": "8,5"},
                              {"club_id": "b", "thi": True, "diem": "8,5"}], "Cấp 1"),
          _hs("NV02", "Mai", [{"club_id": "a", "thi": False, "diem": ""}])]
    du = _bytes([_clb("a", "Dự án A"), _clb("b", "Dự án B")], hs, cfg=CA_NHAN)
    ws_hs = _wb(du)["2. Nhân viên"]
    tieu_de = [c.value for c in ws_hs[1]]
    assert tieu_de == ["Mã HS", "Họ tên", "Cấp bậc", "Điểm", "Nguyện vọng 1", "Nguyện vọng 2",
                       "Nguyện vọng 3"]
    assert [c.value for c in ws_hs[3]][:6] == ["NV01", "Lan", "Cấp 1", 8.5, "Dự án A", "Dự án B"]
    assert [c.value for c in ws_hs[4]][3] is None                  # không thi
    doc = _doc(du, cfg=CA_NHAN)
    assert not doc["loi"], doc["loi"]
    lan, mai = doc["students"]
    assert lan["diem_ca_nhan"] == "8.5" or lan["diem_ca_nhan"] == "8,5"
    # Điểm theo người nằm ở CẤP NGƯỜI, không chép vào từng nguyện vọng (mở rộng lúc xếp).
    assert [(x["club_id"], x["thi"], x["diem"]) for x in lan["nv"]] == [
        ("a", False, ""), ("b", False, "")]
    assert so_nhap.diem_cua_nguoi(lan) == 8.5 and so_nhap.diem_cua_nguoi(mai) is None
    assert mai["nv"] == [{"club_id": "a", "thi": False, "diem": ""}] and mai["diem_ca_nhan"] == ""


def test_diem_theo_nguoi_chu_thi_va_diem_sai():
    cac_dong = [("NV01", "thi"), ("NV02", "abc"), ("NV03", -3), ("NV04", 7)]
    wb = openpyxl.Workbook()
    a = wb.active
    a.title = "1. Dự án"
    a.append(["Tên CLB", "Chỉ tiêu"])
    a.append(["Dự án A", 5])
    h = wb.create_sheet("2. Nhân viên")
    h.append(["Mã HS", "Họ tên", "Điểm", "NV1"])
    for sid, d in cac_dong:
        h.append([sid, sid, d, "Dự án A"])
    b = io.BytesIO()
    wb.save(b)
    doc = _doc(b.getvalue(), cfg=CA_NHAN)
    sai = [e for e in doc["loi"] if e["code"] == "so_nhap_diem_ca_nhan_sai"]
    assert sorted(e["params"]["student_id"] for e in sai) == ["NV02", "NV03"]
    assert sai[0]["params"]["sheet"] == "2. Nhân viên"
    assert MESSAGES["so_nhap_diem_ca_nhan_sai"]["vi"] and MESSAGES["so_nhap_diem_ca_nhan_sai"]["en"]
    nv01 = next(s for s in doc["students"] if s["student_id"] == "NV01")
    assert nv01["diem_ca_nhan"] == "thi" and so_nhap.diem_cua_nguoi(nv01) is None   # đã thi, chưa có điểm


def test_diem_theo_nguoi_tu_choi_cot_diem_tung_clb_co_du_lieu():
    """Sổ cũ có 'Điểm 1, Điểm 2…' CÓ SỐ nạp vào workspace per_person: không đoán một điểm cho cả
    người từ các điểm từng CLB, và cũng không lặng lẽ bỏ (điểm mất mà không ai biết) — báo lỗi."""
    cu = _bytes([_clb("a", "A")], [_hs("H", "h", [{"club_id": "a", "thi": True, "diem": "9"}])])
    doc = _doc(cu, cfg=CA_NHAN)
    assert [e["code"] for e in doc["loi"]] == ["so_nhap_diem_sai_che_do"]


def test_diem_theo_nguoi_cot_diem_tung_clb_trong_thi_bo_qua_khong_loi():
    """Cột 'Điểm k' còn đó nhưng TRỐNG (sổ mẫu cũ chưa điền điểm): không có gì để mất, không lỗi."""
    cu = _bytes([_clb("a", "A")], [_hs("H", "h", [{"club_id": "a", "thi": False, "diem": ""}])])
    doc = _doc(cu, cfg=CA_NHAN)
    assert not doc["loi"]
    assert doc["students"][0]["nv"][0]["thi"] is False


def test_diem_theo_nguoi_khong_dem_thi_tung_clb():
    """max_tests đếm 'thi từng CLB'; điểm theo người không có khái niệm đó."""
    cfg = {"rules": {"max_choices": 8, "max_tests": 1, "score_scope": "per_person"}}
    clubs = [_clb(c, c.upper()) for c in "abcd"]
    hs = [_hs("H", "h", [{"club_id": c, "thi": True, "diem": "9"} for c in "abcd"])]
    assert not _doc(_bytes(clubs, hs, cfg=cfg), cfg=cfg)["loi"]


# ------------------------------------------------------------------ trần nguyện vọng / thi

def _sach(clubs, hs, cfg):
    return _doc(_bytes(clubs, hs, cfg=cfg), cfg=cfg)


def test_doc_so_tran_nguyen_vong_theo_luat():
    clubs = [_clb(c, c.upper()) for c in "abcde"]
    hs = [_hs("H", "h", [{"club_id": c, "thi": False, "diem": ""} for c in "abcd"])]
    cfg = {"rules": {"max_choices": 3}}
    loi = _sach(clubs, hs, cfg)["loi"]
    assert _ma_loi({"loi": loi}) == ["so_nhap_qua_tran_nv"] and loi[0]["params"]["tran"] == 3
    assert not _sach(clubs, hs, {"rules": {"max_choices": 4}})["loi"]
    assert not _sach(clubs, hs, None)["loi"]            # mặc định 10


def test_doc_so_tran_thi_theo_luat_va_khong_gioi_han():
    clubs = [_clb(c, c.upper()) for c in "abcdefghijkl"]
    hs = [_hs("H", "h", [{"club_id": c, "thi": True, "diem": "5"} for c in "abcdefghijkl"])]
    cfg_vo_han = {"rules": {"max_choices": 20, "max_tests": None}}
    assert not _sach(clubs, hs, cfg_vo_han)["loi"]      # 12 chỗ thi, không giới hạn
    loi = _sach(clubs, hs, {"rules": {"max_choices": 20, "max_tests": 5}})["loi"]
    assert _ma_loi({"loi": loi}) == ["so_nhap_qua_tran_thi"] and loi[0]["params"]["tran"] == 5
    # thiếu khoá max_tests = mặc định 5, KHÁC với None
    assert _ma_loi({"loi": _sach(clubs, hs, {"rules": {"max_choices": 20}})["loi"]}) \
        == ["so_nhap_qua_tran_thi"]


# ------------------------------------------------------------------ qua API (workspace thật)

@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


def _api(goc, tmp_path, cfg):
    slug = ws.tao(goc, "Thử", cfg)
    xuat = tmp_path / "xuat"
    xuat.mkdir(exist_ok=True)
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=goc)


def _cau_hinh(max_choices=10, max_tests=5, **rest):
    return {"industry": "company", "labels": CONG_TY["labels"],
            "rules": {"max_choices": max_choices, "max_tests": max_tests, **rest}}


def test_api_tran_nguyen_vong_3_tu_choi_nguyen_vong_thu_tu(goc, tmp_path):
    api = _api(goc, tmp_path, _cau_hinh(max_choices=3))
    for c in "abcd":
        api.create_or_update_club(c, c.upper(), 5, 0, "")
    api.create_student_if_missing("S1", "An")
    ok = api.submit_preferences("S1", ["a", "b", "c"])
    assert ok["ok"], ok["errors"]
    res = api.submit_preferences("S1", ["a", "b", "c", "d"])
    assert res["ok"] is False
    loi = res["errors"][0]
    assert loi["code"] == "pref_too_many" and loi["params"]["tran"] == 3 and loi["params"]["count"] == 4
    # và CSV nguyện vọng: em có 4 NV bị bỏ cả buổi kèm cảnh báo mang đúng trần
    csv = "student_id,name,pref_1,pref_2,pref_3,pref_4\nS2,Bình,a,b,c,d\n"
    r = api.import_preferences_csv(csv)
    canh_bao = (r["data"]["warnings"] if r["ok"] else r["errors"])
    assert any(w["code"] == "csv_pref_too_many_skipped" and w["params"]["tran"] == 3
               for w in canh_bao), canh_bao


def test_api_check_data_integrity_dung_tran_cua_workspace(goc, tmp_path):
    api = _api(goc, tmp_path, _cau_hinh(max_choices=10))
    for c in "abcd":
        api.create_or_update_club(c, c.upper(), 5, 0, "")
    api.create_student_if_missing("S1", "An")
    assert api.submit_preferences("S1", list("abcd"))["ok"]
    assert api.check_data_integrity()["ok"]
    cfg = api.get_workspace_config()["data"]["config"]
    cfg["rules"]["max_choices"] = 3          # hạ trần SAU khi đã nhập 4 nguyện vọng
    assert api.update_workspace_config(cfg)["ok"]
    res = api.check_data_integrity()
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "pref_too_many" and res["errors"][0]["params"]["tran"] == 3


def test_api_khong_gioi_han_thi_nhan_12_cho(goc, tmp_path):
    api = _api(goc, tmp_path, _cau_hinh(max_choices=20, max_tests=None))
    ids = ["c%02d" % i for i in range(12)]
    for c in ids:
        api.create_or_update_club(c, c, 5, 0, "")
    api.create_student_if_missing("S1", "An")
    res = api.submit_test_selection("S1", ids)
    assert res["ok"], res["errors"]
    # nạp CSV chọn thi: 12 CLB, không bị cắt
    csv = "student_id,name," + ",".join("test_club_%d" % (i + 1) for i in range(12)) + "\n" \
        + "S2,Bình," + ",".join(ids) + "\n"
    r = api.import_test_selection_csv(csv)
    assert r["ok"], r["errors"]
    assert not [w for w in r["data"]["warnings"] if "tran" in w["params"]]
    with api._ket_noi_doc() as cur:
        n = cur.execute("SELECT COUNT(*) FROM club_test_selection WHERE student_id='S2'").fetchone()[0]
    assert n == 12
    # sức khoẻ dữ liệu: không báo "thi quá trần"
    codes = [w["code"] for w in api.get_data_health_report()["data"]["warnings"]]
    assert not any(c.startswith("health_thi_qua_tran") for c in codes)


def test_api_tran_thi_2_van_chan_va_canh_bao(goc, tmp_path):
    api = _api(goc, tmp_path, _cau_hinh(max_tests=2))
    for c in "abc":
        api.create_or_update_club(c, c.upper(), 5, 0, "")
    api.create_student_if_missing("S1", "An")
    res = api.submit_test_selection("S1", list("abc"))
    assert res["ok"] is False and res["errors"][0]["params"]["tran"] == 2
    assert api.submit_test_selection("S1", list("ab"))["ok"]
    cfg = api.get_workspace_config()["data"]["config"]
    cfg["rules"]["max_tests"] = 1            # hạ trần sau khi đã tick 2
    api.update_workspace_config(cfg)
    ma = [w for w in api.get_data_health_report()["data"]["warnings"]
          if w["code"] == "health_thi_qua_tran"]
    assert ma and ma[0]["params"]["tran"] == 1


def test_api_mac_dinh_truong_hoc_van_tran_10_va_5(api):
    for c in "abcdefghijk":
        api.create_or_update_club(c, c.upper(), 5, 0, "")
    api.create_student_if_missing("S1", "An")
    assert api.submit_preferences("S1", list("abcdefghij"))["ok"]
    r = api.submit_preferences("S1", list("abcdefghijk"))
    assert r["ok"] is False and r["errors"][0]["params"]["tran"] == 10
    assert api.submit_test_selection("S1", list("abcde"))["ok"]
    r = api.submit_test_selection("S1", list("abcdef"))
    assert r["ok"] is False and r["errors"][0]["params"]["tran"] == 5


def test_api_nhap_so_cu_vao_workspace_nhan_tuy_chinh(goc, tmp_path):
    api = _api(goc, tmp_path, _cau_hinh())
    cu = _bytes([_clb("a", "Cờ vua", 3), _clb("b", "Bóng đá", 4)],
                [_hs("H1", "An", [{"club_id": "a", "thi": True, "diem": "9"}])])
    res = api.import_so_nhap(_b64(cu))
    assert res["ok"], res["errors"]
    assert res["data"]["n_clubs_created"] == 2 and res["data"]["n_students_created"] == 1


def test_api_company_xuat_mau_roi_nap_lai(goc, tmp_path):
    """Một workspace công ty: tải sổ mẫu -> điền -> nạp."""
    api = _api(goc, tmp_path, _cau_hinh(max_choices=3))
    api.create_or_update_club("du_an_a", "Dự án A", 3, 0, "")
    res = api.tao_so_nhap_mau()
    assert res["ok"], res["errors"]
    wb = openpyxl.load_workbook(res["data"]["path"])
    assert wb.sheetnames == ["1. Dự án", "2. Nhân viên", "Hướng dẫn"]
    assert wb["1. Dự án"]["A2"].value == "Dự án A"       # CLB đang có điền sẵn
    hs = wb["2. Nhân viên"]
    # A13.7: sổ mẫu luôn có cột "Điểm quyết tâm" -> mỗi nhóm ba cột
    assert [c.value for c in hs[1]][3:7] == ["Nguyện vọng 1", None, None, "Nguyện vọng 2"]
    hs.append(["NV01", "Lan", None, "Dự án A", 8])
    b = io.BytesIO()
    wb.save(b)
    r = api.import_so_nhap(_b64(b.getvalue()))
    assert r["ok"], r["errors"]
    assert r["data"]["n_students_created"] == 1 and r["data"]["n_scores_written"] == 1
    # xuất dữ liệu đầu vào hiện tại cũng theo nhãn
    ra = api.export_du_lieu_dau_vao()
    assert ra["ok"], ra["errors"]
    assert openpyxl.load_workbook(ra["data"]["path"]).sheetnames[:2] == ["1. Dự án", "2. Nhân viên"]


def test_api_mau_truong_hoc_giong_het_truoc_day(api, tmp_path):
    api.create_or_update_club("a", "Cờ vua", 5, 1, "cs")
    res = api.tao_so_nhap_mau(str(tmp_path / "m.xlsx"))
    assert res["ok"]
    wb = openpyxl.load_workbook(res["data"]["path"])
    assert wb.sheetnames == ["1. CLB", "2. Học sinh", "Hướng dẫn"]
    assert [c.value for c in wb["1. CLB"][1]] == so_nhap.COT_CLB
    # Hai hàng tiêu đề: hàng 1 có 3 cột đầu + 15 ô gộp; hàng 2 có 15 cặp CLB/Điểm thi.
    assert len([c for c in wb["2. Học sinh"][1] if c.value]) == 3 + 15
    # A13.7: sổ mẫu có thêm cột "Điểm quyết tâm" -> ba cột mỗi nhóm.
    assert len([c for c in wb["2. Học sinh"][2] if c.value]) == 3 * 15


def test_api_diem_theo_nguoi_nap_va_tao_mau(goc, tmp_path):
    api = _api(goc, tmp_path, _cau_hinh(max_choices=3, score_scope="per_person"))
    api.create_or_update_club("a", "Dự án A", 3, 0, "")
    api.create_or_update_club("b", "Dự án B", 3, 0, "")
    mau = api.tao_so_nhap_mau()
    wb = openpyxl.load_workbook(mau["data"]["path"])
    hs = wb["2. Nhân viên"]
    assert [c.value for c in hs[1]] == ["Mã HS", "Họ tên", "Cấp bậc", "Điểm", "Nguyện vọng 1",
                                        "Nguyện vọng 2", "Nguyện vọng 3"]
    hs.append(["NV01", "Lan", None, 8.5, "Dự án A", "Dự án B"])
    b = io.BytesIO()
    wb.save(b)
    r = api.import_so_nhap(_b64(b.getvalue()))
    assert r["ok"], r["errors"]
    # Điểm lưu MỘT ô ở người (students.diem_ca_nhan); không chép sang club_scores.
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT diem_ca_nhan FROM students WHERE student_id='NV01'").fetchone()[0] == 8.5
        assert cur.execute("SELECT COUNT(*) FROM club_scores").fetchone()[0] == 0
    # …và khi nạp để xếp thì điểm mở rộng ra cả hai chỗ đã xếp nguyện vọng.
    tested = rp.load_from_sqlite(api.db_path, api._cfg_ws()["rules"])[2]
    assert tested == {"a": {"NV01": 8.5}, "b": {"NV01": 8.5}}


def test_api_error_so_nhap_dich_theo_nhan():
    from i18n_errors import format_message
    loi = format_message("so_nhap_khong_phai_so", {}, "vi", CONG_TY["labels"])
    assert '"1. Dự án" và "2. Nhân viên"' in loi
    en = format_message("so_nhap_khong_phai_so", {}, "en", CONG_TY["labels"])
    assert '"1. Dự án" and "2. Nhân viên"' in en        # tên sheet là chữ THẬT trên tệp: luôn vi
    mac_dinh = format_message("so_nhap_khong_phai_so", {}, "en")
    assert '"1. CLB" and "2. Học sinh"' in mac_dinh
