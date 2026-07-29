import os
import sys
import subprocess

def build():
    print("==========================================")
    print("   NOVA DOWNLOADER - PYINSTALLER BUILD    ")
    print("==========================================")

    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "dist")

    # Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define separator based on platform (; for Windows, : for Unix)
    sep = ";" if sys.platform == "win32" else ":"

    # Build PyInstaller command with explicit flet_desktop hidden imports
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=NovaDownloader",
        f"--icon={os.path.join(project_root, 'assets', 'icon.ico')}",
        f"--add-data={os.path.join(project_root, 'assets')}{sep}assets",
        f"--add-data={os.path.join(project_root, 'core')}{sep}core",
        f"--add-data={os.path.join(project_root, 'database')}{sep}database",
        f"--add-data={os.path.join(project_root, 'services')}{sep}services",
        f"--add-data={os.path.join(project_root, 'ui')}{sep}ui",
        f"--add-data={os.path.join(project_root, 'utils')}{sep}utils",
        "--hidden-import=flet",
        "--hidden-import=flet_desktop",
        "--hidden-import=flet_core",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtMultimedia",
        "--hidden-import=mutagen",
        "--hidden-import=yt_dlp",
        os.path.join(project_root, "main_flet.py")
    ]

    print(f"[*] Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    output_exe_folder = os.path.join(dist_dir, "NovaDownloader")
    print(f"[+] Build successful! Output located at: {output_exe_folder}")

if __name__ == "__main__":
    build()
