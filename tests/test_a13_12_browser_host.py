"""A13.12 (BAO_CAO_SOAT_NHAP 1.1, 1.2): máy chủ dự phòng bằng trình duyệt. Dữ liệu MÔ PHỎNG.

  * 1.1 (CHẶN): bấm F5 làm `pagehide` gửi `/__closed__`; máy chủ không được tắt ngay. Chỉ tắt khi
    sau lúc báo đóng không còn lưu hiệu nào (không ping, không kết nối sống mới) trong ngưỡng chờ;
  * 1.2: mọi nhánh lỗi HTTP trả `errors = [{code, params}]` (bất biến 6), mã nằm ở `i18n_errors.py`.
"""

import json
import os
import time
import urllib.error
import urllib.request

import pytest

import browser_host
from i18n_errors import MESSAGES

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _post(url, data=b"", headers=None):
    req = urllib.request.Request(url, data=data, method="POST", headers=headers or {})
    return urllib.request.urlopen(req, timeout=5)


def _con_song(base, token):
    try:
        urllib.request.urlopen(f"{base}/index.html?t={token}", timeout=1).read()
        return True
    except urllib.error.HTTPError:
        raise
    except Exception:
        return False


@pytest.fixture
def host(api, monkeypatch):
    monkeypatch.setattr(browser_host, "_CHO_SAU_BAO_DONG_SECONDS", 2.0, raising=False)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")
    return base, token


def test_tai_lai_trang_khong_tat_may_chu(host):
    """F5: trang cũ báo đóng, trang mới ping và mở kết nối sống ngay sau đó."""
    base, token = host
    assert json.loads(_post(f"{base}/__closed__?t={token}").read())["ok"] is True
    _post(f"{base}/__ping__")                                   # trang mới nạp xong
    song = urllib.request.urlopen(f"{base}/__alive__?t={token}", timeout=5)
    try:
        time.sleep(5)                                           # quá ngưỡng chờ (2 s) + vài nhịp
        assert _con_song(base, token), "F5 làm máy chủ tắt"
    finally:
        song.close()


def test_dong_that_van_tat_may_chu(host):
    base, token = host
    _post(f"{base}/__closed__?t={token}")
    han = time.time() + 12
    while time.time() < han:
        if not _con_song(base, token):
            return
        time.sleep(0.3)
    pytest.fail("đóng thật mà máy chủ vẫn chạy")


def test_bao_dong_roi_trang_moi_chi_ping_van_giu_may_chu(host):
    base, token = host
    _post(f"{base}/__closed__?t={token}")
    for _ in range(5):
        _post(f"{base}/__ping__")
        time.sleep(1)
    assert _con_song(base, token)


# ------------------------------------------------------------------ 1.2: lỗi HTTP có mã

def _loi(base, duong, token="", data=b"{}", dau=None):
    h = {"Content-Type": "application/json", **({"X-Kiosk-Token": token} if token else {}),
         **(dau or {})}
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base + duong, data=data, headers=h)
    return e.value.code, json.loads(e.value.read())


def _la_loi_co_ma(body, ma):
    assert body["ok"] is False
    assert body["errors"] and all(isinstance(x, dict) and set(x) == {"code", "params"}
                                  for x in body["errors"]), body
    assert body["errors"][0]["code"] == ma
    assert ma in MESSAGES and set(MESSAGES[ma]) >= {"vi", "en"}


def test_token_sai_tra_ma_loi_khong_phai_chuoi_tho(host):
    base, _ = host
    ma, body = _loi(base, "/__api__/get_dashboard_status", token="sai")
    assert ma == 403
    _la_loi_co_ma(body, "http_bi_tu_choi")


def test_dong_dong_closed_token_sai_tra_ma_loi(host):
    base, _ = host
    ma, body = _loi(base, "/__closed__?t=sai")
    assert ma == 403
    _la_loi_co_ma(body, "http_bi_tu_choi")


def test_diem_cuoi_la_tra_ma_loi(host):
    base, _ = host
    ma, body = _loi(base, "/khong-co")
    assert ma == 404
    _la_loi_co_ma(body, "http_khong_co_dich")


def test_ham_la_va_ham_rieng_tra_ma_loi_kem_ten(host):
    base, token = host
    for ten in ("khong_co_ham_nay", "_backup_db"):
        ma, body = _loi(base, "/__api__/" + ten, token=token)
        assert ma == 404
        _la_loi_co_ma(body, "http_khong_co_ham")
        assert body["errors"][0]["params"] == {"ten": ten}


def test_than_qua_lon_tra_ma_loi(host):
    base, token = host
    ma, body = _loi(base, "/__api__/get_dashboard_status", token=token,
                    dau={"Content-Length": str(browser_host._TRAN_THAN_YEU_CAU + 1)}, data=b"")
    assert ma == 413
    _la_loi_co_ma(body, "http_than_qua_lon")
    assert body["errors"][0]["params"] == {"toi_da_mb": browser_host._TRAN_THAN_YEU_CAU // (1024 * 1024)}
