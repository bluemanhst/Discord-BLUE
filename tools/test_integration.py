# tools/test_integration.py
# Test tich hop: nap main.pyw that (mock tkinter) + mo phong bam nut.
# Cach chay:  python tools/test_integration.py   (exit 0 = tat ca pass)

import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, TOOLS_DIR)

# QUAN TRONG: phai nap tkinter gia lap TRUOC moi import khac, vi utils.theme cache
# lai module ttk ngay khi duoc import -> nap muon se crash configure_ttk_styles().
import tkinter_mock  # noqa: E402,F401

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
print("Discord BLUE - Test tich hop: nap main.pyw that + mo phong bam nut")
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
# Test KHONG duoc ghi de config.json that cua nguoi dung -> tro sang file tam
import tempfile
import config as config_module
import utils.sound as sound_module

_tmp_dir = tempfile.mkdtemp(prefix="discord_blue_test_")
config_module.CONFIG_FILE = os.path.join(_tmp_dir, "config.json")
config_module.config_data.clear()
config_module.config_data.update(copy.deepcopy(config_module.DEFAULT_CONFIG))

# Tat am thanh + tray trong luc test (khong beep, khong tao icon khay that)
sound_module.notify = lambda *a, **k: None
sound_module.set_all = lambda *a, **k: None

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


class FakeThread:
    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}

    def start(self):
        calls.append(self._args)

    def join(self, *a, **k):
        return None

    def is_alive(self):
        # Worker that bai khong chay that trong test; join loop trong
        # run_single_account van phai chay duoc.
        return False


def _set(widget, text):
    widget._text = text


def _reset_run_state():
    app_main.bot_running[0] = False
    warnings_shown.clear()
    infos_shown.clear()
    calls.clear()
    import threading as _th
    _th.Thread = FakeThread
    # main.pyw dùng "import threading" + "threading.Thread(...)"
    try:
        app_main.threading.Thread = FakeThread
    except Exception:
        pass
    app_main.run_single_account = lambda *a, **k: calls.append(("run", a))


_reset_run_state()


def _mk_profile(token="tok1", chans=("123",), msgs=("hello",),
                cd_min=60, cd_max=90, feats=None):
    """Profile mau de test start_trigger (kien truc profiles thay txt_* an)."""
    ch_list = [{"id": c, "cd_min": cd_min, "cd_max": cd_max, "messages": []}
               for c in chans]
    return {
        "name": "Acc test", "enabled": True, "token": token,
        "channel_ids": list(chans), "channels": ch_list,
        "cooldown_min": cd_min,
        "cooldown_max": cd_max, "messages": list(msgs),
        "features": dict(feats or {}),
    }


def _set_profiles(profs):
    # start_trigger doc profiles tu config_data (khong dung txt_tokens/txt_channels an nua)
    # + profiles_ctx["save_current"] trong mock UI doc widget rong -> ghi de token.
    # Giu data test: tam vo hieu save_current + refresh trong lúc BAT.
    app_main.config_data["profiles"] = copy.deepcopy(list(profs))
    try:
        _ctx = app_main.profiles_ctx
        _ctx["_test_save"] = _ctx.get("save_current")
        _ctx["save_current"] = lambda: None
        _feat = app_main.frame_features_page
        if hasattr(_feat, "save_to_active_profile"):
            _feat["_test_save_feat"] = _feat.save_to_active_profile
            _feat.save_to_active_profile = lambda: None
    except Exception:
        pass


def _restore_ctx():
    try:
        _ctx = app_main.profiles_ctx
        if "_test_save" in _ctx:
            _ctx["save_current"] = _ctx.pop("_test_save")
        _feat = app_main.frame_features_page
        if hasattr(_feat, "_test_save_feat"):
            _feat.save_to_active_profile = _feat._test_save_feat
            delattr(_feat, "_test_save_feat")
    except Exception:
        pass


_set_profiles([])
app_main.start_trigger()
check("thieu token -> canh bao + khong chay",
      app_main.bot_running[0] is False and any("Token" in str(w) for w in warnings_shown))

_reset_run_state()
_set_profiles([_mk_profile(chans=())])
app_main.start_trigger()
check("thieu channel -> canh bao + khong chay",
      app_main.bot_running[0] is False and any("Channel" in str(w) for w in warnings_shown))

_reset_run_state()
_set_profiles([_mk_profile(cd_min=90, cd_max=10)])
app_main.start_trigger()
n_run_bad_cd = len([c for c in calls if isinstance(c, tuple) and len(c) == 9])
check("cooldown min>max -> tu swap va van chay duoc",
      app_main.bot_running[0] is True and n_run_bad_cd == 1)

_reset_run_state()
_set_profiles([_mk_profile(feats={"typing_min_sec": 9, "typing_max_sec": 2})])
app_main.start_trigger()
check("typing min>max -> normalize tu swap, van chay duoc",
      app_main.bot_running[0] is True)

# --- tiep: case chay thanh cong + nut DUNG ---
_reset_run_state()
_set_profiles([_mk_profile(token="tok1", chans=("111",)),
               _mk_profile(token="tok2", chans=("222",))])
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

# --- 3b. chat markup parser (preview emoji + markdown) ---
from utils.chat_markup import parse_markup

segs = parse_markup(":FragmentSDSayenDripIV: :For: **Justice Bunny Set**")
emo_names = [s["name"] for s in segs if s["type"] == "emoji_name"]
bold_txt = [s.get("text", "") for s in segs if "bold" in (s.get("styles") or set())]
check("markup: emoji :name: duoc tach (2 cai)",
      emo_names == ["FragmentSDSayenDripIV", "For"])
check("markup: **bold** duoc nhan dang",
      any(b == "Justice Bunny Set" for b in bold_txt))

segs2 = parse_markup("<a:wave:123456789012345678> <:heart:987654321098765432>")
emo_ids = [s for s in segs2 if s["type"] == "emoji_id"]
check("markup: emoji <:name:id> / <a:name:id> co ID + animated",
      len(emo_ids) == 2 and emo_ids[0]["animated"] is True
      and emo_ids[1]["animated"] is False
      and emo_ids[0]["id"] == "123456789012345678"
      and emo_ids[1]["name"] == "heart")

segs3 = parse_markup("dong 1\ndong 2 `code` *it* ~~strike~~ __under__")
check("markup: xuong hang + code/italic/strike/underline",
      any(s["type"] == "newline" for s in segs3)
      and any("code" in (s.get("styles") or set()) and s.get("text") == "code"
              for s in segs3)
      and any("italic" in (s.get("styles") or set()) and s.get("text") == "it"
              for s in segs3)
      and any("strike" in (s.get("styles") or set()) and s.get("text") == "strike"
              for s in segs3)
      and any("underline" in (s.get("styles") or set()) and s.get("text") == "under"
              for s in segs3))

# --- 3b2. resolve emoji shortcode -> <name:id> truoc khi gui ---
from utils.chat_markup import resolve_emoji_shortcodes

_MAP = {"emoji_11": {"id": "111111111111111111", "animated": False},
        "wave": {"id": "222222222222222222", "animated": True}}
check("resolve: :name: co trong map -> <:name:id>",
      resolve_emoji_shortcodes(":emoji_11: :emoji_41:", _MAP)
      == "<:emoji_11:111111111111111111> :emoji_41:")
check("resolve: animated -> <a:name:id>",
      resolve_emoji_shortcodes("hi :wave: !", _MAP)
      == "hi <a:wave:222222222222222222> !")
check("resolve: emoji da co ID giu nguyen (khong lam vo)",
      resolve_emoji_shortcodes("<:emoji_11:999999999999999999>", _MAP)
      == "<:emoji_11:999999999999999999>")
check("resolve: map rong / text khac giu nguyen",
      resolve_emoji_shortcodes(":emoji_11:", {}) == ":emoji_11:"
      and resolve_emoji_shortcodes("**bold** ok", _MAP) == "**bold** ok")

# --- 3b3. fallback emoji goc Unicode cua Discord (khong can guild) ---
# Luu y: ten test khong chua ky tu emoji (console cp1252 khong in duoc).
from utils.chat_markup import unicode_emoji as _uni
check("unicode: :smile: -> emoji goc (khong can guild)",
      resolve_emoji_shortcodes("hi :smile: !", {}) == "hi 😄 !")
check("unicode: :face_holding_back_tears: -> emoji goc",
      resolve_emoji_shortcodes(":face_holding_back_tears:", {}) == "🥹")
check("unicode: :+1: -> thumbup / :-1: -> thumbdown (regex mo rong dau +-)",
      resolve_emoji_shortcodes(":+1: :-1:", {}) == "👍 👎")
check("unicode: :joy: / :rofl: / :100:",
      resolve_emoji_shortcodes(":joy: :rofl: :100:", {}) == "😂 🤣 💯")
check("unicode: uu tien custom emoji hon unicode (cung ten)",
      resolve_emoji_shortcodes(":smile:", {"smile": {"id": "333333333333333333", "animated": False}})
      == "<:smile:333333333333333333>")
check("unicode: khong phai emoji -> giu nguyen (khong lam vo text thuong)",
      resolve_emoji_shortcodes(":emoji_11: :khong_phai_emoji:", {}) == ":emoji_11: :khong_phai_emoji:")

# --- 3b3b. dong bo GUI vs PREVIEW: shortcode so -> keycap (khong con so phang) ---
check("dong bo: :two: -> keycap 2️⃣ (khong con so phang '2')",
      resolve_emoji_shortcodes(":two:", {}) == _uni("two")
      and resolve_emoji_shortcodes(":two:", {}) == "2️⃣")
check("dong bo: :zero:..:nine: deu la keycap (== unicode_emoji)",
      all(resolve_emoji_shortcodes(f":{n}:", {}) == _uni(n)
          for n in ("zero", "one", "two", "three", "four",
                    "five", "six", "seven", "eight", "nine")))
check("dong bo: :keycap_ten: -> 🔟",
      resolve_emoji_shortcodes(":keycap_ten:", {}) == "🔟")
# Ten 1 ky tu (:a: :b: :x: :o: :m:) - truoc day bi bo qua vi regex {2,32}
check("dong bo: ten 1 ky tu :a: :b: :x: :o: :m: convert dung",
      resolve_emoji_shortcodes(":a: :b: :x: :o: :m:", {})
      == "🅰️ 🅱️ ❌ ⭕ Ⓜ️")
# Ten dai >32 ky tu - truoc day bi bo qua
check("dong bo: ten dai (53 ky tu) convert dung",
      resolve_emoji_shortcodes(":raised_hand_with_part_between_middle_and_ring_fingers:", {})
      == "🖖")
check("dong bo: ten dai khac (:face_with_open_eyes_and_hand_over_mouth:)",
      resolve_emoji_shortcodes(":face_with_open_eyes_and_hand_over_mouth:", {}) == "🫢")
# Ky tu Latinh mo rong trong ten (piñata)
check("dong bo: ten co ky tu Latinh :piñata: -> 🪅",
      resolve_emoji_shortcodes(":piñata:", {}) == "🪅")
# Quet toan bo dataset: moi shortcode phai gui == unicode_emoji (0 lech)
import json as _json
_ds = _json.load(open("assets/emoji_unicode.json", encoding="utf-8"))
_leech = [n for n in _ds if _uni(n) is not None
          and resolve_emoji_shortcodes(":" + n + ":", {}) != _uni(n)]
check("dong bo: QUET 2073 emoji -> 0 lech giua gui va preview",
      len(_leech) == 0, detail=str(_leech[:10]))

check("unicode: unicode_emoji() tra dung / ngoai danh sach -> None",
      _uni("smile") == "😄" and _uni("khong ton tai") is None
      and _uni("") is None)

# --- 3b4. twemoji_url: ky tu Unicode -> URL anh mau cho preview ---
from utils.chat_markup import twemoji_url as _tw
check("twemoji: :rofl: -> 1f923.png",
      _tw("🤣").endswith("/1f923.png"))
check("twemoji: :smile: -> 1f604.png",
      _tw("😄").endswith("/1f604.png"))
check("twemoji: :+1: (U+1F44D) -> 1f44d.png",
      _tw("👍").endswith("/1f44d.png"))
check("twemoji: bo variation selector FE0F (U+2764 FE0F -> 2764)",
      _tw("❤️").endswith("/2764.png") and "\ufe0f" not in _tw("❤️"))
check("twemoji: None / rong -> None",
      _tw("") is None and _tw(None) is None)

# --- 3c. regression: run_single_account that that NameError (5 bien thieu sau refactor) ---
# Truoc day 5 bien (default_messages/schedule_*/smart_templates) bi mat khi
# refactor song song -> thread chay that bi NameError ngay, bot khong gui gi.
# Test goi ham THAT voi bot_running=[False] + FakeThread (khong chay worker that).
import discord.bot as _bot_mod


class _FakeLog:
    def __init__(self):
        self.rows = []

    def insert(self, *a):
        self.rows.append(a)

    def see(self, *a):
        return None


_ne_err = ""
_ge_mod = None
_ge_orig = None
try:
    import discord.guild_emojis as _ge_mod
    _ge_orig = (_ge_mod.load_disk_cache,
                _ge_mod.ensure_emoji_library,
                _ge_mod.fetch_emojis_for_channel)
    _ge_mod.load_disk_cache = lambda *a, **k: None
    _ge_mod.ensure_emoji_library = lambda *a, **k: None
    _ge_mod.fetch_emojis_for_channel = lambda *a, **k: {}
    _bot_mod.run_single_account(
        "tok_test", 1, ["123"], 60, 90, ["hello"], _FakeLog(), {}, [False],
        run_id=99, generation_ref=[99], profile_name="Acc 1",
        channels=[{"id": "123", "cd_min": 1, "cd_max": 1, "messages": ["x"]}])
except NameError as e:
    _ne_err = str(e)
finally:
    if _ge_mod is not None and _ge_orig is not None:
        (_ge_mod.load_disk_cache, _ge_mod.ensure_emoji_library,
         _ge_mod.fetch_emojis_for_channel) = _ge_orig
check("run_single_account khong NameError (default_messages/schedule...)",
      not _ne_err, detail=_ne_err)
calls.clear()

# --- 3d. thu vien emoji Nitro: merge uu tien guild kenh + cache dia TTL ---
import discord.guild_emojis as _ge
check("merge: emoji guild kenh thang khi trung ten",
      _ge.merge_emoji_maps({"x": {"id": "1", "animated": False, "guild_id": "other"}},
                            prefer_guild_id="other")["x"]["id"] == "1"
      and _ge.merge_emoji_maps(None, prefer_guild_id="99") == {}
      and _ge.merge_emoji_maps({"a": {"id": "2"}}, prefer_guild_id=None) == {"a": {"id": "2"}})
_tmp_emoji = os.path.join(_tmp_dir, "emoji_cache.json")
_ge.save_disk_cache({"y": {"id": "9", "animated": True}}, path=_tmp_emoji)
check("disk cache: ghi -> doc duoc (con fresh)",
      (_ge.load_disk_cache(path=_tmp_emoji) or {}).get("y", {}).get("id") == "9")
check("disk cache: het han -> None",
      _ge.load_disk_cache(max_age=-1, path=_tmp_emoji) is None)

# --- 3e. chon server dung emoji: uu tien + normalize profile ---
_orig_get = _ge.get_guild_id
_orig_fetch = _ge.fetch_emojis_for_guilds
try:
    _FAKE = {"g1": {"test": {"id": "1", "animated": False, "guild_id": "g1"}},
             "g2": {"test": {"id": "2", "animated": True, "guild_id": "g2"},
                    "rieng": {"id": "3", "animated": False, "guild_id": "g2"}}}
    _ge.get_guild_id = lambda cid, tok: "g1"
    # fetch fake giu thu tu: guild dau tien thang khi trung ten
    def _fake_fetch(tok, gids, **k):
        out = {}
        for g in (gids or []):
            for n, i in _FAKE.get(str(g), {}).items():
                if n not in out:
                    out[n] = dict(i)
        return out
    _ge.fetch_emojis_for_guilds = _fake_fetch
    _m1 = _ge.build_selected_emoji_map("tok", "ch1", ["g2"])
    check("chon server: guild channel (g1) thang khi trung :test:",
          _m1.get("test", {}).get("id") == "1"
          and _m1.get("rieng", {}).get("id") == "3")
    _ge.get_guild_id = lambda cid, tok: None
    _m2 = _ge.build_selected_emoji_map("tok", None, ["g2", "g1"])
    check("chon server: tick truoc (g2) thang khi khong co channel",
          _m2.get("test", {}).get("id") == "2")
    check("chon server: url avatar + rong",
          _ge.guild_icon_url("g", None) is None
          and _ge.guild_icon_url("g", "abc", size=64).endswith("/abc.png?size=64")
          and _ge.guild_icon_url("g", "a_xyz").endswith("/a_xyz.gif?size=64")
          and _ge.fetch_emojis_for_guilds("t", []) == {}
          and _ge.build_selected_emoji_map("", None, []) == {})
finally:
    _ge.get_guild_id = _orig_get
    _ge.fetch_emojis_for_guilds = _orig_fetch
import profiles as _prof_mod
_p = _prof_mod.normalize_profile({"name": "Acc 9",
                                  "emoji_guilds": ["g1", "g1", " ", "g2"]},
                                 index=9)
check("profile: normalize giu emoji_guilds (dedup + bo rong)",
      _p.get("emoji_guilds") == ["g1", "g2"])
_p2 = _prof_mod.normalize_profile({"name": "Acc cu"}, index=1)
check("profile: config cu thieu emoji_guilds -> []",
      _p2.get("emoji_guilds") == [])
check("profile: default moi co emoji_guilds",
      _prof_mod.default_profile().get("emoji_guilds") == [])

# --- 4. i18n: moi key dung trong code phai dich duoc o ca 2 ngon ngu ---
import json
import re
import language


def _flatten_lang(d, prefix=""):
    """Lam phang dict long nhau thanh {section.key: value}"""
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten_lang(v, key))
        else:
            out[key] = v
    return out


with open(os.path.join(ROOT, "languages", "vietnamese.json"), "r", encoding="utf-8") as _f:
    _vi_keys = _flatten_lang(json.load(_f))

_src_all = ""
for _dirpath, _, _names in os.walk(ROOT):
    if any(s in _dirpath for s in ("build", "dist", ".git", "__pycache__", "tools")):
        continue
    for _name in _names:
        if _name.endswith((".py", ".pyw")):
            with open(os.path.join(_dirpath, _name), "r", encoding="utf-8", errors="ignore") as _f:
                _src_all += _f.read()

_used_keys = [k for k in _vi_keys
              if re.search(r'["\']' + re.escape(k) + r'["\']', _src_all)]

_untranslated = []
for _code in ("vietnamese", "english"):
    language.set_language(_code)
    for _key in _used_keys:
        if language.t(_key) == _key:
            _untranslated.append(f"{_code}:{_key}")

check(f"moi key dung trong code deu dich duoc o ca 2 ngon ngu ({len(_used_keys)} key)",
      not _untranslated, detail=str(_untranslated[:5]))
language.set_language("vietnamese")

print("=" * 60)
print(f"KET QUA: {PASS} pass, {FAIL} fail")
if FAILURES:
    print("FAIL: " + ", ".join(FAILURES))
    sys.exit(1)
print("KET QUA: DAT")
sys.exit(0)

