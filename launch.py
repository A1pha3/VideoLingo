"""VideoLingo Enhanced Launcher - Pre-flight checks + logging."""

import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"startup_{datetime.now():%Y%m%d_%H%M%S}.log"


def log(message):
    line = f"[{datetime.now():%H:%M:%S}] {message}"
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def check_package(name, import_name=None):
    import_name = import_name or name
    try:
        module = __import__(import_name)
        return getattr(module, "__version__", "ok")
    except ImportError:
        return None


def main():
    errors = []
    warnings = []

    log(f"Python: {sys.version.split()[0]} ({sys.executable})")

    for package_name, import_name in [("streamlit", None), ("json_repair", "json_repair")]:
        if not check_package(package_name, import_name):
            errors.append(f"{package_name} not installed. Run: python install.py")

    torch_version = check_package("torch")
    if torch_version:
        import torch

        if torch.cuda.is_available():
            log(
                f"torch: {torch_version}, cuda: {torch.version.cuda}, "
                f"gpu: {torch.cuda.get_device_name(0)}"
            )
        else:
            warnings.append("torch has no CUDA support. GPU disabled. Reinstall: python install.py")
            log(f"torch: {torch_version} (CPU only)")

    if not check_package("whisperx"):
        warnings.append("whisperx not installed. ASR will fail.")

    if not shutil.which("ffmpeg"):
        errors.append("ffmpeg not found in PATH. Install: choco install ffmpeg")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex(("127.0.0.1", 8501)) == 0:
            warnings.append("Port 8501 in use. Close other app or use --server.port 8502")

    for warning in warnings:
        log(f"[WARN] {warning}")
    for error in errors:
        log(f"[ERROR] {error}")

    if errors:
        print()
        for error in errors:
            print(f"  [ERROR] {error}")
        print(f"\n  Fix errors above. Log: {LOG_FILE}\n")
        sys.exit(1)

    if warnings:
        print()
        for warning in warnings:
            print(f"  [WARN] {warning}")
        print()

    log("Launching Streamlit...")
    os.environ["PYTHONWARNINGS"] = "ignore"
    try:
        process = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "st.py", "--logger.level", "error"],
            cwd=str(SCRIPT_DIR),
        )
        if process.returncode != 0:
            log(f"Streamlit exited with code {process.returncode}")
            print(f"\n  Streamlit crashed (code {process.returncode}). See: {LOG_FILE}\n")
            sys.exit(process.returncode)
    except KeyboardInterrupt:
        log("Stopped by user")


if __name__ == "__main__":
    main()