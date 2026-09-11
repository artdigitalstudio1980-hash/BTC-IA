"""Guardrails spec §9 — enforced in code."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / ".env.example"

def test_default_is_paper():
    assert ENV_EXAMPLE.exists()
    assert "LIVE_TRADING=false" in ENV_EXAMPLE.read_text()

def test_max_position_guard():
    txt = ENV_EXAMPLE.read_text()
    assert "MAX_POSITION_PCT=5" in txt
    assert "MAX_DAILY_LOSS_PCT=2" in txt

def test_kill_switch_path():
    assert ENV_EXAMPLE.exists()
    assert "KILL_SWITCH_FILE=/tmp/btc-ai-kill" in ENV_EXAMPLE.read_text()

def test_testnet_default():
    assert "testnet.binance.vision" in ENV_EXAMPLE.read_text()
