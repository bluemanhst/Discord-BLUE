# tools/audit.py
# Kiem tra tinh nhat quan du an: compile, key ngon ngu, config mau, spec/build.
# Cach chay:  python tools/audit.py   (exit 0 = dat, exit 1 = co loi)

import compileall
import json
import os
import re
import sys

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
    codes = ["vietnamese", "english", "chinese"]
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
                if "." in key:
                    used.add(key)
                    if "theme_page.apply" in key:
                        print(f"DEBUG: {os.path.relpath(full, ROOT)} "
                              f"line {src[:m.start()].count(chr(10)) + 1}: [{key}] "
                              f"ctx=...{src[max(0, m.start()-60):m.start() + 60]!r}...")
    missing_vi = sorted(k for k in used if k not in data["vietnamese"])
    if missing_vi:
        fail(f"Key dung trong code nhung thieu trong VI ({len(missing_vi)}): {missing_vi[:10]}")
    else:
        ok(f"Key ngon ngu trong code deu co trong VI ({len(used)} key)")
    for code in ("english", "chinese"):
        missing = sorted(k for k in data["vietnamese"] if k not in data[code])
        if missing:
            fail(f"languages/{code}.json thieu {len(missing)} key so voi VI: {missing[:10]}")
        else:
            ok(f"languages/{code}.json du key nhu VI ({len(data[code])} key)")
    ph = re.compile(r"\{(\d+)\}")
    mismatch = []
    for key, vi_text in data["vietnamese"].items():
        vi_ph = sorted(ph.findall(vi_text))
        for code in ("english", "chinese"):
            if sorted(ph.findall(data[code].get(key, ""))) != vi_ph:
                mismatch.append(key)
                break
    if mismatch:
        fail(f"Placeholder lech giua cac ngon ngu ({len(mismatch)}): {mismatch[:10]}")
    else:
        ok("Placeholder {n} khop nhau giua 3 ngon ngu")
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

