# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['RDR2ConflictChecker.py'],
    pathex=['.'],  # 
    binaries=[],
    datas=[('resources/icon.ico', 'resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'PyQt5', 'PySide2', 'PyQt6', 'PySide6'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RDR2ModManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                # Disable UPX compression to reduce AV false positives
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico',
    version='file_version_info.txt',   
)



