# -*- coding: utf-8 -*-
"""T4M-BK1, BK2: sinh bộ dựng danh sách + công thức vào một thư mục.

    cd mau_forms_thi_clb && python -m bo_dung_t4m.sinh_bk1 --de-thi de_thi.json --ra ./ra_bk1

Ra: 01_lists/ (site_script_t4m.json, <list>_mau.csv, KIEM_COT_ECA.md), 02_app/ (4 tệp .txt), README_BK1.md.
Sinh lại cho cùng từng byte. TH: chưa chạy trên Power Apps / SharePoint.
"""

import argparse
import os
import sys

from . import cong_thuc, cong_thuc_fa, cot_lists, mau_csv, site_script

DONG_TH = "TH: chưa chạy trên Power Apps / SharePoint"


def _readme(tep_lists, tep_app):
    L = [DONG_TH, "", "# Bộ dựng T4M-BK1, BK2 (nháp cho IT)", "",
         "Mọi thứ dưới đây là **bản nháp chưa chạy** trên SharePoint / Power Apps. Thử trên BẢN SAO list và app, không đụng bản thật.",
         "Tệp `.json` và `.csv` không chèn được dòng chú thích (sẽ hỏng khi nhập); dòng TH ở trên áp cho cả hai loại.",
         "", "## 01_lists/ (tạo list và cột)", ""]
    L += ["- `%s`" % t for t in tep_lists]
    L += ["", "Cách A/B: áp `site_script_t4m.json` (số hành động in khi sinh; trần 30 đồng bộ, 300 không đồng bộ).",
          "Cách C: Microsoft Lists > tạo từ bảng tính bằng `<list>_mau.csv`; ECA có sẵn thì dùng `KIEM_COT_ECA.md`.",
          "", "## 02_app/ (công thức Power Fx, dán vào BẢN SAO app)", ""]
    L += ["- `%s`" % t for t in tep_app]
    L += ["", "Cột Choice dùng giá trị của dữ liệu giả; giá trị thật của trường là HỎI-IT.", ""]
    return "\n".join(L)


def ghi_tat_ca(ra, de, in_ra=print, fa=False):
    """Sinh toàn bộ vào thư mục `ra`; trả danh sách tệp đã ghi (đường dẫn tương đối). `fa` (FA-M5): cột ECA của FA-DAA."""
    d_lists = os.path.join(ra, "01_lists")
    d_app = os.path.join(ra, "02_app")
    os.makedirs(d_lists, exist_ok=True)
    os.makedirs(d_app, exist_ok=True)
    tat_ca = cot_lists.TAT_CA_FA if fa else None
    tep_lists = ["site_script_t4m.json"] + mau_csv.ghi_csv_mau(d_lists, tat_ca) + ["KIEM_COT_ECA.md"]
    site_script.ghi(os.path.join(d_lists, "site_script_t4m.json"), in_ra, tat_ca)
    mau_csv.ghi_kiem_cot_eca(os.path.join(d_lists, "KIEM_COT_ECA.md"), fa)
    tep_app = cong_thuc.ghi(d_app, de)
    if fa:                                   # GAP-11: màn đăng ký FA (đặc tả §12), chỉ ở bộ dựng --fa-daa
        tep_app = sorted(tep_app + cong_thuc_fa.ghi_fa(d_app, de))
    with open(os.path.join(ra, "README_BK1.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(_readme(sorted(tep_lists), tep_app))
    return (["01_lists/" + t for t in sorted(tep_lists)] + ["02_app/" + t for t in tep_app] + ["README_BK1.md"])


def main(argv=None):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import bieu_mau as bm
    ap = argparse.ArgumentParser(description="Sinh site script, CSV mẫu, bảng kiểm cột và công thức Power Fx.")
    ap.add_argument("--de-thi", default=bm.DE_THI_MAC_DINH)
    ap.add_argument("--ra", default="ra_bk1")
    a = ap.parse_args(argv)
    for t in ghi_tat_ca(a.ra, bm.doc_de_thi(a.de_thi)):
        print("  " + t)


if __name__ == "__main__":
    main()
