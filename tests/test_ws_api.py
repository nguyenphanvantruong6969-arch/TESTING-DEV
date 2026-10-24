"""Hàm API workspace (api_workspace.py): hợp đồng {ok, data, errors}, chuyển workspace, an toàn."""

import base64
import copy
import os
import sqlite3

import pytest

import cau_hinh_ws as ch
import workspace as ws
from api import PipelineAPI
from i18n_errors import MESSAGES

# Mọi hàm API workspace "quản lý" (không tính get_workspace_state — phép thử chế độ).
HAM_QUAN_LY = {
    "list_workspaces": (),
    "list_templates": (),
    "open_workspace": ("truong-hoc",),
    "create_workspace": ("X", None),
    "rename_workspace": ("truong-hoc", "Y"),
    "delete_workspace": ("truong-hoc", "XOA"),
    "duplicate_workspace": ("truong-hoc", "Z", True),
    "save_as_template": ("truong-hoc", "M"),
    "export_workspace": ("truong-hoc",),
    "import_workspace": ("", "x.zip"),
    "get_workspace_config": (),
    "update_workspace_config": ({},),
}


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


@pytest.fixture
def api(goc, tmp_path):
    slug = ws.tao(goc, "Trường học", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat),
                       thu_muc_goc_ws=goc)


def _ma_loi(res):
    assert res["ok"] is False and res["data"] is None
    assert len(res["errors"]) == 1 and set(res["errors"][0]) == {"code", "params"}
    ma = res["errors"][0]["code"]
    # mã nào cũng phải dịch được cả hai ngôn ngữ
    assert MESSAGES[ma]["vi"] and MESSAGES[ma]["en"]
    return ma


def _n_clb(api):
    return api.get_dashboard_status()["data"]["n_clubs"]


# ------------------------------------------------------------ chế độ tắt (argv)

def test_che_do_dung_duong_dan_csdl_tat_moi_ham_workspace(tmp_path):
    api = PipelineAPI(str(tmp_path / "rieng.db"))
    for ten, tham_so in HAM_QUAN_LY.items():
        res = getattr(api, ten)(*tham_so)
        assert _ma_loi(res) == "ws_tat_che_do", ten
    # không hàm nào kịp làm gì: không thư mục workspaces, không đổi db_path
    assert not os.path.exists(os.path.join(str(tmp_path), "workspaces"))
    assert api.db_path == str(tmp_path / "rieng.db")


def test_trang_thai_che_do_tat_van_tra_nhan_mac_dinh(tmp_path):
    api = PipelineAPI(str(tmp_path / "rieng.db"))
    d = api.get_workspace_state()["data"]
    assert d["enabled"] is False and d["chon"] is True and d["slug"] is None
    assert d["config"] == ch.MAC_DINH_TRUONG_HOC


# ------------------------------------------------------------ trạng thái / danh sách

def test_trang_thai_khi_dang_mo_mot_workspace(api):
    d = api.get_workspace_state()["data"]
    assert (d["enabled"], d["chon"], d["slug"], d["name"]) == (True, True, "truong-hoc", "Trường học")
    assert d["config"]["rules"] == ch.MAC_DINH_TRUONG_HOC["rules"]


def test_chua_chon_thi_trang_thai_va_danh_sach_noi_dung(goc):
    a = ws.tao(goc, "A", None)
    ws.tao(goc, "B", None)
    api = PipelineAPI(ws.duong_dan_db(goc, a), thu_muc_goc_ws=goc, ws_da_chon=False)
    assert api.get_workspace_state()["data"]["chon"] is False
    d = api.list_workspaces()["data"]
    assert d["dang_mo"] is None and not any(w["dang_mo"] for w in d["workspaces"])
    assert api.open_workspace("b")["ok"]
    assert api.get_workspace_state()["data"]["chon"] is True
    assert api.list_workspaces()["data"]["dang_mo"] == "b"


def test_list_workspaces(api, goc):
    ws.tao(goc, "Công ty ABC", {"industry": "company"})
    d = api.list_workspaces()["data"]
    assert d["dang_mo"] == "truong-hoc"
    ds = {w["slug"]: w for w in d["workspaces"]}
    assert set(ds) == {"truong-hoc", "cong-ty-abc"}
    assert ds["truong-hoc"]["dang_mo"] is True and ds["cong-ty-abc"]["dang_mo"] is False
    assert (ds["cong-ty-abc"]["name"], ds["cong-ty-abc"]["industry"]) == ("Công ty ABC", "company")
    assert "path" not in ds["cong-ty-abc"]  # giao diện không cần đường dẫn máy


def test_list_templates_co_mau_truong_hoc_dung_san(api):
    mau = api.list_templates()["data"]["templates"]
    assert mau[0]["builtin"] is True and mau[0]["name"] == "Trường học"


# ------------------------------------------------------------ mở / chuyển

def test_open_workspace_doi_csdl_va_tra_cau_hinh(api, goc):
    api.create_or_update_club("A", "CLB A", 3, 0, None)
    assert _n_clb(api) == 1
    cfg = {"industry": "company", "labels": {"person": {"vi": "Nhân viên", "en": "Employee"}}}
    slug = api.create_workspace("Công ty", cfg)["data"]["slug"]

    res = api.open_workspace(slug)

    assert res["ok"] and res["data"]["name"] == "Công ty"
    assert res["data"]["config"]["labels"]["person"] == {"vi": "Nhân viên", "en": "Employee"}
    assert api.db_path == ws.duong_dan_db(goc, "cong-ty")
    assert _n_clb(api) == 0                      # dữ liệu của workspace CŨ không lọt sang
    api.create_or_update_club("B", "CLB B", 2, 0, None)
    assert api.open_workspace("truong-hoc")["ok"]
    assert _n_clb(api) == 1                      # và ghi ở workspace mới không lọt về
    with sqlite3.connect(ws.duong_dan_db(goc, "truong-hoc")) as c:
        assert [r[0] for r in c.execute("SELECT club_id FROM clubs")] == ["A"]


def test_open_workspace_xoa_bo_nho_dem_xuat(api, goc):
    api._bo_nho_xuat = {"x": 1}
    slug = api.create_workspace("B")["data"]["slug"]
    api.open_workspace(slug)
    assert api._bo_nho_xuat is None


def test_open_workspace_chay_init_db_cho_csdl_cu(api, goc):
    cu = os.path.join(goc, "workspaces", "cu")
    os.makedirs(cu)
    sqlite3.connect(os.path.join(cu, "app.db")).close()   # tệp rỗng, chưa có bảng nào
    assert api.open_workspace("cu")["ok"]
    assert api.get_dashboard_status()["ok"]


@pytest.mark.parametrize("slug", ["khong-co", "../x", "", "_trash", None])
def test_slug_khong_ton_tai_hoac_xau(api, slug):
    for goi in (lambda: api.open_workspace(slug), lambda: api.rename_workspace(slug, "N"),
                lambda: api.duplicate_workspace(slug, "N"), lambda: api.save_as_template(slug, "N"),
                lambda: api.export_workspace(slug), lambda: api.delete_workspace(slug, "XOA")):
        assert _ma_loi(goi()) == "ws_khong_co"
    assert api.db_path.endswith(os.path.join("truong-hoc", "app.db"))


# ------------------------------------------------------------ tạo / đổi tên / nhân bản

def test_create_workspace(api, goc):
    cfg = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    cfg["rules"].update(max_choices=4, max_tests=None, priority="tier", tier_mode="strict",
                        tiers=["Cao", "Thấp"])
    res = api.create_workspace("Sự kiện 2026", cfg)
    assert res["ok"] and res["data"] == {"slug": "su-kien-2026"}
    doc = ch.doc_cau_hinh(ws.duong_dan_db(goc, "su-kien-2026"))
    assert doc["name"] == "Sự kiện 2026" and doc["rules"] == cfg["rules"]
    assert api.db_path.endswith(os.path.join("truong-hoc", "app.db"))   # tạo chưa phải mở


def test_create_workspace_trung_ten_them_hau_to(api):
    assert api.create_workspace("Trường học")["data"]["slug"] == "truong-hoc-2"


@pytest.mark.parametrize("ten, cfg", [
    ("", None), ("  ", None),
    ("X", {"rules": {"max_choices": 0}}),
    ("X", {"labels": {"person": {"vi": ""}}}),
    ("X", {"rules": {"priority": "bậy"}}),
    ("X", "khong phai dict"),
])
def test_create_workspace_du_lieu_sai(api, goc, ten, cfg):
    res = api.create_workspace(ten, cfg)
    assert _ma_loi(res) == "ws_du_lieu_sai"
    assert res["errors"][0]["params"]["detail"]          # lý do nằm ở chi tiết kỹ thuật
    assert [w["slug"] for w in ws.danh_sach(goc)] == ["truong-hoc"]


def test_rename_workspace(api, goc):
    res = api.rename_workspace("truong-hoc", "  Tên mới ")
    assert res["ok"] and res["data"] == {"slug": "truong-hoc", "name": "Tên mới"}
    assert api.get_workspace_state()["data"]["name"] == "Tên mới"
    assert os.path.isdir(os.path.join(goc, "workspaces", "truong-hoc"))   # thư mục giữ slug
    assert _ma_loi(api.rename_workspace("truong-hoc", " ")) == "ws_du_lieu_sai"


def test_duplicate_workspace_kem_va_khong_kem_du_lieu(api, goc):
    api.create_or_update_club("A", "CLB A", 3, 0, None)
    kem = api.duplicate_workspace("truong-hoc", "Bản có dữ liệu", True)
    khong = api.duplicate_workspace("truong-hoc", "Bản trống", False)
    assert kem["data"]["slug"] == "ban-co-du-lieu" and khong["data"]["slug"] == "ban-trong"
    api.open_workspace("ban-co-du-lieu")
    assert _n_clb(api) == 1
    api.open_workspace("ban-trong")
    assert _n_clb(api) == 0
    assert api.get_workspace_state()["data"]["name"] == "Bản trống"


# ------------------------------------------------------------ xoá

def test_delete_can_chuoi_xac_nhan_xoa(api, goc):
    slug = api.create_workspace("B")["data"]["slug"]
    for sai in ("", "xoa", "XOA ", None, "DELETE"):
        assert _ma_loi(api.delete_workspace(slug, sai)) == "reset_confirmation_mismatch"
    assert os.path.isdir(os.path.join(goc, "workspaces", slug))      # chưa mất gì
    assert not os.path.exists(os.path.join(goc, "workspaces", "_trash"))


def test_delete_dua_vao_thung_rac_kem_ban_sao_luu(api, goc):
    slug = api.create_workspace("B")["data"]["slug"]
    res = api.delete_workspace(slug, "XOA")
    assert res["ok"] and res["data"]["slug"] == slug
    thung = res["data"]["thung_rac"]
    assert os.path.dirname(thung) == os.path.join(goc, "workspaces", "_trash")
    assert any(t.startswith("app.db.bak-") for t in os.listdir(thung))
    assert slug not in {w["slug"] for w in api.list_workspaces()["data"]["workspaces"]}


def test_delete_khong_xoa_duoc_workspace_dang_mo(api, goc):
    assert _ma_loi(api.delete_workspace("truong-hoc", "XOA")) == "ws_khong_xoa_dang_mo"
    assert os.path.isfile(ws.duong_dan_db(goc, "truong-hoc"))


def test_delete_workspace_vua_roi_di_thi_xoa_duoc(api):
    slug = api.create_workspace("B")["data"]["slug"]
    api.open_workspace(slug)
    api.open_workspace("truong-hoc")
    assert api.delete_workspace(slug, "XOA")["ok"]


# ------------------------------------------------------------ mẫu, zip

def test_save_as_template_roi_dung_de_tao(api, goc):
    cfg = {"industry": "company", "rules": {"max_choices": 3}}
    slug = api.create_workspace("Công ty", cfg)["data"]["slug"]
    res = api.save_as_template(slug, "Mẫu công ty")
    assert res["ok"] and os.path.isfile(res["data"]["path"])
    mau = [m for m in api.list_templates()["data"]["templates"] if not m["builtin"]]
    assert [(m["name"], m["config"]["rules"]["max_choices"]) for m in mau] == [("Mẫu công ty", 3)]
    moi = api.create_workspace("Chi nhánh", mau[0]["config"])["data"]["slug"]
    assert ch.doc_cau_hinh(ws.duong_dan_db(goc, moi))["rules"]["max_choices"] == 3
    assert _ma_loi(api.save_as_template(slug, " ")) == "ws_du_lieu_sai"


def test_export_vao_thu_muc_xuat_khong_de_len(api, tmp_path):
    a = api.export_workspace("truong-hoc")
    b = api.export_workspace("truong-hoc")
    assert a["ok"] and b["ok"] and a["data"]["path"] != b["data"]["path"]
    assert os.path.dirname(a["data"]["path"]) == str(tmp_path / "xuat") == a["data"]["dir"]
    assert os.path.getsize(a["data"]["path"]) > 0


def test_export_roi_import_base64_khu_hoi(api, goc):
    api.create_or_update_club("A", "CLB A", 3, 0, None)
    api.rename_workspace("truong-hoc", "Sổ gốc")
    duong = api.export_workspace("truong-hoc")["data"]["path"]
    b64 = base64.b64encode(open(duong, "rb").read()).decode()

    res = api.import_workspace(b64, "so-goc.zip")

    assert res["ok"] and res["data"]["slug"] == "so-goc"   # slug đặt theo TÊN, không theo tên tệp
    moi = res["data"]["slug"]
    assert res["data"]["name"] == "Sổ gốc"
    api.open_workspace(moi)
    assert _n_clb(api) == 1


def test_import_loi(api, goc):
    assert _ma_loi(api.import_workspace("không phải base64!!", "a.zip")) == "ws_du_lieu_sai"
    gia = base64.b64encode(b"day khong phai zip").decode()
    assert _ma_loi(api.import_workspace(gia, "a.zip")) == "ws_du_lieu_sai"
    assert [w["slug"] for w in ws.danh_sach(goc)] == ["truong-hoc"]


def test_import_tu_choi_zip_slip(api, goc, tmp_path):
    import zipfile
    z = str(tmp_path / "xau.zip")
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("app.db", b"x")
        f.writestr("../evil.txt", b"x")
    b64 = base64.b64encode(open(z, "rb").read()).decode()
    assert _ma_loi(api.import_workspace(b64, "xau.zip")) == "ws_du_lieu_sai"
    assert not os.path.exists(os.path.join(goc, "evil.txt"))
    assert not os.path.exists(os.path.join(goc, "workspaces", "evil.txt"))


def test_import_ten_tep_co_duong_dan_khong_thoat_ra_ngoai(api):
    # ten_tep chỉ dùng đặt tên dự phòng; đường dẫn trong đó bị cắt bỏ
    duong = api.export_workspace("truong-hoc")["data"]["path"]
    b64 = base64.b64encode(open(duong, "rb").read()).decode()
    assert api.import_workspace(b64, "../../etc/x.zip")["ok"]


# ------------------------------------------------------------ cấu hình

def test_get_va_update_workspace_config(api, goc):
    d = api.get_workspace_config()["data"]
    assert d["slug"] == "truong-hoc" and d["config"]["name"] == "Trường học"

    cfg = d["config"]
    cfg["rules"]["max_choices"] = 6
    cfg["labels"]["slot"] = {"vi": "Dự án", "en": ""}
    res = api.update_workspace_config(cfg)

    assert res["ok"]
    assert res["data"]["config"]["labels"]["slot"] == {"vi": "Dự án", "en": "Dự án"}
    nhan = api.get_workspace_state()["data"]["config"]
    assert nhan["rules"]["max_choices"] == 6 and nhan["labels"]["slot"]["vi"] == "Dự án"


def test_update_config_cho_workspace_khac_khong_doi_workspace_dang_mo(api, goc):
    slug = api.create_workspace("B")["data"]["slug"]
    cfg = api.get_workspace_config(slug)["data"]["config"]
    cfg["rules"]["max_choices"] = 2
    api.update_workspace_config(cfg, slug)
    assert api.get_workspace_config(slug)["data"]["config"]["rules"]["max_choices"] == 2
    assert api.get_workspace_config()["data"]["config"]["rules"]["max_choices"] == 10


def test_update_config_sai_khong_ghi(api):
    cfg = api.get_workspace_config()["data"]["config"]
    cfg["rules"]["max_choices"] = 99
    assert _ma_loi(api.update_workspace_config(cfg)) == "ws_du_lieu_sai"
    assert api.get_workspace_config()["data"]["config"]["rules"]["max_choices"] == 10


def test_thuoc_tinh_workspace_cua_doi_tuong_deu_co_gach_duoi(api):
    # pywebview đệ quy vào thuộc tính CÔNG KHAI không gọi được (xem test_do_api).
    ws_attr = [k for k in vars(api) if "ws" in k]
    assert ws_attr and all(k.startswith("_") for k in ws_attr), ws_attr
