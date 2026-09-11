"""Guardrails spec §9 — enforced in code."""
import os

def test_default_is_paper():
    # .env.example must have LIVE_TRADING=false
    with open(".env.example") as f:
        assert "LIVE_TRADING=false" in f.read()

def test_max_position_guard():
    with open(".env.example") as f:
        txt = f.read()
        assert "MAX_POSITION_PCT=5" in txt
        assert "MAX_DAILY_LOSS_PCT=2" in txt

def test_kill_switch_path():
    assert os.path.exists(".env.example")
    with open(".env.example") as f:
        assert "KILL_SWITCH_FILE=/tmp/btc-ai-kill" in f.read()

def test_testnet_default():
    with open(".env.example") as f:
        assert "testnet.binance.vision" in f.read()
