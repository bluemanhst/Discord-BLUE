# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.pyw'],
    pathex=[],
    binaries=[],
    datas=[('assets/discord_logo.png', 'assets'), ('assets/facebook_logo.png', 'assets'), ('assets/logo_discord_blue.ico', 'assets'), ('assets/logo_blue_labs.png', 'assets'), ('assets/emoji_unicode.json', 'assets'), ('config.example.json', '.'), ('languages', 'languages')],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'requests', 'pystray', 'pystray._win32', 'discord.bot', 'discord.dashboard', 'discord.token_validator', 'discord.channel_validator', 'utils.theme', 'utils.splash_screen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Discord BLUE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/logo_discord_blue.ico'],
)
