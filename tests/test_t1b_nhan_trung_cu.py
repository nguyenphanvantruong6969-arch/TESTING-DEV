# -*- coding: utf-8 -*-
"""T1b — workspace cũ đã trùng nhãn hai danh từ vẫn lưu được (đổi tên, đổi luật).

Chỉ chặn cặp trùng MỚI so với cấu hình đang lưu. Dữ liệu là dữ liệu MÔ PHỎNG."""

import json
import os
import re
import sqlite3

import cau_hinh_ws as ch
import workspace as ws
from api import PipelineAPI

TRUNG = {"labels": {"group": {"vi": "Lớp", "en": "Class"}}}     # nhóm ưu tiên trùng nhãn Lớp


def _api(tmp_path, cfg_tho=None):
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    if cfg_tho is not None:      # giả lập cấu hình đã lưu từ bản cũ, không qua kiểm trùng
        day_du = ch._chuan_hoa(cfg_tho, kiem_trung=False)
        conn = sqlite3.connect(db)
        conn.execute("INSERT OR REPLACE INTO workspace_settings VALUES ('config', ?)",
                     (json.dumps(day_du, ensure_ascii=False),))
        conn.commit()
        conn.close()
    return PipelineAPI(db, thu_muc_goc_ws=goc), slug


def test_cu_trung_doi_ten_workspace_van_luu_duoc(tmp_path):
    api, slug = _api(tmp_path, TRUNG)
    kq = api.update_workspace_config({"name": "Tên mới"}, slug)
    assert kq["ok"], kq
    assert kq["data"]["config"]["name"] == "Tên mới"
    assert kq["data"]["config"]["labels"]["group"]["vi"] == "Lớp"


def test_cu_trung_doi_mot_luat_van_luu_duoc(tmp_path):
    api, slug = _api(tmp_path, TRUNG)
    kq = api.update_workspace_config({"rules": {"max_choices": 4}}, slug)
    assert kq["ok"], kq
    assert kq["data"]["config"]["rules"]["max_choices"] == 4


def test_sach_dat_thanh_trung_van_bi_tu_choi(tmp_path):
    api, slug = _api(tmp_path)
    kq = api.update_workspace_config(TRUNG, slug)
    assert not kq["ok"] and kq["errors"][0]["code"] == "nhan_trung_danh_tu"
    assert ch.doc_cau_hinh(api.db_path)["labels"]["group"]["vi"] != "Lớp"     # chưa ghi gì


def test_cu_trung_them_cap_trung_thu_hai_bi_tu_choi(tmp_path):
    api, slug = _api(tmp_path, TRUNG)
    kq = api.update_workspace_config({"labels": {"person": {"vi": "Điểm", "en": "People"}}}, slug)
    assert not kq["ok"] and kq["errors"][0]["code"] == "nhan_trung_danh_tu"
    assert {kq["errors"][0]["params"]["a"], kq["errors"][0]["params"]["b"]} == {"person", "score"}
    assert ch.doc_cau_hinh(api.db_path)["labels"]["person"]["vi"] != "Điểm"


def test_cu_trung_sua_nhan_het_trung_luu_duoc(tmp_path):
    api, slug = _api(tmp_path, TRUNG)
    kq = api.update_workspace_config(
        {"labels": {"group": {"vi": "Cấp bậc", "en": "Level"}}}, slug)
    assert kq["ok"], kq
    assert ch.cac_cap_nhan_trung(kq["data"]["config"]["labels"]) == []
    # sau khi sạch, đặt lại thành trùng là cặp MỚI: bị chặn
    kq = api.update_workspace_config(TRUNG, slug)
    assert not kq["ok"] and kq["errors"][0]["code"] == "nhan_trung_danh_tu"


def test_t1a_so_mau_tinh_trung_so_mau_phan_mem_tao_moi_sheet(tmp_path):
    """T1a: mau_csv/SO_NHAP_CLB.xlsx giống sổ mẫu phần mềm tạo ở MỌI ô của MỌI sheet (cả Hướng dẫn)."""
    import openpyxl
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api = PipelineAPI(str(tmp_path / "a.db"))
    p = api.tao_so_nhap_mau(str(tmp_path / "phan_mem.xlsx"))["data"]["path"]
    a = openpyxl.load_workbook(os.path.join(goc, "mau_csv", "SO_NHAP_CLB.xlsx"))
    b = openpyxl.load_workbook(p)
    assert a.sheetnames == b.sheetnames
    for ten in a.sheetnames:
        assert [[c.value for c in r] for r in a[ten].iter_rows()] \
            == [[c.value for c in r] for r in b[ten].iter_rows()], ten
    huong = [r[0].value or "" for r in a["Hướng dẫn"].iter_rows()]
    assert any("Cột Lớp (tuỳ chọn)" in d for d in huong)
    # G3: quy tắc chữ giao diện cũng áp cho sheet Hướng dẫn: không gạch dài, không xưng "em/tôi/tớ"
    for d in huong:
        assert "—" not in d, d
        assert not re.search(r"\b(em|tôi|tớ)\b", d, re.I), d
