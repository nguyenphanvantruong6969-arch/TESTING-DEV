"""FA-M7 G0: nền dùng chung của ba phiên (A, B, C) — đóng gói `mau_forms_thi_clb` và đường dẫn thư mục `forms/`.

  * `kiosk.spec` liệt kê MỌI mô-đun của `mau_forms_thi_clb` mà `forms_dot.py` và ba `api_forms*.py` nhập, cộng mười
    mô-đun hợp đồng; mỗi mô-đun nhập được qua `nap_mau_forms()`; tên mô-đun không trùng mô-đun gốc;
  * đường dẫn của `forms_dot` đều nằm dưới thư mục chứa app.db và được tạo khi cần;
  * ba mixin có trong `PipelineAPI`.
Dữ liệu MÔ PHỎNG.
"""
import ast
import importlib
import os

import pytest

import forms_dot

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_MAU = os.path.join(GOC, "mau_forms_thi_clb")
TEP_API = ("api_forms.py", "api_forms_nap.py", "api_forms_bo.py", "forms_dot.py")
HOP_DONG = ("bieu_mau", "so_de_thi", "tao_mau_forms", "chuyen_forms_sang_phan_mem", "chuyen_phieu_clb",
            "phan_tich_cau_hoi", "danh_sach_chua_dang_ky", "doi_chieu_lists", "ghep_ket_qua_email",
            "tao_bo_dung_t4m")


def _mo_dun_mau():
    return {f[:-3] for f in os.listdir(THU_MUC_MAU) if f.endswith(".py")}


def _nhap_boi(ten_tep):
    with open(os.path.join(GOC, ten_tep), encoding="utf-8") as f:
        cay = ast.parse(f.read())
    ra = set()
    for n in ast.walk(cay):
        if isinstance(n, ast.Import):
            ra.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            ra.add(n.module.split(".")[0])
        elif isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "import_module" and n.args \
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            ra.add(n.args[0].value.split(".")[0])
    return ra


def _hidden_imports():
    with open(os.path.join(GOC, "kiosk.spec"), encoding="utf-8") as f:
        van_ban = f.read()
    return van_ban


def test_spec_liet_ke_moi_mo_dun_hop_dong():
    spec = _hidden_imports()
    for m in HOP_DONG:
        assert '"%s"' % m in spec, m
    assert "mau_forms_thi_clb" in spec.split("Analysis(")[1].split("pathex=")[1].split("]")[0]


def test_spec_liet_ke_moi_mo_dun_ma_ba_tep_api_nhap():
    spec = _hidden_imports()
    mau = _mo_dun_mau()
    for tep in TEP_API:
        for m in _nhap_boi(tep) & mau:
            assert '"%s"' % m in spec, (tep, m)


def test_spec_co_goi_bo_dung_t4m_va_de_thi_mac_dinh():
    spec = _hidden_imports()
    assert '"bo_dung_t4m"' in spec
    assert "de_thi.json" in spec


def test_khong_trung_ten_mo_dun_goc():
    goc = {f[:-3] for f in os.listdir(GOC) if f.endswith(".py")}
    assert not (goc & _mo_dun_mau())


@pytest.mark.parametrize("ten", HOP_DONG)
def test_nhap_duoc_qua_nap_mau_forms(ten):
    import sys
    forms_dot.nap_mau_forms()
    dem = sys.path.count(THU_MUC_MAU)
    assert dem >= 1
    forms_dot.nap_mau_forms()           # idempotent: gọi lại không chèn thêm
    assert sys.path.count(THU_MUC_MAU) == dem
    assert importlib.import_module(ten)


def test_duong_dan_forms_dot_nam_duoi_thu_muc_db(tmp_path):
    db = str(tmp_path / "ws" / "app.db")
    os.makedirs(os.path.dirname(db))
    goc = os.path.join(str(tmp_path), "ws", "forms")
    assert forms_dot.thu_muc_forms(db) == goc and os.path.isdir(goc)
    assert forms_dot.duong_de_dot(db) == os.path.join(goc, "de_thi.json")
    assert forms_dot.duong_so_nhap_clb_dot(db) == os.path.join(goc, "SO_NHAP_CLB_CLB.xlsx")
    assert forms_dot.thu_muc_nap(db) == os.path.join(goc, "nap") and os.path.isdir(forms_dot.thu_muc_nap(db))
    assert forms_dot.thu_muc_tai_len(db) == os.path.join(goc, "nap", "tai_len")
    assert os.path.isdir(forms_dot.thu_muc_tai_len(db))
    assert forms_dot.duong_email_ma_hs(db) == os.path.join(goc, "nap", "EMAIL_MA_HS.csv")
    assert forms_dot.thu_muc_bieu_mau(db) == os.path.join(goc, "bieu_mau") and os.path.isdir(
        forms_dot.thu_muc_bieu_mau(db))


def test_doc_de_dot_thieu_tep_nem_file_not_found(tmp_path):
    db = str(tmp_path / "app.db")
    with pytest.raises(FileNotFoundError):
        forms_dot.doc_de_dot(db)


def test_doc_de_dot_doc_dung_tep(tmp_path):
    import shutil
    db = str(tmp_path / "app.db")
    shutil.copy(os.path.join(THU_MUC_MAU, "de_thi.json"), forms_dot.duong_de_dot(db))
    forms_dot.nap_mau_forms()
    import bieu_mau
    assert forms_dot.doc_de_dot(db) == bieu_mau.doc_de_thi()


def test_ba_mixin_co_trong_pipeline_api(api):
    from api_forms import FormsMixin
    from api_forms_bo import FormsBoMixin
    from api_forms_nap import FormsNapMixin
    for m in (FormsMixin, FormsNapMixin, FormsBoMixin):
        assert isinstance(api, m)
