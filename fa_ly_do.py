"""Câu giải thích kết quả FA-DAA cho học sinh (V§9.1) — MỘT nơi duy nhất giữ mẫu câu.

Hàm nhận MỘT dòng lý do (`fa_daa.ly_do_ket_qua`) và tên CLB; câu chỉ nói về học sinh đó và CLB —
KHÔNG bao giờ chứa mã hay tên học sinh khác (rủi ro C3). Không hứa "ưu tiên bù kỳ sau": ưu tiên bù
(D1) chưa làm trong kỳ này.

Dữ liệu trong test là dữ liệu MÔ PHỎNG.
"""

from __future__ import annotations


def _so(x) -> str:
    """12.0 -> '12'; 7.3 -> '7,3' (dấu phẩy thập phân kiểu Việt, FA-D7L)."""
    if x is None:
        return ""
    f = float(x)
    return str(int(f)) if f.is_integer() else str(round(f, 2)).replace(".", ",")


def cau_ly_do(dong: dict, ten_clb: str) -> str:
    """Câu tiếng Việt giải thích `dong` (một dòng `fa_ly_do`) cho chính học sinh đó."""
    ma = dong.get("reason")
    if dong.get("outcome") == "ACCEPTED":
        return "Em được xếp vào %s – nguyện vọng %s của em." % (ten_clb, dong.get("rank_in_list"))
    if ma == "SCORE":
        return ("%s đủ chỗ với các bạn có điểm thử thách cao hơn (điểm chuẩn %s, em %s)."
                % (ten_clb, _so(dong.get("cut_score")), _so(dong.get("diem_em"))))
    if ma == "MEDAL":
        return ("Em và các bạn bằng điểm; các bạn có huy chương cao hơn ở %s được xét trước."
                % ten_clb)
    if ma == "RESERVED":
        return "%s dành chỗ cho các bạn đã được giữ chỗ nên em chưa vào được." % ten_clb
    if ma == "LOTTERY":
        cau = ("Em bằng %s bạn khác ở mọi tiêu chí, tranh %s chỗ cuối; số bốc thăm của em chưa trúng."
               % (dong.get("n_hoa"), dong.get("k_cho")))
        if dong.get("waitlist_pos"):
            cau += " Em đứng thứ %s danh sách chờ." % dong["waitlist_pos"]
        return cau
    if ma == "BELOW_PASS":
        return "Em chưa đạt mốc %s điểm của %s." % (_so(dong.get("cut_score")), ten_clb)
    if ma == "NOT_ATTEMPTED":
        return "Em chưa làm bài thử thách của %s nên chưa được xét ở CLB này." % ten_clb
    if ma == "CLUB_CLOSED":
        return "%s không đủ thành viên tối thiểu nên tạm không mở kỳ này." % ten_clb
    if ma == "KHONG_DANG_KY":
        return "Em chưa đăng ký CLB nào ở buổi này nên được xếp vào %s (CLB Tự do)." % ten_clb
    if ma == "HET_NGUYEN_VONG":
        return ("Các CLB em đã chọn ở buổi này đều đủ chỗ nên em được xếp vào %s (CLB Tự do)."
                % ten_clb)
    return ""
