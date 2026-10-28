# -*- coding: utf-8 -*-
"""Canh skill `soat-ma`: bảy mục tự kiểm của `kiem_nhanh.py`, mỗi mục một ca ĐẠT và các ca KHÔNG ĐẠT dựng
trong thư mục tạm (không đụng kho thật), cộng khung skill (SKILL.md, dòng trong CLAUDE.md).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test."""

import os
import shutil
import subprocess
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_SKILL = os.path.join(GOC, ".claude", "skills", "soat-ma")
SCRIPT = os.path.join(THU_MUC_SKILL, "scripts", "kiem_nhanh.py")
sys.path.insert(0, os.path.join(THU_MUC_SKILL, "scripts"))

import kiem_nhanh as kn  # noqa: E402

I18N_JS = '''(function (global) {
  const UI_STRINGS = {
    vi: {
      ten_a: "Xin chào",
      ten_b: "Lưu lại",
    },
    en: {
      ten_a: "Hello",
      ten_b: "Save",
    },
  };
})(window);
'''
I18N_LOI = 'MESSAGES = {"loi_a": {"vi": "Lỗi một", "en": "Error one"}}\n'
INDEX_HTML = ('<html><body><h1 data-i18n="ten_a">Tiêu đề</h1><p>Chữ tĩnh</p>'
              '<input placeholder="Tìm"></body></html>')
JS_DUNG = 'showToast("x", "error", [{ code: "loi_a", params: {} }]);\n'


def ghi(goc, rel, noi_dung):
    duong = os.path.join(str(goc), *rel.split("/"))
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(noi_dung)
    return duong


@pytest.fixture
def kho(tmp_path):
    """Một kho nhỏ HỢP LỆ: i18n.js, i18n_errors.py, i18n_loi.js (sinh thật), index.html, js/x.js."""
    ghi(tmp_path, "i18n.js", I18N_JS)
    ghi(tmp_path, "i18n_errors.py", I18N_LOI)
    ghi(tmp_path, "index.html", INDEX_HTML)
    ghi(tmp_path, "js/x.js", JS_DUNG)
    shutil.copy(os.path.join(GOC, "tao_i18n_js.py"), str(tmp_path / "tao_i18n_js.py"))
    subprocess.run([sys.executable, "tao_i18n_js.py"], cwd=str(tmp_path), check=True,
                   capture_output=True)
    return tmp_path


def dat(ket_qua):
    return ket_qua[0]


# ------------------------------------------------------------------ ruff

def _co_ruff():
    r = subprocess.run([sys.executable, "-m", "ruff", "--version"], capture_output=True)
    return r.returncode == 0


@pytest.mark.skipif(not _co_ruff(), reason="chưa cài ruff (requirements-dev.txt)")
def test_ruff_dat_va_khong_dat(tmp_path):
    ghi(tmp_path, "ok.py", "x = 1\nprint(x)\n")
    assert dat(kn.kiem_ruff(str(tmp_path)))
    ghi(tmp_path, "hong.py", "print(ten_chua_dinh_nghia)\n")
    ok, chi_tiet = kn.kiem_ruff(str(tmp_path))
    assert not ok and any("F821" in d or "ten_chua_dinh_nghia" in d for d in chi_tiet)


# ------------------------------------------------------------------ chu_cam

def test_chu_cam_dat(kho):
    assert dat(kn.kiem_chu_cam(str(kho))), kn.kiem_chu_cam(str(kho))[1]


@pytest.mark.parametrize("sua, mong_doi", [
    (("i18n.js", "Xin chào", "Chào bạn"), "bạn"),
    (("i18n.js", "Lưu lại", "Các em lưu lại"), "em"),
    (("i18n.js", "Hello", "Save your work"), "your"),
    (("i18n.js", "Hello", "Preference points (Wharton)"), "Wharton"),
    (("i18n_errors.py", "Lỗi một", "Lỗi rồi, bạn thử lại nhé"), "bạn"),
    (("i18n_errors.py", "Error one", "You can try again"), "You"),
    (("index.html", "Chữ tĩnh", "Chào bạn"), "bạn"),
    (("index.html", 'placeholder="Tìm"', 'placeholder="Điểm Wharton"'), "Wharton"),
])
def test_chu_cam_khong_dat(kho, sua, mong_doi):
    tep, cu, moi = sua
    duong = kho / tep
    duong.write_text(duong.read_text(encoding="utf-8").replace(cu, moi), encoding="utf-8")
    ok, chi_tiet = kn.kiem_chu_cam(str(kho))
    assert not ok
    assert any(mong_doi in d for d in chi_tiet), chi_tiet


def test_chu_cam_chu_du_phong_cua_data_i18n_khong_bi_soat(kho):
    # Chữ trong phần tử có data-i18n chỉ là dự phòng: bị thay bằng khoá i18n.js lúc chạy.
    duong = kho / "index.html"
    duong.write_text(duong.read_text(encoding="utf-8").replace(
        'data-i18n="ten_a">Tiêu đề', 'data-i18n="ten_a">Chào bạn'), encoding="utf-8")
    assert dat(kn.kiem_chu_cam(str(kho)))


# ------------------------------------------------------------------ ma_loi_js

def test_ma_loi_js_dat(kho):
    assert dat(kn.kiem_ma_loi_js(str(kho)))


def test_ma_loi_js_ma_trung_khoa_ui_van_dat(kho):
    ghi(kho, "js/y.js", 'x({ code: "ten_a", params: {} });\n')
    assert dat(kn.kiem_ma_loi_js(str(kho)))


@pytest.mark.parametrize("tep, dong", [
    ("js/x.js", 'a({ code: "ma_khong_co", params: {} });\n'),
    ("js/y.js", 'if (e.code === "ma_khac_nua") {}\n'),
    ("index.html", '<script>b({code: "ma_trong_html"})</script>\n'),
])
def test_ma_loi_js_khong_dat(kho, tep, dong):
    duong = kho / tep
    cu = duong.read_text(encoding="utf-8") if duong.exists() else ""
    duong.parent.mkdir(exist_ok=True)
    duong.write_text(cu + dong, encoding="utf-8")
    ok, chi_tiet = kn.kiem_ma_loi_js(str(kho))
    assert not ok and any("không có trong i18n_errors.py" in d for d in chi_tiet)


# ------------------------------------------------------------------ i18n_loi_khop

def test_i18n_loi_khop_dat(kho):
    assert dat(kn.kiem_i18n_loi_khop(str(kho)))


def test_i18n_loi_khop_khong_dat_khi_them_ma_ma_chua_sinh_lai(kho):
    (kho / "i18n_errors.py").write_text(
        'MESSAGES = {"loi_a": {"vi": "Lỗi một", "en": "Error one"},\n'
        '            "loi_b": {"vi": "Lỗi hai", "en": "Error two"}}\n', encoding="utf-8")
    ok, chi_tiet = kn.kiem_i18n_loi_khop(str(kho))
    assert not ok and "tao_i18n_js.py" in chi_tiet[0]


def test_i18n_loi_khop_khong_dat_khi_sua_tay_tep_sinh(kho):
    (kho / "i18n_loi.js").write_text(
        (kho / "i18n_loi.js").read_text(encoding="utf-8") + "// sửa tay\n", encoding="utf-8")
    assert not dat(kn.kiem_i18n_loi_khop(str(kho)))


def test_i18n_loi_khop_khong_dat_khi_thieu_tep(kho):
    os.remove(str(kho / "i18n_loi.js"))
    ok, chi_tiet = kn.kiem_i18n_loi_khop(str(kho))
    assert not ok and "thiếu" in chi_tiet[0]


# ------------------------------------------------------------------ i18n_khoa

def test_i18n_khoa_dat(kho):
    assert dat(kn.kiem_i18n_khoa(str(kho)))


@pytest.mark.parametrize("cu, moi, mong_doi", [
    ('      ten_b: "Save",\n', "", "thiếu tiếng Anh"),          # bỏ bản EN của một khoá
    ('      ten_b: "Lưu lại",\n', "", "thiếu tiếng Việt"),      # bỏ bản VI của một khoá
    ('ten_a: "Hello"', 'ten_a: ""', "rỗng"),
])
def test_i18n_khoa_khong_dat(kho, cu, moi, mong_doi):
    duong = kho / "i18n.js"
    van = duong.read_text(encoding="utf-8")
    assert cu in van
    duong.write_text(van.replace(cu, moi), encoding="utf-8")
    ok, chi_tiet = kn.kiem_i18n_khoa(str(kho))
    assert not ok and any(mong_doi in d for d in chi_tiet), chi_tiet


# ------------------------------------------------------------------ khong_sua_nhat_ky

def test_khong_sua_nhat_ky_dat(tmp_path):
    ghi(tmp_path, "a.py", '''
def f(cur):
    cur.execute("SELECT * FROM run_history")
    cur.execute("INSERT INTO wharton_nhat_ky (luc) VALUES (?)", ("x",))
    cur.execute("DELETE FROM match_results")
    cur.execute("UPDATE run_meta SET x = 1")

_RESET_BANG = {"hoc_sinh": ["wharton_bids", "match_results", "students"]}
''')
    assert dat(kn.kiem_khong_sua_nhat_ky(str(tmp_path)))


@pytest.mark.parametrize("ma_py, mong_doi", [
    ('cur.execute("DELETE FROM run_history")', "DELETE FROM"),
    ('cur.execute("delete   from wharton_nhat_ky where id = 1")', "DELETE FROM"),
    ('cur.execute("UPDATE wharton_nhat_ky SET nguoi = ? ", ("x",))', "UPDATE"),
    ('cur.execute("""DELETE\n        FROM run_history""")', "DELETE FROM"),
    ('cur.execute("DROP TABLE IF EXISTS run_history")', "DROP TABLE"),
    ('_RESET_BANG = {"tat_ca": ["wharton_bids", "run_history", "students"]}', "run_history"),
    ('_BANG_RANG_BUOC = ("students", "wharton_nhat_ky")', "wharton_nhat_ky"),
])
def test_khong_sua_nhat_ky_khong_dat(tmp_path, ma_py, mong_doi):
    ghi(tmp_path, "b.py", "def g(cur):\n    pass\n\n" + ma_py + "\n")
    ok, chi_tiet = kn.kiem_khong_sua_nhat_ky(str(tmp_path))
    assert not ok and any(mong_doi.lower() in d.lower() for d in chi_tiet), chi_tiet
    assert "b.py:" in chi_tiet[0]


def test_khong_sua_nhat_ky_khong_tinh_tests_va_docs(tmp_path):
    ghi(tmp_path, "tests/t.py", 'x = "DELETE FROM run_history"\n')
    ghi(tmp_path, "docs/d.py", 'x = "UPDATE wharton_nhat_ky"\n')
    assert dat(kn.kiem_khong_sua_nhat_ky(str(tmp_path)))


# ------------------------------------------------------------------ trung_khit

@pytest.fixture(scope="module")
def hai_ban(tmp_path_factory):
    """Hai bản sao nhỏ của kho (mã .py + dữ liệu của hai bộ đầu), dùng chung cho các ca trùng khít."""
    goc = tmp_path_factory.mktemp("trung_khit")
    a, b = goc / "a", goc / "b"
    for ban in (a, b):
        os.makedirs(str(ban / "du_lieu_test"))
        for t in os.listdir(GOC):
            if t.endswith(".py"):
                shutil.copy(os.path.join(GOC, t), str(ban / t))
        shutil.copy(os.path.join(GOC, "du_lieu_test", "do_anh_huong_seed.py"),
                    str(ban / "du_lieu_test" / "do_anh_huong_seed.py"))
        for thu_muc in ("vi_du_huong_dan", "bo_sach"):
            shutil.copytree(os.path.join(GOC, "du_lieu_test", thu_muc),
                            str(ban / "du_lieu_test" / thu_muc),
                            ignore=shutil.ignore_patterns("*.xlsx", "*.md", "*.py", "__pycache__"))
    return a, b


def test_trung_khit_dat_khi_hai_ban_giong_nhau(hai_ban):
    a, b = hai_ban
    ok, chi_tiet = kn.kiem_trung_khit(str(a), str(b), seeds=(1, 7), so_bo=2)
    assert ok, chi_tiet
    assert "4 ca" in chi_tiet[0]


def test_trung_khit_khong_dat_khi_doi_thu_tu_uu_tien(hai_ban):
    a, b = hai_ban
    tep = b / "rbda_priority_pipeline.py"
    van = tep.read_text(encoding="utf-8")
    cu = "key=lambda sid: (-tested_scores_for_club[sid], stb_lottery[sid], sid),"
    assert van.count(cu) == 1
    tep.write_text(van.replace(cu, "key=lambda sid: (tested_scores_for_club[sid], stb_lottery[sid], sid),"),
                   encoding="utf-8")
    try:
        ok, chi_tiet = kn.kiem_trung_khit(str(a), str(b), seeds=(1, 7), so_bo=2)
    finally:
        tep.write_text(van, encoding="utf-8")
    assert not ok and any("lệch" in d for d in chi_tiet), chi_tiet


def test_trung_khit_khong_dat_khi_ban_khong_chay_duoc(tmp_path, hai_ban):
    a, _ = hai_ban
    ok, chi_tiet = kn.kiem_trung_khit(str(a), str(tmp_path), seeds=(1,), so_bo=1)
    assert not ok and "lỗi" in chi_tiet[0]


# ------------------------------------------------------------------ nhánh so sánh (git)

def _git(thu_muc, *lenh):
    subprocess.run(["git", "-C", str(thu_muc), *lenh], check=True, capture_output=True)


def test_giai_nen_nhanh_dat_va_khong_dat(tmp_path):
    kho_git = tmp_path / "kho"
    kho_git.mkdir()
    _git(kho_git, "init", "-q", "-b", "main")
    _git(kho_git, "config", "user.email", "a@b.c")
    _git(kho_git, "config", "user.name", "a")
    (kho_git / "x.txt").write_text("1", encoding="utf-8")
    _git(kho_git, "add", ".")
    _git(kho_git, "commit", "-q", "-m", "c")
    dich = tmp_path / "ra"
    dich.mkdir()
    assert kn._giai_nen_nhanh(str(kho_git), "main", str(dich)) is None
    assert (dich / "x.txt").read_text(encoding="utf-8") == "1"
    loi = kn._giai_nen_nhanh(str(kho_git), "nhanh_khong_ton_tai", str(tmp_path / "ra2"))
    assert loi and "nhanh_khong_ton_tai" in loi


def test_chay_trung_khit_thieu_nhanh_so_sanh_la_khong_dat_khong_phai_bo_qua(tmp_path):
    kho_git = tmp_path / "kho"
    kho_git.mkdir()
    _git(kho_git, "init", "-q", "-b", "main")
    ra = []
    ket_qua = kn.chay(str(kho_git), co_so="khong_co", chi={"trung_khit"}, in_ra=ra.append)
    assert not ket_qua["trung_khit"][0]
    assert ra[0].startswith("KHÔNG ĐẠT") and "khong_co" in "".join(ra)


# ------------------------------------------------------------------ chạy cả lệnh

def test_chay_in_dat_khong_dat_va_ma_thoat(kho, capsys):
    ma = kn.main(["--goc", str(kho), "--chi", "chu_cam,ma_loi_js,i18n_loi_khop,i18n_khoa,khong_sua_nhat_ky"])
    ra = capsys.readouterr().out
    assert ma == 0 and ra.count("ĐẠT") >= 6 and "KHÔNG ĐẠT" not in ra.split("-" * 60)[0]
    assert "5/5 mục ĐẠT" in ra
    (kho / "js" / "y.js").write_text('a({ code: "khong_co" });\n', encoding="utf-8")
    ma = kn.main(["--goc", str(kho), "--chi", "ma_loi_js,i18n_khoa"])
    ra = capsys.readouterr().out
    assert ma == 1 and "KHÔNG ĐẠT  ma_loi_js" in ra and "ĐẠT        i18n_khoa" in ra
    assert "KHÔNG ĐẠT: ma_loi_js" in ra


def test_mot_muc_hong_khong_che_muc_khac(tmp_path):
    # i18n.js không có: mục đọc nó phải báo KHÔNG ĐẠT kèm lý do, mục khác vẫn chạy.
    ghi(tmp_path, "a.py", "x = 1\n")
    ket_qua = kn.chay(str(tmp_path), chi={"i18n_khoa", "khong_sua_nhat_ky"}, in_ra=lambda _: None)
    assert not ket_qua["i18n_khoa"][0] and "không chạy được" in ket_qua["i18n_khoa"][1][0]
    assert ket_qua["khong_sua_nhat_ky"][0]


def test_muc_la_bi_tu_choi():
    with pytest.raises(SystemExit) as e:
        kn.main(["--chi", "muc_khong_co"])
    assert e.value.code == 2


def test_chay_script_that_tren_kho_that_cac_muc_nhanh():
    """Kho thật phải qua các mục nhanh: ai thêm xưng hô cấm, mã lỗi lạ, khoá i18n lệch, hay xoá nhật ký
    thì test này đỏ trước khi push."""
    r = subprocess.run(
        [sys.executable, "-I", SCRIPT, "--chi", "chu_cam,ma_loi_js,i18n_loi_khop,i18n_khoa,khong_sua_nhat_ky"],
        cwd=os.path.dirname(GOC), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "5/5 mục ĐẠT" in r.stdout


# ------------------------------------------------------------------ khung skill

def test_skill_md_co_khung_dung():
    noi_dung = open(os.path.join(THU_MUC_SKILL, "SKILL.md"), encoding="utf-8").read()
    dau = noi_dung.split("---")[1]
    assert "name: soat-ma" in dau
    mo_ta = [d for d in dau.splitlines() if d.startswith("description:")][0]
    for tu in ("soát mã", "kiểm trước khi push", "review", "code review", "tự kiểm"):
        assert tu in mo_ta
    for muc in ("KHÔNG dùng subagent", "Chỉ báo cáo", "main...HEAD", "Điểm tốt", "Kết luận tầng",
                "Bảo mật", "Hiệu năng", "Đúng đắn", "Bảo trì"):
        assert muc in noi_dung
    for ma, _ in kn.MUC:                 # mọi mục tự kiểm đều được mô tả trong SKILL.md
        assert "`%s`" % ma in noi_dung


def test_claude_md_co_dong_truoc_khi_push():
    van = open(os.path.join(GOC, "CLAUDE.md"), encoding="utf-8").read()
    assert "Trước khi push: chạy skill `soat-ma`" in van


def test_skill_khong_nam_trong_goi_zip_nguoi_dung():
    """soat-ma là công cụ của người làm mã, không phát cho người dùng cuối (khác tao-google-form-clb và
    xu-li-raw-forms): không có trong danh sách đóng gói."""
    sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
    import dong_goi_skill
    assert "soat-ma" not in str(dong_goi_skill.GOI)
