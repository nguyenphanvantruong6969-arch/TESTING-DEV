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
from rbda_priority_pipeline import dung_fa_daa, khoa_sap_buoi

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
            return _fail(err("error_saving_preferences", detail=str(e)))

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
            return _fail(err("error_saving_preferences", detail=str(e)))
