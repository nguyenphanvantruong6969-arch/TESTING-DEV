# -*- coding: utf-8 -*-
"""Sinh bộ dữ liệu MÔ PHỎNG, tiếng Việt, để thử tính năng workspace (không gian làm việc).

Kịch bản: "Công ty Bình Minh" phân nhân viên vào dự án nội bộ trong hai ngày
(Thứ 3, Thứ 5). Từ vựng khác hẳn trường học, nên màn hình, Sổ nhập và tệp xuất
đều phải đổi theo nhãn:

    Học sinh -> Nhân viên · Câu lạc bộ -> Dự án · Buổi -> Ngày
    Nhóm ưu tiên -> Diện ưu tiên · Điểm -> Điểm phỏng vấn

Luật: tối đa 5 nguyện vọng và 2 dự án phỏng vấn mỗi ngày; điểm theo từng dự án.

Ghi ra ba tệp cạnh script này:
    cau_hinh_workspace.json  — cấu hình (để đối chiếu, hoặc gõ tay vào trình tạo 4 bước)
    cong-ty-binh-minh.zip    — workspace đã gắn cấu hình VÀ nạp sẵn sổ; dùng "Nhập workspace"
    SO_NHAP_DU_AN.xlsx       — Sổ nhập theo đúng nhãn của workspace

Mọi tên người đều bịa, ghép từ bảng họ/đệm/tên. Tất định theo SEED.

    python du_lieu_test/bo_thu_workspace/tao_bo_workspace.py
"""

import base64
import json
import os
import random
import shutil
import sys
import tempfile

DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.normpath(os.path.join(DAY, "..", ".."))
sys.path.insert(0, GOC)

import so_nhap  # noqa: E402
import workspace as ws  # noqa: E402
from cau_hinh_ws import chuan_hoa  # noqa: E402

SEED = 2026
TEN_WS = "Công ty Bình Minh"

CAU_HINH = {
    "industry": "company",
    "labels": {
        "person": {"vi": "Nhân viên", "en": "Employee"},
        "slot": {"vi": "Dự án", "en": "Project"},
        "session": {"vi": "Ngày", "en": "Day"},
        "group": {"vi": "Diện ưu tiên", "en": "Priority group"},
        "score": {"vi": "Điểm phỏng vấn", "en": "Interview score"},
    },
    "rules": {
        "max_choices": 5,
        "max_tests": 2,
        "priority": "score",
        "tier_mode": "reserve",
        "score_scope": "per_slot",
        "tiers": [],
    },
}

# (mã, tên, ngày, chỉ tiêu, suất ưu tiên, diện, có phỏng vấn)
DU_AN = [
    ("da_chuyendoiso", "Chuyển đổi số kho hàng", "thu_3", 8, 2, "tan_tuyen", True),
    ("da_appbanhang", "Ứng dụng bán hàng di động", "thu_3", 7, 0, "", True),
    ("da_baocaotc", "Báo cáo tài chính quý", "thu_3", 6, 0, "", False),
    ("da_dulieukh", "Phân tích dữ liệu khách hàng", "thu_3", 6, 0, "", False),
    ("da_daotao", "Đào tạo nội bộ", "thu_5", 8, 2, "tan_tuyen", False),
    ("da_website", "Làm mới website công ty", "thu_5", 7, 0, "", True),
    ("da_csr", "Chương trình cộng đồng (CSR)", "thu_5", 6, 0, "", False),
    ("da_tuyendung", "Ngày hội tuyển dụng", "thu_5", 5, 1, "noi_bat", True),
]

_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Ngô", "Đặng", "Dương", "Lý"]
_DEM = ["Văn", "Thị", "Minh", "Gia", "Bảo", "Khánh", "Hoài", "Quốc", "Thanh", "Anh", "Ngọc"]
_TEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Huy", "Khoa", "Lan", "Linh", "Long",
        "Mai", "Nam", "Ngân", "Phong", "Phúc", "Quân", "Tâm", "Thảo", "Trang", "Tú", "Vy"]

SO_NV = 54          # tổng chỗ 53 -> hơi chật, đủ để có người không có dự án ngày đó


def sinh():
    rnd = random.Random(SEED)
    clubs = [{"club_id": cid, "name": ten, "capacity": cho, "reserve_capacity": ut,
              "reserve_group": nhom, "buoi": ngay}
             for cid, ten, ngay, cho, ut, nhom, _ in DU_AN]
    theo_ngay = {}
    for c in clubs:
        theo_ngay.setdefault(c["buoi"], []).append(c["club_id"])
    phong_van = {d[0] for d in DU_AN if d[6]}

    students = []
    for i in range(1, SO_NV + 1):
        nhom = "tan_tuyen" if rnd.random() < 0.2 else ("noi_bat" if rnd.random() < 0.1 else "")
        nv = []
        # Bận một ngày là hợp lệ; bận CẢ HAI ngày thì phần mềm cảnh báo (không khai gì).
        ban = rnd.choice(sorted(theo_ngay)) if rnd.random() < 0.15 else None
        for ngay in sorted(theo_ngay):
            if ngay == ban:
                continue
            ds = theo_ngay[ngay]
            chon = rnd.sample(ds, rnd.randint(1, min(len(ds), CAU_HINH["rules"]["max_choices"])))
            so_thi = 0
            for cid in chon:
                thi = (cid in phong_van and so_thi < CAU_HINH["rules"]["max_tests"]
                       and rnd.random() < 0.8)
                so_thi += thi
                diem = ("%.1f" % rnd.uniform(5.0, 10.0)).replace(".", ",") if thi else ""
                nv.append({"club_id": cid, "thi": thi, "diem": diem})
        students.append({"student_id": "NV%03d" % i,
                         "name": "%s %s %s" % (rnd.choice(_HO), rnd.choice(_DEM), rnd.choice(_TEN)),
                         "reserve_group": nhom, "nv": nv})
    return clubs, students


def main():
    cfg = chuan_hoa(dict(CAU_HINH, name=TEN_WS))
    with open(os.path.join(DAY, "cau_hinh_workspace.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    clubs, students = sinh()
    so_nhap.ghi_so_nhap(os.path.join(DAY, "SO_NHAP_DU_AN.xlsx"), clubs, students, cfg=cfg)

    root = tempfile.mkdtemp()
    try:
        slug = ws.tao(root, TEN_WS, CAU_HINH)
        # Nạp sẵn sổ vào workspace: người thử chỉ cần nhập zip, mở, bấm chạy.
        from api import PipelineAPI
        db = ws.duong_dan_db(root, slug)
        with open(os.path.join(DAY, "SO_NHAP_DU_AN.xlsx"), "rb") as f:
            kq = PipelineAPI(db, thu_muc_xuat=root).import_so_nhap(
                base64.b64encode(f.read()).decode())
        if not kq["ok"] or kq["data"].get("warnings"):
            raise SystemExit("Nạp sổ vào workspace thất bại: %r" % kq)
        for tep in os.listdir(os.path.dirname(db)):   # bản sao lưu lúc nạp không đi theo
            if tep != ws.TEN_DB and not tep.endswith(".zip"):
                p = os.path.join(os.path.dirname(db), tep)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        ws.xuat_zip(root, slug, os.path.join(DAY, slug + ".zip"))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("Đã ghi: cau_hinh_workspace.json, SO_NHAP_DU_AN.xlsx, %s.zip "
          "(%d dự án, %d nhân viên)" % (slug, len(clubs), len(students)))


if __name__ == "__main__":
    main()
