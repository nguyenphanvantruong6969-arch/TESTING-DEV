"""FormsMixin — bước "Chuẩn bị đợt" (FA-M7, worker A): chọn đường A / B, rồi (FA-M7) nạp CLB và đề thi.

Đường (`rules.fa_duong`) ∈ {"A", "B"}, mặc định chưa chọn; KHÔNG thuộc luật xếp, không đổi kết quả xếp.
"""
import sqlite3

import cau_hinh_ws
from api_workspace import CauHinhHong, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok

DUONG_HOP_LE = ("A", "B")


class FormsMixin:

    def get_fa_duong(self):
        """Đường đang chọn: {"duong": "A" | "B" | None}."""
        try:
            duong = self._luat_nghiem().get("fa_duong")
        except (ValueError, CauHinhHong) as e:
            return _fail(loi_cau_hinh(e) if isinstance(e, CauHinhHong) else err("ws_cau_hinh_hong", detail=str(e)))
        return _ok({"duong": duong if duong in DUONG_HOP_LE else None})

    def dat_fa_duong(self, duong):
        """Lưu đường A / B vào `rules.fa_duong`. Giá trị khác -> `forms_duong_chua_chon`."""
        if not isinstance(duong, str) or duong not in DUONG_HOP_LE:
            return _fail(err("forms_duong_chua_chon"))
        with self._khoa_ghi:
            try:
                da_luu = cau_hinh_ws.doc_cau_hinh(self.db_path, nghiem=True)
                cau_hinh_ws.ghi_cau_hinh(
                    self.db_path, cau_hinh_ws.tron_len(da_luu, {"rules": {"fa_duong": duong}}))
            except (ValueError, CauHinhHong, sqlite3.Error) as e:
                return _fail(loi_cau_hinh(e) if isinstance(e, CauHinhHong) else err("ws_cau_hinh_hong", detail=str(e)))
        return _ok({"duong": duong})
