# tools/audit.py
# Kiem tra tinh nhat quan du an: compile, key ngon ngu (thieu/thua), ten theme,
# config mau, spec/build, pattern nguy hiem.
# Cach chay:  python tools/audit.py   (exit 0 = dat, exit 1 = co loi)

import compileall
import json
import os
import re
import sys

# Console Windows (cp1252) khong in duoc ten theme co dau tieng Viet -> ep UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def fail(message):
    FAILURES.append(message)
    print(f"[FAIL] {message}")


def ok(message):
    print(f"[ OK ] {message}")


def check_compile():
    bad = []
    for dirpath, _, filenames in os.walk(ROOT):
        if any(s in dirpath for s in ("build", "dist", ".git", "__pycache__")):
            continue
        for name in filenames:
            if name.endswith((".py", ".pyw")):
                full = os.path.join(dirpath, name)
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        compile(f.read(), full, "exec")
                except SyntaxError as e:
                    bad.append(f"{os.path.relpath(full, ROOT)}: {e}")
    if bad:
        fail("Loi cu phap:\n  " + "\n  ".join(bad))
    else:
        ok("Compile OK (khong loi cu phap)")


def _flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        elif isinstance(v, str):
            out[key] = v
    return out


def check_languages():
    lang_dir = os.path.join(ROOT, "languages")
    codes = ["vietnamese", "english"]
    data = {}
    for code in codes:
        path = os.path.join(lang_dir, f"{code}.json")
        if not os.path.exists(path):
            fail(f"Thieu file ngon ngu: languages/{code}.json")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data[code] = _flatten(json.load(f))
        except Exception as e:
            fail(f"File languages/{code}.json loi JSON: {e}")
            return
    used = set()
    for dirpath, _, filenames in os.walk(ROOT):
        if any(s in dirpath for s in ("build", "dist", ".git", "__pycache__", "tools")):
            continue
        for name in filenames:
            if not name.endswith((".py", ".pyw")):
                continue
            full = os.path.join(dirpath, name)
            try:
                with open(full, "r", encoding="utf-8") as f:
                    src = f.read()
            except Exception:
                continue
            pat = r"language\s*\.\s*t\(\s*[\"']([A-Za-z0-9_\.]+)[\"']"
            for m in re.finditer(pat, src):
                key = m.group(1)
                if "." not in key:
                    continue
                # t("prefix_" + x) la key dong -> chi la tien to, khong phai key that
                if src[m.end():m.end() + 8].lstrip().startswith("+"):
                    continue
                used.add(key)
    missing_vi = sorted(k for k in used if k not in data["vietnamese"])
    if missing_vi:
        fail(f"Key dung trong code nhung thieu trong VI ({len(missing_vi)}): {missing_vi[:10]}")
    else:
        ok(f"Key ngon ngu trong code deu co trong VI ({len(used)} key)")
    for code in ("english",):
        missing = sorted(k for k in data["vietnamese"] if k not in data[code])
        if missing:
            fail(f"languages/{code}.json thieu {len(missing)} key so voi VI: {missing[:10]}")
        else:
            ok(f"languages/{code}.json du key nhu VI ({len(data[code])} key)")
    ph = re.compile(r"\{(\d+)\}")
    mismatch = []
    for key, vi_text in data["vietnamese"].items():
        vi_ph = sorted(ph.findall(vi_text))
        for code in ("english",):
            if sorted(ph.findall(data[code].get(key, ""))) != vi_ph:
                mismatch.append(key)
                break
    if mismatch:
        fail(f"Placeholder lech giua cac ngon ngu ({len(mismatch)}): {mismatch[:10]}")
    else:
        ok("Placeholder {n} khop nhau giua cac ngon ngu")
def check_config_sample():
    sys.path.insert(0, ROOT)
    try:
        from config import DEFAULT_CONFIG, REMOVED_FEATURE_KEYS
    except Exception as e:
        fail(f"Khong import duoc config.DEFAULT_CONFIG: {e}")
        return
    sample_path = os.path.join(ROOT, "config.example.json")
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            sample = json.load(f)
    except Exception as e:
        fail(f"config.example.json loi: {e}")
        return
    problems = []
    for key in DEFAULT_CONFIG:
        if key not in sample:
            problems.append(f"thieu key cap 1: {key}")
    for key in sample:
        if key not in DEFAULT_CONFIG:
            problems.append(f"thua key cap 1: {key}")
    for key in DEFAULT_CONFIG.get("features", {}):
        if key not in sample.get("features", {}):
            problems.append(f"thieu features.{key}")
    for key in sample.get("features", {}):
        if key not in DEFAULT_CONFIG.get("features", {}):
            problems.append(f"thua features.{key}")
    for key in REMOVED_FEATURE_KEYS:
        if key in sample.get("features", {}):
            problems.append(f"config mau van chua key da go bo: {key}")
    if problems:
        fail("config.example.json lech voi DEFAULT_CONFIG:\n  " + "\n  ".join(problems))
    else:
        ok("config.example.json khop DEFAULT_CONFIG")


def check_build_files():
    try:
        with open(os.path.join(ROOT, "Discord BLUE.spec"), "r", encoding="utf-8") as f:
            spec = f.read()
        with open(os.path.join(ROOT, "build.bat"), "r", encoding="utf-8") as f:
            bat = f.read()
    except Exception as e:
        fail(f"Khong doc duoc spec/bat: {e}")
        return
    problems = []
    # cac module noi bo (discord.*, utils.*) PyInstaller tu phat hien qua import;
    # chi can liet ke thu vien ben ngoai + module de quen mat truoc day
    for token in ["languages", "assets/logo.ico", "assets/discord_logo.png",
                  "assets/facebook_logo.png", "pystray", "discord.bot",
                  "discord.dashboard", "discord.token_validator"]:
        if token not in spec:
            problems.append(f"spec thieu: {token}")
    if "Discord BLUE.spec" not in bat:
        problems.append("build.bat khong goi Discord BLUE.spec")
    if "upx=False" not in spec and "upx = False" not in spec:
        problems.append("spec chua tat UPX (upx=False)")
    if problems:
        fail("Kiem tra build:\n  " + "\n  ".join(problems))
    else:
        ok("spec + build.bat dong bo (1 nguon cau hinh, da bundle languages/assets/tray)")


def _read_all_sources():
    """Doc toan bo source (bo qua build/dist/tools) -> {relpath: text}"""
    sources = {}
    for dirpath, _, filenames in os.walk(ROOT):
        if any(s in dirpath for s in ("build", "dist", ".git", "__pycache__", "tools")):
            continue
        for name in filenames:
            if not name.endswith((".py", ".pyw")):
                continue
            full = os.path.join(dirpath, name)
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    sources[os.path.relpath(full, ROOT)] = f.read()
            except Exception:
                continue
    return sources


def check_unused_language_keys():
    """Key co trong file ngon ngu nhung khong noi nao dung = refactor i18n bo do dang"""
    lang_path = os.path.join(ROOT, "languages", "vietnamese.json")
    try:
        with open(lang_path, "r", encoding="utf-8") as f:
            keys = _flatten(json.load(f))
    except Exception as e:
        fail(f"Khong doc duoc languages/vietnamese.json: {e}")
        return
    src = "\n".join(_read_all_sources().values())
    # t("prefix_" + x) -> key dong, tinh ca cac key bat dau bang prefix do
    dyn_prefixes = re.findall(r'language\s*\.\s*t\(\s*["\']([A-Za-z0-9_.]+_)["\']\s*\+', src)
    unused = [k for k in sorted(keys)
              if not re.search(r'["\']' + re.escape(k) + r'["\']', src)
              and not any(k.startswith(p) for p in dyn_prefixes)]
    if unused:
        fail(f"Key ngon ngu khai bao nhung KHONG dung trong code ({len(unused)}): "
             + ", ".join(unused[:10]))
    else:
        ok(f"Moi key ngon ngu deu duoc dung trong code ({len(keys)} key)")


def check_theme_names():
    """Ten theme trong config/DEFAULT phai ton tai trong utils.theme.THEMES"""
    sys.path.insert(0, ROOT)
    try:
        from utils.theme import THEMES, DEFAULT_THEME_NAME
        from config import DEFAULT_CONFIG
    except Exception as e:
        fail(f"Khong import duoc utils.theme/config: {e}")
        return
    problems = []
    if DEFAULT_THEME_NAME not in THEMES:
        problems.append(f"DEFAULT_THEME_NAME '{DEFAULT_THEME_NAME}' khong co trong THEMES")
    if DEFAULT_CONFIG.get("current_theme") not in THEMES:
        problems.append(
            f"DEFAULT_CONFIG['current_theme'] '{DEFAULT_CONFIG.get('current_theme')}' khong co trong THEMES")
    try:
        with open(os.path.join(ROOT, "config.example.json"), "r", encoding="utf-8") as f:
            sample = json.load(f)
        if sample.get("current_theme") not in THEMES:
            problems.append(
                f"config.example.json current_theme '{sample.get('current_theme')}' khong co trong THEMES")
    except Exception as e:
        problems.append(f"Khong doc duoc config.example.json: {e}")
    if problems:
        fail("Ten theme lech voi utils.theme.THEMES:\n  " + "\n  ".join(problems))
    else:
        ok(f"Ten theme dong bo ({len(THEMES)} theme: " + ", ".join(THEMES) + ")")


def check_danger_patterns():
    patterns = {
        r"importlib\.reload\(\s*constants\s*\)": "con reload(constants) lam mat theme",
        r"config\.update\(\{[^\}]*tokens": "con ghi de config bang dict rut gon",
        r"from discord import": "import nham package discord.py ben ngoai",
    }
    hits = []
    for dirpath, _, filenames in os.walk(ROOT):
        if any(s in dirpath for s in ("build", "dist", ".git", "__pycache__", "tools")):
            continue
        for name in filenames:
            if not name.endswith((".py", ".pyw")):
                continue
            full = os.path.join(dirpath, name)
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                src = f.read()
            for pat, desc in patterns.items():
                if re.search(pat, src):
                    hits.append(f"{os.path.relpath(full, ROOT)}: {desc}")
    if hits:
        fail("Phat hien pattern nguy hiem:\n  " + "\n  ".join(hits))
    else:
        ok("Khong con pattern nguy hiem (reload/ghi de config/nham package discord)")


def main():
    print("=" * 60)
    print("Discord BLUE - Audit tinh nhat quan")
    print("=" * 60)
    check_compile()
    check_languages()
    check_unused_language_keys()
    check_theme_names()
    check_config_sample()
    check_build_files()
    check_danger_patterns()
    print("=" * 60)
    if FAILURES:
        print(f"KET QUA: {len(FAILURES)} NHOM LOI")
        return 1
    print("KET QUA: DAT - moi kiem tra deu pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

