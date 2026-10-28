"""Chấm điểm mù: danh sách thí sinh từng CLB và lưu điểm.

Một phần của PipelineAPI (xem api.py) — tách riêng cho dễ đọc; mọi hàm
public ở đây vẫn là hàm của PipelineAPI và giao diện gọi được như cũ.
"""

from api_workspace import CauHinhHong
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok


class ChamDiemMixin:
    # -----------------------------------------------------------------
    # CHẤM ĐIỂM MÙ (blind scoring) — trước đây club_scores chỉ được
    # điền qua seed_sample_data(), KHÔNG có màn hình cho giáo viên chấm
    # thật. Yêu cầu thiết kế cốt lõi "chấm mù" (grader không thấy STB,
    # không thấy thứ hạng nguyện vọng của học sinh) được ĐẢM BẢO Ở ĐÂY
    # bằng cách chỉ trả về student_id + tên — KHÔNG BAO GIỜ trả stb_number
    # hay preferences trong bất kỳ hàm nào của mục này.
    # -----------------------------------------------------------------

    def get_scoring_overview(self):
        """Tổng quan tiến độ chấm điểm theo từng club — cho màn hình chọn club để chấm."""
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute("""
                    SELECT c.club_id, c.name,
                           COUNT(DISTINCT t.student_id) AS n_applicants,
                           COUNT(DISTINCT sc.student_id) AS n_scored
                    FROM clubs c
                    LEFT JOIN club_test_selection t ON t.club_id = c.club_id
                    LEFT JOIN club_scores sc ON sc.club_id = c.club_id AND sc.student_id = t.student_id
                    GROUP BY c.club_id
                    ORDER BY c.club_id
                """).fetchall()
            return _ok([dict(r) for r in rows])
        except Exception as e:
            return _fail(err("error_reading_scoring_overview", detail=str(e)))

    # -----------------------------------------------------------------
    # CHẤM ĐIỂM THEO NGƯỜI (workspace `score_scope = per_person`): MỘT điểm cho cả người,
    # lưu ở students.diem_ca_nhan. Vẫn chấm mù: chỉ mã và tên, không số bốc thăm, không
    # nguyện vọng. Điểm này được mở rộng ra các nơi người đó có nguyện vọng lúc xếp
    # (`load_from_sqlite`), nên sửa một điểm là sửa một ô.
    # -----------------------------------------------------------------
    def _soat_cham_theo_nguoi(self):
        """None nếu workspace chấm điểm theo người, ngược lại là lỗi để trả về."""
        if self._luat_nghiem()["score_scope"] != "per_person":
            return err("scoring_not_per_person")
        return None

    def get_person_scoring_list(self):
        """Danh sách mọi người cần chấm: {student_id, name, score}, score None = chưa chấm."""
        try:
            loi = self._soat_cham_theo_nguoi()
            if loi:
                return _fail(loi)
            with self._ket_noi_doc() as cur:
                rows = cur.execute(
                    "SELECT student_id, name, diem_ca_nhan AS score FROM students "
                    "ORDER BY student_id").fetchall()
            return _ok({
                "persons": [dict(r) for r in rows],
                "n_scored": sum(1 for r in rows if r["score"] is not None),
            })
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_reading_scoring_list", detail=str(e)))

    def submit_person_scores(self, scores: list):
        """Lưu điểm theo người. scores: [{"student_id": "...", "score": 8.5}, ...].

        Cùng luật số như `submit_club_scores` (nhận "8,5", từ chối âm / không phải số);
        ô trống xoá điểm của người đó."""
        try:
            if not isinstance(scores, list) or not scores:
                return _fail(err("scores_must_be_nonempty_list"))
            loi = self._soat_cham_theo_nguoi()
            if loi:
                return _fail(loi)
            with self._ket_noi_ghi() as cur:
                co = {r[0] for r in cur.execute("SELECT student_id FROM students")}
                n_saved, skipped = 0, []
                for entry in scores:
                    sid = entry.get("student_id") if isinstance(entry, dict) else None
                    if sid not in co:
                        skipped.append(err("student_not_found", student_id=str(
                            sid if isinstance(entry, dict) else entry)))
                        continue
                    diem = entry.get("score")
                    if diem is None or diem == "":
                        cur.execute("UPDATE students SET diem_ca_nhan = NULL "
                                    "WHERE student_id = ?", (sid,))
                        continue
                    so = self._doc_diem(diem if isinstance(diem, str) else str(diem))
                    if so is None:
                        skipped.append(err("score_not_a_number", student_id=sid, diem_goc=diem))
                        continue
                    if so < 0:
                        skipped.append(err("score_negative", student_id=sid, diem_goc=so))
                        continue
                    cur.execute("UPDATE students SET diem_ca_nhan = ? WHERE student_id = ?",
                                (so, sid))
                    n_saved += 1
            return _ok({"n_saved": n_saved, "warnings": skipped})
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_saving_scores", detail=str(e)))

    def get_club_applicants_for_scoring(self, club_id: str):
        """
        Danh sách học sinh cần chấm cho 1 club — CHỈ mã số, tên, và
        điểm đã chấm trước đó (nếu có, để sửa). KHÔNG kèm STB, KHÔNG
        kèm thứ hạng nguyện vọng — đúng yêu cầu chấm mù (blind scoring).
        """
        try:
            with self._ket_noi_doc() as cur:
                club = cur.execute(
                    "SELECT club_id, name FROM clubs WHERE club_id = ?", (club_id,)
                ).fetchone()
                if not club:
                    return _fail(err("club_not_found", club_id=club_id))
                rows = cur.execute("""
                    SELECT s.student_id, s.name, sc.score
                    FROM club_test_selection t
                    JOIN students s ON s.student_id = t.student_id
                    LEFT JOIN club_scores sc ON sc.student_id = t.student_id AND sc.club_id = t.club_id
                    WHERE t.club_id = ?
                    ORDER BY s.student_id
                """, (club_id,)).fetchall()
                return _ok({
                    "club_id": club["club_id"],
                    "club_name": club["name"],
                    "applicants": [dict(r) for r in rows],
                })
        except Exception as e:
            return _fail(err("error_reading_scoring_list", detail=str(e)))

    def submit_club_scores(self, club_id: str, scores: list):
        """
        Lưu điểm chấm cho 1 club. scores: [{"student_id": "...", "score": 8.5}, ...]
        Chỉ cho điểm học sinh THỰC SỰ có trong club_test_selection của
        club này (không thể chấm 'khống' cho học sinh không thi/xét).
        """
        try:
            if not isinstance(scores, list) or not scores:
                return _fail(err("scores_must_be_nonempty_list"))
            luat = self._luat_nghiem()
            if luat["score_scope"] == "per_person" or luat["priority"] == "tier":
                # Thuật toán bỏ qua club_scores ở hai chế độ này: lưu mà báo "đã lưu" là nói dối.
                return _fail(err("scoring_not_per_slot"))

            with self._ket_noi_ghi() as cur:
                club_exists = cur.execute(
                    "SELECT 1 FROM clubs WHERE club_id = ?", (club_id,)
                ).fetchone()
                if not club_exists:
                    return _fail(err("club_not_found", club_id=club_id))

                valid_applicants = {
                    r[0] for r in cur.execute(
                        "SELECT student_id FROM club_test_selection WHERE club_id = ?",
                        (club_id,),
                    ).fetchall()
                }

                n_saved, n_xoa, skipped = 0, 0, []
                for entry in scores:
                    if not isinstance(entry, dict):
                        skipped.append(err("score_not_applicant", student_id=str(entry)))
                        continue
                    sid = entry.get("student_id")
                    score = entry.get("score")
                    if sid not in valid_applicants:
                        skipped.append(err("score_not_applicant", student_id=sid))
                        continue
                    if score is None or score == "":
                        # cho phep xoa diem (bo trong o) bang cach xoa ban ghi
                        cur.execute(
                            "DELETE FROM club_scores WHERE student_id = ? AND club_id = ?",
                            (sid, club_id),
                        )
                        n_xoa += 1
                        continue
                    # Dùng CHUNG bộ đọc số với đường nạp tệp, thay vì float()
                    # thẳng. `_doc_diem` nhận cả dấu phẩy thập phân kiểu Việt
                    # ("8,5") lẫn dấu chấm, và loại inf/nan. Trước đây hai cửa
                    # hai luật: nạp tệp hiểu "8,5" là 8.5, còn màn hình chấm
                    # điểm thì không — mà đó mới là cửa giáo viên gõ tay.
                    so = self._doc_diem(score if isinstance(score, str) else str(score))
                    if so is None:
                        skipped.append(err("score_not_a_number", student_id=sid, diem_goc=score))
                        continue
                    score = so
                    # Điểm âm: đường NẠP TỆP đã từ chối từ trước
                    # (csv_score_negative), nhưng màn hình chấm điểm thì nhận.
                    # Cùng một lỗi thừa dấu trừ, bắt được hay không lại tuỳ
                    # giáo viên đi cửa nào — đo được: -9 vào lọt ở đây, và em
                    # điểm cao nhất tụt xuống dưới tất cả, mất chỗ.
                    if score < 0:
                        skipped.append(err("score_negative", student_id=sid, diem_goc=score))
                        continue
                    cur.execute(
                        "INSERT INTO club_scores (student_id, club_id, score) VALUES (?, ?, ?) "
                        "ON CONFLICT(student_id, club_id) DO UPDATE SET score = excluded.score",
                        (sid, club_id, score),
                    )
                    n_saved += 1

            # Lượt chỉ có ô điểm sai (không lưu, không xoá được dòng nào) mà trả ok là để người
            # chấm tưởng đã lưu (A13.8): trả lỗi, liệt kê từng em / giá trị. Lượt lẫn ô đúng và
            # sai vẫn lưu phần đúng, ok kèm warnings như cũ.
            sai_gia_tri = [w for w in skipped
                           if w["code"] in ("score_not_a_number", "score_negative")]
            if sai_gia_tri and not n_saved and not n_xoa:
                return _fail(sai_gia_tri)
            return _ok({"club_id": club_id, "n_saved": n_saved, "warnings": skipped})
        except CauHinhHong as e:
            return _fail(err("ws_cau_hinh_hong", detail=str(e)))
        except Exception as e:
            return _fail(err("error_saving_scores", detail=str(e)))
