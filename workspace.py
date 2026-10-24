"""
workspace.py
============
Các workspace trên đĩa. Mỗi workspace là một thư mục `root/workspaces/<slug>/`
chứa `app.db` riêng (cấu hình nằm TRONG app.db — xem cau_hinh_ws.py).

    root/
      workspaces/
        truong-hoc/app.db
        cong-ty-abc/app.db
        _trash/truong-hoc-20260101_101500_123456/   <- workspace đã xoá
      templates/
        truong-hoc.json                              <- mẫu cấu hình (không dữ liệu)

Mọi hàm nhận `root` làm tham số; module KHÔNG giữ trạng thái toàn cục.

Hai nguyên tắc:
  * KHÔNG xoá vĩnh viễn gì cả. "Xoá" workspace là dời cả thư mục vào `_trash`
    (kèm một bản sao lưu app.db), và người dùng muốn lấy lại thì chép ra.
  * Sao chép CSDL luôn qua SQLite Backup API chứ không chép tệp thô, như
    `PipelineAPI._backup_db`: chép thô có thể chụp phải trạng thái nửa-ghi.

Trên Windows không dời/xoá được thư mục khi tệp bên trong còn đang mở —
`xoa` yêu cầu người gọi đã đóng workspace đó.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import sqlite3
import stat
import tempfile
import zipfile

from cau_hinh_ws import (
    MAC_DINH_TRUONG_HOC,
    chuan_hoa,
    doc_cau_hinh,
    ghi_cau_hinh,
)
from rbda_priority_pipeline import connect_db, init_db
from so_nhap import bo_dau

THU_MUC_WS = "workspaces"
THU_MUC_RAC = "_trash"
THU_MUC_MAU = "templates"
TEN_DB = "app.db"

SLUG_TRUONG_HOC = "truong-hoc"
TEN_TRUONG_HOC = "Trường học"
# Mẫu dựng sẵn không phải tệp nào cả. Dấu gạch dưới đầu để KHÔNG BAO GIỜ trùng
# slug của một mẫu người dùng lưu (slug workspace chỉ có a-z, 0-9 và '-').
SLUG_MAU_TRUONG_HOC = "_truong-hoc"

TEN_FILE_GHI_CHU = "DA_CHUYEN_SANG_WORKSPACES.txt"
# Thư mục dựng dở của di_chuyen_db_cu. Chỉ đổi tên thành `workspaces` khi đã
# xong hết — xem vì sao ở đó.
_THU_MUC_DANG_DUNG = "_workspaces_dang_dung"

_RE_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Slug dài quá thì thư mục không tạo được (Windows giới hạn cả đường dẫn ở 260 ký tự).
_SLUG_TOI_DA = 60
# Tên thiết bị của Windows: một thư mục tên `con` hay `nul` không tạo / mở được ở đó.
_TEN_THIET_BI = frozenset(
    {"con", "prn", "aux", "nul"}
    | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)})
# Trần dung lượng GIẢI NÉN của app.db trong zip nhập vào (chống zip bomb). Một app.db
# thật của trường vài trăm học sinh chỉ cỡ vài MB; 500 MB là rộng rãi.
TRAN_GIAI_NEN_BYTE = 500 * 1024 * 1024
_RE_ONG_DAN = re.compile(r"^[A-Za-z]:")


# ---------------------------------------------------------------------------
# Đường dẫn và slug
# ---------------------------------------------------------------------------

def _thu_muc_ws(root: str) -> str:
    return os.path.join(root, THU_MUC_WS)


def duong_dan_db(root: str, slug: str) -> str:
    """Đường dẫn app.db của workspace `slug` (không kiểm có tồn tại không)."""
    return os.path.join(_thu_muc_ws(root), _kiem_slug(slug), TEN_DB)


def _kiem_slug(slug) -> str:
    """Slug hợp lệ mới được ghép vào đường dẫn — chặn `..`, `/`, `_trash`…"""
    if not isinstance(slug, str) or not _RE_SLUG.match(slug):
        raise ValueError("Mã workspace không hợp lệ: %r." % (slug,))
    return slug


def _thu_muc_ton_tai(root: str, slug: str) -> str:
    thu_muc = os.path.join(_thu_muc_ws(root), _kiem_slug(slug))
    if not os.path.isfile(os.path.join(thu_muc, TEN_DB)):
        raise ValueError("Không có workspace '%s'." % slug)
    return thu_muc


def _kiem_ten(ten) -> str:
    if not isinstance(ten, str) or not ten.strip():
        raise ValueError("Tên workspace không được để trống.")
    return ten.strip()


def _tao_slug(ten: str) -> str:
    """'Trường học' -> 'truong-hoc'. Tên toàn ký hiệu thì dùng 'workspace'.

    Cắt ở `_SLUG_TOI_DA` ký tự, và tên trùng tên thiết bị của Windows (con, nul,
    com1...) được thêm tiền tố `ws-` để thư mục tạo được ở mọi máy.
    """
    slug = "-".join(bo_dau(ten).split())[:_SLUG_TOI_DA].strip("-") or "workspace"
    if slug in _TEN_THIET_BI:
        slug = "ws-" + slug
    return slug


def _slug_trong(root: str, ten: str) -> str:
    """Slug từ `ten`; đã có thư mục cùng tên thì thêm -2, -3, …

    Kiểm theo THƯ MỤC chứ không theo app.db: một thư mục dở dang (chưa có
    app.db) vẫn chiếm chỗ, và dựng đè lên nó là trộn hai workspace.
    """
    goc = _tao_slug(ten)
    slug, n = goc, 1
    while os.path.exists(os.path.join(_thu_muc_ws(root), slug)):
        n += 1
        slug = "%s-%d" % (goc, n)
    return slug


def _dau_thoi_gian() -> str:
    # Cùng khuôn với PipelineAPI._backup_db.
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _chep_db(nguon: str, dich: str, *, du_phong_chep_tep: bool = False) -> None:
    """Chép CSDL bằng SQLite Backup API (cùng kiểu `PipelineAPI._backup_db`).

    Hỏng giữa chừng thì xoá bản dở: nó mang tên một app.db thật.

    `du_phong_chep_tep`: nguồn hỏng không đọc được bằng Backup API thì chép
    nguyên tệp. Dùng cho bản sao lưu trước khi xoá: một workspace hỏng vẫn phải
    xoá được, và vẫn phải còn bản để cứu.
    """
    src = None
    try:
        # `connect_db` đã chạm vào tệp (PRAGMA), nên tệp hỏng báo lỗi ngay ở đây.
        src = connect_db(nguon)
        dst = sqlite3.connect(dich)
        try:
            src.backup(dst)
        finally:
            dst.close()
    except BaseException as e:
        try:
            os.remove(dich)
        except OSError:
            pass
        if du_phong_chep_tep and isinstance(e, sqlite3.Error):
            shutil.copy2(nguon, dich)
            return
        raise
    finally:
        if src is not None:
            src.close()


# ---------------------------------------------------------------------------
# Liệt kê / tạo / đổi tên
# ---------------------------------------------------------------------------

def danh_sach(root: str) -> list[dict]:
    """[{slug, name, industry, path, modified}] của mọi workspace, xếp theo slug.

    `path` là đường dẫn app.db (thứ cần để mở). `modified` là giờ sửa app.db,
    dạng 'YYYY-MM-DD HH:MM:SS'. Bỏ qua `_trash` và mọi thư mục bắt đầu bằng
    '_' (kể cả thư mục đang dựng dở), và thư mục không có app.db.
    """
    goc = _thu_muc_ws(root)
    if not os.path.isdir(goc):
        return []
    ra = []
    for slug in sorted(os.listdir(goc)):
        db = os.path.join(goc, slug, TEN_DB)
        if slug.startswith("_") or not os.path.isfile(db):
            continue
        cfg = doc_cau_hinh(db)
        ra.append({
            "slug": slug,
            "name": cfg["name"] or slug,
            "industry": cfg["industry"],
            "path": db,
            "modified": datetime.datetime.fromtimestamp(
                os.path.getmtime(db)).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return ra


def tao(root: str, name: str, cfg: dict | None = None) -> str:
    """Dựng workspace mới tên `name` với cấu hình `cfg` (None = mặc định trường học).

    Trả về slug. `cfg["name"]`, nếu có, bị `name` ghi đè. `cfg` sai thì ném
    ValueError TRƯỚC khi đụng tới đĩa.
    """
    name = _kiem_ten(name)
    cau_hinh = dict(cfg or {})
    cau_hinh["name"] = name
    chuan_hoa(cau_hinh)

    slug = _slug_trong(root, name)
    thu_muc = os.path.join(_thu_muc_ws(root), slug)
    os.makedirs(thu_muc)
    try:
        db = os.path.join(thu_muc, TEN_DB)
        init_db(db)
        ghi_cau_hinh(db, cau_hinh)
    except BaseException:
        # Thư mục VỪA tạo ngay trên, chưa có dữ liệu của ai: dọn là an toàn.
        shutil.rmtree(thu_muc, ignore_errors=True)
        raise
    return slug


def doi_ten(root: str, slug: str, new_name: str) -> None:
    """Đổi `config.name`. Thư mục giữ nguyên slug."""
    new_name = _kiem_ten(new_name)
    db = os.path.join(_thu_muc_ton_tai(root, slug), TEN_DB)
    # nghiem: đọc-rồi-ghi-lại. Cấu hình hiện có mà đọc không được thì từ chối đổi tên,
    # KHÔNG lặng lẽ ghi mặc định đè lên nhãn và luật của workspace.
    cfg = doc_cau_hinh(db, nghiem=True)
    cfg["name"] = new_name
    ghi_cau_hinh(db, cfg)


# ---------------------------------------------------------------------------
# Xoá (vào thùng rác) / nhân bản
# ---------------------------------------------------------------------------

def xoa(root: str, slug: str) -> str:
    """Sao lưu app.db trong thư mục rồi DỜI cả thư mục vào `_trash`. Trả đường dẫn mới.

    Không xoá vĩnh viễn gì. Bản sao lưu nằm TRONG thư mục bị dời, nên mở
    thư mục trong `_trash` là có cả app.db lẫn bản sao.
    """
    thu_muc = _thu_muc_ton_tai(root, slug)
    _chep_db(os.path.join(thu_muc, TEN_DB),
             os.path.join(thu_muc, "%s.bak-%s" % (TEN_DB, _dau_thoi_gian())),
             du_phong_chep_tep=True)

    rac = os.path.join(_thu_muc_ws(root), THU_MUC_RAC)
    os.makedirs(rac, exist_ok=True)
    dich = os.path.join(rac, "%s-%s" % (slug, _dau_thoi_gian()))
    shutil.move(thu_muc, dich)
    return dich


def nhan_ban(root: str, slug: str, new_name: str, kem_du_lieu: bool) -> str:
    """Nhân bản workspace `slug` thành `new_name`. Trả slug mới.

    kem_du_lieu=True : chép cả CSDL (Backup API) — học sinh, CLB, kết quả, lịch
                       sử chạy, khoá bốc thăm… đều theo sang.
    kem_du_lieu=False: CSDL mới trống, cùng cấu hình.
    """
    new_name = _kiem_ten(new_name)
    nguon = os.path.join(_thu_muc_ton_tai(root, slug), TEN_DB)
    cfg = doc_cau_hinh(nguon, nghiem=True)   # xem `doi_ten`: không nhân bản một cấu hình đoán

    if not kem_du_lieu:
        return tao(root, new_name, cfg)

    cfg["name"] = new_name
    chuan_hoa(cfg)
    moi = _slug_trong(root, new_name)
    thu_muc = os.path.join(_thu_muc_ws(root), moi)
    os.makedirs(thu_muc)
    try:
        db = os.path.join(thu_muc, TEN_DB)
        _chep_db(nguon, db)
        init_db(db)  # nguồn từ bản cũ vẫn lên đúng schema
        ghi_cau_hinh(db, cfg)
    except BaseException:
        shutil.rmtree(thu_muc, ignore_errors=True)
        raise
    return moi


# ---------------------------------------------------------------------------
# Mẫu cấu hình
# ---------------------------------------------------------------------------

def luu_mau(root: str, slug: str, ten_mau: str) -> str:
    """Lưu CẤU HÌNH (không dữ liệu) của workspace `slug` thành mẫu tên `ten_mau`.

    Ghi `root/templates/<slug>.json` — đặt tên theo workspace nguồn, nên lưu lại
    từ cùng workspace thì CẬP NHẬT mẫu đó chứ không sinh thêm. Trả đường dẫn tệp.
    """
    ten_mau = _kiem_ten(ten_mau)
    cfg = doc_cau_hinh(os.path.join(_thu_muc_ton_tai(root, slug), TEN_DB), nghiem=True)
    cfg["name"] = ten_mau
    thu_muc = os.path.join(root, THU_MUC_MAU)
    os.makedirs(thu_muc, exist_ok=True)
    duong = os.path.join(thu_muc, slug + ".json")
    # Ghi ra tệp tạm rồi đổi tên: mất điện giữa chừng không để lại mẫu cụt.
    tam = duong + ".tmp"
    with open(tam, "w", encoding="utf-8") as f:
        json.dump({"name": ten_mau, "config": cfg}, f, ensure_ascii=False, indent=2)
    os.replace(tam, duong)
    return duong


def danh_sach_mau(root: str) -> list[dict]:
    """[{slug, name, builtin, config}]. Mẫu dựng sẵn "Trường học" luôn đứng đầu.

    Tệp mẫu hỏng hoặc cấu hình không hợp lệ thì bỏ qua (không ném): một tệp
    hỏng không được làm mất cả danh sách.
    """
    cfg_truong = json.loads(json.dumps(MAC_DINH_TRUONG_HOC))
    cfg_truong["name"] = TEN_TRUONG_HOC
    ra = [{"slug": SLUG_MAU_TRUONG_HOC, "name": TEN_TRUONG_HOC,
           "builtin": True, "config": cfg_truong}]
    thu_muc = os.path.join(root, THU_MUC_MAU)
    if not os.path.isdir(thu_muc):
        return ra
    for ten_tep in sorted(os.listdir(thu_muc)):
        slug, duoi = os.path.splitext(ten_tep)
        if duoi != ".json" or not _RE_SLUG.match(slug):
            continue
        try:
            with open(os.path.join(thu_muc, ten_tep), encoding="utf-8") as f:
                du_lieu = json.load(f)
            cfg = chuan_hoa(du_lieu["config"])
            ten = du_lieu.get("name")
            if not isinstance(ten, str) or not ten.strip():
                ten = cfg["name"] or slug
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
        ra.append({"slug": slug, "name": ten, "builtin": False, "config": cfg})
    return ra


# ---------------------------------------------------------------------------
# Xuất / nhập zip
# ---------------------------------------------------------------------------

def _la_tep_phu(ten: str) -> bool:
    """Bản sao lưu và tệp phụ của SQLite — không đưa vào zip."""
    return ".bak-" in ten or ten.endswith(("-journal", "-wal", "-shm"))


def xuat_zip(root: str, slug: str, dest_path: str) -> str:
    """Nén workspace `slug` vào `dest_path`. app.db nằm ở GỐC zip.

    app.db đi vào zip qua Backup API (ảnh chụp nhất quán dù app đang mở). Bản
    sao lưu `app.db.bak-*` và các tệp `*.zip` trong thư mục không đi theo: bản sao
    lưu chỉ làm zip phình ra, còn zip là kết quả của các lần xuất trước.
    """
    thu_muc = _thu_muc_ton_tai(root, slug)
    dest_path = os.path.abspath(dest_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with tempfile.TemporaryDirectory() as tam:
        anh_chup = os.path.join(tam, TEN_DB)
        _chep_db(os.path.join(thu_muc, TEN_DB), anh_chup)
        try:
            with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(anh_chup, TEN_DB)
                for thu, _, tep in os.walk(thu_muc):
                    for t in sorted(tep):
                        day_du = os.path.join(thu, t)
                        tuong_doi = os.path.relpath(day_du, thu_muc)
                        if tuong_doi == TEN_DB or _la_tep_phu(t):
                            continue
                        # Zip đích có thể nằm NGAY trong thư mục workspace (Tải xuống không ghi
                        # được thì xuất lùi về cạnh app.db): không nén chính nó, và không nén các
                        # zip xuất trước (mỗi lần xuất sẽ phình thêm một lớp).
                        if t.lower().endswith(".zip") or \
                                os.path.realpath(day_du) == os.path.realpath(dest_path):
                            continue
                        z.write(day_du, tuong_doi.replace(os.sep, "/"))
        except BaseException:
            try:
                os.remove(dest_path)
            except OSError:
                pass
            raise
    return dest_path


def _kiem_ten_trong_zip(ten: str) -> list[str]:
    """Tách tên một mục zip thành các thành phần, hoặc ném ValueError (zip-slip).

    Chặn: đường dẫn tuyệt đối (`/x`, `\\x`, `C:\\x`), mọi thành phần `..`, và
    byte NUL. Coi CẢ `/` lẫn `\\` là dấu phân cách — zip tạo trên Windows có
    thể mang `\\`, và Windows hiểu `..\\x` là thoát ra ngoài.
    """
    if "\x00" in ten:
        raise ValueError("Zip không an toàn: tên tệp chứa ký tự NUL.")
    if ten.startswith(("/", "\\")) or _RE_ONG_DAN.match(ten):
        raise ValueError("Zip không an toàn: đường dẫn tuyệt đối '%s'." % ten)
    phan = [p for p in re.split(r"[\\/]+", ten) if p not in ("", ".")]
    if ".." in phan:
        raise ValueError("Zip không an toàn: đường dẫn chứa '..' ('%s')." % ten)
    return phan


def nhap_zip(root: str, zip_path: str) -> str:
    """Nhập zip do `xuat_zip` tạo ra thành workspace mới. Trả slug.

    Giải nén vào thư mục tạm (`_nhap-*`, nằm cạnh để đổi tên được trong một
    bước) rồi mới đặt vào chỗ — hỏng giữa chừng không để lại workspace dở.
    Slug lấy từ tên trong cấu hình; đã có thì thêm -2, -3 như `tao`.

    Raises:
        ValueError: không phải zip, có mục không an toàn (zip-slip), thiếu
            app.db ở gốc, hoặc app.db không phải CSDL SQLite.
    """
    goc = _thu_muc_ws(root)
    os.makedirs(goc, exist_ok=True)
    tam = tempfile.mkdtemp(prefix="_nhap-", dir=goc)
    try:
        try:
            z = zipfile.ZipFile(zip_path)
        except (zipfile.BadZipFile, OSError) as e:
            raise ValueError("Không đọc được tệp zip: %s" % e)
        with z:
            muc = []
            for info in z.infolist():
                phan = _kiem_ten_trong_zip(info.filename)     # zip-slip: kiểm MỌI mục
                # Liên kết tượng trưng: giải ra sẽ trỏ tới nơi tuỳ ý.
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError("Zip không an toàn: liên kết '%s'." % info.filename)
                if info.flag_bits & 0x1:
                    raise ValueError("Zip không an toàn: '%s' được mã hoá." % info.filename)
                if phan:
                    muc.append((info, phan))
            if not any(phan == [TEN_DB] and not info.is_dir() for info, phan in muc):
                raise ValueError("Zip không phải workspace: thiếu %s ở gốc." % TEN_DB)

            goc_tam = os.path.realpath(tam)
            # Trần dung lượng GIẢI NÉN cho cả zip, đếm BYTE THẬT khi chép: tiêu đề zip
            # (`file_size`) khai sao cũng được, nên không tin nó.
            con_lai = TRAN_GIAI_NEN_BYTE
            for info, phan in muc:
                dich = os.path.join(tam, *phan)
                # Đã lọc ở trên; kiểm lại trên đường dẫn thật cho chắc.
                if os.path.commonpath([goc_tam, os.path.realpath(dich)]) != goc_tam:
                    raise ValueError("Zip không an toàn: '%s'." % info.filename)
                if info.is_dir():
                    os.makedirs(dich, exist_ok=True)
                    continue
                # Tệp phụ của SQLite (-journal / -wal / -shm) và bản sao lưu KHÔNG được vào:
                # SQLite sẽ tự phát lại một nhật ký có sẵn khi mở app.db.
                if _la_tep_phu(phan[-1]):
                    continue
                os.makedirs(os.path.dirname(dich), exist_ok=True)
                with z.open(info) as nguon, open(dich, "wb") as ra:
                    while True:
                        khoi = nguon.read(1024 * 1024)
                        if not khoi:
                            break
                        con_lai -= len(khoi)
                        if con_lai < 0:
                            raise ValueError("Zip quá lớn: giải nén ra hơn %d MB." % (
                                TRAN_GIAI_NEN_BYTE // (1024 * 1024)))
                        ra.write(khoi)

        db = os.path.join(tam, TEN_DB)
        try:
            init_db(db)  # từ chối tệp không phải SQLite; nâng zip bản cũ lên schema mới
            # NGHIÊM: cấu hình có mà đọc không được (JSON hỏng, khoá/giá trị của bản phần mềm
            # khác...) thì từ chối cả zip. Đọc "dễ tính" sẽ ra mặc định trường học với tên rỗng,
            # rồi `ghi_cau_hinh` ở dưới ghi mặc định đó ĐÈ lên nhãn và luật thật trong zip.
            cfg = doc_cau_hinh(db, nghiem=True)
        except sqlite3.DatabaseError as e:
            raise ValueError("app.db trong zip không phải CSDL hợp lệ: %s" % e)
        except ValueError as e:
            raise ValueError("Cấu hình workspace trong zip không đọc được (có thể do bản phần mềm "
                             "khác tạo ra): %s" % e)
        if not cfg["name"]:
            cfg["name"] = os.path.splitext(os.path.basename(zip_path))[0] or "workspace"
            ghi_cau_hinh(db, cfg)

        slug = _slug_trong(root, cfg["name"])
        os.replace(tam, os.path.join(goc, slug))
        return slug
    except BaseException:
        shutil.rmtree(tam, ignore_errors=True)
        raise


# ---------------------------------------------------------------------------
# Di trú app.db cũ
# ---------------------------------------------------------------------------

_GHI_CHU_DI_CHUYEN = (
    "Phần mềm nay quản lý nhiều không gian làm việc (workspace). Tệp app.db "
    "cũ của thầy/cô đã được chuyển nguyên vẹn, cùng các bản sao lưu app.db.bak-*, "
    "vào thư mục workspaces\\truong-hoc (workspace \"Trường học\"); dữ liệu "
    "không bị thay đổi. Phần mềm tự mở workspace đó khi khởi động. Muốn quay "
    "về cách cũ, chép app.db từ thư mục này ra cạnh chương trình và xoá "
    "thư mục workspaces.\n"
)


def _tep_can_chuyen(root: str) -> list[str]:
    """app.db, tệp nhật ký đi kèm, và các bản sao lưu — tên tệp, không phải đường dẫn.

    Tệp `-journal`/`-wal`/`-shm` PHẢI đi cùng app.db: SQLite dùng chúng để
    khôi phục giao dịch dang dở, tách chúng ra là mất quyền khôi phục đó.
    """
    ra = []
    for t in sorted(os.listdir(root)):
        if not os.path.isfile(os.path.join(root, t)):
            continue
        if t in (TEN_DB, TEN_DB + "-journal", TEN_DB + "-wal", TEN_DB + "-shm") \
                or t.startswith(TEN_DB + ".bak-"):
            ra.append(t)
    return ra


def di_chuyen_db_cu(root: str) -> bool:
    """`root/app.db` (bản trước khi có workspace) -> `root/workspaces/truong-hoc/`.

    Chỉ chạy khi có `root/app.db` VÀ chưa có `root/workspaces` — chạy lần hai là
    không làm gì. Trả True nếu vừa di trú.

    Dựng trong `_workspaces_dang_dung` rồi đổi tên MỘT lần thành `workspaces`,
    vì `workspaces` xuất hiện chính là dấu "đã di trú". Nếu tạo nó trước rồi
    mới dời tệp, mất điện giữa chừng sẽ để `app.db` nằm lại bên ngoài mà lần
    sau không ai di trú nữa. Với cách này, hỏng giữa chừng thì lần sau chạy
    tiếp phần còn lại (tệp nào đã dời thì bỏ qua).
    """
    dang_dung = os.path.join(root, _THU_MUC_DANG_DUNG)
    dich = os.path.join(dang_dung, SLUG_TRUONG_HOC)
    if os.path.exists(_thu_muc_ws(root)):
        return False
    # Có app.db ở ngoài, HOẶC lần trước đã dời xong app.db mà chưa kịp đổi tên.
    if not (os.path.isfile(os.path.join(root, TEN_DB))
            or os.path.isfile(os.path.join(dich, TEN_DB))):
        return False

    os.makedirs(dich, exist_ok=True)
    # Lần trước đã dời xong app.db THẬT vào `dich` rồi mới dừng; từ đó có thể đã có một
    # app.db MỚI mọc lên ở `root` (màn phục hồi "bắt đầu mới", hay bản phần mềm cũ chạy
    # lại). Dời nó đè lên là xoá mất dữ liệu thật — mà `shutil.move` đè không báo trên cả
    # POSIX lẫn Windows (rename lỗi thì lùi về chép-đè). Nên không bao giờ đè: tệp của
    # app.db mới (kể cả `-journal`/`-wal`, vốn thuộc về CHÍNH nó, không phải app.db thật)
    # được dời sang bên cạnh dưới tên có hậu tố `.trung-<giờ>`, để không mất mà cũng không
    # bị SQLite nhận nhầm.
    da_co_db_that = os.path.isfile(os.path.join(dich, TEN_DB))
    hau_to = ".trung-%s" % _dau_thoi_gian()
    for t in _tep_can_chuyen(root):
        la_ho_so_db = t == TEN_DB or t.startswith(TEN_DB + "-")
        ten_dich = t
        if os.path.exists(os.path.join(dich, t)) or (da_co_db_that and la_ho_so_db):
            ten_dich = t + hau_to
        shutil.move(os.path.join(root, t), os.path.join(dich, ten_dich))

    try:
        ghi_cau_hinh(os.path.join(dich, TEN_DB), {"name": TEN_TRUONG_HOC})
    except sqlite3.Error:
        # app.db hỏng: vẫn dời nó đi nguyên trạng. Màn phục hồi/ khôi phục
        # sẽ xử lý khi mở; ở đây chỉ không có tên, danh sách dùng slug thay.
        pass

    os.replace(dang_dung, _thu_muc_ws(root))
    try:
        with open(os.path.join(root, TEN_FILE_GHI_CHU), "w", encoding="utf-8") as f:
            f.write(_GHI_CHU_DI_CHUYEN)
    except OSError:
        pass  # chỉ là lời nhắn; dữ liệu đã an toàn
    return True
