"""SG-2 (C1): không gian mặc định (Trường học, điểm quyết tâm bật) không được bẫy người mới.

Tái hiện của Fable: 4 CLB, 10 em, mỗi em 2 nguyện vọng cùng buổi, ô điểm quyết tâm để trống -> lần chạy bị chặn mà
bước xem trước không nói gì. Dữ liệu MÔ PHỎNG.
"""
import base64

import cau_hinh_ws as ch
import so_nhap
from i18n_errors import format_message


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _so(tmp_path, n_hs=10, diem=None, thi=False, luon_co_cot_w=False):
    clubs = [{"club_id": "C%d" % i, "name": "CLB %d" % i, "capacity": 10, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""} for i in range(4)]
    hs = []
    for i in range(n_hs):
        nv = [{"club_id": "C0", "thi": thi, "diem": "", **({"diem_w": diem[0]} if diem else {})},
              {"club_id": "C1", "thi": thi, "diem": "", **({"diem_w": diem[1]} if diem else {})}]
        hs.append({"student_id": "h%d" % i, "name": "Em %d" % i, "reserve_group": "", "nv": nv})
    p = str(tmp_path / "so.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs, luon_co_cot_w=luon_co_cot_w)
    return p


def _tim(ra, ma):
    return [w for w in ra["data"]["canh_bao"] if w["code"] == ma]


MA = "so_nhap_canh_bao_wharton_trong"


def test_xem_truoc_bao_o_trong_mot_dong_co_so_dem(api, tmp_path):
    ra = api.xem_truoc_so_nhap(_b64(_so(tmp_path)))
    assert ra["ok"], ra
    w = _tim(ra, MA)
    assert len(w) == 1 and w[0]["params"]["n"] == 10 and w[0]["params"]["vd"] == "h0"
    assert ra["data"]["loi"] == []                                    # chỉ cảnh báo, vẫn nhập được
    for ngon in ("vi", "en"):
        chu = format_message(MA, {**w[0]["params"], "person_l": "x", "slot_l": "y"}, ngon).lower()
        assert ("tắt" in chu if ngon == "vi" else "turn" in chu)      # nói cách sửa


def test_diem_tren_0_thi_khong_bao(api, tmp_path):
    ra = api.xem_truoc_so_nhap(_b64(_so(tmp_path, diem=(60, 40), luon_co_cot_w=True)))
    assert ra["ok"], ra
    assert _tim(ra, MA) == []


def test_diem_toan_0_van_bao(api, tmp_path):
    ra = api.xem_truoc_so_nhap(_b64(_so(tmp_path, diem=(0, 0), luon_co_cot_w=True)))
    assert len(_tim(ra, MA)) == 1


def test_mot_clb_moi_quy_thi_khong_bao(api, tmp_path):
    """Quỹ chỉ có một CLB được tự điền 100: C0 thi, C1 không thi -> hai quỹ một CLB, không cảnh báo."""
    clubs = [{"club_id": "C0", "name": "A", "capacity": 5, "reserve_capacity": 0, "reserve_group": "",
              "buoi": ""}, {"club_id": "C1", "name": "B", "capacity": 5, "reserve_capacity": 0,
                            "reserve_group": "", "buoi": ""}]
    hs = [{"student_id": "h1", "name": "E", "reserve_group": "",
           "nv": [{"club_id": "C0", "thi": True, "diem": 5}, {"club_id": "C1", "thi": False, "diem": ""}]}]
    p = str(tmp_path / "so.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs)
    assert _tim(api.xem_truoc_so_nhap(_b64(p)), MA) == []


def test_tat_diem_quyet_tam_thi_khong_bao_va_chay_duoc(api, tmp_path):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    p = _so(tmp_path)
    ra = api.xem_truoc_so_nhap(_b64(p))
    assert ra["ok"] and _tim(ra, MA) == []
    assert api.import_so_nhap(_b64(p))["ok"]
    assert api.run_pipeline(seed=1)["ok"]


def test_khong_tat_thi_lan_chay_bi_chan_nhu_cu(api, tmp_path):
    """Câu chặn gốc giữ nguyên (quyết định B3); lời chỉ đường nằm ở khung lỗi trên giao diện."""
    assert api.import_so_nhap(_b64(_so(tmp_path)))["ok"]
    kq = api.run_pipeline(seed=1)
    assert not kq["ok"] and kq["errors"][0]["code"] == "wharton_ho_so_chua_hop_le"


def test_mac_dinh_van_la_bat():
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["wharton"] is True


def test_huong_dan_khong_noi_o_trong_la_0_chung_chung():
    chu = "\n".join(so_nhap._huong_dan_co_dau(ch.MAC_DINH_TRUONG_HOC))
    assert "ô trống tính là 0" not in chu
    assert "từ hai" in chu and "bị chặn" in chu
