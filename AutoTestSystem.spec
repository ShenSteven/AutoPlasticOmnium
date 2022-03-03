# -*- mode: python ; coding: utf-8 -*-
# pyinstaller -y --clean --noconsole --debug=all  --distpath=./dist/ -n AutoTestSystem --icon="test.ico" --add-data="ui/main.ui;ui" --add-data="ui/images.qrc;ui" --add-data="ui/images;ui" --add-data="conf/*.yaml;conf" --add-data="scripts;scripts" main.py --runtime-hook="runtimehook.py"
# pyinstaller AutoTestSystem.spec

added_files = [
    ('ui/main.ui', 'ui'),
    ('ui/images.qrc', 'ui'),
    ('ui/images', 'ui'),
    ('conf/*.yaml', 'conf'),
    ('setup.py', '.'),
    ('scripts', 'scripts')
]

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('ui/main.ui', 'ui'), ('ui/images.qrc', 'ui'), ('ui/images', 'ui'), ('conf/*.yaml', 'conf'), ('scripts', 'scripts')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=['runtimehook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='AutoTestSystem',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='test.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='AutoTestSystem')
