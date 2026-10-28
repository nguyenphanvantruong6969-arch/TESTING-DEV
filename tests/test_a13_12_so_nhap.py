"""A13.12 (BAO_CAO_SOAT_NHAP 1.4, 1.5): đọc / ghi Sổ nhập. Dữ liệu MÔ PHỎNG dựng trong test.

  * 1.4: cột phụ (ví dụ "Ghi chú") ở BÊN PHẢI nhóm cuối không bị tính vào nhóm cuối, nên không
    làm cả sổ bị từ chối; cột lạ NẰM TRONG nhóm vẫn là lỗi `so_nhap_cot_lech_nhom`;
  * 1.5: ô điểm quyết tâm là chữ số Unicode không phải 0-9 ("²", "٣") không làm `ghi_so_nhap`
    sụp: chuỗi gốc được giữ để người nhập thấy ô sai.
"""

import io

import pytest

openpyxl = pytest.importorskip("openpyxl")

import so_nhap  # noqa: E402
from test_so_nhap_hai_hang import (  # noqa: E402
    CFG_W, HS, SV, SV_W, _bytes, _doc, _hs, _ma_loi, _nv, _sua,
)


def test_cot_ghi_chu_ben_phai_nhom_cuoi_khong_lam_hong_ca_so():
    def them_ghi_chu(ws):
        c = ws.max_column + 1
        ws.cell(row=2, column=c, value="Ghi chú")
        ws.cell(row=3, column=c, value="em này ốm")
    kq = _doc(_sua(_bytes(SV), them_ghi_chu))
    assert kq["loi"] == [], _ma_loi(kq)
    assert [s["student_id"] for s in kq["students"]] == ["HS1", "HS2"]
    assert [x["club_id"] for x in kq["students"][0]["nv"]] == ["A", "B", "C"]


def test_nhieu_cot_phu_ben_phai_van_doc_duoc_voi_workspace_bat_diem_quyet_tam():
    def them(ws):
        c = ws.max_column
        for i, ten in enumerate(("Ghi chú", "Người nhập"), start=1):
            ws.cell(row=2, column=c + i, value=ten)
            ws.cell(row=3, column=c + i, value="x")
    kq = _doc(_sua(_bytes(SV_W, cfg=CFG_W), them), cfg=CFG_W)
    assert kq["loi"] == [], _ma_loi(kq)
    assert kq["students"][0]["nv"][0]["diem_w"] in (100, "100")


def test_cot_la_nam_trong_nhom_cuoi_van_la_loi():
    """Giữ lưới an toàn: tiêu đề lạ NẰM TRONG nhóm (sai chữ cột điểm) vẫn bị chặn."""
    def doi(ws):
        ws.cell(row=2, column=ws.max_column, value="Diem thii")
    kq = _doc(_sua(_bytes(SV), doi))
    assert any(c == "so_nhap_cot_lech_nhom" for c, _ in _ma_loi(kq)), _ma_loi(kq)
    assert kq["students"] == []


@pytest.mark.parametrize("chu", ["²", "٣", "①", "५"])
def test_ghi_so_nhap_khong_sup_voi_chu_so_unicode_o_diem_quyet_tam(chu):
    sv = [_hs("HS1", [_nv("A", True, 7.5, diem_w=chu), _nv("B", diem_w=60)])]
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, [{"club_id": "A", "name": "CLB A", "capacity": 5,
                             "reserve_capacity": 0, "reserve_group": "", "buoi": ""},
                            {"club_id": "B", "name": "CLB B", "capacity": 5,
                             "reserve_capacity": 0, "reserve_group": "", "buoi": ""}],
                        sv, cfg=CFG_W)
    ws = openpyxl.load_workbook(io.BytesIO(b.getvalue()))[HS]
    o = [ws.cell(row=3, column=c).value for c in range(1, ws.max_column + 1)]
    assert chu in o, o                   # chuỗi gốc được giữ, không biến thành số


def test_chu_so_ascii_van_thanh_so_nguyen():
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, [{"club_id": "A", "name": "CLB A", "capacity": 5,
                             "reserve_capacity": 0, "reserve_group": "", "buoi": ""}],
                        [_hs("HS1", [_nv("A", True, 7.5, diem_w=" 100 ")])], cfg=CFG_W)
    ws = openpyxl.load_workbook(io.BytesIO(b.getvalue()))[HS]
    assert 100 in [ws.cell(row=3, column=c).value for c in range(1, ws.max_column + 1)]
