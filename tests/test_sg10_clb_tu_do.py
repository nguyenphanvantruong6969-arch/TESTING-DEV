"""SG-10 (M2): CLB Tự do (FA) không có giới hạn chỗ -> `get_club_fill_stats` đánh dấu `tu_do`, để màn kết quả
hiện số thành viên + "không giới hạn chỗ" thay vì "150%", và ô "Chỗ còn trống" bỏ CLB Tự do. Không FA: không đổi.

Dữ liệu là dữ liệu MÔ PHỎNG dựng trong test.
"""

from _fa import bat_fa, dung_fa_clb, dung_hs_fa


def _dung_fa(api, so_hs=12):
    bat_fa(api)
    dung_fa_clb(api, G=(3, "GIOI_HAN"), T=(5, "TU_DO"))   # T lưu chỉ tiêu 5 nhưng sẽ có nhiều em hơn
    ids = [f"HS{i:03d}" for i in range(1, so_hs + 1)]
    dung_hs_fa(api, *ids, nv={i: ["T"] for i in ids})
    assert api.run_pipeline(seed=7)["ok"]


def _theo_ma(api):
    return {c["club_id"]: c for c in api.get_club_fill_stats()["data"]}


def test_clb_tu_do_co_co_tu_do_va_nhieu_hon_chi_tieu_luu(api):
    _dung_fa(api)
    t, g = _theo_ma(api)["T"], _theo_ma(api)["G"]
    assert t["tu_do"] is True
    assert t["matched"] == 12 and t["capacity"] == 5     # 240% nếu tính theo chỉ tiêu lưu: con số vô nghĩa
    assert g["tu_do"] is False


def test_tong_cho_trong_loai_clb_tu_do(api):
    _dung_fa(api)
    ds = api.get_club_fill_stats()["data"]
    gioi_han = [c for c in ds if not c["tu_do"]]
    assert [c["club_id"] for c in gioi_han] == ["G"]
    assert sum(max(0, c["capacity"] - c["matched"]) for c in gioi_han) <= 3


def test_khong_fa_khong_co_tu_do(api):
    api.create_or_update_club("clb_a", "CLB A", capacity=2)
    ds = api.get_club_fill_stats()["data"]
    assert ds and all(c["tu_do"] is False for c in ds)
