# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building single-file Windows executable
Embeds all dependencies and creates djvu2pdf.exe
"""

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect all necessary data files
datas = []

# Add the TOC parser module
datas.append(('djvu2pdf_toc_parser.py', '.'))

# Add binaries directory if it exists (will contain Windows executables)
# bin/ should contain: djvused.exe, ddjvu.exe, pdfbeads.exe, tiffsplit.exe, and DLLs
if os.path.exists('bin'):
    datas.append(('bin', 'bin'))

a = Analysis(
    ['djvu2pdf_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinterdnd2',
        'djvu2pdf_converter',
        'djvu2pdf_toc_parser',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='djvu2pdf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file here if you have one: 'icon.ico'
)
