# -*- coding: utf-8 -*-
"""So hai Sổ nhập CLB (trước / sau khi giáo viên sửa): từ chối GIẢM chỉ tiêu và ĐỔI loại CLB.

Dùng: python so_sanh_suc_chua.py SO_NHAP_TRUOC.xlsx SO_NHAP_SAU.xlsx

Mã thoát: 0 = hợp lệ (chỉ tăng chỉ tiêu, thêm CLB mới, hoặc đặt loại lần đầu); 1 = có vi phạm
(in từng dòng); 2 = không đọc được tệp / sổ có lỗi. Loại CLB bị khoá từ lúc MỞ đăng ký (V§4.1).
Chỉ in mã CLB và chỉ tiêu; không có tên hay mã học sinh.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CAU = {
    "GIAM_SUC_CHUA": "chỉ tiêu giảm từ {truoc} xuống {sau} (chỉ được tăng)",
    "DOI_LOAI": "loại CLB đổi từ {truoc} sang {sau} (loại bị khóa từ lúc mở đăng ký)",
    "MAT_CLB": "CLB không còn trong sổ mới (chỉ tiêu cũ {truoc})",
}


def doc_clb(duong_dan):
    """{club_id: {capacity, loai}} từ một Sổ nhập; ném ValueError nếu sổ lỗi."""
    import openpyxl

    import so_nhap

    wb = openpyxl.load_workbook(duong_dan, data_only=True)
    kq = so_nhap.doc_so_nhap(wb)
    if kq["loi"]:
        raise ValueError("%s: sổ có %d lỗi" % (duong_dan, len(kq["loi"])))
    return {c["club_id"]: {"capacity": c["capacity"], "loai": c.get("loai")} for c in kq["clubs"]}


def main(argv=None):
    # Cửa sổ lệnh / ống dẫn Windows mặc định cp1252: in tiếng Việt sẽ ném UnicodeEncodeError.
    for _luong in (sys.stdout, sys.stderr):
        if hasattr(_luong, "reconfigure"):
            _luong.reconfigure(encoding="utf-8", errors="replace")
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        truoc, sau = doc_clb(argv[0]), doc_clb(argv[1])
    except Exception as e:                      # tệp không có, không phải xlsx, sổ lỗi
        print("Không đọc được: %s" % e)
        return 2
    import fa_daa

    loi = fa_daa.kiem_chi_tang(truoc, sau)
    for x in loi:
        print("CLB %s: %s" % (x["club_id"], CAU[x["loi"]].format(truoc=x["truoc"], sau=x["sau"])))
    if loi:
        print("Từ chối: %d vi phạm." % len(loi))
        return 1
    print("Hợp lệ: chỉ tăng chỉ tiêu, không đổi loại.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
