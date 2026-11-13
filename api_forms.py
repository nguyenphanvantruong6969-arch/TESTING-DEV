"""FormsMixin — bước "Chuẩn bị đợt" (FA-M7, worker A): chọn đường A / B, rồi (FA-M7) nạp CLB và đề thi.

Đường (`rules.fa_duong`) ∈ {"A", "B"}, mặc định chưa chọn; KHÔNG thuộc luật xếp, không đổi kết quả xếp.
"""
import base64
import csv
import io
import json
import os
import shutil
import sqlite3
import tempfile

import cau_hinh_ws
import forms_dot
import so_nhap
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok

DUONG_HOP_LE = ("A", "B")
TEN_TEP_KET_QUA_PHIEU = "phieu_clb_ket_qua.json"          # tóm tắt lần nạp bước 1, để mở lại thẻ vẫn thấy


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

    # ------------------------------------------------------------------
    # FA-M7: bước "1. CLB" và "2. Đề thi" — nguồn MỘT lần (TH = chưa thử trên Microsoft / Google thật)
    # ------------------------------------------------------------------
    def _bytes_xlsx(self, file_base64):
        """base64 -> (bytes, None) hoặc (None, lỗi); soát rỗng và cỡ như các nút nạp Excel khác."""
        try:
            du_lieu = base64.b64decode(file_base64 or "", validate=False)
        except Exception as e:
            return None, err("xlsx_read_failed", detail=str(e))
        if not du_lieu:
            return None, err("xlsx_empty")
        return du_lieu, self._soat_co_xlsx(du_lieu)

    @staticmethod
    def _doc_ky_truoc(ky_truoc_base64):
        """CSV (name,buoi,capacity) của kỳ trước -> list dict, hoặc None khi không gửi."""
        if not ky_truoc_base64:
            return None
        van_ban = base64.b64decode(ky_truoc_base64, validate=False).decode("utf-8-sig")
        ds = list(csv.DictReader(io.StringIO(van_ban)))
        for d in ds:
            int(d["capacity"])
            d["name"]
        return ds

    @staticmethod
    def _dong_bao_cao(ds):
        """[{ma, clb, ...}] -> [{ma, clb, noi_dung}] bằng câu tiếng Việt của báo cáo Phiếu CLB."""
        import chuyen_phieu_clb as pc
        return [{"ma": x["ma"], "clb": x["clb"], "noi_dung": pc.NOI_DUNG.get(x["ma"], x["ma"])} for x in ds]

    @staticmethod
    def _clb_hien_thi(clubs):
        return [{"club_id": c["club_id"], "name": c["name"], "buoi": c.get("buoi") or "",
                 "buoi_nhan": so_nhap.nhan_buoi(c.get("buoi") or ""), "loai": c.get("loai"),
                 "loai_nhan": so_nhap.NHAN_LOAI_HIEN_THI.get(c.get("loai"), ""), "chi_tieu": c.get("capacity"),
                 # SG-6: khoá chỉ có khi CLB khai giờ / địa điểm (bảng bước 1 hiện cột khi có).
                 **{k: c[k] for k in so_nhap.KHOA_GIO if c.get(k)}}
                for c in clubs]

    def nap_phieu_clb(self, file_base64, ky_truoc_base64=""):
        """Bước 1: tệp xuất "Phiếu thiết lập CLB" -> `forms/SO_NHAP_CLB_CLB.xlsx` + báo cáo (KHÔNG ghi CLB vào app.db).

        Trả {n_clb, theo_loai, loi, canh_bao, chan, clubs}. Dòng lỗi trong báo cáo: bước vẫn đỏ ở giao diện nhưng
        các CLB hợp lệ vẫn được lưu. Tệp sai dạng hoặc không CLB nào hợp lệ -> `phieu_clb_tep_sai`, tệp cũ giữ nguyên."""
        forms_dot.nap_mau_forms()
        import chuyen_phieu_clb as pc
        from i18n_errors import format_all
        du_lieu, loi_co = self._bytes_xlsx(file_base64)
        if loi_co or du_lieu is None:
            return _fail(loi_co)
        with self._khoa_ghi:
            thu_muc = forms_dot.thu_muc_forms(self.db_path)
            with tempfile.TemporaryDirectory(dir=thu_muc) as tam:
                tep_tai_len = os.path.join(tam, "PHIEU_CLB.xlsx")
                with open(tep_tai_len, "wb") as f:
                    f.write(du_lieu)
                try:
                    ky = self._doc_ky_truoc(ky_truoc_base64)
                    tom = pc.chuyen_phieu(tep_tai_len, os.path.join(tam, "ra"), ky)
                except Exception as e:           # LoiPhieu, tệp không phải xlsx, CSV kỳ trước sai
                    return _fail(err("phieu_clb_tep_sai", detail=str(e)))
                kq = tom["kq"]
                loi, canh_bao = self._dong_bao_cao(kq["loi"]), self._dong_bao_cao(kq["canh_bao"])
                chan = format_all(kq["kiem_truoc"])
                if not kq["clubs"]:
                    return _fail(err("phieu_clb_tep_sai", detail="; ".join(
                        "%s: %s" % (x["clb"], x["noi_dung"]) for x in loi) or "không có CLB hợp lệ nào"))
                theo_loai = {}
                for c in kq["clubs"]:
                    nhan = so_nhap.NHAN_LOAI_HIEN_THI.get(c["loai"], c["loai"])
                    theo_loai[nhan] = theo_loai.get(nhan, 0) + 1
                du = {"n_clb": len(kq["clubs"]), "theo_loai": theo_loai, "loi": loi, "canh_bao": canh_bao, "chan": chan}
                shutil.copyfile(tep_tai_len, os.path.join(thu_muc, "PHIEU_CLB.xlsx"))
                shutil.copyfile(tom["bao_cao"], os.path.join(thu_muc, "BAO_CAO_PHIEU_CLB.md"))
                with open(os.path.join(thu_muc, TEN_TEP_KET_QUA_PHIEU), "w", encoding="utf-8") as f:
                    json.dump(du, f, ensure_ascii=False)
                os.replace(tom["so_nhap"], forms_dot.duong_so_nhap_clb_dot(self.db_path))
        return _ok({**du, "clubs": self._clb_hien_thi(kq["clubs"])})

    def _clb_dot(self):
        """CLB của bước 1 đọc lại từ tệp của đợt; chưa có -> None."""
        forms_dot.nap_mau_forms()
        import so_de_thi
        try:
            return so_de_thi.doc_clb_dot(forms_dot.duong_so_nhap_clb_dot(self.db_path))
        except FileNotFoundError:
            return None

    def get_forms_buoc_12(self):
        """Trạng thái hai bước để vẽ giao diện: {clb: {co, n_clb, theo_loai, clubs, loi, canh_bao, chan},
        de: {co, khop, n_clb_thi, n_cau}}. `khop` = các CLB của đề đúng là các CLB của bước 1 hiện tại."""
        try:
            clubs = self._clb_dot()
        except Exception as e:
            return _fail(err("phieu_clb_tep_sai", detail=str(e)))
        clb = {"co": clubs is not None, "n_clb": 0, "theo_loai": {}, "clubs": [], "loi": [], "canh_bao": [], "chan": []}
        if clubs is not None:
            clb.update(n_clb=len(clubs), clubs=self._clb_hien_thi(clubs))
            try:
                with open(os.path.join(forms_dot.thu_muc_forms(self.db_path), TEN_TEP_KET_QUA_PHIEU),
                          encoding="utf-8") as f:
                    clb.update({k: v for k, v in json.load(f).items() if k in ("theo_loai", "loi", "canh_bao", "chan")})
            except (OSError, ValueError):
                pass
        de = {"co": False, "khop": False, "n_clb_thi": 0, "n_cau": 0}
        try:
            d = forms_dot.doc_de_dot(self.db_path)
        except (FileNotFoundError, ValueError, KeyError):
            d = None
        if d is not None:
            import phan_tich_cau_hoi
            thi = [c for c in d["cau_lac_bo"] if c["de_thi"]]
            de.update(co=True, n_clb_thi=len(thi),
                      n_cau=sum(len(b) for c in d["cau_lac_bo"] for b in phan_tich_cau_hoi.cac_bien_the(c)),
                      khop=clubs is not None and {c["club_id"] for c in d["cau_lac_bo"]} == {c["club_id"] for c in clubs})
        return _ok({"clb": clb, "de": de})

    def tai_mau_de_thi(self, output_path=""):
        """Bước 2: ghi `MAU_DE_THI_KIOSK.xlsx` vào thư mục Tải xuống, trang `CLB` điền sẵn CLB của bước 1."""
        try:
            clubs = self._clb_dot()
        except Exception as e:
            return _fail(err("phieu_clb_tep_sai", detail=str(e)))
        if clubs is None:
            return _fail(err("forms_chua_co_clb"))
        import so_de_thi
        try:
            path = self._duong_xuat(output_path, "MAU_DE_THI_KIOSK.xlsx")
            so_de_thi.ghi_mau_kiosk(path, clubs)
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("de_thi_tep_sai", detail=self._chi_tiet_loi_xuat(e)))
        return _ok({"path": path, "dir": os.path.dirname(path), "n_clb": len(clubs)})

    def nap_de_thi(self, file_base64):
        """Bước 2: tệp đề (Excel) -> `forms/de_thi.json` (cùng dạng tệp CLI đọc). Gom MỌI lỗi (mỗi lỗi một
        `de_thi_tep_sai`); có lỗi thì KHÔNG ghi gì. CLB không có câu hỏi = không thi."""
        try:
            clubs = self._clb_dot()
        except Exception as e:
            return _fail(err("phieu_clb_tep_sai", detail=str(e)))
        if clubs is None:
            return _fail(err("forms_chua_co_clb"))
        du_lieu, loi_co = self._bytes_xlsx(file_base64)
        if loi_co or du_lieu is None:
            return _fail(loi_co)
        import phan_tich_cau_hoi
        import so_de_thi
        with self._khoa_ghi:
            with tempfile.TemporaryDirectory(dir=forms_dot.thu_muc_forms(self.db_path)) as tam:
                tep = os.path.join(tam, "de.xlsx")
                with open(tep, "wb") as f:
                    f.write(du_lieu)
                de, loi = so_de_thi.doc_so_de_thi(tep, clubs)
                if loi:
                    return _fail([err("de_thi_tep_sai", detail=x) for x in loi])
                ra = {"_ghi_chu": "Sinh tu tep Excel de thi o buoc 2 (Chuan bi dot); khong sua tay.", **de}
                tam_json = os.path.join(tam, "de_thi.json")
                with open(tam_json, "w", encoding="utf-8") as f:
                    json.dump(ra, f, ensure_ascii=False, indent=1)
                os.replace(tam_json, forms_dot.duong_de_dot(self.db_path))
        thi = [c for c in de["cau_lac_bo"] if c["de_thi"]]
        return _ok({"n_clb": len(clubs), "n_clb_thi": len(thi),
                    "n_cau": sum(len(b) for c in thi for b in phan_tich_cau_hoi.cac_bien_the(c))})
