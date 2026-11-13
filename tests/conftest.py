import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from api import PipelineAPI


@pytest.fixture
def api(tmp_path):
    return PipelineAPI(str(tmp_path / "app.db"))

@pytest.fixture
def api_factory(tmp_path):
    """Dựng NHIỀU PipelineAPI độc lập trong cùng một test.

    Cần cho các test quét nhiều seed: mỗi seed phải chạy trên một CSDL
    sạch, nếu không dữ liệu của lần trước còn nguyên và làm lệch kết quả.
    """
    dem = {"n": 0}

    def tao():
        dem["n"] += 1
        thu_muc = tmp_path / ("db%d" % dem["n"])
        thu_muc.mkdir()
        return PipelineAPI(str(thu_muc / "app.db"))

    return tao

@pytest.fixture(autouse=True)
def khong_ghi_vao_thu_muc_tai_ve_that(tmp_path, monkeypatch):
    """Chốt chặn cho TOÀN BỘ bộ test.

    `export_csv("")` giờ đặt tệp vào thư mục Tải xuống của người dùng.
    Không có fixture này thì chạy pytest trên máy thật sẽ rải tệp kết
    quả vào Downloads của người đó — bộ test không bao giờ được để lại
    rác ngoài thư mục tạm của chính nó.
    """
    cho_tam = tmp_path / "TaiXuong_gia"
    cho_tam.mkdir(exist_ok=True)
    monkeypatch.setenv("RBDA_THU_MUC_TAI_VE", str(cho_tam))


@pytest.fixture(autouse=True)
def tieu_de_giu_ma_cho_test_cu(request):
    """SG-12: các test viết TRƯỚC khi biểu mẫu chuyển sang tiêu đề thuần dựng tệp xuất bằng các hàm tên câu của
    `bieu_mau` (và so với chữ có mã). Chúng chạy ở chế độ GIỮ MÃ — đúng là "tệp xuất cũ có mã vẫn nạp được". Tiêu đề
    thuần được kiểm riêng ở `tests/test_sg12_tieu_de_thuan.py` (module này chạy ở chế độ mặc định = thuần). Test nào kiểm ĐẦU RA MẶC ĐỊNH của
    bộ sinh (`tmf.main` không cờ) đánh dấu `@pytest.mark.tieu_de_thuan` để so với chữ thuần."""
    if request.module.__name__.startswith("test_sg12") or request.node.get_closest_marker("tieu_de_thuan"):
        yield                      # test kiểm đầu ra MẶC ĐỊNH của bộ sinh (tiêu đề thuần): không ép chế độ giữ mã
        return
    duong = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mau_forms_thi_clb")
    if duong not in sys.path:
        sys.path.insert(0, duong)
    import bieu_mau
    with bieu_mau.che_do_giu_ma(True):
        yield
