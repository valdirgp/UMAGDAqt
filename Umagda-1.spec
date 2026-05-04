# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Umagda-1.py'],
    pathex=[],
    binaries=[],
    datas=[('Controller', 'Controller'), ('General', 'General'), ('Model', 'Model'), ('View', 'View'), ('C:/Users/aluno/AppData/Local/Programs/Python/Python312/Lib/site-packages/pyIGRF', 'pyIGRF')],
    hiddenimports=[],
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
    name='Umagda-1',
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
    icon=['General\\images\\univap.ico'],
)
