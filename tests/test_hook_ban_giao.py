"""Hook Stop bàn giao theo vai (.claude/hooks/handoff_khi_day_ngu_canh.py), T3-HT."""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "handoff_khi_day_ngu_canh.py"


def _chay(tmp_path, tokens, vai=None, env_nguong=None):
    (tmp_path / ".claude").mkdir(exist_ok=True)
    if vai is not None:
        (tmp_path / ".claude" / "phien_vai.json").write_text(json.dumps(vai), encoding="utf-8")
    if not (tmp_path / ".git").exists():
        subprocess.run(["git", "init", "-q", "-b", "claude/x"], cwd=tmp_path, check=True)
    tp = tmp_path / "t.jsonl"
    tp.write_text(json.dumps({"message": {"usage": {"input_tokens": tokens}}}) + "\n", encoding="utf-8")
    # Giữ PATH của hệ thống (Windows cần nó để tìm git); bỏ HANDOFF_TOKENS của máy chạy test.
    env = {k: v for k, v in os.environ.items() if k != "HANDOFF_TOKENS"}
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    if env_nguong:
        env["HANDOFF_TOKENS"] = str(env_nguong)
    r = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps({"transcript_path": str(tp)}),
        capture_output=True, text=True, env=env, cwd=tmp_path,
    )
    return r.returncode, r.stderr


def test_khong_co_vai_giu_hanh_vi_cu(tmp_path):
    assert _chay(tmp_path, 399_000)[0] == 0
    ma, loi = _chay(tmp_path, 401_000)
    assert ma == 2 and "docs/phien/claude__x.md" in loi and "NEW session" in loi


def test_impl_bao_coordinator(tmp_path):
    ma, loi = _chay(tmp_path, 401_000, {"vai": "impl", "coord_id": "session_C", "nguong": 400000})
    assert ma == 2
    assert "docs/phien/claude__x__impl.md" in loi
    assert "send_message to session session_C" in loi and "HANDOFF impl" in loi


def test_coord_nguong_rieng(tmp_path):
    vai = {"vai": "coord", "nguong": 700000}
    assert _chay(tmp_path, 650_000, vai)[0] == 0
    ma, loi = _chay(tmp_path, 701_000, vai)
    assert ma == 2 and "T3_GIAO_THUC.md" in loi and "create_session" in loi


def test_bien_moi_truong_thang_tep_vai(tmp_path):
    assert _chay(tmp_path, 150_000, {"vai": "tester", "nguong": 400000}, env_nguong=100_000)[0] == 2


def test_tep_vai_hong_thi_nhu_cu(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "phien_vai.json").write_text("{hong", encoding="utf-8")
    ma, loi = _chay(tmp_path, 401_000)
    assert ma == 2 and "NEW session" in loi


def test_stop_hook_active_khong_chan(tmp_path):
    r = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps({"stop_hook_active": True}),
        capture_output=True, text=True,
    )
    assert r.returncode == 0
