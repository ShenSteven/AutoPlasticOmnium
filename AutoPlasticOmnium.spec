# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

block_cipher = None #pyi_crypto.PyiBlockCipher(key="'steven1986.11'")

added_files = [
    ('ui/images/*', 'ui/images'),
    ('ui/ui_main.ui', 'ui'),
    ('runin/ui_login.ui', 'runin'),
    ('conf/*.yaml', 'conf'),
    ('conf/*.db', 'conf'),
    ('conf/__version__.py', 'conf'),
    ('manual.docx', '.'),
    ('tool/*', 'tool'),
    ('scripts/*.json', 'scripts'),
    ('scripts/*.xlsx', 'scripts')]

for folder in ['M4','M6','SX5GEV']:
    flash_files = [('flash/' + os.path.basename(str(item)), ('flash/' + os.path.basename(str(item)))) for item in
          list(Path().absolute().rglob(rf"flash\{folder}"))]
    added_files.extend(flash_files)

added_files += copy_metadata('nidaqmx')

def file_name(file_dir, ext):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == ext:
                L.append('scripts.'+os.path.splitext(file)[0])
    return L
hiddenimports_files = file_name('./scripts','.py')

a = Analysis(
    ['main.py'],
    pathex=['./'],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports_files,
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
    name='AutoPlasticOmnium',
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
    icon='ui/images/PO.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoPlasticOmnium',
)
