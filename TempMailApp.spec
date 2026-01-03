import os
import platform

# Determine absolute path to the current directory
block_cipher = None
base_path = os.getcwd()

# Select icon based on OS
icon_file = 'ico.ico'
if platform.system() == 'Darwin':
    icon_file = 'icns.icns' # Assuming you have this for Mac
    
icon_path = os.path.join(base_path, icon_file)
main_script = os.path.join(base_path, 'main.py')

a = Analysis(
    [main_script],
    pathex=[base_path],
    binaries=[],
    datas=[('saved_emails.json', '.')],
    hiddenimports=['requests'],
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
    name='TempMailApp',
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
    icon=[icon_path],
)
