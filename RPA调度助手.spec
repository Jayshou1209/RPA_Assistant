# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('config.py', '.'), ('token.txt', '.'), ('api_client.py', '.'), ('scraper.py', '.'), ('dispatcher.py', '.'), ('enhanced_scraper.py', '.'), ('real_api_scraper.py', '.'), ('gui_dispatcher.py', '.'), ('gui_scraper.py', '.')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'tkinter.scrolledtext', 'api_client', 'scraper', 'dispatcher', 'enhanced_scraper', 'real_api_scraper', 'gui_dispatcher', 'gui_scraper', 'pandas', 'openpyxl', 'requests', 'pytz', 'concurrent.futures'],
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
    name='RPA调度助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
