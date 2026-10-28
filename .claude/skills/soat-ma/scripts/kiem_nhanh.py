#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kiem_nhanh.py — soát nhanh trước khi push: MỘT lệnh, mỗi mục in ĐẠT / KHÔNG ĐẠT.

    python .claude/skills/soat-ma/scripts/kiem_nhanh.py
    python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --chi ruff,i18n_khoa

Bảy mục tự động được (chỉ dùng thư viện chuẩn của Python; `ruff` là công cụ ngoài, đã có trong
requirements-dev.txt):

  ruff              `ruff check .` sạch
  chu_cam           chữ HIỂN THỊ (i18n.js, i18n_errors.py, index.html) không có xưng hô cấm
                    ("bạn", "các em", "em" ở tiếng Việt; "you", "your" ở tiếng Anh) và không
                    lộ tên nội bộ "Wharton"
  ma_loi_js         mọi mã lỗi JS nhắc tới (`code: "…"`) đều có trong i18n_errors.py
  i18n_loi_khop     i18n_loi.js khớp từng byte với bản sinh lại từ i18n_errors.py
  i18n_khoa         i18n.js: tập khoá tiếng Việt và tiếng Anh bằng nhau, không giá trị rỗng
  trung_khit        cấu hình mặc định cho kết quả TRÙNG KHÍT với nhánh so sánh (mặc định
                    `main`): từng dòng match_results + số bốc thăm, 3 bộ dữ liệu × 5 seed
  khong_sua_nhat_ky không có UPDATE / DELETE / DROP trên run_history và wharton_nhat_ky

Mục nào không chạy được (thiếu công cụ, không tìm thấy nhánh so sánh) tính là KHÔNG ĐẠT kèm lý do:
một mục bị bỏ qua im lặng chính là loại lỗi mà bước soát này tồn tại để bắt.

Mã thoát: 0 khi mọi mục đã chạy đều ĐẠT, 1 nếu có mục KHÔNG ĐẠT.
Soát bằng mắt (logic, giao diện, tài liệu) vẫn phải làm theo SKILL.md; tệp này chỉ lo phần máy làm được.
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from html.parser import HTMLParser

# .../<goc>/.claude/skills/soat-ma/scripts/kiem_nhanh.py -> <goc>
GOC_MAC_DINH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            *([os.pardir] * 4)))

# Xưng hô cấm trong chữ người dùng thấy, và tên nội bộ không được lọt ra.
CAM_VI = re.compile(r"\b(bạn|các bạn|em|các em)\b", re.I)
CAM_EN = re.compile(r"\b(you|your|yours)\b", re.I)
CAM_NOI_BO = re.compile(r"wharton", re.I)

SEED_MAC_DINH = (1, 7, 42, 99, 12345)
BO_DU_LIEU_MAC_DINH = 3
BANG_NHAT_KY = ("run_history", "wharton_nhat_ky")
THU_MUC_BO_QUA = {".git", ".venv", ".venv_build", "build", "dist", "node_modules", "__pycache__",
                  "tests", "docs"}


# ---------------------------------------------------------------------------
# Đọc nguồn
# ---------------------------------------------------------------------------

def _doc(duong) -> str:
    with io.open(duong, encoding="utf-8") as f:
        return f.read()


def _tep_py(goc):
    """Mọi .py của sản phẩm (không tính tests/ và docs/), kể cả trong .claude/."""
    for thu_muc, ds, tep in os.walk(goc):
        # Bỏ chính skill này: các mẫu tìm kiếm của nó tự khớp với chính nó.
        ds[:] = [d for d in ds if d not in THU_MUC_BO_QUA and d != "soat-ma"]
        for t in sorted(tep):
            if t.endswith(".py"):
                yield os.path.join(thu_muc, t)


def _tep_js(goc):
    ra = []
    js = os.path.join(goc, "js")
    if os.path.isdir(js):
        ra += [os.path.join(js, t) for t in sorted(os.listdir(js)) if t.endswith(".js")]
    for t in ("chung.js", "recovery.js"):
        if os.path.isfile(os.path.join(goc, t)):
            ra.append(os.path.join(goc, t))
    return ra


def _chay_py(goc, ma_py):
    """Chạy một đoạn Python trong tiến trình riêng, `goc` đứng đầu đường tìm mô-đun (cờ -I bỏ
    thư mục hiện tại). Trả stdout dạng byte; lỗi thì ném RuntimeError."""
    r = subprocess.run([sys.executable, "-I", "-c",
                        "import sys; sys.path.insert(0, %r)\n%s" % (goc, ma_py)],
                       cwd=goc, capture_output=True)
    if r.returncode != 0:
        loi = r.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError(loi[-1] if loi else "lỗi không rõ")
    return r.stdout


def _messages(goc) -> dict:
    ra = _chay_py(goc, "import json, i18n_errors\n"
                       "sys.stdout.buffer.write(json.dumps(i18n_errors.MESSAGES).encode('utf-8'))")
    return json.loads(ra.decode("utf-8"))


def _khoi_i18n(goc):
    """({khoá: chuỗi thô} tiếng Việt, {khoá: chuỗi thô} tiếng Anh) của UI_STRINGS trong i18n.js."""
    dong = _doc(os.path.join(goc, "i18n.js")).split("\n")
    vi = next(i for i, l in enumerate(dong) if l.strip() == "vi: {")
    en = next(i for i, l in enumerate(dong) if l.strip() == "en: {")
    cuoi = next((i for i in range(en + 1, len(dong)) if re.match(r"^\s{0,4}\};", dong[i])), len(dong))
    mau = re.compile(
        r'^\s+([A-Za-z0-9_]+):\s*((?:"(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`)'
        r'(?:\s*\+\s*(?:"(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`))*)', re.M)

    def gom(a, b):
        return {m.group(1): m.group(2) for m in mau.finditer("\n".join(dong[a:b]))}

    return gom(vi, en), gom(en, cuoi)


class _ChuHienThi(HTMLParser):
    """Chữ người dùng thấy trong HTML: chữ trong thẻ và vài thuộc tính; bỏ <script>, <style>.

    Chữ nằm trong phần tử có `data-i18n*` chỉ là chữ DỰ PHÒNG: giao diện thay nó bằng khoá của
    i18n.js lúc chạy (và khoá đó đã được soát ở i18n.js), nên không soát lần hai ở đây."""

    THUOC_TINH = ("title", "aria-label", "placeholder", "alt")
    TU_DONG = {"br", "img", "input", "meta", "link", "hr"}

    def __init__(self):
        super().__init__()
        self.ra = []
        self._bo = 0
        self._ngan = []          # mỗi thẻ đang mở: có data-i18n hay không

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        co_khoa = any(k.startswith("data-i18n") and k != "data-i18n-aria-label"
                      and not k.startswith("data-i18n-aria") for k in d)
        if tag in ("script", "style"):
            self._bo += 1
        for k, v in attrs:
            if k in self.THUOC_TINH and v and not any(x.startswith("data-i18n-" + k) for x in d):
                self.ra.append(v)
        if tag not in self.TU_DONG:
            self._ngan.append(co_khoa)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._bo:
            self._bo -= 1
        if tag not in self.TU_DONG and self._ngan:
            self._ngan.pop()

    def handle_data(self, data):
        if not self._bo and data.strip() and not any(self._ngan):
            self.ra.append(data.strip())


# ---------------------------------------------------------------------------
# Các mục kiểm. Mỗi hàm trả (đạt: bool, chi tiết: list[str]).
# ---------------------------------------------------------------------------

def kiem_ruff(goc):
    lenh = [sys.executable, "-m", "ruff", "check", "."]
    try:
        r = subprocess.run(lenh, cwd=goc, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        return False, ["không chạy được ruff: %s" % e]
    ra = (r.stdout + r.stderr).strip()
    if r.returncode != 0 and "No module named ruff" in ra:
        return False, ["chưa cài ruff (pip install -r requirements-dev.txt)"]
    return r.returncode == 0, [] if r.returncode == 0 else ra.splitlines()[-12:]


def kiem_chu_cam(goc):
    loi = []

    def soi(nguon, chu, ngon_ngu):
        cam = [(CAM_VI if ngon_ngu == "vi" else CAM_EN, "xưng hô cấm")]
        cam.append((CAM_NOI_BO, "tên nội bộ \"Wharton\""))
        for mau, ly_do in cam:
            m = mau.search(chu)
            if m:
                loi.append("%s [%s]: %s «%s» trong «%s»" % (nguon, ngon_ngu, ly_do, m.group(0),
                                                            chu.strip()[:70]))

    vi, en = _khoi_i18n(goc)
    for ngon_ngu, bang in (("vi", vi), ("en", en)):
        for khoa, chu in sorted(bang.items()):
            soi("i18n.js:%s" % khoa, chu, ngon_ngu)
    for ma, ban in sorted(_messages(goc).items()):
        for ngon_ngu in ("vi", "en"):
            if isinstance(ban, dict) and ban.get(ngon_ngu):
                soi("i18n_errors.py:%s" % ma, ban[ngon_ngu], ngon_ngu)
    html = os.path.join(goc, "index.html")
    if os.path.isfile(html):
        p = _ChuHienThi()
        p.feed(_doc(html))
        for chu in p.ra:                       # chữ gốc trong HTML là tiếng Việt
            soi("index.html", chu, "vi")
    return not loi, loi[:15] + (["… và %d chỗ nữa" % (len(loi) - 15)] if len(loi) > 15 else [])


def kiem_ma_loi_js(goc):
    # Mã hợp lệ: có bản dịch ở i18n_errors.py, hoặc trùng tên một khoá UI của i18n.js (câu chính do
    # t(khoá) dịch, mã chỉ để mang `params.detail`).
    ma_co = set(_messages(goc)) | set(_khoi_i18n(goc)[0])
    mau = re.compile(r"""\bcode\s*(?::|===|==)\s*["']([a-z][a-z0-9_]*)["']""")
    thieu = {}
    nguon = _tep_js(goc)
    if os.path.isfile(os.path.join(goc, "index.html")):
        nguon.append(os.path.join(goc, "index.html"))
    for duong in nguon:
        for ma in mau.findall(_doc(duong)):
            if ma not in ma_co:
                thieu.setdefault(ma, os.path.relpath(duong, goc))
    return not thieu, ["mã «%s» (%s) không có trong i18n_errors.py" % (m, t)
                       for m, t in sorted(thieu.items())]


def kiem_i18n_loi_khop(goc):
    for t in ("i18n_errors.py", "tao_i18n_js.py", "i18n_loi.js"):
        if not os.path.isfile(os.path.join(goc, t)):
            return False, ["thiếu %s" % t]
    try:
        sinh = _chay_py(goc, "import tao_i18n_js\n"
                             "sys.stdout.buffer.write(tao_i18n_js.noi_dung().encode('utf-8'))")
    except RuntimeError as e:
        return False, ["tao_i18n_js.py lỗi: %s" % e]
    with open(os.path.join(goc, "i18n_loi.js"), "rb") as f:
        hien_co = f.read()
    if sinh == hien_co:
        return True, []
    return False, ["i18n_loi.js lệch bản sinh lại (%d byte so với %d): chạy `python tao_i18n_js.py`"
                   % (len(hien_co), len(sinh))]


def kiem_i18n_khoa(goc):
    vi, en = _khoi_i18n(goc)
    loi = []
    if not vi or not en:
        return False, ["không đọc được khối vi/en của i18n.js"]
    for k in sorted(set(vi) - set(en)):
        loi.append("khoá «%s» có tiếng Việt, thiếu tiếng Anh" % k)
    for k in sorted(set(en) - set(vi)):
        loi.append("khoá «%s» có tiếng Anh, thiếu tiếng Việt" % k)
    for ngon_ngu, bang in (("vi", vi), ("en", en)):
        for k, v in sorted(bang.items()):
            if v.strip("\"'` ") == "":
                loi.append("khoá «%s» [%s] có giá trị rỗng" % (k, ngon_ngu))
    return not loi, loi[:15]


_CHAY_BO = r'''
import json, os, sys, tempfile
goc, ra, seeds, so_bo = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")], int(sys.argv[4])
sys.path[:0] = [goc, os.path.join(goc, "du_lieu_test")]
os.chdir(goc)
import do_anh_huong_seed as d
import api as api_mod
kq = {}
for ten, tep in d.BO_DU_LIEU[:so_bo]:
    for seed in seeds:
        with tempfile.TemporaryDirectory() as tam:
            db = d.nap_bo(tam, tep)
            a = api_mod.PipelineAPI(db)
            r = a.run_pipeline(seed=seed)
            with a._ket_noi_doc() as cur:
                mr = [list(x) for x in cur.execute(
                    "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref, round_num "
                    "FROM match_results ORDER BY student_id, buoi")]
                stb = [list(x) for x in cur.execute(
                    "SELECT student_id, stb_number FROM students ORDER BY student_id")]
            kq["%s|%d" % (ten.split()[0], seed)] = {"ok": r["ok"], "match_results": mr, "stb": stb}
with open(ra, "w", encoding="utf-8") as f:
    json.dump(kq, f, sort_keys=True)
'''


def _chay_bo(goc, seeds, so_bo):
    with tempfile.TemporaryDirectory() as tam:
        ra = os.path.join(tam, "ra.json")
        r = subprocess.run([sys.executable, "-I", "-c", _CHAY_BO, goc, ra,
                            ",".join(str(s) for s in seeds), str(so_bo)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not os.path.isfile(ra):
            raise RuntimeError("chạy bộ dữ liệu ở %s lỗi: %s" % (
                goc, (r.stderr.strip().splitlines() or ["?"])[-1]))
        with io.open(ra, encoding="utf-8") as f:
            return json.load(f)


def kiem_trung_khit(goc_moi, goc_cu, seeds=SEED_MAC_DINH, so_bo=BO_DU_LIEU_MAC_DINH):
    """So từng dòng match_results và số bốc thăm giữa hai bản mã (cấu hình mặc định)."""
    try:
        moi, cu = _chay_bo(goc_moi, seeds, so_bo), _chay_bo(goc_cu, seeds, so_bo)
    except RuntimeError as e:
        return False, [str(e)]
    loi = []
    for khoa in sorted(set(moi) | set(cu)):
        if khoa not in moi or khoa not in cu:
            loi.append("ca «%s» chỉ có ở một bên" % khoa)
        elif moi[khoa] != cu[khoa]:
            a, b = moi[khoa]["match_results"], cu[khoa]["match_results"]
            lech = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
            loi.append("ca «%s» lệch: %d dòng match_results khác, ok %s/%s, số bốc thăm %s"
                       % (khoa, lech, moi[khoa]["ok"], cu[khoa]["ok"],
                          "khác" if moi[khoa]["stb"] != cu[khoa]["stb"] else "giống"))
    return not loi, loi[:10] if loi else ["%d ca (%d bộ × %d seed) trùng khít" % (len(moi), so_bo, len(seeds))]


def _giai_nen_nhanh(goc, ref, dich):
    """Giải nén cây thư mục của `ref` (git archive) vào `dich`. Trả None hoặc thông báo lỗi.
    `main` không có trong bản sao cục bộ thì thử `origin/main`."""
    thu = [ref] + (["origin/" + ref] if "/" not in ref else [])
    r = None
    for ten in thu:
        r = subprocess.run(["git", "-C", goc, "archive", "--format=tar", ten], capture_output=True)
        if r.returncode == 0:
            break
    if r is None or r.returncode != 0:
        loi = r.stderr.decode("utf-8", "replace").strip().splitlines() if r else []
        return "không đọc được nhánh so sánh «%s»: %s" % (ref, loi[-1] if loi else "?")
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as t:
        try:
            t.extractall(dich, filter="data")      # Python 3.12+: không tin tên tệp trong kho
        except TypeError:
            t.extractall(dich)
    return None


def _khoi_ngoac(van, vi_tri):
    """Đoạn văn bản từ dấu mở ngoặc ở `vi_tri` tới dấu đóng tương ứng (bỏ qua ngoặc trong chuỗi)."""
    sau = {"[": "]", "{": "}", "(": ")"}
    ngan, chuoi = [], None
    for i in range(vi_tri, len(van)):
        c = van[i]
        if chuoi:
            if c == chuoi and van[i - 1] != "\\":
                chuoi = None
        elif c in "\"'":
            chuoi = c
        elif c in sau:
            ngan.append(sau[c])
        elif ngan and c == ngan[-1]:
            ngan.pop()
            if not ngan:
                return van[vi_tri:i + 1]
    return van[vi_tri:]


def kiem_khong_sua_nhat_ky(goc):
    """Bảng dấu vết chỉ được ghi THÊM. Hai kiểu vi phạm:
    (1) câu SQL viết thẳng UPDATE / DELETE FROM / DROP TABLE / TRUNCATE trên chúng;
    (2) tên bảng nằm trong một danh sách kiểu `_RESET_BANG` / `_BANG_…` mà mã duyệt để xoá hay dựng lại
        theo tên (`DELETE FROM %s`) — thêm tên vào đó cũng là xoá, dù không có câu SQL nào nhắc tới.
    Không tính tests/ và docs/."""
    ten = "|".join(BANG_NHAT_KY)
    sua = re.compile(r"\b(UPDATE|DELETE\s+FROM|DROP\s+TABLE(?:\s+IF\s+EXISTS)?|TRUNCATE(?:\s+TABLE)?)"
                     r"\s+[\"']?(%s)\b" % ten, re.I)
    danh_sach = re.compile(r"^\s*([A-Za-z_]*(?:BANG|RESET|XOA|DROP)[A-Za-z_]*)\s*(?::[^=\n]+)?=\s*([\[\{\(])",
                           re.M | re.I)
    ten_trong = re.compile(r"[\"'](%s)[\"']" % ten)
    loi = []
    for duong in _tep_py(goc):
        van = _doc(duong)
        rel = os.path.relpath(duong, goc)
        for m in sua.finditer(van):
            so_dong = van.count("\n", 0, m.start()) + 1
            loi.append("%s:%d: %s trên %s" % (rel, so_dong, " ".join(m.group(1).split()).upper(),
                                              m.group(2)))
        for m in danh_sach.finditer(van):
            khoi = _khoi_ngoac(van, m.end() - 1)
            for t in ten_trong.finditer(khoi):
                so_dong = van.count("\n", 0, m.end() - 1 + t.start()) + 1
                loi.append("%s:%d: bảng %s nằm trong danh sách %s (mã duyệt danh sách để xoá/dựng lại)"
                           % (rel, so_dong, t.group(1), m.group(1)))
    return not loi, loi[:15]


# ---------------------------------------------------------------------------
# Điều phối
# ---------------------------------------------------------------------------

MUC = [
    ("ruff", "ruff check . sạch"),
    ("chu_cam", "chữ hiển thị: không xưng hô cấm, không lộ «Wharton»"),
    ("ma_loi_js", "mã lỗi trong JS đều có trong i18n_errors.py"),
    ("i18n_loi_khop", "i18n_loi.js khớp bản sinh lại"),
    ("i18n_khoa", "khoá i18n đủ tiếng Việt và tiếng Anh"),
    ("trung_khit", "trùng khít với nhánh so sánh (3 bộ × 5 seed)"),
    ("khong_sua_nhat_ky", "không UPDATE/DELETE trên run_history, wharton_nhat_ky"),
]


def chay(goc, co_so="main", chi=None, bo_qua=(), seeds=SEED_MAC_DINH, so_bo=BO_DU_LIEU_MAC_DINH,
         in_ra=print):
    """Chạy các mục; trả {mã mục: (đạt, chi tiết)}. `in_ra` nhận từng dòng kết quả."""
    ket_qua = {}
    for ma, mo_ta in MUC:
        if (chi and ma not in chi) or ma in bo_qua:
            continue
        try:
            if ma == "ruff":
                kq = kiem_ruff(goc)
            elif ma == "chu_cam":
                kq = kiem_chu_cam(goc)
            elif ma == "ma_loi_js":
                kq = kiem_ma_loi_js(goc)
            elif ma == "i18n_loi_khop":
                kq = kiem_i18n_loi_khop(goc)
            elif ma == "i18n_khoa":
                kq = kiem_i18n_khoa(goc)
            elif ma == "khong_sua_nhat_ky":
                kq = kiem_khong_sua_nhat_ky(goc)
            else:
                with tempfile.TemporaryDirectory() as tam:
                    loi = _giai_nen_nhanh(goc, co_so, tam)
                    kq = (False, [loi]) if loi else kiem_trung_khit(goc, tam, seeds, so_bo)
        except Exception as e:                    # một mục hỏng không được che các mục khác
            kq = (False, ["không chạy được: %s: %s" % (type(e).__name__, e)])
        ket_qua[ma] = kq
        in_ra("%-10s %-18s %s" % ("ĐẠT" if kq[0] else "KHÔNG ĐẠT", ma, mo_ta))
        for dong in kq[1]:
            in_ra("             · " + dong)
    return ket_qua


def main(argv=None):
    # Cửa sổ lệnh / ống dẫn Windows mặc định cp1252: in tiếng Việt sẽ ném UnicodeEncodeError.
    for _luong in (sys.stdout, sys.stderr):
        if hasattr(_luong, "reconfigure"):
            _luong.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--goc", default=GOC_MAC_DINH, help="thư mục gốc của kho (mặc định: kho chứa tệp này)")
    p.add_argument("--co-so", default="main", help="nhánh/commit so trùng khít (mặc định: main)")
    p.add_argument("--chi", default="", help="chỉ chạy các mục này, cách nhau dấu phẩy")
    p.add_argument("--bo-qua", default="", help="bỏ các mục này (ghi rõ lý do trong báo cáo)")
    p.add_argument("--so-seed", type=int, default=len(SEED_MAC_DINH), help="số seed (mặc định 5)")
    ns = p.parse_args(argv)
    hop_le = {m for m, _ in MUC}
    chi = {x for x in ns.chi.split(",") if x}
    bo_qua = {x for x in ns.bo_qua.split(",") if x}
    la = (chi | bo_qua) - hop_le
    if la:
        p.error("mục lạ: %s (có: %s)" % (", ".join(sorted(la)), ", ".join(m for m, _ in MUC)))
    seeds = SEED_MAC_DINH[:max(1, ns.so_seed)]
    ket_qua = chay(os.path.abspath(ns.goc), ns.co_so, chi, bo_qua, seeds)
    hong = [m for m, (dat, _) in ket_qua.items() if not dat]
    print("-" * 60)
    print("%d/%d mục ĐẠT%s" % (len(ket_qua) - len(hong), len(ket_qua),
                               "" if not hong else " — KHÔNG ĐẠT: " + ", ".join(hong)))
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
