from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPECPATH).parent

main_analysis = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "content"), "content"),
        (str(project_root / "assets"), "assets"),
    ],
    hiddenimports=["app.runtime.python_runner"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Qt uses the Windows system ICU DLLs. A developer PATH (for example,
# a local Poppler install) can otherwise inject an incompatible ICU build.
main_analysis.binaries = [
    entry
    for entry in main_analysis.binaries
    if not (
        Path(entry[0]).name.lower().startswith("icu")
        and Path(entry[0]).name.lower().endswith(".dll")
    )
]

main_pyz = PYZ(main_analysis.pure)
main_exe = EXE(
    main_pyz,
    main_analysis.scripts,
    [],
    exclude_binaries=True,
    name="PythonLearner",
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
    icon=str(project_root / "assets" / "app-icon.ico"),
    version=str(project_root / "packaging" / "version_info.txt"),
)

worker_analysis = Analysis(
    [str(project_root / "worker_main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("pip"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PySide6"],
    noarchive=False,
)
worker_pyz = PYZ(worker_analysis.pure)
worker_exe = EXE(
    worker_pyz,
    worker_analysis.scripts,
    [],
    exclude_binaries=True,
    name="PythonWorker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

collection = COLLECT(
    main_exe,
    main_analysis.binaries,
    main_analysis.datas,
    worker_exe,
    worker_analysis.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PythonLearner",
)
