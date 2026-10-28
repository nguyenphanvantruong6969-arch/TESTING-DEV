"""api_workspace.py — các hàm API quản lý WORKSPACE (không gian làm việc).

Một phần của PipelineAPI (xem api.py), ghép bằng mixin như các tệp api_*.py khác.

Chỉ hoạt động khi PipelineAPI được dựng với `thu_muc_goc_ws` (main.py truyền
vào khi KHÔNG có đường dẫn CSDL trong argv). Chạy với đường dẫn CSDL riêng thì
mọi hàm ở đây trả lỗi `ws_tat_che_do` — một CSDL, không workspace, như trước.
Riêng `get_workspace_state` luôn gọi được: nó là phép thử "đang ở chế độ nào"
mà giao diện hỏi trước tiên.

Việc thật nằm ở workspace.py (đĩa) và cau_hinh_ws.py (cấu hình); tệp này chỉ
gói chúng vào hợp đồng {ok, data, errors} và lo phần RIÊNG của một tiến trình
đang chạy: đổi `self.db_path` an toàn giữa các lời gọi song song.
"""

import base64
import binascii
import functools
import os
import sqlite3
import tempfile

import cau_hinh_ws
import workspace
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import init_db


class CauHinhHong(Exception):
    """Cấu hình của workspace đang mở có nhưng ĐỌC KHÔNG ĐƯỢC (JSON hỏng, khoá/giá trị của bản
    phần mềm khác, CSDL đang bị khoá...). Khác "chưa có cấu hình" (= mặc định trường học).

    Nơi quyết định kết quả (chạy xếp, trần nhập) phải DỪNG khi gặp nó, không được lặng lẽ
    lùi về luật trường học."""

    ma = "ws_cau_hinh_hong"


class CsdlBan(CauHinhHong):
    """CSDL đang bị tiến trình khác giữ khoá (hết thời gian chờ). KHÔNG phải cấu hình hỏng: thử lại
    sau vài giây là được, nên báo mã riêng `csdl_dang_ban` — vẫn là CauHinhHong để mọi nơi đang
    bắt CauHinhHong tiếp tục DỪNG đúng như trước."""

    ma = "csdl_dang_ban"


def loi_cau_hinh(e) -> dict:
    """Mục lỗi dịch được cho một CauHinhHong: `csdl_dang_ban` hay `ws_cau_hinh_hong`."""
    return err(getattr(e, "ma", "ws_cau_hinh_hong"), detail=str(e))


class LoiDuongXuat(Exception):
    """Đường xuất không dùng được (đang là một thư mục có sẵn): mang sẵn mục lỗi dịch được, để
    từng hàm xuất trả `_fail(e.loi)` thay vì lỗi chung "xuất hỏng"."""

    def __init__(self, loi):
        super().__init__(loi.get("code"))
        self.loi = loi


class _LoiWs(Exception):
    """Lỗi nghiệp vụ đã có mã dịch được — chuyển thẳng thành err(code, **params)."""

    def __init__(self, code, **params):
        super().__init__(code)
        self.code = code
        self.params = params


def _ws_phuong_thuc(ham):
    """Bọc một hàm API workspace: chặn khi tắt chế độ, và đổi ngoại lệ thành lỗi dịch được."""
    @functools.wraps(ham)
    def boc(self, *args, **kwargs):
        if not self._goc_ws:
            return _fail(err("ws_tat_che_do"))
        try:
            return ham(self, *args, **kwargs)
        except _LoiWs as e:
            return _fail(err(e.code, **e.params))
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except ValueError as e:
            # workspace.py / cau_hinh_ws.py nêu lý do bằng tiếng Việt: để ở
            # "chi tiết kỹ thuật" (giao diện gấp sẵn), câu chính thì song ngữ.
            return _fail(err("ws_du_lieu_sai", detail=str(e)))
        except Exception as e:
            return _fail(self._loi_co_ghi_vet(err("ws_loi_khong_ro", detail=str(e))))
    return boc


class WorkspaceMixin:
    # `_goc_ws`: thư mục gốc chứa workspaces/ (None = tắt chế độ).
    # `_ws_da_chon`: người dùng đã chọn workspace chưa. Có nhiều workspace lúc
    # khởi động thì chưa — CSDL cho `db_path` lúc đó chỉ là chỗ tạm để đối tượng
    # sống được, và giao diện hiện màn chọn đè lên trên.

    # ---------------------------------------------------------------- nội bộ

    def _cfg_ws(self, nghiem: bool = False) -> dict:
        """Cấu hình của workspace đang mở (mặc định trường học nếu CSDL chưa có).

        Dùng được cả khi chạy với đường dẫn CSDL riêng. Đọc ở ĐẦU mỗi thao tác — trước khi
        mở giao dịch ghi — chứ không giữa chừng.

        `nghiem=False` (mặc định): cấu hình đọc không được thì lùi về mặc định — đủ cho nơi chỉ
        HIỂN THỊ (nhãn, tên). `nghiem=True`: ném `CauHinhHong` — cho nơi QUYẾT ĐỊNH."""
        if not nghiem:
            return cau_hinh_ws.doc_cau_hinh(self.db_path)
        try:
            return cau_hinh_ws.doc_cau_hinh(self.db_path, nghiem=True)
        except (ValueError, sqlite3.Error) as e:
            if isinstance(e, sqlite3.OperationalError) and (
                    "locked" in str(e).lower() or "busy" in str(e).lower()):
                raise CsdlBan(
                    "CSDL đang bận (%s). Chờ vài giây rồi thử lại." % e) from e
            raise CauHinhHong(
                "Không đọc được cấu hình của workspace (%s). Hãy kiểm tra hoặc đặt lại cấu "
                "hình rồi thử lại." % e) from e

    def _luat_nghiem(self) -> dict:
        """`rules` của workspace đang mở, đọc NGHIÊM (xem `_cfg_ws`)."""
        return self._cfg_ws(nghiem=True)["rules"]

    def _tran_nguyen_vong(self) -> int:
        """Số nguyện vọng tối đa mỗi buổi (`rules.max_choices`)."""
        return self._luat_nghiem()["max_choices"]

    def _tran_thi(self):
        """Số CLB thi tối đa mỗi buổi (`rules.max_tests`); None = không giới hạn."""
        return self._luat_nghiem()["max_tests"]

    def _ws_slug_dang_mo(self):
        """Slug của workspace đang mở, None nếu db_path nằm ngoài workspaces/."""
        if not self._goc_ws:
            return None
        db = os.path.realpath(self.db_path)
        thu_muc = os.path.dirname(db)
        goc = os.path.realpath(os.path.join(self._goc_ws, workspace.THU_MUC_WS))
        if os.path.basename(db) == workspace.TEN_DB and os.path.dirname(thu_muc) == goc:
            return os.path.basename(thu_muc)
        return None

    def _ws_db(self, slug) -> str:
        """Đường dẫn app.db của workspace `slug`; ném _LoiWs nếu không có."""
        try:
            db = workspace.duong_dan_db(self._goc_ws, slug)
        except ValueError:
            raise _LoiWs("ws_khong_co", slug=str(slug))
        if not os.path.isfile(db):
            raise _LoiWs("ws_khong_co", slug=str(slug))
        return db

    def _ws_hien_tai(self, slug) -> str:
        """`slug` rỗng = workspace đang mở."""
        slug = (slug or "").strip() or self._ws_slug_dang_mo()
        if not slug:
            raise _LoiWs("ws_khong_co", slug="")
        return slug

    # ---------------------------------------------------------------- trạng thái

    def get_workspace_state(self):
        """Giao diện hỏi lúc khởi động: có workspace không, đã chọn chưa, nhãn là gì.

        `config` luôn có (CSDL không có hàng cấu hình thì là mặc định trường
        học) nên giao diện lấy nhãn từ đây ở cả hai chế độ.
        """
        try:
            # Không giữ _khoa_ghi: chỉ ĐỌC, và không đáng để màn hình khởi động chờ một
            # lần chạy sắp xếp đang giữ khoá.
            cfg = cau_hinh_ws.doc_cau_hinh(self.db_path)
            bat = bool(self._goc_ws)
            return _ok({
                "enabled": bat,
                "chon": (not bat) or bool(self._ws_da_chon),
                "slug": self._ws_slug_dang_mo(),
                "name": cfg["name"],
                "config": cfg,
            })
        except Exception as e:
            return _fail(self._loi_co_ghi_vet(err("ws_loi_khong_ro", detail=str(e))))

    def dat_tieu_de_cua_so(self, tieu_de):
        """Đặt tiêu đề cửa sổ gốc (pywebview). Chế độ trình duyệt không có cửa sổ để đặt:
        giao diện đã đổi `document.title`, và hàm này lặng lẽ không làm gì.

        Không nằm trong `_ws_phuong_thuc`: tiêu đề cửa sổ không phụ thuộc có workspace
        hay không, và một lời gọi hỏng không đáng làm giao diện báo lỗi."""
        try:
            cua_so = self._window
            if cua_so is not None and hasattr(cua_so, "set_title"):
                cua_so.set_title(str(tieu_de or "")[:200])
            return _ok({"tieu_de": str(tieu_de or "")[:200]})
        except Exception as e:
            return _fail(self._loi_co_ghi_vet(err("ws_loi_khong_ro", detail=str(e))))

    # ---------------------------------------------------------------- danh sách

    @_ws_phuong_thuc
    def list_workspaces(self):
        dang_mo = self._ws_slug_dang_mo() if self._ws_da_chon else None
        ds = []
        for w in workspace.danh_sach(self._goc_ws):
            ds.append({
                "slug": w["slug"], "name": w["name"], "industry": w["industry"],
                "modified": w["modified"], "dang_mo": w["slug"] == dang_mo,
            })
        return _ok({"workspaces": ds, "dang_mo": dang_mo})

    @_ws_phuong_thuc
    def list_templates(self):
        return _ok({"templates": workspace.danh_sach_mau(self._goc_ws)})

    # ---------------------------------------------------------------- mở / tạo

    @_ws_phuong_thuc
    def open_workspace(self, slug):
        """Chuyển sang workspace `slug`: đổi db_path, init_db, bỏ bộ nhớ đệm.

        Giữ `_khoa_ghi` suốt lúc đổi: một lần chạy đang dở (hoặc lời ghi từ
        luồng khác) phải xong TRƯỚC, nếu không nó ghi vào CSDL của workspace
        MỚI những gì tính cho workspace cũ.
        """
        db = self._ws_db(slug)
        with self._khoa_ghi:
            init_db(db)
            self.db_path = db
            self._bo_nho_xuat = None   # bộ nhớ đệm duy nhất gắn với CSDL
            self._ws_da_chon = True
            cfg = cau_hinh_ws.doc_cau_hinh(db)
        return _ok({"slug": slug, "name": cfg["name"], "config": cfg})

    @_ws_phuong_thuc
    def create_workspace(self, name, cfg=None):
        """Dựng workspace mới (chưa mở). `cfg` thiếu khoá = mặc định trường học."""
        slug = workspace.tao(self._goc_ws, name, cfg)
        return _ok({"slug": slug})

    @_ws_phuong_thuc
    def rename_workspace(self, slug, new_name):
        self._ws_db(slug)
        with self._khoa_ghi:
            workspace.doi_ten(self._goc_ws, slug, new_name)
        return _ok({"slug": slug, "name": (new_name or "").strip()})

    @_ws_phuong_thuc
    def duplicate_workspace(self, slug, new_name, kem_du_lieu=True):
        self._ws_db(slug)
        with self._khoa_ghi:
            moi = workspace.nhan_ban(self._goc_ws, slug, new_name, bool(kem_du_lieu))
        return _ok({"slug": moi})

    @_ws_phuong_thuc
    def delete_workspace(self, slug, xac_nhan=""):
        """Dời workspace vào thùng rác (không xoá vĩnh viễn). Cần xac_nhan == "XOA".

        Không xoá được workspace ĐANG MỞ: trên Windows tệp đang mở không dời
        được, và xoá cái đang làm việc cũng chẳng ai muốn. Mở workspace khác
        trước.
        """
        if xac_nhan != self._RESET_CONFIRM:
            return _fail(err("reset_confirmation_mismatch", can_go=self._RESET_CONFIRM))
        self._ws_db(slug)
        # "Đang mở" là cái người dùng ĐÃ CHỌN. Lúc khởi động nhiều workspace, `db_path` chỉ là
        # chỗ tạm cho đối tượng API sống được (xem main.khoi_dong_workspace) và giao diện đang
        # hiện màn chọn: workspace tạm đó chưa ai mở nên xoá được như mọi cái khác.
        if self._ws_da_chon and slug == self._ws_slug_dang_mo():
            raise _LoiWs("ws_khong_xoa_dang_mo", slug=slug)
        with self._khoa_ghi:
            la_cho_tam = slug == self._ws_slug_dang_mo()     # chưa ai chọn, chỉ là chỗ đứng tạm
            thung = workspace.xoa(self._goc_ws, slug)
            if la_cho_tam:
                # `db_path` không được trỏ vào thư mục vừa dời đi: mọi lời gọi sau (trạng thái,
                # kiểm tra dữ liệu...) sẽ đọc một tệp không còn. Chuyển sang workspace còn lại,
                # cái sửa gần nhất (như main.khoi_dong_workspace).
                con_lai = workspace.danh_sach(self._goc_ws)
                if con_lai:
                    self.db_path = max(con_lai, key=lambda w: w["modified"])["path"]
        return _ok({"slug": slug, "thung_rac": thung})

    # ---------------------------------------------------------------- mẫu / zip

    @_ws_phuong_thuc
    def save_as_template(self, slug, ten_mau):
        self._ws_db(slug)
        duong = workspace.luu_mau(self._goc_ws, slug, ten_mau)
        return _ok({"path": duong, "slug": slug})

    @_ws_phuong_thuc
    def export_workspace(self, slug, output_path=""):
        """Nén workspace thành .zip đặt vào thư mục xuất (Tải xuống), không ghi đè."""
        self._ws_db(slug)
        dich = self._duong_xuat(output_path, slug + ".zip")
        workspace.xuat_zip(self._goc_ws, slug, dich)
        return _ok({"path": dich, "dir": os.path.dirname(dich)})

    @_ws_phuong_thuc
    def import_workspace(self, file_base64, ten_tep=""):
        """Nhập .zip (gửi lên dạng base64) thành workspace mới. `ten_tep` chỉ để đặt tên dự phòng."""
        try:
            du_lieu = base64.b64decode(file_base64 or "", validate=True)
        except (binascii.Error, ValueError) as e:
            raise ValueError("Dữ liệu tải lên không phải base64: %s" % e)
        ten = os.path.basename((ten_tep or "").replace("\\", "/")) or "workspace.zip"
        with tempfile.TemporaryDirectory() as tam:
            duong = os.path.join(tam, ten)
            with open(duong, "wb") as f:
                f.write(du_lieu)
            with self._khoa_ghi:
                slug = workspace.nhap_zip(self._goc_ws, duong)
        cfg = cau_hinh_ws.doc_cau_hinh(workspace.duong_dan_db(self._goc_ws, slug))
        return _ok({"slug": slug, "name": cfg["name"]})

    # ---------------------------------------------------------------- cấu hình

    @_ws_phuong_thuc
    def get_workspace_config(self, slug=""):
        """Cấu hình của workspace `slug` (rỗng = đang mở)."""
        slug = self._ws_hien_tai(slug)
        return _ok({"slug": slug,
                    "config": cau_hinh_ws.doc_cau_hinh(self._ws_db(slug))})

    @_ws_phuong_thuc
    def update_workspace_config(self, cfg, slug=""):
        """Kiểm rồi ghi cấu hình. Thư mục (slug) giữ nguyên dù đổi tên.

        `cfg` có thể chỉ một phần: phần không nhắc tới GIỮ NGUYÊN như đã lưu (không đặt lại về
        mặc định trường học). Cấu hình đã lưu mà đọc không được thì từ chối, không ghi đè."""
        slug = self._ws_hien_tai(slug)
        db = self._ws_db(slug)
        with self._khoa_ghi:
            da_luu = cau_hinh_ws.doc_cau_hinh(db, nghiem=True)
            moi = cau_hinh_ws.ghi_cau_hinh(db, cau_hinh_ws.tron_len(da_luu, cfg))
        return _ok({"slug": slug, "config": moi})
