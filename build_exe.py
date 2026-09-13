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

    # Build PyInstaller command collecting all flet package data (icons.json, fonts, etc.)
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
        "--collect-all=flet",
        "--collect-all=flet_desktop",
        "--collect-all=flet_core",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtMultimedia",
        "--hidden-import=mutagen",
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp_ejs",
        "--hidden-import=darkdetect",
        "--hidden-import=PIL",
        os.path.join(project_root, "main_flet.py")
    ]

    print(f"[*] Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    output_exe_folder = os.path.join(dist_dir, "NovaDownloader")
    print(f"[+] PyInstaller build finished! Checking FFmpeg bundling...")

    # Ensure FFmpeg binaries are bundled into dist/NovaDownloader/ffmpeg/
    target_ffmpeg_dir = os.path.join(output_exe_folder, "ffmpeg")
    os.makedirs(target_ffmpeg_dir, exist_ok=True)

    import shutil
    ffmpeg_candidates = [
        os.path.join(project_root, "ffmpeg"),
        r"C:\ffmpeg\bin",
        r"C:\ffmpeg",
    ]
    which_ff = shutil.which("ffmpeg")
    if which_ff:
        ffmpeg_candidates.append(os.path.dirname(which_ff))

    ffmpeg_src_dir = None
    for cand in ffmpeg_candidates:
        if os.path.exists(os.path.join(cand, "ffmpeg.exe")):
            ffmpeg_src_dir = cand
            break

    if ffmpeg_src_dir:
        print(f"[*] Found FFmpeg binaries in: {ffmpeg_src_dir}")
        for bin_name in ["ffmpeg.exe", "ffprobe.exe"]:
            src_file = os.path.join(ffmpeg_src_dir, bin_name)
            dst_file = os.path.join(target_ffmpeg_dir, bin_name)
            if os.path.exists(src_file):
                print(f"[*] Copying {bin_name} -> {dst_file}")
                shutil.copy2(src_file, dst_file)
            else:
                print(f"[!] Info: {bin_name} not found in {ffmpeg_src_dir}")
        if os.path.exists(os.path.join(target_ffmpeg_dir, "ffmpeg.exe")):
            print(f"[+] Portable FFmpeg successfully bundled into: {target_ffmpeg_dir}")
    else:
        print("[!] WARNING: No ffmpeg.exe found to bundle! Ensure FFmpeg is placed in .\ffmpeg or installed on PATH.")

    print(f"[+] Final portable build ready at: {output_exe_folder}")

if __name__ == "__main__":
    build()
