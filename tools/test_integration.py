# tools/test_integration.py
# Test tich hop: nap main.pyw that (mock tkinter) + mo phong bam nut.
# Cach chay:  python tools/test_integration.py   (exit 0 = 31/31 pass)

import copy
import os
import re
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0
FAILURES = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"[PASS] {name}")
    else:
        FAIL += 1
        FAILURES.append(name)
        print(f"[FAIL] {name} {detail}")


print("=" * 60)
print("Discord BLUE - Test tich hop (28 assertions)")
print("=" * 60)
# --- 1. Helpers: schedule / spintax / sleep co the ngat ---
from utils.helpers import (is_in_schedule, process_spintax,
                           interruptible_sleep, should_stop,
                           ThreadSafeLog, process_smart_template)

check("schedule tat -> luon True", is_in_schedule(False, "22:00", "06:00") is True)
check("schedule gio hanh chinh hien tai khong crash",
      isinstance(is_in_schedule(True, "00:00", "23:59"), bool))
check("schedule qua dem khong crash",
      isinstance(is_in_schedule(True, "22:00", "06:00"), bool))
check("schedule sai format -> mac dinh True",
      is_in_schedule(True, "xx", "yy") is True)
check("spintax chon 1 trong cac lua chon",
      process_spintax("{a|b|c}") in ("a", "b", "c"))
check("spintax khong de lai ngoac thua", "{" not in process_spintax("{a|b|c}")
      and "}" not in process_spintax("{a|b|c}"))
check("smart template tra ve chuoi", isinstance(process_smart_template("hello {a|b}"), str))
check("should_stop khi bot dung", should_stop([False], 1, [1]) is True)
check("should_stop khi generation lech", should_stop([True], 1, [2]) is True)
check("should_stop khi cung generation", should_stop([True], 2, [2]) is False)
t0_log = ThreadSafeLog()
t0_log.insert("end", "dong 1", "system")
t0_log.insert("end", "dong 2")


class FakeText:
    def __init__(self):
        self.rows = []

    def insert(self, index, text, tag=None):
        self.rows.append((text, tag))

    def see(self, index=None):
        pass


_fake = FakeText()
check("ThreadSafeLog.drain ghi du 2 dong", t0_log.drain(_fake) == 2 and len(_fake.rows) == 2)
check("ThreadSafeLog.drain het hang doi -> 0", t0_log.drain(_fake) == 0)

# --- 2. Config: validate + clean key da go bo ---
from config import DEFAULT_CONFIG, REMOVED_FEATURE_KEYS, validate_config

bad_cfg = {"cooldown_min": 90, "cooldown_max": 10,
           "features": {"typing_min_sec": 9, "typing_max_sec": 2,
                        "status_simulation": True, "dashboard_enabled": True}}
validated, warnings = validate_config(bad_cfg)
check("validate doi min/max cooldown", validated["cooldown_min"] == 10
      and validated["cooldown_max"] == 90)
check("validate doi min/max typing", validated["features"]["typing_min_sec"] == 2
      and validated["features"]["typing_max_sec"] == 9)
check("validate xoa key da go bo",
      all(k not in validated["features"] for k in ("status_simulation", "dashboard_enabled")))
check("validate giu key la (language)", validated.get("language") == "vietnamese")
check("validate co canh bao", isinstance(warnings, list) and len(warnings) > 0)
check("validate config None -> None", validate_config(None)[0] is None)
check("REMOVED_FEATURE_KEYS khong con trong DEFAULT_CONFIG",
      all(k not in DEFAULT_CONFIG.get("features", {}) for k in REMOVED_FEATURE_KEYS))

# --- 3. Nap main.pyw that voi tkinter gia lap + mo phong bam nut ---
import tkinter_mock  # noqa: F401 - nap mock truoc khi import main
import importlib.util

spec = importlib.util.spec_from_file_location("app_main", os.path.join(ROOT, "main.pyw"))
app_main = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(app_main)
    check("nap main.pyw that khong loi", True)
except Exception as e:
    check("nap main.pyw that khong loi", False, str(e)[:300])
    print("=" * 60)
    print(f"KET QUA: {PASS} pass, {FAIL} fail")
    sys.exit(1)

import tkinter.messagebox as _mb

warnings_shown = []
infos_shown = []
_orig_warn = _mb.showwarning
_orig_info = _mb.showinfo
_mb.showwarning = lambda *a, **k: warnings_shown.append(a)
_mb.showinfo = lambda *a, **k: infos_shown.append(a)

calls = []
RealThread = __import__("threading").Thread


class FakeThread:
    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}

    def start(self):
        calls.append(self._args)

    def join(self, *a, **k):
        return None


def _set(widget, text):
    widget._text = text


def _reset_run_state():
    app_main.bot_running[0] = False
    warnings_shown.clear()
    infos_shown.clear()
    calls.clear()
    import threading as _th
    _th.Thread = FakeThread
    app_main.run_single_account = lambda *a, **k: calls.append(("run", a))


_reset_run_state()
_set(app_main.txt_tokens, "")
_set(app_main.txt_channels, "123")
app_main.start_trigger()
check("thieu token -> canh bao + khong chay",
      app_main.bot_running[0] is False and any("Token" in str(w) for w in warnings_shown))

_reset_run_state()
_set(app_main.txt_tokens, "tok1")
_set(app_main.txt_channels, "")
app_main.start_trigger()
check("thieu channel -> canh bao + khong chay",
      app_main.bot_running[0] is False and any("Channel" in str(w) for w in warnings_shown))

_reset_run_state()
_set(app_main.txt_tokens, "tok1")
_set(app_main.txt_channels, "123")
_set(app_main.txt_messages, "hello")
_set(app_main.entry_min, "90")
_set(app_main.entry_max, "10")
_set(app_main.entry_delete_delay, "0")
_set(app_main.entry_typing_min, "2")
_set(app_main.entry_typing_max, "5")
_set(app_main.entry_break_after_min, "15")
_set(app_main.entry_break_after_max, "25")
_set(app_main.entry_break_duration_min, "10")
_set(app_main.entry_break_duration_max, "30")
_set(app_main.entry_schedule_start, "09:00")
_set(app_main.entry_schedule_end, "17:00")
app_main.start_trigger()
check("cooldown min>max -> canh bao + khong chay",
      app_main.bot_running[0] is False and any("Cooldown" in str(w) for w in warnings_shown))

_reset_run_state()
_set(app_main.txt_tokens, "tok1")
_set(app_main.txt_channels, "123")
_set(app_main.txt_messages, "hello")
_set(app_main.entry_min, "60")
_set(app_main.entry_max, "90")
_set(app_main.entry_typing_min, "9")
_set(app_main.entry_typing_max, "2")
app_main.start_trigger()
check("typing min>max -> canh bao + khong chay",
      app_main.bot_running[0] is False and len(warnings_shown) > 0)

# --- tiep: case chay thanh cong + nut DUNG ---
_reset_run_state()
_set(app_main.txt_tokens, "tok1\ntok2")
_set(app_main.txt_channels, "111\n222")
_set(app_main.txt_messages, "hello")
_set(app_main.entry_min, "60")
_set(app_main.entry_max, "90")
_set(app_main.entry_delete_delay, "0")
_set(app_main.entry_typing_min, "2")
_set(app_main.entry_typing_max, "5")
_set(app_main.entry_break_after_min, "15")
_set(app_main.entry_break_after_max, "25")
_set(app_main.entry_break_duration_min, "10")
_set(app_main.entry_break_duration_max, "30")
_set(app_main.entry_schedule_start, "00:00")
_set(app_main.entry_schedule_end, "23:59")
gen_before = app_main.bot_generation[0]
app_main.start_trigger()
n_run = len([c for c in calls if isinstance(c, tuple) and len(c) == 9])
check("config hop le -> bot chay + tao 2 thread",
      app_main.bot_running[0] is True and n_run == 2)
check("moi lan BAT tang generation",
      app_main.bot_generation[0] == gen_before + 1)
check("config sau BAT giu language/theme",
      "language" in app_main.config_data and "current_theme" in app_main.config_data)

gen_stop = app_main.bot_generation[0]
app_main.stop_trigger()
check("nut DUNG tat bot + tang generation",
      app_main.bot_running[0] is False and app_main.bot_generation[0] == gen_stop + 1)

print("=" * 60)
print(f"KET QUA: {PASS} pass, {FAIL} fail")
if FAILURES:
    print("FAIL: " + ", ".join(FAILURES))
    sys.exit(1)
print("KET QUA: DAT")
sys.exit(0)

