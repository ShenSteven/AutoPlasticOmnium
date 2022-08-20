# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import os
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

block_cipher = pyi_crypto.PyiBlockCipher(key="'steven1986.11'")

added_files = [
    ('ui/images/*', 'ui/images'),
    ('ui/ui_main.ui', 'ui'),
    ('conf/*.yaml', 'conf'),
    ('conf/*.db', 'conf'),
    ('conf/__version__.py', 'conf'),
    ('manual.docx', '.'),
    ('restart.exe', '.'),
    ('scripts/*.json', 'scripts'),
    ('scripts/*.xlsx', 'scripts')]

flash_files = [('flash/' + os.path.basename(str(item)), ('flash/' + os.path.basename(str(item)))) for item in
      list(Path().absolute().rglob(r"flash\*"))]
added_files.extend(flash_files)

added_files += copy_metadata('nidaqmx')

a = Analysis(
    ['main.py'],
    pathex=['./'],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [('v', None, 'OPTION')],
    exclude_binaries=True,
    name='AutoAMLS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='test.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoAMLS',
)
