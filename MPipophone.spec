# -*- mode: python ; coding: utf-8 -*-

import site
import os

# Get mediapipe package path
mediapipe_path = None
for site_package in site.getsitepackages():
    potential_path = os.path.join(site_package, 'mediapipe')
    if os.path.exists(potential_path):
        mediapipe_path = potential_path
        break

# Prepare datas list
datas_list = [('src\\data', 'data')]
if mediapipe_path:
    datas_list.append((mediapipe_path, 'mediapipe'))

a = Analysis(
    ['src\\main'],
    pathex=[],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.pose',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solutions.drawing_styles',
    ],
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
    name='MPipophone',
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
