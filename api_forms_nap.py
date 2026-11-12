"""FormsNapMixin — bước 4 "Nạp kết quả đăng ký và bài thi" của thẻ "Chuẩn bị đợt" (FA-M9, worker B).

TH = CHƯA thử trên Microsoft thật. Tệp tải lên giữ ở `forms/nap/tai_len/` (để bấm lựa chọn lần hai không phải
chọn lại tệp); kết quả chuyển đổi ghi ở `forms/nap/` (SO_NHAP_CLB.xlsx, EMAIL_MA_HS.csv, BANG_DIEM.xlsx, ...). Việc
nhập vào app.db vẫn do `import_so_nhap` có sẵn làm: lớp này KHÔNG có mã nhập thứ hai.
"""
import base64
import csv
import io
import os
import tempfile

import forms_dot
from api_workspace import CauHinhHong, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok

LOAI_HIEN_THI = ("dang_ky", "bai_thi", "lists")
DUOI_TEP = (".xlsx", ".xlsm", ".csv")


def _ten_an_toan(ten):
    """Tên tệp tải lên -> tên an toàn trong `tai_len` (bỏ thư mục, ký tự lạ)."""
    ten = os.path.basename(str(ten or "").replace("\\", "/")).strip()
    return "".join(c if (c.isalnum() or c in " ._-()[]") else "_" for c in ten)


class FormsNapMixin:

    # ------------------------------------------------------------------
    # đọc dữ liệu chung
    # ------------------------------------------------------------------
    def _duong_forms(self):
        """-> ("A"|"B", None) hoặc (None, lỗi)."""
        try:
            duong = self._luat_nghiem().get("fa_duong")
        except (ValueError, CauHinhHong) as e:
            return None, (loi_cau_hinh(e) if isinstance(e, CauHinhHong) else err("ws_cau_hinh_hong", detail=str(e)))
        if duong not in ("A", "B"):
            return None, err("forms_duong_chua_chon")
        return duong, None

    def _tieu_de_tep(self, ten, du_lieu):
        """Dòng tiêu đề của tệp (không ghi gì vào đợt). Tệp hỏng -> ném ngoại lệ."""
        import chuyen_forms_sang_phan_mem as cv
        if str(ten).lower().endswith(".csv"):
            van_ban = du_lieu.decode("utf-8-sig")
            dong = next(csv.reader(io.StringIO(van_ban)), None)
            if dong is None:
                raise ValueError("tệp trống")
            return [str(x).strip() for x in dong]
        loi = self._soat_co_xlsx(du_lieu)
        if loi:
            raise ValueError(loi["code"])
        with tempfile.TemporaryDirectory(dir=forms_dot.thu_muc_nap(self.db_path)) as tam:
            p = os.path.join(tam, "x.xlsx")
            with open(p, "wb") as f:
                f.write(du_lieu)
            return cv.doc_tep_xuat(p)[0]

    def _de_hoac_none(self):
        """Đề thi của đợt, hoặc None khi chưa có / hỏng (nhận diện tệp không cần đề)."""
        try:
            return forms_dot.doc_de_dot(self.db_path)
        except Exception:
            return None

    @staticmethod
    def _co_bien_the(de):
        import phan_tich_cau_hoi as pt
        return any(len(pt.cac_bien_the(c)) > 1 for c in de["cau_lac_bo"] if c.get("de_thi"))

    def _mot_tep(self, ten, du_lieu, duong, de):
        """Thông tin một tệp: {ten, loai, bien_the_doan, loi}. `loi` = err(...) hoặc None."""
        import chuyen_forms_sang_phan_mem as cv
        d = {"ten": ten, "loai": "khong_ro", "bien_the_doan": None, "loi": None}
        try:
            tieu = self._tieu_de_tep(ten, du_lieu)
        except Exception as e:
            d["loi"] = err("xlsx_read_failed", detail="%s: %s" % (ten, e))
            return d
        loai = cv.nhan_dien_tep(ten, tieu)
        d["loai"] = loai
        if loai == "khong_ro":
            d["loi"] = err("forms_tep_khong_nhan_ra", ten=ten)
        elif loai == "sau_ket_qua":
            d["loi"] = err("forms_tep_sau_ket_qua", ten=ten)
        elif (duong, loai) in (("A", "dang_ky"), ("B", "lists")):
            d["loi"] = err("forms_tep_sai_duong", ten=ten, duong=duong)
        elif loai == "bai_thi" and de is not None:
            d["bien_the_doan"] = cv.doan_bien_the(de, tieu)
        return d

    @staticmethod
    def _giai_ma_tep(f):
        ten = _ten_an_toan((f or {}).get("ten"))
        try:
            du_lieu = base64.b64decode((f or {}).get("base64") or "", validate=False)
        except Exception:
            du_lieu = b""
        return ten, du_lieu

    # ------------------------------------------------------------------
    # FA-M9
    # ------------------------------------------------------------------
    def nhan_dien_tep_forms(self, files):
        """Phân loại từng tệp người dùng thả vào, KHÔNG ghi gì. `files` = [{ten, base64}].

        Trả {tep: [{ten, loai, bien_the_doan, loi}], can_chon_de}. `loai` ∈ dang_ky | bai_thi | lists | sau_ket_qua |
        khong_ro; `loi` (err hoặc None) nói tệp không dùng được ở đường hiện tại; `bien_the_doan` ("A"/"B"/"C"/None) chỉ
        có cho tệp bài thi; `can_chon_de` = đề của đợt có biến thể, nên giao diện bắt chọn khi đoán không ra."""
        duong, loi = self._duong_forms()
        if loi:
            return _fail(loi)
        de = self._de_hoac_none()
        ra = []
        for f in files or []:
            ten, du_lieu = self._giai_ma_tep(f)
            if not ten or not du_lieu:
                ra.append({"ten": ten or "?", "loai": "khong_ro", "bien_the_doan": None,
                           "loi": err("xlsx_empty") if ten else err("forms_tep_khong_nhan_ra", ten="?")})
                continue
            ra.append(self._mot_tep(ten, du_lieu, duong, de))
        return _ok({"tep": ra, "can_chon_de": bool(de) and self._co_bien_the(de)})

    def _tep_da_tai_len(self):
        thu_muc = forms_dot.thu_muc_tai_len(self.db_path)
        return sorted(n for n in os.listdir(thu_muc) if os.path.isfile(os.path.join(thu_muc, n)))

    def get_forms_nap(self):
        """Trạng thái bước 4 để vẽ lại khi mở thẻ: các tệp đã tải lên (đã phân loại) và Sổ nhập đã chuyển (nếu có)."""
        duong, loi = self._duong_forms()
        if loi:
            return _fail(loi)
        de = self._de_hoac_none()
        thu_muc = forms_dot.thu_muc_tai_len(self.db_path)
        tep = []
        for ten in self._tep_da_tai_len():
            with open(os.path.join(thu_muc, ten), "rb") as f:
                tep.append(self._mot_tep(ten, f.read(), duong, de))
        so_nhap = os.path.join(forms_dot.thu_muc_nap(self.db_path), "SO_NHAP_CLB.xlsx")
        return _ok({"tep": tep, "co_so_nhap": os.path.isfile(so_nhap),
                    "can_chon_de": bool(de) and self._co_bien_the(de)})

    def lay_so_nhap_nap(self):
        """Sổ nhập đã chuyển (`forms/nap/SO_NHAP_CLB.xlsx`) dạng base64, để gọi `import_so_nhap` có sẵn."""
        p = os.path.join(forms_dot.thu_muc_nap(self.db_path), "SO_NHAP_CLB.xlsx")
        if not os.path.isfile(p):
            return _fail(err("forms_chua_chuyen_tep"))
        with open(p, "rb") as f:
            return _ok({"ten": "SO_NHAP_CLB.xlsx", "base64": base64.b64encode(f.read()).decode("ascii")})

    @staticmethod
    def _lua_chon_sach(lua_chon):
        lc = lua_chon if isinstance(lua_chon, dict) else {}
        kq = {}
        if lc.get("dieu_chinh") in ("ap_dung", "giu"):
            kq["dieu_chinh"] = lc["dieu_chinh"]
        bo = []
        for x in lc.get("bo_cau") or []:
            try:
                clb, de_chu, so = x
                bo.append((str(clb), str(de_chu), int(so)))
            except (TypeError, ValueError):
                continue
        if bo:
            kq["bo_cau"] = bo
        return kq

    def chuyen_tep_forms(self, files, bien_the, lua_chon):
        """Chuyển các tệp Forms / List thành Sổ nhập FA (`forms/nap/SO_NHAP_CLB.xlsx`), chưa nhập vào app.db.

        `files` = [{ten, base64}] (lưu vào `forms/nap/tai_len/`, thay bộ tệp cũ); rỗng / None = dùng lại các tệp đã tải
        lên (bấm lựa chọn lần hai). `bien_the` = {tên tệp: "A"|"B"|"C"} (thiếu thì dùng đề đoán được). `lua_chon` =
        {dieu_chinh: "ap_dung"|"giu", bo_cau: [[clb, đề, số câu]]}.

        Trả {trang_thai: "xong"|"cho_xac_nhan", n_hoc_sinh, n_bai_thi, canh_bao, ghi_chu, cau_co_co, xem_truoc,
        cho_xac_nhan: {clb, bao_cao, thong_bao}?}. Lỗi đề / tệp -> `forms_khong_chuyen_duoc`, không ghi Sổ."""
        import chuyen_forms_sang_phan_mem as cv
        duong, loi = self._duong_forms()
        if loi:
            return _fail(loi)
        try:
            de = forms_dot.doc_de_dot(self.db_path)
        except FileNotFoundError:
            return _fail(err("forms_chua_co_de"))
        except Exception as e:
            return _fail(err("de_thi_tep_sai", detail=str(e)))
        so_nhap_clb = forms_dot.duong_so_nhap_clb_dot(self.db_path)
        if not os.path.isfile(so_nhap_clb):
            return _fail(err("forms_chua_co_clb"))
        thu_muc = forms_dot.thu_muc_tai_len(self.db_path)
        with self._khoa_ghi:
            if files:
                for ten in self._tep_da_tai_len():
                    os.remove(os.path.join(thu_muc, ten))
                for f in files:
                    ten, du_lieu = self._giai_ma_tep(f)
                    if ten and du_lieu and ten.lower().endswith(DUOI_TEP):
                        with open(os.path.join(thu_muc, ten), "wb") as g:
                            g.write(du_lieu)
            ten_cac_tep = self._tep_da_tai_len()
            if not ten_cac_tep:
                return _fail(err("forms_thieu_tep_nap"))
            theo_loai = {"dang_ky": [], "bai_thi": [], "lists": []}
            loi_tep, doan = [], {}
            for ten in ten_cac_tep:
                with open(os.path.join(thu_muc, ten), "rb") as g:
                    d = self._mot_tep(ten, g.read(), duong, de)
                if d["loi"]:
                    loi_tep.append(d["loi"])
                else:
                    theo_loai[d["loai"]].append(ten)
                    doan[ten] = d["bien_the_doan"]
            if loi_tep:
                return _fail(loi_tep)
            nguon = theo_loai["lists"] if duong == "A" else theo_loai["dang_ky"]
            if not nguon:
                return _fail(err("forms_thieu_tep_dang_ky", duong=duong))
            if duong == "A" and len(nguon) > 1:
                return _fail(err("forms_nhieu_tep_list"))
            chon = {_ten_an_toan(k): v for k, v in (bien_the or {}).items()}
            bien_the_tep, thieu = None, []
            if self._co_bien_the(de):
                bien_the_tep = {}
                for ten in theo_loai["bai_thi"]:
                    chu = chon.get(ten) or doan.get(ten)
                    if chu not in ("A", "B", "C"):
                        thieu.append(err("forms_can_chon_de", ten=ten))
                    else:
                        bien_the_tep[ten] = chu
            if thieu:
                return _fail(thieu)
            dd = lambda ds: [os.path.join(thu_muc, n) for n in ds]  # noqa: E731
            try:
                kq = cv.chuyen_fa_daa_du_lieu(
                    forms_dot.thu_muc_nap(self.db_path), de, so_nhap_clb,
                    dang_ky_xlsx=dd(theo_loai["dang_ky"]) if duong == "B" else (),
                    lists=dd(nguon)[0] if duong == "A" else None,
                    quiz_xlsx=dd(theo_loai["bai_thi"]), bien_the_tep=bien_the_tep,
                    lua_chon=self._lua_chon_sach(lua_chon))
            except Exception as e:
                return _fail(err("forms_khong_chuyen_duoc", detail=str(e)))
        if kq["trang_thai"] == "loi":
            return _fail(err("forms_khong_chuyen_duoc", detail=kq["thong_bao"]))
        if kq["trang_thai"] == "cho_xac_nhan":
            return _ok({"trang_thai": "cho_xac_nhan",
                        "cho_xac_nhan": {"clb": kq["clb"], "bao_cao": kq["bao_cao"], "thong_bao": kq["thong_bao"]}})
        du = {"trang_thai": "xong", "n_hoc_sinh": kq["n_hoc_sinh"], "n_bai_thi": kq["n_bai_thi"],
              "canh_bao": [{"dong": d, "ma": m, "noi_dung": n} for d, m, n in kq["canh_bao"]],
              "ghi_chu": kq["ghi_chu"], "cau_co_co": kq["cau_co_co"], "xem_truoc": None, "loi_xem_truoc": []}
        so = self.lay_so_nhap_nap()
        if so["ok"]:
            xt = self.xem_truoc_so_nhap(so["data"]["base64"])
            if xt["ok"]:
                du["xem_truoc"] = xt["data"]
            else:
                du["loi_xem_truoc"] = xt["errors"]
        return _ok(du)
