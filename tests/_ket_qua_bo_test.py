"""Chạy một bộ trong du_lieu_test/ bằng phần mềm thật với hạt giống cố định, trả kết quả
dưới dạng dữ liệu so sánh được. Dùng cho test "mặc định trường học cho ra đúng kết quả như
trước khi có luật workspace" (tests/test_ws_luat.py)."""

import glob
import io
import os

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BO = {
    "nhieu_buoi": "bo_nhieu_buoi",
    "sach": "bo_sach",
    "can_bang": "bo_can_bang",
}


def nap_bo(api, ten_bo):
    thu_muc = os.path.join(GOC, "du_lieu_test", BO[ten_bo])
    for tep in sorted(glob.glob(os.path.join(thu_muc, "*_0[123]_*.csv"))):
        with io.open(tep, encoding="utf-8-sig") as f:
            res = api.import_csv_auto(f.read())
        assert res["ok"], (tep, res["errors"])


def chay_bo(api, ten_bo, seed=42):
    """-> [(student_id, buoi, club_id, matched_tier, rank)] sắp theo thứ tự cố định."""
    nap_bo(api, ten_bo)
    res = api.run_pipeline(seed=seed)
    assert res["ok"], res
    with api._ket_noi_doc() as cur:
        return [list(r) for r in cur.execute(
            "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref "
            "FROM match_results ORDER BY student_id, buoi")]
