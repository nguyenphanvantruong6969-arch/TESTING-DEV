# -*- coding: utf-8 -*-
"""T4M-BK4: MỘT lệnh sinh thư mục "nhập là dựng" cho IT (Microsoft: SharePoint List, Power Apps, Power Automate, Forms).

    python mau_forms_thi_clb/tao_bo_dung_t4m.py --de-thi mau_forms_thi_clb/de_thi.json --ra ./bo_dung_t4m [--zip]

Ra (trong --ra):
    01_lists/          site script + CSV mẫu + bảng kiểm cột ECA          (bo_dung_t4m.sinh_bk1, T4M-BK1)
    02_app/            công thức Power Fx bốn màn                          (bo_dung_t4m.sinh_bk1, T4M-BK2)
    03_flow/           BANG_FLOW.md/.csv: một flow DaLam_<ClubId> mỗi CLB có đề (T4M-BK3)
    04_forms/          tao_mau_forms.sinh_moi_clb (gọi như hàm, không viết lại): .docx Quick Import, CAI_DAT, CLB.csv
    HUONG_DAN_IT.md    thứ tự dựng, mỗi bước một dòng pass/fail trỏ về R1..R38 và HDT §9
    README_BK1.md      mục lục của 01_lists, 02_app (do sinh_bk1)
--zip: thêm `<--ra>.zip` NGOÀI thư mục (tên sắp xếp, giờ cố định: sinh lại cho cùng từng byte).

Không sửa lõi, schema, hợp đồng CSV. Kiểm đề trước khi ghi: lỗi thì không ghi tệp nào.
TH: chưa chạy trên Power Apps / SharePoint / Power Automate.
"""

import argparse
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bieu_mau as bm  # noqa: E402
import tao_mau_forms as tm  # noqa: E402
from bo_dung_t4m import bang_flow, huong_dan_it, sinh_bk1, site_script  # noqa: E402

GIO_ZIP = (2026, 1, 1, 0, 0, 0)
TEN_HUONG_DAN = "HUONG_DAN_IT.md"


def _tat_ca_tep(thu_muc):
    ds = []
    for goc, _d, tep in os.walk(thu_muc):
        for t in tep:
            ds.append(os.path.relpath(os.path.join(goc, t), thu_muc).replace(os.sep, "/"))
    return sorted(ds)


def ghi_zip(thu_muc, duong_zip):
    """Nén `thu_muc` thành `duong_zip` (nằm NGOÀI thư mục): tên sắp xếp, giờ và quyền cố định."""
    with zipfile.ZipFile(duong_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for ten in _tat_ca_tep(thu_muc):
            zi = zipfile.ZipInfo(ten, date_time=GIO_ZIP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(os.path.join(thu_muc, *ten.split("/")), "rb") as f:
                zf.writestr(zi, f.read())


def tao_bo_dung(de, ra, tao_zip=False, in_ra=print):
    """Sinh cả bốn thư mục + HUONG_DAN_IT.md vào `ra`. Trả đường dẫn zip (hoặc None).

    Lỗi đề (không CLB nào có đề, quá trần câu) -> bm.LoiDeThi trước khi ghi bất cứ gì."""
    tm._kiem_moi_clb(de)
    ra = os.path.abspath(ra)
    os.makedirs(ra, exist_ok=True)
    sinh_bk1.ghi_tat_ca(ra, de, in_ra=in_ra)
    bang_flow.ghi(os.path.join(ra, "03_flow"), de)
    tm.sinh_moi_clb(de, os.path.join(ra, "04_forms"))
    hang = bang_flow.hang_flow(de)
    n = site_script.dem_hanh_dong(site_script.tao_site_script())
    with open(os.path.join(ra, TEN_HUONG_DAN), "w", encoding="utf-8", newline="\n") as f:
        f.write(huong_dan_it.tao(de, n, hang, site_script.TRAN_DONG_BO, site_script.TRAN_KHONG_DONG_BO))
    duong_zip = None
    if tao_zip:
        duong_zip = ra.rstrip(os.sep) + ".zip"
        ghi_zip(ra, duong_zip)
    return duong_zip


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--de-thi", default=bm.DE_THI_MAC_DINH, help="de_thi.json")
    ap.add_argument("--ra", required=True, help="thư mục ghi bộ dựng")
    ap.add_argument("--zip", action="store_true", help="thêm <ra>.zip (ngoài thư mục)")
    a = ap.parse_args(argv)
    try:
        de = bm.doc_de_thi(a.de_thi)
        duong_zip = tao_bo_dung(de, a.ra, tao_zip=a.zip)
    except (bm.LoiDeThi, ValueError, OSError) as e:
        print("KHÔNG GHI TỆP NÀO — %s" % e, file=sys.stderr)
        return 1
    ra = os.path.abspath(a.ra)
    n_flow = len(bang_flow.hang_flow(de))
    print("Đã sinh bộ dựng T4M cho IT: %d flow, %d tệp trong %s" % (n_flow, len(_tat_ca_tep(ra)), ra))
    for t in _tat_ca_tep(ra):
        print("  " + t)
    if duong_zip:
        print("Zip: " + duong_zip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
