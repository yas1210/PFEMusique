# -*- mode: python ; coding: utf-8 -*-

import site
import os
import sys

mediapipe_path = None
for site_package in site.getsitepackages():
    potential_path = os.path.join(site_package, "mediapipe")
    if os.path.exists(potential_path):
        mediapipe_path = potential_path
        break

datas_list = []

if os.path.exists("src/data"):
    datas_list.append(("src/data", "data"))

if mediapipe_path:
    datas_list.append((mediapipe_path, "mediapipe"))

# Ajouter la soundfont FluidSynth si elle existe
if os.path.exists("src/data/GeneralUser.sf2"):
    datas_list.append(("src/data/GeneralUser.sf2", "data"))

a = Analysis(
    ["src/main.py"],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        "mediapipe",
        "mediapipe.python",
        "mediapipe.python.solutions",
        "mediapipe.python.solutions.pose",
        "mediapipe.python.solutions.drawing_utils",
        "mediapipe.python.solutions.drawing_styles",
        "fluidsynth",       # ajout pour Mac
        "pyfluidsynth",     # ajout pour Mac
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
    name="MPipophone",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,       # False recommandé sur Mac ARM
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Bloc Mac uniquement — génère un vrai .app double-cliquable
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="MPipophone.app",
        icon=None,             
        bundle_identifier="com.musicmove.mpipophone",
        info_plist={
            "NSCameraUsageDescription": "MusicMove utilise la caméra pour détecter les mouvements.",
            "NSMicrophoneUsageDescription": "MusicMove peut utiliser le microphone.",
            "CFBundleShortVersionString": "1.0.0",
        },
    )