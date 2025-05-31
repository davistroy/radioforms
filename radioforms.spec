# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for RadioForms
Creates single-file executable for Windows, macOS, and Linux
"""

import sys
from pathlib import Path

# Build configuration
block_cipher = None
app_name = 'RadioForms'
app_version = '1.0.0'

# Platform-specific settings
if sys.platform == 'win32':
    icon_file = 'resources/radioforms.ico'
    executable_name = f'{app_name}-Windows.exe'
elif sys.platform == 'darwin':
    icon_file = 'resources/radioforms.icns'
    executable_name = f'{app_name}-macOS'
else:  # Linux
    icon_file = 'resources/radioforms.png'
    executable_name = f'{app_name}-Linux'

# Analysis configuration
a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Include documentation
        ('docs/*.md', 'docs'),
        ('docs/adr/*.md', 'docs/adr'),
        ('docs/api/*.md', 'docs/api'),
        # Include forms analysis
        ('forms/*.md', 'forms'),
        # Include rules and guidelines
        ('rules/*.md', 'rules'),
        # Include any resource files (if they exist)
        # ('resources/*', 'resources'),
    ],
    hiddenimports=[
        # PySide6 modules that might not be auto-detected
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        # SQLite3 (usually included by default)
        'sqlite3',
        # JSON and other standard library modules
        'json',
        'logging',
        'datetime',
        'pathlib',
        # Application modules
        'src.app.application',
        'src.database.connection',
        'src.database.schema',
        'src.forms.ics213',
        'src.services.form_service',
        'src.services.file_service',
        'src.ui.main_window',
        'src.ui.ics213_widget',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ (Python bytecode archive)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=executable_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression to reduce file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if Path(icon_file).exists() else None,
    version='version_info.txt' if Path('version_info.txt').exists() else None,
)

# macOS App Bundle (only for macOS)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{app_name}.app',
        icon=icon_file if Path(icon_file).exists() else None,
        bundle_identifier=f'com.radioforms.{app_name.lower()}',
        version=app_version,
        info_plist={
            'CFBundleName': app_name,
            'CFBundleDisplayName': 'RadioForms',
            'CFBundleVersion': app_version,
            'CFBundleShortVersionString': app_version,
            'CFBundleIdentifier': f'com.radioforms.{app_name.lower()}',
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'RFMS',
            'LSMinimumSystemVersion': '10.14.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'RadioForms JSON',
                    'CFBundleTypeExtensions': ['json'],
                    'CFBundleTypeRole': 'Editor',
                    'CFBundleTypeIconFile': icon_file if Path(icon_file).exists() else None,
                }
            ],
        },
    )