"""Dựng sẵn một cơ sở dữ liệu ĐÃ NẠP VÀ ĐÃ CHẤM ĐIỂM để demo.

    ./.venv/bin/python du_lieu_test/tao_db_demo.py                 # mặc định: Wharton BẬT
    ./.venv/bin/python du_lieu_test/tao_db_demo.py --tat-wharton   # bản cũ, tái lập số liệu đã công bố
    ./.venv/bin/python du_lieu_test/tao_db_demo.py --ra /tmp/x.db  # ghi ra chỗ khác

⚠️  DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT.

VÌ SAO CẦN TỆP NÀY
Bộ ba tệp Excel nay đã kèm sẵn điểm chấm (cột score_*), nên nạp tệp là
chạy được ngay. Tệp .db này chỉ để tiết kiệm thêm bước nạp: hôm trình
bày chép nó vào cạnh app là mở lên bấm "Chạy phân bổ" luôn.

HAI CHẾ ĐỘ
  * Mặc định (A13.13): cấu hình mặc định của phần mềm (Wharton BẬT), nạp
    `SO_NHAP_DQT_120HS_HOP_LE.xlsx` — một Sổ nhập có điểm quyết tâm HỢP LỆ
    (điểm quyết tâm là dữ liệu MÔ PHỎNG, sinh bởi `sinh_du_lieu_diem_quyet_tam.py`).
    Chọn bản 120HS vì nó giữ nguyên nguyện vọng và điểm thi của
    `SO_NHAP_MAU_120HS_3BUOI.xlsx`, chỉ thêm điểm quyết tâm; đủ nhỏ để demo nhanh.
  * `--tat-wharton`: dựng y như trước A13.13 — bộ ba TEST_01..03, ghi
    `wharton: false`. Dùng để tái lập mọi số liệu đã công bố (CLAUDE.md quy tắc 4).

CỐ Ý DỪNG TRƯỚC KHI CHẠY PHÂN BỔ. Phần đáng xem nhất là lúc thuật toán
chạy và kết quả hiện ra — nếu dựng sẵn cả phần đó thì không còn gì để xem.
"""

import argparse
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import PipelineAPI

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DICH = os.path.join(THU_MUC, "app_DEMO_da_cham_diem.db")

SO_NHAP_DQT = "SO_NHAP_DQT_120HS_HOP_LE.xlsx"

TEP = [
    "TEST_01_danh_sach_CLB.xlsx",
    "TEST_02_chon_CLB_muon_thi.xlsx",
    "TEST_03_xep_hang_nguyen_vong.xlsx",
]


def doc_xlsx(api, ten):
    with open(os.path.join(THU_MUC, ten), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = api.xlsx_to_csv_text(b64)
    if not r["ok"]:
        raise SystemExit("khong doc duoc %s: %r" % (ten, r["errors"]))
    d = r["data"]
    return d["csv_text"] if isinstance(d, dict) else d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tat-wharton", action="store_true",
                    help="dung ban cu: bo ba TEST_01..03, wharton=false")
    ap.add_argument("--ra", default=DICH, help="duong dan .db dau ra (mac dinh: %s)" % DICH)
    a = ap.parse_args(argv)
    dich = os.path.abspath(a.ra)

    if os.path.exists(dich):
        os.remove(dich)
    api = PipelineAPI(dich)
    if a.tat_wharton:
        # A13.13: mặc định đã BẬT; số liệu cũ = tắt RÕ RÀNG
        __import__("cau_hinh_ws").ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})

    if a.tat_wharton:
        for ten in TEP:
            r = api.import_csv_auto(doc_xlsx(api, ten))
            if not r["ok"]:
                raise SystemExit("nhap that bai %s: %r" % (ten, r["errors"]))
            print("  nap  %-38s ok" % ten)
    else:
        # Sổ nhập nhiều sheet (CLB + học sinh): đi đường import_so_nhap.
        with open(os.path.join(THU_MUC, SO_NHAP_DQT), "rb") as f:
            r = api.import_so_nhap(base64.b64encode(f.read()).decode())
        if not r["ok"]:
            raise SystemExit("nhap that bai %s: %r" % (SO_NHAP_DQT, r["errors"]))
        print("  nap  %-38s ok" % SO_NHAP_DQT)

    # KHONG cham diem o day nua: diem den thang tu cot score_* trong
    # TEST_02. Cham them o day se ghi de len diem that cua tep.
    hr = api.get_data_health_report()["data"]
    print("\nCanh bao du lieu con lai: %d (nghiem trong: %d)"
          % (hr["n_warnings"], hr["n_high"]))
    for w in hr["warnings"]:
        print("   %s" % w["code"])

    print("\nDa dung: %s  (wharton: %s)" % (dich, "TAT" if a.tat_wharton else "BAT"))
    print("CHUA chay phan bo — de danh cho luc demo.")


if __name__ == "__main__":
    main()
