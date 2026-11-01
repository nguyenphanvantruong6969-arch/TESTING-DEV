# -*- coding: utf-8 -*-
"""Thêm ĐIỂM QUYẾT TÂM MÔ PHỎNG hợp lệ vào các bộ ví dụ giao người dùng (A13.13). MỘT lệnh.

    python du_lieu_test/them_diem_quyet_tam_vao_mau.py

DỮ LIỆU MÔ PHỎNG: điểm do máy sinh bằng `random.Random(seed)` với seed cố định ở bảng DICH
dưới đây; không phải khảo sát thật, không gõ tay. Chạy lại cho ra đúng cùng byte.

Vì sao có tệp này: từ A13.13, workspace trường học BẬT điểm quyết tâm theo mặc định, nên bộ
ví dụ "nạp là chạy" phải có điểm hợp lệ (mỗi quỹ của mỗi buổi chia đủ 100 điểm). Hợp đồng cột
CSV KHÔNG đổi: chỉ thêm cột `wp_k` (hoặc `<buoi>_wp_k`) cạnh `pref_k` (`<buoi>_pref_k`).

Làm gì với mỗi bộ (thư mục, tệp nguyện vọng, tệp chọn thi, tệp danh sách CLB):
  1. đọc nguyện vọng và ô tick thi; quỹ 1 = CLB em có tick thi, quỹ 2 = CLB còn lại, mỗi BUỔI
     một lần (xem `rbda_priority_pipeline.kiem_ho_so_wharton`);
  2. quỹ chỉ có một CLB thì ghi 100; quỹ nhiều CLB thì chia 100 theo trọng số ngẫu nhiên có
     seed, phần dư dồn cho CLB đứng trước;
  3. ghi lại tệp nguyện vọng (.csv, và .xlsx nếu có) kèm cột `wp`, rồi dựng lại các Sổ nhập
     `.xlsx` của bộ đó bằng `mau_csv/tao_so_nhap.py` (đọc cột `wp` từ CSV).
"""

import copy
import csv
import io
import os
import random
import re
import sys

import openpyxl
from openpyxl.styles import Font

_DAY = os.path.dirname(os.path.abspath(__file__))
_GOC = os.path.dirname(_DAY)
sys.path.insert(0, _GOC)
sys.path.insert(0, os.path.join(_GOC, "mau_csv"))

MAU = os.path.join(_GOC, "mau_csv")
# (thư mục, tệp nguyện vọng, tệp chọn thi, tệp CLB, tệp .xlsx tương ứng của tệp nguyện vọng, seed)
DICH = [
    (os.path.join(_DAY, "vi_du_huong_dan"), "VIDU_03_xep_hang_nguyen_vong",
     "VIDU_02_chon_CLB_muon_thi", "VIDU_01_danh_sach_CLB", True, 112026101),
    (os.path.join(MAU, "vi_du_day_du"), "03_xep_hang_nguyen_vong",
     "02_chon_CLB_muon_thi", "01_danh_sach_CLB", False, 112026102),
    (os.path.join(MAU, "vi_du_ca_tuan"), "03_xep_hang_nguyen_vong",
     "02_chon_CLB_muon_thi", "01_danh_sach_CLB", False, 112026103),
    (MAU, "08_nguyen_vong_nhieu_buoi", "07_chon_club_thi_nhieu_buoi",
     "06_danh_sach_club_nhieu_buoi", False, 112026104),
]
_RE_PREF = re.compile(r"^(?:(?P<buoi>.+)_)?pref_(?P<k>\d+)$")
_RE_WP = re.compile(r"^(?:(?P<buoi>.+)_)?wp_(?P<k>\d+)$")


def _doc_csv(duong):
    with io.open(duong, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def chia_diem(rng, n):
    """Chia đúng 100 điểm nguyên cho `n` CLB (n >= 1); phần dư dồn cho CLB đầu."""
    if n == 1:
        return [100]
    trong_so = [rng.randint(1, 9) for _ in range(n)]
    tong = sum(trong_so)
    diem = [100 * w // tong for w in trong_so]
    diem[0] += 100 - sum(diem)
    return diem


def tinh_wp(tieu_de, dong_nv, dong_thi, buoi_cua, seed):
    """-> (cột wp mới theo thứ tự, {student_id: {cột wp: điểm}}). Hàm thuần của đầu vào + seed."""
    rng = random.Random(seed)
    cot_pref = []
    for c in tieu_de:
        m = _RE_PREF.match(c or "")
        if m:
            cot_pref.append((m.group("buoi"), int(m.group("k")), c))
    cot_wp = {c: ((b + "_" if b else "") + "wp_%d" % k) for b, k, c in cot_pref}
    thi = {}
    for r in dong_thi:
        sid = (r.get("student_id") or "").strip()
        thi[sid] = {(v or "").strip() for c, v in r.items()
                    if c and c.startswith("test_club_") and (v or "").strip()}
    ra = {}
    for r in dong_nv:
        sid = (r.get("student_id") or "").strip()
        if not sid:
            continue
        theo_buoi = {}
        for b, k, c in sorted(cot_pref, key=lambda x: (x[0] or "", x[1])):
            cid = (r.get(c) or "").strip()
            if cid:
                theo_buoi.setdefault(buoi_cua.get(cid, b or ""), []).append((c, cid))
        dd = {}
        for buoi in sorted(theo_buoi):
            ds = theo_buoi[buoi]
            for quy in (True, False):
                tap = [(c, cid) for c, cid in ds if (cid in thi.get(sid, set())) is quy]
                for (c, _), d in zip(tap, chia_diem(rng, len(tap)) if tap else []):
                    dd[cot_wp[c]] = d
        ra[sid] = dd
    return [cot_wp[c] for _, _, c in cot_pref], ra


def _ghi_csv(duong, tieu_de, dong):
    with io.open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu_de)
        for r in dong:
            w.writerow([r.get(c, "") for c in tieu_de])


def _them_vao_xlsx(duong, cot_moi, ra):
    wb = openpyxl.load_workbook(duong)
    ws = wb.worksheets[0]
    tieu_de = [c.value for c in ws[1]]
    for c in [t for t in tieu_de if t and _RE_WP.match(str(t))]:       # chạy lại: bỏ cột cũ
        ws.delete_cols(tieu_de.index(c) + 1)
        tieu_de = [x.value for x in ws[1]]
    mau = ws.cell(row=1, column=len(tieu_de))
    cot0 = len(tieu_de) + 1
    for j, ten in enumerate(cot_moi):
        o = ws.cell(row=1, column=cot0 + j, value=ten)
        o.font, o.fill, o.alignment, o.border = (copy.copy(mau.font), copy.copy(mau.fill),
                                                 copy.copy(mau.alignment), copy.copy(mau.border))
    for i in range(2, ws.max_row + 1):
        sid = str(ws.cell(row=i, column=1).value or "").strip()
        for j, ten in enumerate(cot_moi):
            if sid in ra and ten in ra[sid]:
                ws.cell(row=i, column=cot0 + j, value=ra[sid][ten])
    if "Ghi chú" in wb.sheetnames:
        gc = wb["Ghi chú"]
        dong = [c.value for c in gc["A"]]
        if not any(str(v or "").startswith("Cột wp_") for v in dong):
            gc.append([""])
            for chu in ("Cột wp_k (hoặc <buoi>_wp_k) = ĐIỂM QUYẾT TÂM MÔ PHỎNG của nguyện vọng k:",
                        "mỗi quỹ của mỗi buổi chia đủ 100 điểm. Sinh bằng",
                        "du_lieu_test/them_diem_quyet_tam_vao_mau.py (seed cố định)."):
                gc.append([chu])
            gc.cell(row=gc.max_row - 2, column=1).font = Font(bold=False)
    wb.save(duong)


def main():
    import tao_so_nhap as tsn
    for thu_muc, nv, thi, clb, co_xlsx, seed in DICH:
        p_nv = os.path.join(thu_muc, nv + ".csv")
        tieu_de, dong_nv = _doc_csv(p_nv)
        tieu_de = [c for c in tieu_de if not _RE_WP.match(c or "")]       # idempotent
        dong_nv = [{k: v for k, v in r.items() if not _RE_WP.match(k or "")} for r in dong_nv]
        _, dong_thi = _doc_csv(os.path.join(thu_muc, thi + ".csv"))
        _, dong_clb = _doc_csv(os.path.join(thu_muc, clb + ".csv"))
        buoi_cua = {r["club_id"]: (r.get("buoi") or "").strip() for r in dong_clb}
        cot_moi, ra = tinh_wp(tieu_de, dong_nv, dong_thi, buoi_cua, seed)
        for r in dong_nv:
            r.update(ra.get((r.get("student_id") or "").strip(), {}))
        _ghi_csv(p_nv, tieu_de + cot_moi, dong_nv)
        if co_xlsx:
            _them_vao_xlsx(os.path.join(thu_muc, nv + ".xlsx"), cot_moi, ra)
        print("  %-60s +%d cột wp, %d em" % (os.path.relpath(p_nv, _GOC), len(cot_moi), len(ra)))
    # Sổ nhập dựng lại từ bộ ba CSV (đọc cột wp)
    for ten_bo in tsn.BO_VI_DU:
        print("  sổ", tsn.tao_vi_du(ten_bo))
    for thu_muc, tien_to, duoi, ten in tsn.BO_DU_LIEU_TEST[:1]:
        print("  sổ", tsn.tao_du_lieu_test_mot(thu_muc, tien_to, duoi, ten))


if __name__ == "__main__":
    main()
