"""Thẻ Quản lý (CLB, học sinh, nhóm dự trữ), nhập tại chỗ ở kiosk,
và vùng xoá dữ liệu.

Một phần của PipelineAPI (xem api.py) — tách riêng cho dễ đọc; mọi hàm
public ở đây vẫn là hàm của PipelineAPI và giao diện gọi được như cũ.
"""

import getpass
import json
import os

from api_chung import (
    _now,
)
import so_nhap
from api_workspace import CauHinhHong
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    BUOI_MAC_DINH,
    WHARTON_NGAN_SACH,
    WHARTON_TU_DIEN_MOT_CLB,
    dung_wharton,
    kiem_ho_so_wharton,
    loi_suc_chua,
    sap_buoi,
    tu_dien_wharton_mot_clb,
)


class QuanLyMixin:
    # -----------------------------------------------------------------
    # TAB "QUẢN LÝ CLUB & DỰ TRỮ" (admin thao tác trực tiếp — trường tự quyết)
    # -----------------------------------------------------------------

    def list_clubs_admin(self):
        """Giống list_clubs nhưng KÈM reserve_group, cho màn hình quản lý.

        Trước đây hàm này chỉ `return self.list_clubs()`, mà list_clubs
        không chọn cột reserve_group — nên bảng quản lý club luôn hiện
        "—" ở cột nhóm dự trữ dù DB có đủ dữ liệu. Nhóm dự trữ là cơ chế
        cốt lõi của RB-DA, hiển thị sai ở đây dễ khiến người vận hành
        tưởng chưa gán gì và đi cấu hình lại nhầm.
        """
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute(
                    "SELECT club_id, name, capacity, reserve_capacity, "
                    "reserve_group, buoi FROM clubs ORDER BY COALESCE(buoi, '') COLLATE THU_TU_BUOI, club_id"
                ).fetchall()
            return _ok([dict(r) for r in rows])
        except Exception as e:
            return _fail(err("error_reading_club_list", detail=str(e)))

    @staticmethod
    def chuan_hoa_buoi(raw) -> str:
        """Chuẩn hoá nhãn buổi sinh hoạt. Rỗng -> "" (nghĩa là buổi mặc định).

        Cùng cách chuẩn hoá với nhãn dự trữ: bỏ khoảng trắng thừa, hạ chữ
        thường, đổi khoảng trắng thành gạch dưới. "Thứ 3" và "thu 3" và
        "thu_3" phải ra cùng một buổi — không thì hai CLB cùng giờ lại được
        coi là hai buổi khác nhau, và học sinh trúng cả hai.

        Thứ trong tuần về MỘT mã chuẩn (`thu_3`, `chu_nhat`) — đúng như Sổ nhập
        CLB (`so_nhap.ma_buoi`). Trước đây form ghi "Thứ 3" thành `thứ_3` còn
        sổ ghi `thu_3`: cùng giờ mà thành hai buổi.
        """
        return so_nhap.ma_buoi(raw)

    def create_or_update_club(
        self, club_id: str, name: str, capacity: int,
        reserve_capacity: int = 0, reserve_group: str = "", buoi: str = "",
    ):
        """
        Tạo mới hoặc cập nhật 1 club (UPSERT theo club_id).
        reserve_group: chuỗi tự do do trường tự đặt (vd 'chinh_sach',
        'khoi10', hoặc để trống '' nếu club không có dự trữ).
        buoi: buổi sinh hoạt (vd 'thu_3'). Để trống nếu trường chỉ tổ
        chức một buổi — khi đó mọi CLB thuộc cùng một buổi mặc định và
        phần mềm chạy y hệt bản không có tính năng nhiều buổi.
        """
        try:
            capacity = int(capacity)
            reserve_capacity = int(reserve_capacity)
            loi = loi_suc_chua(capacity, reserve_capacity)
            if loi:
                if loi == "capacity_not_positive":
                    return _fail(err("capacity_must_be_positive"))
                if loi == "reserve_negative":
                    return _fail(err("reserve_capacity_negative"))
                return _fail(err("reserve_capacity_exceeds_capacity"))
            # None (loi goi thieu tham so) truoc day nem AttributeError.
            club_id = (club_id or "").strip()
            name = (name or "").strip()
            if not club_id:
                return _fail(err("club_id_required"))

            reserve_group_value = self.chuan_hoa_nhom_du_tru(reserve_group) or None
            buoi_value = self.chuan_hoa_buoi(buoi) or None

            with self._ket_noi_ghi() as cur:
                buoi_value = self._khop_buoi_da_co(cur, buoi_value, buoi)
                self._ghi_clb(cur, club_id, name, capacity, reserve_capacity,
                              reserve_group_value, buoi_value)
            return _ok({"club_id": club_id, "action": "upserted"})
        except Exception as e:
            return _fail(err("error_saving_club", detail=str(e)))

    def delete_club(self, club_id: str):
        """
        Xoá club — CHẶN nếu đã có preferences/match_results tham chiếu
        tới club này, để tránh mất dữ liệu học sinh đã nộp.
        """
        try:
            with self._ket_noi_ghi() as cur:
                n_prefs = cur.execute(
                    "SELECT COUNT(*) FROM preferences WHERE club_id = ?", (club_id,)
                ).fetchone()[0]
                n_matches = cur.execute(
                    "SELECT COUNT(*) FROM match_results WHERE club_id = ?", (club_id,)
                ).fetchone()[0]
                if n_prefs > 0 or n_matches > 0:
                    return _fail(err(
                        "cannot_delete_club_referenced",
                        club_id=club_id, n_prefs=n_prefs, n_matches=n_matches,
                    ))
                # Con trước, cha sau: khoá ngoại chặn xoá CLB khi còn dòng
                # đăng ký thi / điểm trỏ tới nó.
                bi_anh_huong = [r[0] for r in cur.execute(
                    "SELECT DISTINCT student_id FROM wharton_bids WHERE club_id = ? "
                    "ORDER BY student_id", (club_id,))]
                cu_w = {sid: self._doc_diem_wharton_cua_em(cur, sid) for sid in bi_anh_huong}
                cur.execute("DELETE FROM wharton_bids WHERE club_id = ?", (club_id,))
                for sid in bi_anh_huong:
                    self._ghi_nhat_ky_wharton(
                        cur, "quan_ly", "xoa_theo_clb", sid, cu_w[sid],
                        self._doc_diem_wharton_cua_em(cur, sid))
                cur.execute("DELETE FROM club_test_selection WHERE club_id = ?", (club_id,))
                cur.execute("DELETE FROM club_scores WHERE club_id = ?", (club_id,))
                cur.execute("DELETE FROM clubs WHERE club_id = ?", (club_id,))
            return _ok({"club_id": club_id, "deleted": True})
        except Exception as e:
            return _fail(err("error_deleting_club", detail=str(e)))

    def list_reserve_groups_in_use(self):
        """Danh sách các reserve_group đang được dùng (để gợi ý trong form, tránh gõ sai chính tả)."""
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute(
                    "SELECT DISTINCT reserve_group FROM clubs WHERE reserve_group IS NOT NULL "
                    "UNION "
                    "SELECT DISTINCT reserve_group FROM students WHERE reserve_group IS NOT NULL"
                ).fetchall()
            return _ok(sorted(r[0] for r in rows if r[0]))
        except Exception as e:
            return _fail(err("error_reading_reserve_groups", detail=str(e)))

    def set_student_reserve_group(self, student_id: str, reserve_group: str):
        """Gán (hoặc gỡ, nếu reserve_group='') diện dự trữ cho 1 học sinh."""
        try:
            with self._ket_noi_ghi() as cur:
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
                ).fetchone()
                if not exists:
                    return _fail(err("student_not_found", student_id=student_id))
                value = self.chuan_hoa_nhom_du_tru(reserve_group) or None
                cur.execute(
                    "UPDATE students SET reserve_group = ? WHERE student_id = ?",
                    (value, student_id),
                )
            return _ok({"student_id": student_id, "reserve_group": value})
        except Exception as e:
            return _fail(err("error_assigning_reserve_group", detail=str(e)))

    def bulk_set_reserve_group(self, student_ids: list, reserve_group: str):
        """Gán hàng loạt — dùng khi trường có sẵn danh sách (vd cả 1 khối lớp)."""
        try:
            if not isinstance(student_ids, list) or not student_ids:
                return _fail(err("student_ids_must_be_nonempty_list"))
            value = self.chuan_hoa_nhom_du_tru(reserve_group) or None
            with self._ket_noi_ghi() as cur:
                existing_ids = {
                    r[0] for r in cur.execute("SELECT student_id FROM students").fetchall()
                }
                missing = [sid for sid in student_ids if sid not in existing_ids]
                valid_ids = [sid for sid in student_ids if sid in existing_ids]
                cur.executemany(
                    "UPDATE students SET reserve_group = ? WHERE student_id = ?",
                    [(value, sid) for sid in valid_ids],
                )
            return _ok({"n_updated": len(valid_ids), "not_found": missing})
        except Exception as e:
            return _fail(err("error_bulk_assigning", detail=str(e)))

    def list_students_admin(self, search: str = "", page: int = 1, page_size: int = 100):
        """
        Danh sách học sinh kèm reserve_group hiện tại, cho tab quản lý.
        CÓ PHÂN TRANG (trước đây LIMIT 100 cứng khiến trường >100 học
        sinh bị ẩn âm thầm không báo). Trả kèm total/total_pages để UI
        vẽ nút điều hướng trang.

        Mỗi dòng kèm thêm n_tested/n_ranked (số CLB đã chọn thi / số
        nguyện vọng đã xếp) — dùng ở tab Nhập dự phòng để người vận hành
        thấy ngay em nào còn thiếu mà không phải bấm vào từng em.

        Kèm luôn tested_clubs [{club_id, name, buoi}] và ranked_clubs
        [{club_id, name, buoi, rank}] (theo thứ tự nguyện vọng) để thẻ
        kết quả tìm kiếm hiện được TÊN CLB em đã chọn.
        """
        try:
            page = max(1, int(page))
            page_size = max(1, min(int(page_size), 500))
            offset = (page - 1) * page_size

            with self._ket_noi_doc() as cur:

                where_clause = ""
                params: tuple = ()
                if search:
                    where_clause = " WHERE khop_tim(s.student_id, ?) OR khop_tim(s.name, ?)"
                    params = (search, search)

                total = cur.execute(
                    f"SELECT COUNT(*) FROM students s{where_clause}", params
                ).fetchone()[0]

                rows = cur.execute(
                    f"""
                    SELECT s.student_id, s.name, s.reserve_group,
                           COALESCE(ts.n_tested, 0) AS n_tested,
                           COALESCE(pr.n_ranked, 0) AS n_ranked
                    FROM students s
                    LEFT JOIN (
                        SELECT student_id, COUNT(*) AS n_tested
                        FROM club_test_selection GROUP BY student_id
                    ) ts ON ts.student_id = s.student_id
                    LEFT JOIN (
                        SELECT student_id, COUNT(*) AS n_ranked
                        FROM preferences GROUP BY student_id
                    ) pr ON pr.student_id = s.student_id
                    {where_clause}
                    ORDER BY s.student_id LIMIT ? OFFSET ?
                    """,
                    params + (page_size, offset),
                ).fetchall()

                # Tên CLB đã chọn thi / đã xếp nguyện vọng, CHỈ cho các em
                # của trang này — để thẻ tìm kiếm ở tab Nhập tại chỗ nói
                # được em đã chọn NHỮNG CLB nào, không chỉ bao nhiêu.
                # LEFT JOIN: CLB đã bị xoá vẫn hiện bằng mã, không biến mất.
                ds_ma = [r["student_id"] for r in rows]
                chon: dict = {sid: {"tested_clubs": [], "ranked_clubs": []}
                              for sid in ds_ma}
                if ds_ma:
                    dau_hoi = ",".join("?" * len(ds_ma))
                    for r in cur.execute(
                        f"""
                        SELECT t.student_id, t.club_id, c.name, c.buoi
                        FROM club_test_selection t
                        LEFT JOIN clubs c ON c.club_id = t.club_id
                        WHERE t.student_id IN ({dau_hoi})
                        ORDER BY t.student_id, COALESCE(c.name, t.club_id)
                        """,
                        ds_ma,
                    ).fetchall():
                        chon[r["student_id"]]["tested_clubs"].append({
                            "club_id": r["club_id"],
                            "name": r["name"] or r["club_id"],
                            "buoi": r["buoi"] or BUOI_MAC_DINH,
                        })
                    for r in cur.execute(
                        f"""
                        SELECT p.student_id, p.club_id, p.rank, c.name, c.buoi
                        FROM preferences p
                        LEFT JOIN clubs c ON c.club_id = p.club_id
                        WHERE p.student_id IN ({dau_hoi})
                        ORDER BY p.student_id, p.rank
                        """,
                        ds_ma,
                    ).fetchall():
                        chon[r["student_id"]]["ranked_clubs"].append({
                            "club_id": r["club_id"],
                            "name": r["name"] or r["club_id"],
                            "buoi": r["buoi"] or BUOI_MAC_DINH,
                            "rank": r["rank"],
                        })

            total_pages = max(1, (total + page_size - 1) // page_size)
            return _ok({
                "rows": [dict(r, **chon[r["student_id"]]) for r in rows],
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            })
        except Exception as e:
            return _fail(err("error_reading_student_list", detail=str(e)))

    # -----------------------------------------------------------------
    # TAB "NHẬP DỰ PHÒNG" (kiosk fallback entry)
    # -----------------------------------------------------------------

    def list_clubs(self):
        try:
            with self._ket_noi_doc() as cur:
                # Sắp theo BUỔI trước rồi mới tới mã: màn hình nhập tại chỗ
                # dựng danh sách theo thứ tự này, và xếp các CLB cùng buổi
                # cạnh nhau giúp học sinh thấy ngay mình đang chọn trùng giờ.
                rows = cur.execute(
                    "SELECT club_id, name, capacity, reserve_capacity, "
                    "COALESCE(buoi, ?) AS buoi FROM clubs "
                    "ORDER BY buoi COLLATE THU_TU_BUOI, club_id", (BUOI_MAC_DINH,)
                ).fetchall()
            return _ok([dict(r) for r in rows])
        except Exception as e:
            return _fail(err("error_reading_club_list", detail=str(e)))

    def search_students(self, query: str):
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute(
                    "SELECT student_id, name FROM students "
                    "WHERE khop_tim(student_id, ?) OR khop_tim(name, ?) LIMIT 20",
                    (query, query),
                ).fetchall()
            return _ok([dict(r) for r in rows])
        except Exception as e:
            return _fail(err("error_searching_students", detail=str(e)))

    def get_student_entry_state(self, student_id: str):
        """
        Trạng thái nhập liệu hiện tại của 1 học sinh — dùng để tab
        'Nhập dự phòng' hiển thị lại nếu học sinh quay lại kiosk.
        """
        try:
            # Đọc cấu hình TRƯỚC khi mở kết nối đọc; chỉ để HIỂN THỊ nên đọc kiểu không nghiêm
            # (cấu hình hỏng thì coi như tắt, màn hình vẫn mở được như trước).
            bat_wharton = dung_wharton(self._cfg_ws()["rules"])
            with self._ket_noi_doc() as cur:
                student = cur.execute(
                    "SELECT student_id, name FROM students WHERE student_id = ?",
                    (student_id,),
                ).fetchone()
                if not student:
                    return _fail(err("student_not_found", student_id=student_id))

                tested = [
                    r["club_id"]
                    for r in cur.execute(
                        "SELECT club_id FROM club_test_selection WHERE student_id = ?",
                        (student_id,),
                    ).fetchall()
                ]
                prefs = [
                    r["club_id"]
                    for r in cur.execute(
                        "SELECT club_id FROM preferences WHERE student_id = ? ORDER BY rank",
                        (student_id,),
                    ).fetchall()
                ]
                du_lieu = {
                    "student_id": student["student_id"],
                    "name": student["name"],
                    "tested_clubs": tested,
                    "ranked_clubs": prefs,
                }
                if bat_wharton:
                    du_lieu["wharton"] = self._trang_thai_wharton(cur, student_id, tested, prefs)
                return _ok(du_lieu)
        except Exception as e:
            return _fail(err("error_reading_student_state", detail=str(e)))

    # -----------------------------------------------------------------
    # NHẬT KÝ ĐIỂM WHARTON (A13.3)
    #
    # Mọi lần ghi hoặc xoá `wharton_bids` ghi thêm MỘT dòng vào `wharton_nhat_ky`, trong CÙNG giao
    # dịch với thao tác (thao tác hỏng, rollback thì không có dòng ma). Bảng chỉ có INSERT và
    # SELECT: không đường nào xoá hay sửa nó, kể cả `reset_data`.
    # -----------------------------------------------------------------

    @staticmethod
    def _nguoi_may() -> str:
        """Tên tài khoản máy đang chạy phần mềm; lỗi thì rỗng — không bao giờ làm hỏng thao tác."""
        try:
            return str(getpass.getuser() or "")
        except Exception:
            return ""

    @staticmethod
    def _doc_diem_wharton_cua_em(cur, student_id: str) -> dict:
        """Điểm đã lưu của một em: {"w1": {club_id: điểm}, "w2": {...}} (quỹ 1 = đã thi)."""
        ra: dict = {"w1": {}, "w2": {}}
        for cid, tier, diem in cur.execute(
                "SELECT club_id, tier, points FROM wharton_bids WHERE student_id = ? "
                "ORDER BY club_id", (student_id,)):
            ra["w%d" % tier][cid] = diem
        return ra

    @classmethod
    def _ghi_nhat_ky_wharton(cls, cur, nguon: str, hanh_dong: str, student_id=None,
                             cu=None, moi=None) -> None:
        """Ghi thêm một dòng nhật ký (chỉ INSERT). `cu` / `moi` là dict hoặc None."""
        def _json(x):
            return None if x is None else json.dumps(x, sort_keys=True, ensure_ascii=False)
        cur.execute(
            "INSERT INTO wharton_nhat_ky (luc, nguon, nguoi, hanh_dong, student_id, cu_json, moi_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (_now(), nguon, cls._nguoi_may(), hanh_dong, student_id, _json(cu), _json(moi)))

    @staticmethod
    def _co_diem(d: dict) -> bool:
        return bool(d["w1"] or d["w2"])

    # -----------------------------------------------------------------
    # KHOÁ ĐIỂM WHARTON (A13.3)
    #
    # Khoá RIÊNG (`wharton_lock`), không dính `stb_lock`. Lần chạy phân bổ thành công khi Wharton bật
    # tự khoá (xem `_run_pipeline_da_khoa`). Đang khoá thì mọi cửa GHI điểm trả `wharton_da_khoa`;
    # các cửa XOÁ dữ liệu vẫn chạy (và ghi nhật ký). Mở bằng `mo_khoa_wharton`.
    # -----------------------------------------------------------------

    @staticmethod
    def _wharton_dang_khoa(cur) -> bool:
        """Có đang khoá không. Gọi TRONG giao dịch ghi của từng cửa: không có khe giữa kiểm và ghi."""
        r = cur.execute("SELECT is_locked FROM wharton_lock WHERE id = 1").fetchone()
        return bool(r and r[0])

    def get_wharton_lock_status(self):
        """{is_locked, locked_at, unlocked_at} của khoá điểm Wharton (như `get_stb_lock_status`)."""
        try:
            with self._ket_noi_doc() as cur:
                r = cur.execute(
                    "SELECT is_locked, locked_at, unlocked_at FROM wharton_lock WHERE id = 1"
                ).fetchone()
            if not r:
                return _ok({"is_locked": False, "locked_at": None, "unlocked_at": None})
            return _ok({"is_locked": bool(r[0]), "locked_at": r[1], "unlocked_at": r[2]})
        except Exception as e:
            return _fail(err("error_wharton_quan_ly", detail=str(e)))

    _MO_KHOA_WHARTON_CHU = "MO"

    def mo_khoa_wharton(self, xac_nhan: str = ""):
        """Mở khoá sửa điểm Wharton; cần gõ đúng "MO". Ghi nhật ký. KHÔNG đụng STB. Lần chạy xếp
        sau đó khoá lại. Đang mở sẵn thì không đổi gì và không ghi nhật ký."""
        try:
            luat = self._luat_nghiem()
            if not dung_wharton(luat):
                return _fail(err("wharton_chua_bat"))
            if xac_nhan != self._MO_KHOA_WHARTON_CHU:
                return _fail(err("wharton_mo_khoa_sai_xac_nhan",
                                 can_go=self._MO_KHOA_WHARTON_CHU))
            with self._ket_noi_ghi() as cur:
                dang_khoa = self._wharton_dang_khoa(cur)
                if dang_khoa:
                    cur.execute("UPDATE wharton_lock SET is_locked = 0, unlocked_at = ? WHERE id = 1",
                                (_now(),))
                    self._ghi_nhat_ky_wharton(cur, "quan_ly", "mo_khoa")
            return _ok({"was_locked": dang_khoa})
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_wharton_quan_ly", detail=str(e)))

    @staticmethod
    def _trang_thai_wharton(cur, student_id: str, tested: list, prefs: list) -> dict:
        """Khoá `wharton` của `get_student_entry_state` (chỉ có khi workspace bật Wharton).

        `quy_cua_clb` tính theo ô tick HIỆN TẠI; `w1` / `w2` lấy theo cột `tier` ĐÃ LƯU. Dòng
        có tier lệch với ô tick hiện tại (em đổi tick sau khi chia điểm) vẫn được trả nguyên để
        màn hình nhận ra hồ sơ đang lệch và nhắc chia lại — không tự chuyển điểm sang quỹ kia.
        Chỉ trả điểm của CHÍNH em này.
        """
        w: dict = {1: {}, 2: {}}
        for cid, tier, diem in cur.execute(
                "SELECT club_id, tier, points FROM wharton_bids WHERE student_id = ? "
                "ORDER BY club_id", (student_id,)):
            w[tier][cid] = diem
        buoi = {r[0]: (r[1] or BUOI_MAC_DINH) for r in cur.execute(
            "SELECT club_id, buoi FROM clubs")}
        tick = set(tested)
        return {
            "bat": True,
            "ngan_sach": WHARTON_NGAN_SACH,
            "tu_dien_mot_clb": WHARTON_TU_DIEN_MOT_CLB,
            "w1": w[1], "w2": w[2],
            "quy_cua_clb": {c: (1 if c in tick else 2) for c in prefs},
            "buoi_cua_clb": {c: buoi.get(c, BUOI_MAC_DINH) for c in prefs},
            # Các buổi của em theo THỨ TỰ NGÀY của trường (như phần nguyện vọng), để màn hình
            # xếp khung theo buổi mà không phải gọi thêm.
            "ds_buoi": sap_buoi({buoi.get(c, BUOI_MAC_DINH) for c in prefs}),
        }

    def submit_wharton(self, student_id: str, w1: dict, w2: dict):
        """BƯỚC 3 (điểm Wharton) — học sinh chia hai quỹ điểm cho các CLB trong nguyện vọng.

        `w1` {club_id: điểm} chia cho các CLB em có thi, `w2` cho các CLB không thi. KIỂM Ở
        SERVER (đặc tả V6), không tin dữ liệu từ trình duyệt: ghép với nguyện vọng và ô tick
        đang lưu của em rồi chạy `kiem_ho_so_wharton`. Hồ sơ sai thì không ghi gì và trả đúng
        danh sách lỗi của hàm đó. Một quỹ chỉ có MỘT CLB mà chưa đặt điểm thì tự điền 100
        (`tu_dien_wharton_mot_clb`) TRONG BỘ NHỚ để kiểm (cách A): ô tự điền KHÔNG được ghi,
        chỉ ô em đã gửi mới vào `wharton_bids`. Nhờ vậy em thêm CLB thứ hai vào quỹ đó sau này
        thì hồ sơ bị coi là chưa chia, thay vì "hợp lệ" nhờ một ô 100 em chưa từng đặt. Hợp lệ
        thì thay TOÀN BỘ dòng của em, `tier` theo ô tick lúc ghi. Workspace chưa bật Wharton
        thì từ chối. Mọi lần lưu làm đổi điểm ghi một dòng nhật ký (`nguon = "kiosk"`).
        """
        return self._luu_wharton(student_id, w1, w2, "kiosk")

    def _luu_wharton(self, student_id: str, w1: dict, w2: dict, nguon: str):
        """Lõi lưu điểm Wharton của một em, dùng chung cho kiosk (`submit_wharton`) và thẻ Quản lý
        (`admin_save_wharton`): MỘT bản luật kiểm, MỘT chỗ ghi, khác nhau chỉ ở `nguon` của nhật ký."""
        try:
            luat = self._luat_nghiem()           # đọc TRƯỚC khi mở giao dịch ghi
            if not dung_wharton(luat):
                return _fail(err("wharton_chua_bat"))
            if not isinstance(w1, dict) or not isinstance(w2, dict):
                return _fail(err("error_saving_wharton",
                                 detail="w1 va w2 phai la dict {club_id: diem}"))
            with self._ket_noi_ghi() as cur:
                if self._wharton_dang_khoa(cur):
                    return _fail(err("wharton_da_khoa"))
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)).fetchone()
                if not exists:
                    return _fail(err("student_not_found", student_id=student_id))
                prefs = [r[0] for r in cur.execute(
                    "SELECT club_id FROM preferences WHERE student_id = ? ORDER BY rank",
                    (student_id,))]
                tick = {r[0] for r in cur.execute(
                    "SELECT club_id FROM club_test_selection WHERE student_id = ?",
                    (student_id,))}
                clubs = {r[0]: {"buoi": r[1] or BUOI_MAC_DINH} for r in cur.execute(
                    "SELECT club_id, buoi FROM clubs")}
                preferences, clb_thi = {student_id: prefs}, {student_id: tick}
                moi1, moi2 = tu_dien_wharton_mot_clb(
                    preferences, clb_thi, {student_id: dict(w1)}, {student_id: dict(w2)}, clubs)
                loi = kiem_ho_so_wharton(
                    preferences, clb_thi, moi1, moi2, clubs,
                    tran_nguyen_vong=luat["max_choices"])
                if loi:
                    return _fail(loi)
                cu = self._doc_diem_wharton_cua_em(cur, student_id)
                cur.execute("DELETE FROM wharton_bids WHERE student_id = ?", (student_id,))
                dong = ([(student_id, cid, 1, diem) for cid, diem in w1.items()]
                        + [(student_id, cid, 2, diem) for cid, diem in w2.items()])
                cur.executemany(
                    "INSERT INTO wharton_bids (student_id, club_id, tier, points) "
                    "VALUES (?, ?, ?, ?)", dong)
                moi = self._doc_diem_wharton_cua_em(cur, student_id)
                if moi != cu:
                    self._ghi_nhat_ky_wharton(cur, nguon, "luu", student_id, cu, moi)
            return _ok({"student_id": student_id, "n_saved": len(dong)})
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_saving_wharton", detail=str(e)))

    @staticmethod
    def _xoa_diem_khong_con_tick(cur, student_id: str) -> int:
        """Xoá điểm của em ở những CLB em KHÔNG còn tick "muốn thi".

        Bỏ tick là em rút khỏi bài thi đó (quyết định đã chốt 28/09). Trước đây chỉ ô
        tick bị xoá, còn điểm nằm lại: biến mất khỏi màn hình chấm điểm
        (chỉ liệt kê em có tick), không xoá được nữa (`score_not_applicant`),
        mà vẫn xếp em lên Tầng 1 nếu em còn xếp CLB đó làm nguyện vọng.

        Mọi cửa GHI ĐÈ ô tick của một em phải gọi hàm này trong CÙNG giao
        dịch, SAU khi ghi ô tick mới: `submit_test_selection`,
        `reset_student_entry`, `import_test_selection_csv`. Trả số điểm đã
        xoá để màn hình nói ra — xoá điểm giáo viên đã chấm mà im lặng là
        mất dữ liệu không ai hay.
        """
        cur.execute(
            "DELETE FROM club_scores WHERE student_id = ? AND club_id NOT IN "
            "(SELECT club_id FROM club_test_selection WHERE student_id = ?)",
            (student_id, student_id),
        )
        return cur.rowcount

    @staticmethod
    def _ma_clb_khong_ton_tai(cur, ma_clb: list) -> list:
        """Các mã trong `ma_clb` không có trong bảng clubs, giữ thứ tự.

        MỘT truy vấn cho cả danh sách, thay vì một truy vấn mỗi mã.
        """
        if not ma_clb:
            return []
        dau_hoi = ",".join("?" * len(ma_clb))
        co = {r[0] for r in cur.execute(
            "SELECT club_id FROM clubs WHERE club_id IN (%s)" % dau_hoi, list(ma_clb))}
        return [c for c in ma_clb if c not in co]

    def submit_test_selection(self, student_id: str, club_ids: list):
        """
        BƯỚC 1 (độc lập với xếp hạng) — tick-box club muốn thi/xét.
        Ghi đè toàn bộ lựa chọn cũ của học sinh này. Điểm đã chấm cho CLB
        bị bỏ tick bị xoá theo (`n_scores_removed`), xem
        `_xoa_diem_khong_con_tick`.
        """
        try:
            if not isinstance(club_ids, list):
                return _fail(err("club_ids_must_be_list"))
            # Tick trung mot CLB hai lan (giao dien bam dup, loi goi tu ngoai)
            # truoc day vo khoa chinh (student_id, club_id) va CA lan luu
            # hong. Tick la tap hop -> bo trung, giu thu tu dau tien.
            club_ids = list(dict.fromkeys(club_ids))
            tran_thi = self._tran_thi()   # trần của workspace (None = không giới hạn); đọc trước giao dịch
            with self._ket_noi_ghi() as cur:
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
                ).fetchone()
                if not exists:
                    return _fail(err("student_not_found", student_id=student_id))

                invalid = self._ma_clb_khong_ton_tai(cur, club_ids)
                if invalid:
                    return _fail(err("unknown_clubs", club_ids=invalid))

                # Tran tinh THEO TUNG BUOI. Tu choi ca loi goi chu khong cat bot:
                # nguoi dung dang ngoi truoc man hinh va sua duoc ngay, con cat
                # bot la phan mem tu y doi dieu ho vua khai.
                qua = self._buoi_qua_tran(cur, club_ids, tran_thi)
                if qua:
                    b, n = qua
                    return _fail(err(
                        "max_thi_moi_buoi" if b != BUOI_MAC_DINH else "thi_too_many",
                        buoi=b, count=n, tran=tran_thi))

                cur.execute(
                    "DELETE FROM club_test_selection WHERE student_id = ?", (student_id,)
                )
                cur.executemany(
                    "INSERT INTO club_test_selection (student_id, club_id) VALUES (?, ?)",
                    [(student_id, cid) for cid in club_ids],
                )
                n_xoa = self._xoa_diem_khong_con_tick(cur, student_id)
            return _ok({"student_id": student_id, "n_selected": len(club_ids),
                        "n_scores_removed": n_xoa})
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_saving_test_selection", detail=str(e)))

    def submit_preferences(self, student_id: str, ordered_club_ids: list):
        """
        BƯỚC 2 (độc lập với tick-box thi) — xếp hạng nguyện vọng,
        tối đa `rules.max_choices` mỗi buổi (mặc định 10 — giới hạn Microsoft Forms
        Ranking, giữ đồng bộ với luồng nhập chính).
        """
        try:
            if not isinstance(ordered_club_ids, list):
                return _fail(err("ordered_club_ids_must_be_list"))
            if len(ordered_club_ids) == 0:
                return _fail(err("must_rank_at_least_one"))
            # Tran 10 tinh THEO TUNG BUOI, khong phai ca tuan: moi buoi la
            # MOT cau Ranking rieng tren Microsoft Forms, nen 10 moi buoi
            # khop dung cong cu thu phieu. Kiem sau khi mo ket noi vi can tra
            # buoi cua tung CLB.
            if len(ordered_club_ids) != len(set(ordered_club_ids)):
                return _fail(err("duplicate_preference_in_list"))

            tran_nv = self._tran_nguyen_vong()   # trần của workspace; đọc trước giao dịch
            with self._ket_noi_ghi() as cur:
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
                ).fetchone()
                if not exists:
                    return _fail(err("student_not_found", student_id=student_id))

                invalid = self._ma_clb_khong_ton_tai(cur, ordered_club_ids)
                # Soat TRUOC tran moi buoi: ma CLB la khong co buoi, bi
                # don vao buoi mac dinh va bao nham "qua nhieu".
                if invalid:
                    return _fail(err("unknown_clubs", club_ids=invalid))

                qua = self._buoi_qua_tran(cur, ordered_club_ids, tran_nv)
                if qua:
                    b, n = qua
                    return _fail(err(
                        "max_pref_moi_buoi" if b != BUOI_MAC_DINH else "pref_too_many",
                        buoi=b, count=n, tran=tran_nv))

                cur.execute("DELETE FROM preferences WHERE student_id = ?", (student_id,))
                cur.executemany(
                    "INSERT INTO preferences (student_id, club_id, rank) VALUES (?, ?, ?)",
                    [(student_id, cid, i + 1) for i, cid in enumerate(ordered_club_ids)],
                )
                # Bỏ một CLB khỏi nguyện vọng thì điểm Wharton đặt ở CLB đó đi theo (đặc tả
                # 4.2); các dòng khác giữ nguyên. Đặt SAU khi ghi nguyện vọng mới.
                cu_w = self._doc_diem_wharton_cua_em(cur, student_id)
                cur.execute(
                    "DELETE FROM wharton_bids WHERE student_id = ? AND club_id NOT IN "
                    "(SELECT club_id FROM preferences WHERE student_id = ?)",
                    (student_id, student_id))
                if self._co_diem(cu_w):
                    moi_w = self._doc_diem_wharton_cua_em(cur, student_id)
                    if moi_w != cu_w:
                        self._ghi_nhat_ky_wharton(cur, "kiosk", "tia_nguyen_vong",
                                                  student_id, cu_w, moi_w)
            return _ok({"student_id": student_id, "n_ranked": len(ordered_club_ids)})
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_saving_preferences", detail=str(e)))

    def create_student_if_missing(self, student_id: str, name: str):
        """Kiosk fallback: nếu học sinh chưa có trong students, tạo mới (chưa có STB)."""
        try:
            with self._ket_noi_ghi() as cur:
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
                ).fetchone()
                if not exists:
                    cur.execute(
                        "INSERT INTO students (student_id, name, stb_number, reserve_group) "
                        "VALUES (?, ?, NULL, NULL)",
                        (student_id, name),
                    )
            return _ok({"student_id": student_id, "created": not exists})
        except Exception as e:
            return _fail(err("error_creating_student", detail=str(e)))

    def reset_student_entry(self, student_id: str):
        """
        Nút 'Sửa lại từ đầu' — xoá lựa chọn thi (Bước 1) và nguyện vọng
        (Bước 2) hiện tại của học sinh để nhập lại từ đầu tại kiosk.
        Không còn ô tick nào thì điểm đã chấm của em cũng đi theo
        (`n_scores_removed`, xem `_xoa_diem_khong_con_tick`) — nếu không,
        em chỉ nhập lại nguyện vọng là điểm cũ tự sống lại. Điểm theo NGƯỜI
        (`diem_ca_nhan`) thì giữ nguyên.
        KHÔNG xoá bản ghi học sinh (giữ nguyên student_id/tên/STB/reserve_group).
        """
        try:
            with self._ket_noi_ghi() as cur:
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
                ).fetchone()
                if not exists:
                    return _fail(err("student_not_found", student_id=student_id))
                cu_w = self._doc_diem_wharton_cua_em(cur, student_id)
                cur.execute("DELETE FROM wharton_bids WHERE student_id = ?", (student_id,))
                if self._co_diem(cu_w):
                    self._ghi_nhat_ky_wharton(cur, "kiosk", "xoa_mot_em", student_id, cu_w, None)
                cur.execute("DELETE FROM club_test_selection WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM preferences WHERE student_id = ?", (student_id,))
                n_xoa = self._xoa_diem_khong_con_tick(cur, student_id)
                # Điểm theo NGƯỜI (workspace per_person, `students.diem_ca_nhan`) ở LẠI. Điểm
                # từng CLB đi theo ô tick vì nó được chấm cho đúng lựa chọn đó; điểm theo người
                # do giáo viên chấm cho cả người, không gắn với tick hay nguyện vọng nào, nên
                # em nhập lại nguyện vọng ở kiosk không được xoá điểm của giáo viên.
            return _ok({"student_id": student_id, "reset": True,
                        "n_scores_removed": n_xoa})
        except Exception as e:
            return _fail(err("error_resetting_student_entry", detail=str(e)))

    def delete_student(self, student_id: str):
        """
        Nút 'Xoá học sinh' — xoá hẳn học sinh khỏi hệ thống (dùng khi
        tạo nhầm mã / trùng học sinh tại kiosk). CHẶN nếu học sinh đã
        có mặt trong match_results (đã qua lần chạy pipeline gần nhất)
        để tránh làm lệch thống kê lấp đầy club và mất dấu kiểm toán —
        phải chạy lại pipeline (hoặc xử lý ở tab Quản lý) trước.
        """
        try:
            with self._ket_noi_ghi() as cur:
                exists = cur.execute(
                    "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
                ).fetchone()
                if not exists:
                    return _fail(err("student_not_found", student_id=student_id))
                n_matches = cur.execute(
                    "SELECT COUNT(*) FROM match_results WHERE student_id = ?", (student_id,)
                ).fetchone()[0]
                if n_matches > 0:
                    return _fail(err("cannot_delete_student_matched", student_id=student_id))
                cu_w = self._doc_diem_wharton_cua_em(cur, student_id)
                cur.execute("DELETE FROM wharton_bids WHERE student_id = ?", (student_id,))
                if self._co_diem(cu_w):
                    self._ghi_nhat_ky_wharton(cur, "quan_ly", "xoa_mot_em", student_id, cu_w, None)
                cur.execute("DELETE FROM club_test_selection WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM preferences WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM club_scores WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM ket_qua_truoc WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            return _ok({"student_id": student_id, "deleted": True})
        except Exception as e:
            return _fail(err("error_deleting_student", detail=str(e)))

    # -----------------------------------------------------------------
    # XOÁ DỮ LIỆU ĐỂ LÀM LẠI TỪ ĐẦU
    #
    # Nạp file CỘNG THÊM học sinh, không bao giờ xoá — đúng như phải thế,
    # vì trường nạp khối 10 rồi nạp khối 11 thì không được mất khối 10.
    # Nhưng trước đây KHÔNG có đường nào đưa dữ liệu về trống: cách duy
    # nhất là đóng app rồi đổi tên app.db ngoài File Explorer, việc mà
    # không ai tìm ra. Hậu quả không phải chuyện hình thức — học sinh của
    # lần chạy thử trước vẫn chiếm suất và làm lệch kết quả, im lặng.
    # -----------------------------------------------------------------

    _RESET_CONFIRM = "XOA"

    # Xoá theo đúng thứ tự phụ thuộc: bảng con trước, students sau cùng.
    _RESET_BANG = {
        "hoc_sinh": ["wharton_bids", "match_results", "club_scores", "preferences",
                     "club_test_selection", "students"],
        "tat_ca":   ["wharton_bids", "match_results", "club_scores", "preferences",
                     "club_test_selection", "students", "clubs"],
    }

    def reset_data(self, pham_vi: str = "hoc_sinh", xac_nhan: str = ""):
        """Xoá dữ liệu để chạy thử lại từ đầu. LUÔN sao lưu trước.

        pham_vi:
            "hoc_sinh" — xoá học sinh và mọi thứ gắn với học sinh, GIỮ
                         nguyên danh sách CLB (trường hợp thường gặp:
                         giữ CLB, thay khối học sinh khác vào).
            "tat_ca"   — xoá cả CLB.

        xac_nhan phải đúng chuỗi "XOA". Một hàm xoá sạch CSDL mà gọi
        nhầm được từ JS là chuyện không chấp nhận được.

        KHÔNG đụng vào run_history: lược đồ ghi rõ bảng đó "không bao giờ
        xoá/ghi đè" vì đó là nhật ký kiểm toán. Xoá dữ liệu không được
        phép xoá dấu vết đã từng chạy những gì.
        """
        try:
            # Kiểm tra TRƯỚC, sao lưu SAU. Đảo thứ tự thì một lần gọi
            # nhầm vẫn đẻ ra một tệp sao lưu rác mỗi lần.
            if xac_nhan != self._RESET_CONFIRM:
                return _fail(err("reset_confirmation_mismatch",
                                 can_go=self._RESET_CONFIRM))
            bang = self._RESET_BANG.get(pham_vi)
            if bang is None:
                return _fail(err("reset_scope_unknown", pham_vi=pham_vi,
                                 hop_le=", ".join(sorted(self._RESET_BANG))))

            backup_path = self._backup_db()

            with self._ket_noi_ghi() as cur:
                # Đếm TRƯỚC khi xoá — báo sau khi xoá thì con số nào cũng 0.
                da_xoa = {
                    ten: cur.execute("SELECT COUNT(*) FROM %s" % ten).fetchone()[0]
                    for ten in bang
                }
                # Điểm Wharton chỉ hiện trong báo cáo khi có dòng bị xoá: Wharton tắt thì phản
                # hồi y hệt trước vòng 2.
                if not da_xoa.get("wharton_bids"):
                    da_xoa.pop("wharton_bids", None)
                else:
                    # Một dòng tổng trong nhật ký TRƯỚC khi xoá: số dòng và mã các em bị xoá điểm.
                    self._ghi_nhat_ky_wharton(
                        cur, "xoa_du_lieu", "xoa_tat_ca", None,
                        {"so_dong": da_xoa["wharton_bids"],
                         "ma_hoc_sinh": [r[0] for r in cur.execute(
                             "SELECT DISTINCT student_id FROM wharton_bids ORDER BY student_id")]},
                        None)
                for ten in bang:
                    cur.execute("DELETE FROM %s" % ten)

                # run_meta mô tả lần chạy gần nhất, mà lần chạy đó nay không
                # còn dữ liệu nào phía sau.
                cur.execute("DELETE FROM run_meta")
                # Ban chup ket qua truoc va dau van tay cung mo ta lan chay
                # cu — de lai thi tep "thay doi" so voi hoc sinh da xoa.
                cur.execute("DELETE FROM ket_qua_truoc")
                cur.execute("DELETE FROM dau_van_tay_chay")

                # Mở khoá STB. Bỏ bước này thì lần chạy sau đi vào nhánh "đã
                # khoá" và ghi nhật ký là "tái sử dụng STB" cho một bộ số bốc
                # thăm không còn tồn tại — sai cho phần kiểm toán.
                cur.execute(
                    "UPDATE stb_lock SET is_locked = 0, unlocked_at = ? WHERE id = 1",
                    (_now(),),
                )
                # Khoá điểm Wharton mở theo (như khoá STB): dữ liệu đã xoá thì khoá không còn nghĩa.
                # Chỉ khi ĐANG khoá mới đụng tới, nên Wharton tắt thì không có gì đổi.
                if self._wharton_dang_khoa(cur):
                    cur.execute(
                        "UPDATE wharton_lock SET is_locked = 0, unlocked_at = ? WHERE id = 1",
                        (_now(),))
                    self._ghi_nhat_ky_wharton(cur, "xoa_du_lieu", "mo_khoa")
                # Đếm CLB CÒN LẠI ở đây chứ không để giao diện tự suy ra từ
                # phạm vi — suy ra là đoán, và đoán sai thì toast báo một con
                # số không ai kiểm chứng được.
                n_clb_con_lai = cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0]

            return _ok({
                "pham_vi": pham_vi,
                "backup_path": backup_path,
                "backup_name": os.path.basename(backup_path),
                "da_xoa": da_xoa,
                "n_students": da_xoa.get("students", 0),
                "n_clubs": da_xoa.get("clubs", 0),
                "n_clubs_con_lai": n_clb_con_lai,
                "giu_lai_run_history": True,
            })
        except Exception as e:
            return _fail(self._loi_co_ghi_vet(err("error_resetting_data", detail=str(e))))
