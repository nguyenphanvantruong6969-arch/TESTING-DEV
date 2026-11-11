"""SauXepMixin — sau khi xếp (FA gaps, V§9.2–9.3): điểm danh 3 buổi đầu, giải phóng chỗ, mời danh sách chờ.

Mọi đổi chỗ là một dòng GHI THÊM trong `fa_dieu_chinh` (`fa_sau_xep.ghi_dieu_chinh`); không hàm nào ở đây ghi
`match_results` hay `run_history`. Cờ `rules.fa_diem_danh` (mặc định TẮT, cần `fa_daa`).
"""

import datetime

import fa_sau_xep as sx
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import BUOI_MAC_DINH, dung_fa_daa, khoa_sap_buoi

CHU_TRANG_THAI = {"CO_MAT": "Có mặt", "VANG_CO_PHEP": "Vắng có phép", "VANG_KHONG_PHEP": "Vắng không phép"}


class SauXepMixin:

    def _co_diem_danh(self) -> bool:
        luat = self._luat_nghiem()
        return dung_fa_daa(luat) and luat.get("fa_diem_danh") is True

    @staticmethod
    def _diem_danh_cua(cur, run_id_base, buoi, club_id) -> dict:
        """{student_id: {buoi_so: trang_thai}} của một CLB trong lần chạy gốc."""
        ra: dict = {}
        for sid, so, tt in cur.execute(
                "SELECT student_id, buoi_so, trang_thai FROM fa_diem_danh "
                "WHERE run_id_base = ? AND buoi = ? AND club_id = ?", (run_id_base, buoi, club_id)):
            ra.setdefault(sid, {})[so] = tt
        return ra

    @staticmethod
    def _clb_va_buoi(cur) -> dict:
        return {r[0]: {"name": r[1] or r[0], "buoi": r[2]} for r in cur.execute(
            "SELECT c.club_id, c.name, (SELECT MIN(m.buoi) FROM match_results m WHERE m.club_id = c.club_id) "
            "FROM clubs c")}

    def _danh_sach_diem_danh(self, cur):
        """(các CLB có thành viên hay em đã giải phóng, {club_id: [dòng học sinh]})."""
        vi_tri, _, run_goc = sx.doc_vi_tri(cur)
        dc = sx.doc_dieu_chinh(cur)
        clb = self._clb_va_buoi(cur)
        ten = {r[0]: r[1] or "" for r in cur.execute("SELECT student_id, name FROM students")}
        thanh_vien: dict = {}
        for (sid, buoi), cid in vi_tri.items():
            if cid:
                thanh_vien.setdefault((cid, buoi), set()).add(sid)
        for d in dc:
            if d["kind"] == "release" and d["run_id_base"] == run_goc.get(d["buoi"]):
                thanh_vien.setdefault((d["club_from"], d["buoi"]), set())
        ra = {}
        for (cid, buoi), ds in thanh_vien.items():
            run = run_goc.get(buoi)
            giai_phong = sx.da_giai_phong_khoi(dc, run_goc, buoi, cid) - ds
            dd = self._diem_danh_cua(cur, run, buoi, cid)
            dong = []
            for sid in sorted(ds | giai_phong):
                m = dd.get(sid, {})
                dong.append({"student_id": sid, "name": ten.get(sid, ""),
                             "buoi_1": m.get(1, ""), "buoi_2": m.get(2, ""), "buoi_3": m.get(3, ""),
                             "so_vang_khong_phep": sum(1 for v in m.values() if v == "VANG_KHONG_PHEP"),
                             "da_giai_phong": sid in giai_phong})
            ra[cid] = dong
        thu_tu = sorted(ra, key=lambda c: (khoa_sap_buoi((clb.get(c) or {}).get("buoi") or ""), c))
        ds_clb = [{"club_id": c, "name": (clb.get(c) or {}).get("name", c),
                   "buoi": (clb.get(c) or {}).get("buoi") or ""} for c in thu_tu]
        return ds_clb, ra

    def get_diem_danh(self, club_id: str = ""):
        """GAP-1: danh sách điểm danh của một CLB (mặc định CLB đầu tiên). Cờ tắt -> {bat: False}."""
        try:
            if not self._co_diem_danh():
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                ds_clb, ra = self._danh_sach_diem_danh(cur)
            chon = club_id if club_id in ra else (ds_clb[0]["club_id"] if ds_clb else "")
            return _ok({"bat": True, "clubs": ds_clb, "club_id": chon, "hoc_sinh": ra.get(chon, [])})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def luu_diem_danh(self, club_id: str, student_id: str, buoi_so, trang_thai: str):
        """GAP-1: ghi một ô điểm danh ("" = xoá). Đủ 2/3 buổi vắng không phép -> giải phóng chỗ (một dòng
        `release`), rồi mời người đầu danh sách chờ (GAP-2). Một giao dịch."""
        try:
            if not self._co_diem_danh():
                return _fail(err("fa_diem_danh_chua_bat"))
            if buoi_so not in (1, 2, 3) or isinstance(buoi_so, bool) or \
                    (trang_thai not in sx.TRANG_THAI_DIEM_DANH and trang_thai != ""):
                return _fail(err("diem_danh_gia_tri_sai"))
            with self._ket_noi_ghi() as cur:
                vi_tri, _, run_goc = sx.doc_vi_tri(cur)
                buoi = next((b for (s, b), c in vi_tri.items() if s == student_id and c == club_id), None)
                dc = sx.doc_dieu_chinh(cur)
                if buoi is None:
                    buoi = next((b for b in run_goc if student_id in sx.da_giai_phong_khoi(dc, run_goc, b, club_id)),
                                None)
                if buoi is None:
                    return _fail(err("diem_danh_khong_thuoc_clb", student_id=student_id, club_id=club_id))
                run = run_goc[buoi]
                if trang_thai == "":
                    cur.execute("DELETE FROM fa_diem_danh WHERE run_id_base = ? AND buoi = ? AND club_id = ? "
                                "AND student_id = ? AND buoi_so = ?", (run, buoi, club_id, student_id, buoi_so))
                else:
                    cur.execute(
                        "INSERT INTO fa_diem_danh (run_id_base, buoi, club_id, student_id, buoi_so, trang_thai, "
                        "updated_at) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (run_id_base, buoi, club_id, "
                        "student_id, buoi_so) DO UPDATE SET trang_thai = excluded.trang_thai, "
                        "updated_at = excluded.updated_at",
                        (run, buoi, club_id, student_id, buoi_so, trang_thai,
                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                giai_phong = False
                con_la_thanh_vien = vi_tri.get((student_id, buoi)) == club_id
                if con_la_thanh_vien and sx.can_giai_phong(
                        self._diem_danh_cua(cur, run, buoi, club_id).get(student_id, {})):
                    sx.ghi_dieu_chinh(cur, run, buoi, student_id, club_id, None, "release",
                                      actor="diem_danh", note="vang_2_3")
                    giai_phong = True
                    sx.moi_tiep(cur, buoi, club_id)       # GAP-2: mời người đầu danh sách chờ
                return _ok({"da_giai_phong": giai_phong or not con_la_thanh_vien})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    def export_diem_danh(self, output_path: str = ""):
        """GAP-1: `diem_danh.xlsx` — mỗi CLB một trang: mã, họ tên, 3 buổi, số buổi vắng không phép, đã giải phóng."""
        return self._khoa_xuat(self._export_diem_danh_da_khoa, output_path)

    def _export_diem_danh_da_khoa(self, output_path: str = ""):
        from openpyxl import Workbook

        from so_excel import Trang
        try:
            if not self._co_diem_danh():
                return _fail(err("fa_diem_danh_chua_bat"))
            with self._ket_noi_doc() as cur:
                ds_clb, ra = self._danh_sach_diem_danh(cur)
            wb = Workbook()
            wb.remove(wb.active)
            da_dung: set = set()
            for c in ds_clb:
                t = Trang(wb.create_sheet(sx.ten_trang_xlsx(c["name"], da_dung)))
                t.o(1, 1, c["name"], do_rong=False)
                t.hang = 3
                t.bang(["Mã học sinh", "Họ tên", "Buổi 1", "Buổi 2", "Buổi 3", "Số buổi vắng không phép",
                        "Đã giải phóng chỗ"],
                       [[h["student_id"], h["name"]] + [CHU_TRANG_THAI.get(h["buoi_%d" % i], "") for i in (1, 2, 3)]
                        + [h["so_vang_khong_phep"], "Có" if h["da_giai_phong"] else ""]
                        for h in ra[c["club_id"]]], khoa=True)
                t.xong()
            if not ds_clb:
                wb.create_sheet("Điểm danh")
            duong = self._duong_xuat(output_path, "diem_danh.xlsx")
            wb.save(duong)
            return _ok({"path": duong, "n_clb": len(ds_clb)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # GAP-2 -----------------------------------------------------------------------------------------------------------
    def get_moi_cho_trong(self):
        """GAP-2: mọi lời mời vào chỗ trống, mới nhất trước, kèm trạng thái CHO / NHAN / TU_CHOI / HET_HAN.
        Cờ tắt -> {bat: False}."""
        try:
            if not self._co_diem_danh():
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                dc = sx.doc_dieu_chinh(cur)
                vi_tri, _, _ = sx.doc_vi_tri(cur)
                ten_hs = {r[0]: r[1] or "" for r in cur.execute("SELECT student_id, name FROM students")}
                ten_clb = {r[0]: r[1] or r[0] for r in cur.execute("SELECT club_id, name FROM clubs")}
            tt = sx.trang_thai_moi(dc)
            moi = [{"id": d["id"], "buoi": d["buoi"], "club_id": d["club_to"],
                    "club_name": ten_clb.get(d["club_to"], d["club_to"]), "student_id": d["student_id"],
                    "name": ten_hs.get(d["student_id"], ""),
                    "club_hien_tai": vi_tri.get((d["student_id"], d["buoi"])) or "",
                    "created_at": d["created_at"], "trang_thai": tt[d["id"]]}
                   for d in sorted(dc, key=lambda x: -x["id"]) if d["kind"] == "invite_offer"]
            return _ok({"bat": True, "moi": moi})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def tra_loi_moi(self, id_moi, ket_qua: str):
        """GAP-2: trả lời một lời mời đang chờ: "nhan" (đổi chỗ), "tu_choi", "het_han". Sau đó mời người kế tiếp
        (CLB vừa bỏ khi nhận; cùng CLB khi từ chối / hết hạn). Một giao dịch."""
        try:
            if not self._co_diem_danh():
                return _fail(err("fa_diem_danh_chua_bat"))
            if ket_qua not in sx.KIND_TRA_LOI:
                return _fail(err("diem_danh_gia_tri_sai"))
            with self._ket_noi_ghi() as cur:
                vi_tri, _, run_goc = sx.doc_vi_tri(cur)
                m = sx.moi_dang_cho(sx.doc_dieu_chinh(cur), run_goc).get(id_moi)
                if m is None:
                    return _fail(err("moi_khong_con_cho"))
                hien = vi_tri.get((m["student_id"], m["buoi"]))
                if ket_qua == "nhan":
                    sx.ghi_dieu_chinh(cur, m["run_id_base"], m["buoi"], m["student_id"], hien, m["club_to"],
                                      "invite_accept", actor="moi_cho")
                    sx.moi_tiep(cur, m["buoi"], hien)
                else:
                    sx.ghi_dieu_chinh(cur, m["run_id_base"], m["buoi"], m["student_id"], hien, m["club_to"],
                                      sx.KIND_TRA_LOI[ket_qua], actor="moi_cho")
                    sx.moi_tiep(cur, m["buoi"], m["club_to"])
                return _ok({"id": id_moi, "ket_qua": ket_qua})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    # GAP-3 -----------------------------------------------------------------------------------------------------------
    def _co_khieu_nai(self):
        """(bật?, số ngày nhận khiếu nại)."""
        luat = self._luat_nghiem()
        return dung_fa_daa(luat) and luat.get("fa_khieu_nai") is True, luat.get("fa_khieu_nai_so_ngay",
                                                                                sx.SO_NGAY_KHIEU_NAI)

    COT_KHIEU_NAI = ("id", "created_at", "student_id", "buoi", "ghi_chu", "run_id_base", "trang_thai", "xu_ly_at",
                     "xu_ly_ghi_chu")

    def _doc_khieu_nai(self, cur):
        ds = [dict(zip(self.COT_KHIEU_NAI, r)) for r in cur.execute(
            "SELECT %s FROM fa_khieu_nai ORDER BY id DESC" % ", ".join(self.COT_KHIEU_NAI))]
        anh = sx.anh_huong_sau_chay_lai(ds, sx.run_goc_theo_buoi(cur), sx.doc_dieu_chinh(cur))
        for k in ds:
            k.update(anh.get(k["id"], {"da_chay_lai": False, "dieu_chinh_cu": []}))
        return ds

    def gui_khieu_nai(self, student_id: str, buoi: str, ghi_chu: str = ""):
        """GAP-3: gửi một khiếu nại lỗi dữ liệu cho (học sinh, buổi), trong hạn từ lúc công bố kết quả buổi đó."""
        try:
            bat, so_ngay = self._co_khieu_nai()
            if not bat:
                return _fail(err("fa_khieu_nai_chua_bat"))
            with self._ket_noi_ghi() as cur:
                run_goc = sx.run_goc_theo_buoi(cur)
                co = cur.execute("SELECT 1 FROM match_results WHERE student_id = ? AND buoi = ?",
                                 (student_id, buoi)).fetchone()
                if not co or buoi not in run_goc:
                    return _fail(err("khieu_nai_khong_hop_le", student_id=student_id, buoi=buoi))
                run_at = cur.execute("SELECT run_at FROM run_history WHERE run_id = ?",
                                     (run_goc[buoi],)).fetchone()[0]
                luc = sx.bay_gio()
                if not sx.trong_han_khieu_nai(run_at, luc, so_ngay):
                    return _fail(err("khieu_nai_qua_han", so_ngay=so_ngay))
                if cur.execute("SELECT 1 FROM fa_khieu_nai WHERE student_id = ? AND buoi = ? AND trang_thai = 'CHO'",
                               (student_id, buoi)).fetchone():
                    return _fail(err("khieu_nai_trung", student_id=student_id))
                cur.execute("INSERT INTO fa_khieu_nai (created_at, student_id, buoi, loai, ghi_chu, run_id_base, "
                            "trang_thai) VALUES (?, ?, ?, 'DATA_ERROR', ?, ?, 'CHO')",
                            (luc.strftime("%Y-%m-%d %H:%M:%S"), student_id, buoi, str(ghi_chu or ""),
                             run_goc[buoi]))
                return _ok({"id": cur.lastrowid})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    def get_khieu_nai(self):
        """GAP-3: mọi khiếu nại (mới nhất trước), kèm đã chạy lại chưa và các điều chỉnh của lần chạy cũ."""
        try:
            bat, so_ngay = self._co_khieu_nai()
            if not bat:
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                ds = self._doc_khieu_nai(cur)
                ten = {r[0]: r[1] or "" for r in cur.execute("SELECT student_id, name FROM students")}
                ds_buoi = sorted(sx.run_goc_theo_buoi(cur), key=khoa_sap_buoi)
            for k in ds:
                k["name"] = ten.get(k["student_id"], "")
            return _ok({"bat": True, "so_ngay": so_ngay, "ds_buoi": ds_buoi, "khieu_nai": ds})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def xu_ly_khieu_nai(self, id_kn, chap_nhan: bool, ghi_chu: str = ""):
        """GAP-3: quản trị chấp nhận / từ chối. Chấp nhận ghi thêm một dòng `appeal_rerun`; sửa dữ liệu rồi chạy lại
        như thường (hạt giống đã khoá) — hàm này không chạy xếp, không sửa kết quả."""
        try:
            bat, _ = self._co_khieu_nai()
            if not bat:
                return _fail(err("fa_khieu_nai_chua_bat"))
            with self._ket_noi_ghi() as cur:
                k = cur.execute("SELECT student_id, buoi, run_id_base, trang_thai FROM fa_khieu_nai WHERE id = ?",
                                (id_kn,)).fetchone()
                if not k or k[3] != "CHO":
                    return _fail(err("khieu_nai_da_xu_ly"))
                cur.execute("UPDATE fa_khieu_nai SET trang_thai = ?, xu_ly_at = ?, xu_ly_ghi_chu = ? WHERE id = ?",
                            ("CHAP_NHAN" if chap_nhan else "TU_CHOI",
                             sx.bay_gio().strftime("%Y-%m-%d %H:%M:%S"), str(ghi_chu or ""), id_kn))
                if chap_nhan:
                    vi_tri, _, _ = sx.doc_vi_tri(cur)
                    hien = vi_tri.get((k[0], k[1]))
                    sx.ghi_dieu_chinh(cur, k[2], k[1], k[0], hien, hien, "appeal_rerun", actor="khieu_nai",
                                      note="khieu_nai:%d" % id_kn)
                return _ok({"id": id_kn, "chap_nhan": bool(chap_nhan)})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    def export_khieu_nai(self, output_path: str = ""):
        """GAP-3: `khieu_nai.csv` (UTF-8 có BOM, chặn công thức)."""
        return self._khoa_xuat(self._export_khieu_nai_da_khoa, output_path)

    def _export_khieu_nai_da_khoa(self, output_path: str = ""):
        from api_chung import _ghi_csv
        try:
            bat, _ = self._co_khieu_nai()
            if not bat:
                return _fail(err("fa_khieu_nai_chua_bat"))
            with self._ket_noi_doc() as cur:
                ds = self._doc_khieu_nai(cur)
            duong = self._duong_xuat(output_path, "khieu_nai.csv")
            _ghi_csv(duong, ["id", "student_id", "buoi", "trang_thai", "created_at", "ghi_chu", "xu_ly_ghi_chu",
                             "da_chay_lai", "dieu_chinh_cu"],
                     [[k["id"], k["student_id"], k["buoi"], k["trang_thai"], k["created_at"], k["ghi_chu"] or "",
                       k["xu_ly_ghi_chu"] or "", "1" if k["da_chay_lai"] else "0",
                       ";".join(str(i) for i in k["dieu_chinh_cu"])] for k in sorted(ds, key=lambda x: x["id"])])
            return _ok({"path": duong, "n_rows": len(ds)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # GAP-4 -----------------------------------------------------------------------------------------------------------
    def _co_vong_2(self) -> bool:
        luat = self._luat_nghiem()
        return dung_fa_daa(luat) and luat.get("fa_vong_2") is True

    def _du_lieu_vong_2(self, cur, buoi):
        """(buoi, ds_buoi, da_chay, [em theo thứ tự bốc thăm], {club: còn}, run_goc, vi_tri)."""
        from rbda_priority_pipeline import sinh_stb_theo_buoi
        vi_tri, _, run_goc = sx.doc_vi_tri(cur)
        ds_buoi = sorted(run_goc, key=khoa_sap_buoi)
        buoi = buoi if buoi in run_goc else (ds_buoi[0] if ds_buoi else "")
        dc = sx.doc_dieu_chinh(cur)
        da_chay = any(d["kind"] == "round2" and d["buoi"] == buoi and d["run_id_base"] == run_goc.get(buoi)
                      for d in dc)
        nv: dict = {}
        for sid, cid in cur.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
            nv.setdefault(sid, []).append(cid)
        clubs = {r[0]: {"capacity": r[1], "buoi": r[2] or BUOI_MAC_DINH}
                 for r in cur.execute("SELECT club_id, capacity, buoi FROM clubs")}
        tat_ca_buoi = sorted({c["buoi"] for c in clubs.values()}, key=khoa_sap_buoi)
        stb_goc = {r[0]: r[1] for r in cur.execute(
            "SELECT student_id, stb_number FROM students WHERE stb_number IS NOT NULL")}
        seed = (cur.execute("SELECT seed FROM stb_lock WHERE id = 1").fetchone() or [None])[0] or 0
        stb = sinh_stb_theo_buoi(stb_goc, tat_ca_buoi, seed, "stb_ngay").get(buoi, stb_goc) if buoi else {}
        can = sx.can_vong_2(vi_tri, nv, buoi)
        thu_tu = sorted(can, key=lambda s: (stb.get(s, float("inf")), s))
        dang = {}
        for d in sx.moi_dang_cho(dc, run_goc).values():
            if d["buoi"] == buoi:
                dang[d["club_to"]] = dang.get(d["club_to"], 0) + 1
        con = sx.cho_con_lai(vi_tri, {c: v["capacity"] for c, v in clubs.items()}, dang, buoi,
                             {c for c, v in clubs.items() if v["buoi"] == buoi})
        return buoi, ds_buoi, da_chay, thu_tu, con, run_goc, vi_tri

    def get_vong_2(self, buoi: str = ""):
        """GAP-4: học sinh cần vòng 2 (theo thứ tự bốc thăm của buổi) và chỗ còn trống. Cờ tắt -> {bat: False}."""
        try:
            if not self._co_vong_2():
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                buoi, ds_buoi, da_chay, thu_tu, con, _, vi_tri = self._du_lieu_vong_2(cur, buoi)
                ten = {r[0]: r[1] or "" for r in cur.execute("SELECT student_id, name FROM students")}
                ten_clb = {r[0]: r[1] or r[0] for r in cur.execute("SELECT club_id, name FROM clubs")}
            return _ok({"bat": True, "buoi": buoi, "ds_buoi": ds_buoi, "da_chay": da_chay,
                        "hoc_sinh": [{"student_id": s, "name": ten.get(s, ""),
                                      "club_hien_tai": vi_tri.get((s, buoi)) or ""} for s in thu_tu],
                        "cho_con_lai": [{"club_id": c, "name": ten_clb.get(c, c), "con": n} for c, n in con.items()]})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def chay_vong_2_api(self, buoi: str, chon: dict):
        """GAP-4: chạy vòng 2 của `buoi` MỘT lượt với lựa chọn {học sinh: [club_id theo thứ tự muốn]}; mỗi em được xếp
        là một dòng `round2`. Không sửa kết quả xếp."""
        try:
            if not self._co_vong_2():
                return _fail(err("fa_vong_2_chua_bat"))
            if not isinstance(chon, dict):
                return _fail(err("vong_2_lua_chon_sai", student_id="", club_id=""))
            with self._ket_noi_ghi() as cur:
                buoi, _, da_chay, thu_tu, con, run_goc, vi_tri = self._du_lieu_vong_2(cur, buoi)
                if da_chay:
                    return _fail(err("vong_2_da_chay"))
                hop_le = set(thu_tu)
                ds_clb = {r[0] for r in cur.execute("SELECT club_id, buoi FROM clubs")
                          if (r[1] or BUOI_MAC_DINH) == buoi}
                for sid, ds in chon.items():
                    if sid not in hop_le:
                        return _fail(err("vong_2_lua_chon_sai", student_id=sid, club_id=""))
                    for cid in ds or []:
                        if cid not in ds_clb:
                            return _fail(err("vong_2_lua_chon_sai", student_id=sid, club_id=cid))
                xep = sx.chay_vong_2(thu_tu, chon, con)
                for sid, cid in xep:
                    sx.ghi_dieu_chinh(cur, run_goc[buoi], buoi, sid, vi_tri.get((sid, buoi)), cid, "round2",
                                      actor="vong_2")
                da_xep = {s for s, _ in xep}
                return _ok({"buoi": buoi, "xep": [{"student_id": s, "club_id": c} for s, c in xep],
                            "bo_qua": [s for s in thu_tu if s in chon and s not in da_xep]})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    # GAP-5 / GAP-6 ---------------------------------------------------------------------------------------------------
    def _co_phan_hoi(self) -> bool:
        luat = self._luat_nghiem()
        return dung_fa_daa(luat) and luat.get("fa_phan_hoi") is True

    def _doc_phan_hoi(self, cur):
        return [dict(zip(sx.COT_PHAN_HOI, r)) for r in cur.execute(
            "SELECT %s FROM fa_phan_hoi ORDER BY id" % ", ".join(sx.COT_PHAN_HOI))]

    def gui_phan_hoi(self, student_id: str, hai_long, hieu_ly_do, kho_nhat: str):
        """GAP-5: ba câu một chạm của một học sinh ở kiosk (lần sau thay lần trước khi tổng hợp)."""
        try:
            if not self._co_phan_hoi():
                return _fail(err("fa_phan_hoi_chua_bat"))
            if isinstance(hai_long, bool) or hai_long not in (1, 2, 3, 4, 5) or not isinstance(hieu_ly_do, bool) \
                    or kho_nhat not in sx.KHO_NHAT:
                return _fail(err("phan_hoi_gia_tri_sai"))
            with self._ket_noi_ghi() as cur:
                if not cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,)).fetchone():
                    return _fail(err("student_not_found", student_id=student_id))
                cur.execute("INSERT INTO fa_phan_hoi (created_at, student_id, nguon, loai, hai_long, hieu_ly_do, "
                            "kho_nhat) VALUES (?, ?, 'kiosk', 'ket_qua', ?, ?, ?)",
                            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), student_id, hai_long,
                             1 if hieu_ly_do else 0, kho_nhat))
                return _ok({"id": cur.lastrowid})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    def get_phan_hoi_tong_hop(self):
        """GAP-5/6: tổng hợp (không có mã học sinh) của phản hồi 3 câu và khảo sát tuần 3."""
        try:
            if not self._co_phan_hoi():
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                rows = self._doc_phan_hoi(cur)
            return _ok({"bat": True, "ket_qua": sx.tong_hop_phan_hoi(rows, "ket_qua"),
                        "tuan_3": sx.tong_hop_phan_hoi(rows, "tuan_3")})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def nhap_phan_hoi_forms(self, file_base64: str):
        """GAP-5/6 (TH): nạp tệp Excel xuất từ biểu mẫu phản hồi / khảo sát tuần 3. Mã học sinh lạ bị bỏ (đếm)."""
        import base64
        import binascii
        import io

        from openpyxl import load_workbook
        try:
            if not self._co_phan_hoi():
                return _fail(err("fa_phan_hoi_chua_bat"))
            try:
                wb = load_workbook(io.BytesIO(base64.b64decode(file_base64, validate=True)), read_only=True,
                                   data_only=True)
                dong = sx.doc_tep_forms_phan_hoi(wb.worksheets[0].iter_rows(values_only=True))
            except (ValueError, binascii.Error, OSError, KeyError, IndexError) as e:
                return _fail(err("phan_hoi_tep_sai", detail=str(e)))
            except Exception as e:                     # zipfile.BadZipFile, InvalidFileException…
                return _fail(err("phan_hoi_tep_sai", detail=type(e).__name__))
            luc = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dem = {"ket_qua": 0, "tuan_3": 0}
            bo_qua = set()
            with self._ket_noi_ghi() as cur:
                co = {r[0] for r in cur.execute("SELECT student_id FROM students")}
                for d in dong:
                    if d["student_id"] not in co:
                        bo_qua.add(d["student_id"])
                        continue
                    cur.execute(
                        "INSERT INTO fa_phan_hoi (created_at, student_id, nguon, loai, hai_long, hieu_ly_do, "
                        "kho_nhat, con_di, muon_doi) VALUES (?, ?, 'forms', ?, ?, ?, ?, ?, ?)",
                        (luc, d["student_id"], d["loai"], d["hai_long"], d["hieu_ly_do"], d["kho_nhat"],
                         d["con_di"], d["muon_doi"]))
                    dem[d["loai"]] += 1
            return _ok({"n_ket_qua": dem["ket_qua"], "n_tuan_3": dem["tuan_3"], "bo_qua": len(bo_qua)})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    def export_phan_hoi(self, output_path: str = ""):
        """GAP-5/6: `phan_hoi.xlsx` — trang "Tổng hợp" (không có mã), "Chi tiết" (mã học sinh, không có tên)."""
        return self._khoa_xuat(self._export_phan_hoi_da_khoa, output_path)

    def _export_phan_hoi_da_khoa(self, output_path: str = ""):
        from openpyxl import Workbook

        from so_excel import Trang
        try:
            if not self._co_phan_hoi():
                return _fail(err("fa_phan_hoi_chua_bat"))
            with self._ket_noi_doc() as cur:
                rows = self._doc_phan_hoi(cur)
            wb = Workbook()
            t = Trang(wb.active)
            wb.active.title = "Tổng hợp"
            tq = sx.tong_hop_phan_hoi(rows, "ket_qua")
            t.bang(["Chỉ số", "Giá trị"], [
                ["Số học sinh trả lời (3 câu)", tq["n"]],
                ["Hài lòng trung bình (1–5)", "" if tq["hai_long_tb"] is None else round(tq["hai_long_tb"], 2)],
                *[["Hài lòng = %d" % k, v] for k, v in tq["hai_long_dem"].items()],
                ["Tỉ lệ hiểu lý do", "" if tq["hieu_ly_do_ty_le"] is None else round(tq["hieu_ly_do_ty_le"], 3)],
                *[["Khó nhất: %s" % k, v] for k, v in tq["kho_nhat_dem"].items()],
            ])
            t.xong()
            t2 = Trang(wb.create_sheet("Chi tiết"))
            t2.bang(["Mã học sinh", "Loại", "Nguồn", "Hài lòng", "Hiểu lý do", "Khó nhất", "Còn đi", "Muốn đổi",
                     "Thời điểm"],
                    [[r["student_id"], r["loai"], r["nguon"], r["hai_long"], r["hieu_ly_do"], r["kho_nhat"],
                      r["con_di"], r["muon_doi"], r["created_at"]] for r in rows], khoa=True)
            t2.xong()
            t3 = Trang(wb.create_sheet("Tuần 3"))
            tw = sx.tong_hop_phan_hoi(rows, "tuan_3")
            t3.bang(["Chỉ số", "Giá trị"], [
                ["Số học sinh trả lời (tuần 3)", tw["n"]],
                ["Tỉ lệ còn đi CLB", "" if tw["con_di_ty_le"] is None else round(tw["con_di_ty_le"], 3)],
                ["Tỉ lệ muốn đổi CLB", "" if tw["muon_doi_ty_le"] is None else round(tw["muon_doi_ty_le"], 3)],
            ])
            t3.xong()
            duong = self._duong_xuat(output_path, "phan_hoi.xlsx")
            wb.save(duong)
            return _ok({"path": duong, "n_rows": len(rows)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # GAP-8 -----------------------------------------------------------------------------------------------------------
    def get_dashboard(self):
        """GAP-8 (V§11): mọi chỉ số của bảng điều khiển quản trị. Chỉ đọc. FA tắt -> {bat: False}."""
        try:
            if not dung_fa_daa(self._luat_nghiem()):
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                du = sx.doc_du_lieu_dashboard(cur)
            return _ok({"bat": True, "chi_so": sx.chi_so_dashboard(du)})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def export_dashboard(self, output_path: str = ""):
        """GAP-8: `dashboard.xlsx` một trang (Chỉ số, Giá trị, Mục tiêu, Đạt, Nguồn); thiếu dữ liệu ghi "chưa có dữ
        liệu". Không có mã hay tên học sinh."""
        return self._khoa_xuat(self._export_dashboard_da_khoa, output_path)

    def _export_dashboard_da_khoa(self, output_path: str = ""):
        from openpyxl import Workbook

        from so_excel import Trang
        try:
            if not dung_fa_daa(self._luat_nghiem()):
                return _fail(err("fa_chua_bat"))
            with self._ket_noi_doc() as cur:
                ds = sx.chi_so_dashboard(sx.doc_du_lieu_dashboard(cur))
            wb = Workbook()
            wb.active.title = "Dashboard"
            t = Trang(wb.active)

            def gt(c):
                v = c["gia_tri"]
                if v is None:
                    return "chưa có dữ liệu"
                return v if isinstance(v, int) else round(v, 3)
            t.bang(["Chỉ số", "Giá trị", "Mục tiêu", "Đạt", "Nguồn"], [
                [sx.TEN_CHI_SO_DASHBOARD[c["ma"]], gt(c), sx.MUC_TIEU_DASHBOARD[c["muc_tieu"]],
                 "" if c["dat"] is None else ("Đạt" if c["dat"] else "Chưa đạt"), c["nguon"]] for c in ds])
            t.xong()
            duong = self._duong_xuat(output_path, "dashboard.xlsx")
            wb.save(duong)
            return _ok({"path": duong, "n_rows": len(ds)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # GAP-13 ----------------------------------------------------------------------------------------------------------
    def get_vong_doi_cho(self, buoi: str = ""):
        """GAP-13 (V§8.8): ĐO các chu trình cải thiện ổn định trên kết quả DA của `buoi` (mặc định buổi đầu). CHỈ ĐỌC:
        không ghi kết quả hay điều chỉnh. Nhãn "không bảo đảm ổn định" (bất biến 8). Cờ `rules.fa_vong_doi_cho`."""
        import fa_vong_doi_cho as vd
        try:
            luat = self._luat_nghiem()
            if not (dung_fa_daa(luat) and luat.get("fa_vong_doi_cho") is True):
                return _ok({"bat": False})
            with self._ket_noi_doc() as cur:
                clubs = {r[0]: {"loai": r[1], "diem_san": r[2], "buoi": r[3] or BUOI_MAC_DINH} for r in cur.execute(
                    "SELECT club_id, loai, diem_san, buoi FROM clubs")}
                ds_buoi = sorted({b for (b,) in cur.execute("SELECT DISTINCT buoi FROM match_results")},
                                 key=khoa_sap_buoi)
                buoi = buoi if buoi in ds_buoi else (ds_buoi[0] if ds_buoi else "")
                asg = {r[0]: r[1] for r in cur.execute(
                    "SELECT student_id, club_id FROM match_results WHERE buoi = ?", (buoi,))}
                prefs: dict = {}
                for sid, cid in cur.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
                    if cid in clubs and clubs[cid]["buoi"] == buoi:
                        prefs.setdefault(sid, []).append(cid)
                diem: dict = {}
                for cid, sid, d in cur.execute(
                        "SELECT sc.club_id, sc.student_id, sc.score FROM club_scores sc JOIN club_test_selection t "
                        "ON t.student_id = sc.student_id AND t.club_id = sc.club_id"):
                    diem.setdefault(cid, {})[sid] = d
                hc: dict = {}
                for sid, cid, p in cur.execute("SELECT student_id, club_id, points FROM wharton_bids"):
                    hc.setdefault(sid, {})[cid] = p
                giu = cur.execute("SELECT club_id, student_id FROM giu_cho").fetchall()
            khoa = vd.khoa_tho_fa(clubs, prefs, diem, hc, giu)
            _, ds = vd.chay_chu_trinh(asg, prefs, khoa)
            return _ok({"bat": True, "nhan": vd.NHAN_KHONG_BAO_DAM, "buoi": buoi, "ds_buoi": ds_buoi,
                        "chu_trinh": [[{"student_id": s, "club_from": a, "club_to": b} for s, a, b in ct] for ct in ds],
                        "so_em_loi": len({s for ct in ds for s, _, _ in ct})})
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))
