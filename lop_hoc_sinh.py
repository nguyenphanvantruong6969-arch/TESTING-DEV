# -*- coding: utf-8 -*-
"""Chuẩn hoá tên lớp học sinh (A14). Chỉ dùng thư viện chuẩn.

Tách khỏi rbda_priority_pipeline.py (T4-K1) để skill xu-li-raw-forms đóng gói được mà không phải mang
mã thuật toán. rbda_priority_pipeline vẫn xuất tên `chuan_hoa_lop`, hành vi y hệt.
"""

import unicodedata


def chuan_hoa_lop(raw) -> str | None:
    """Chuẩn hoá tên lớp (A14): NFC, bỏ ký tự vô hình (loại Cf: U+200B, U+FEFF…) và ký tự điều
    khiển (Cc), cắt hai đầu, gộp khoảng trắng liên tiếp, IN HOA.

    Rỗng / chỉ khoảng trắng / None -> None (chưa có lớp). Không ép mẫu ("10H1A" hay
    "Ca sáng" đều được) và KHÔNG cắt độ dài (xem LOP_TOI_DA). Dùng chung cho API, nhập CSV,
    Sổ nhập và xuất.
    """
    if raw is None:
        return None
    chu = unicodedata.normalize("NFC", str(raw))
    chu = "".join(c for c in chu if unicodedata.category(c) != "Cf")
    chu = " ".join(chu.split())            # tab / xuống dòng cũng là khoảng trắng: gộp trước
    chu = "".join(c for c in chu if unicodedata.category(c) != "Cc")
    chu = unicodedata.normalize("NFC", chu.upper())
    return chu or None
