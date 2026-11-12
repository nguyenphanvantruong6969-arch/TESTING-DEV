"""FormsBoMixin — bước 3 "Tạo bộ biểu mẫu" của thẻ "Chuẩn bị đợt" (FA-M8, worker C). TH = chưa thử trên Microsoft thật.

Đề lấy từ `forms/de_thi.json` của đợt, đường (A / B) từ `rules.fa_duong`, Loại CLB từ Sổ nhập của bước 1 khi có.
Ghi `forms/bieu_mau/` và MỘT tệp zip `BO_BIEU_MAU_<ngày>.zip` ở thư mục Tải xuống. R3: bộ không dặn đặt đáp án trên Forms
(hàm `tao_bo_bieu_mau` đã đặt `dap_an_tren_forms=False`; API không có tuỳ chọn nào đổi điều đó). Không đụng app.db.
"""
import datetime
import os
import zipfile

import forms_dot
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok

DUONG_HOP_LE = ("A", "B")


class FormsBoMixin:

    def _duong_bo(self):
        """Đường đang chọn ("A" | "B" | None); cấu hình hỏng ném CauHinhHong / ValueError cho bên gọi."""
        duong = self._luat_nghiem().get("fa_duong")
        return duong if duong in DUONG_HOP_LE else None

    def get_bo_bieu_mau(self):
        """Trạng thái để vẽ bước 3: {co_de, duong, co_bien_the}. `co_bien_the` = có CLB nào có đề biến thể."""
        try:
            duong = self._duong_bo()
        except (ValueError, CauHinhHong) as e:
            return _fail(loi_cau_hinh(e) if isinstance(e, CauHinhHong) else err("ws_cau_hinh_hong", detail=str(e)))
        try:
            de = forms_dot.doc_de_dot(self.db_path)
        except (FileNotFoundError, ValueError, KeyError):
            return _ok({"co_de": False, "duong": duong, "co_bien_the": False})
        return _ok({"co_de": True, "duong": duong,
                    "co_bien_the": any(c.get("de_thi_bien_the") for c in de["cau_lac_bo"])})

    def tao_bo_bieu_mau_api(self, tuy_chon=None, output_path=""):
        """Tạo bộ biểu mẫu cho đường đã chọn. `tuy_chon` = {mot_bieu_mau (mặc định True), bien_the (mặc định False)}.

        Trả {path (zip), dir (thư mục chứa zip), ten_zip, thu_muc (bộ trong dữ liệu đợt), n_tep, duong, mot_bieu_mau,
        bien_the}. Lỗi: `forms_chua_co_de`, `forms_duong_chua_chon`, `forms_tao_bo_loi` (đề sai, biến thể không có...)."""
        forms_dot.nap_mau_forms()
        import bieu_mau
        import tao_mau_forms
        tuy_chon = tuy_chon if isinstance(tuy_chon, dict) else {}
        mot_bieu_mau = bool(tuy_chon.get("mot_bieu_mau", True))
        bien_the = bool(tuy_chon.get("bien_the", False))
        try:
            duong = self._duong_bo()
        except (ValueError, CauHinhHong) as e:
            return _fail(loi_cau_hinh(e) if isinstance(e, CauHinhHong) else err("ws_cau_hinh_hong", detail=str(e)))
        try:
            de = forms_dot.doc_de_dot(self.db_path)
        except FileNotFoundError:
            return _fail(err("forms_chua_co_de"))
        except (bieu_mau.LoiDeThi, ValueError, KeyError) as e:
            return _fail(err("forms_tao_bo_loi", detail=str(e)))
        if duong is None:
            return _fail(err("forms_duong_chua_chon"))
        so_nhap = forms_dot.duong_so_nhap_clb_dot(self.db_path)
        with self._khoa_ghi:
            try:
                thu_muc = forms_dot.thu_muc_bieu_mau(self.db_path)
                tao_mau_forms.tao_bo_bieu_mau(
                    de, thu_muc, duong=duong, mot_bieu_mau=mot_bieu_mau, bien_the=bien_the,
                    so_nhap_clb=so_nhap if duong == "B" and os.path.isfile(so_nhap) else None)
                ten = "BO_BIEU_MAU_%s.zip" % datetime.date.today().strftime("%Y%m%d")
                zip_path = self._duong_xuat(output_path, ten)
                tao_mau_forms.ghi_zip_bo(thu_muc, zip_path)
                with zipfile.ZipFile(zip_path) as z:
                    n_tep = len(z.namelist())
            except LoiDuongXuat as e:
                return _fail(e.loi)
            except Exception as e:      # LoiDeThi, đề biến thể sai, ghi tệp lỗi... KHÔNG ghi gì vào app.db
                return _fail(err("forms_tao_bo_loi", detail=self._chi_tiet_loi_xuat(e)))
        return _ok({"path": zip_path, "dir": os.path.dirname(zip_path), "ten_zip": os.path.basename(zip_path),
                    "thu_muc": thu_muc, "n_tep": n_tep, "duong": duong, "mot_bieu_mau": mot_bieu_mau,
                    "bien_the": bien_the})
