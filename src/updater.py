"""Auto-updater that checks GitHub releases and offers to update."""
from __future__ import annotations
import sys
import os
import json
import hashlib
import tempfile
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

CURRENT_VERSION = "1.0.1"
GITHUB_REPO = "wansolanso/Kenshi-Save-Editor"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def is_frozen() -> bool:
    return getattr(sys, '_MEIPASS', None) is not None


def get_current_exe() -> Path | None:
    if is_frozen():
        return Path(sys.executable)
    return None


def check_for_update() -> dict | None:
    """Check GitHub for a newer release. Returns release info dict or None."""
    try:
        req = Request(GITHUB_API, headers={"Accept": "application/vnd.github.v3+json"})
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        tag = data.get("tag_name", "")
        remote_version = tag.lstrip("v")
        if not remote_version or remote_version == CURRENT_VERSION:
            return None

        # Compare versions
        try:
            from packaging.version import Version
            if Version(remote_version) <= Version(CURRENT_VERSION):
                return None
        except ImportError:
            # Fallback: tuple compare
            def _ver(s):
                return tuple(int(x) for x in s.split(".") if x.isdigit())
            if _ver(remote_version) <= _ver(CURRENT_VERSION):
                return None

        # Find the exe asset
        exe_asset = None
        checksum_asset = None
        for asset in data.get("assets", []):
            name = asset["name"]
            if name.endswith(".exe"):
                exe_asset = asset
            elif name == "CHECKSUMS.txt":
                checksum_asset = asset

        if not exe_asset:
            return None

        # Get expected hash from CHECKSUMS.txt
        expected_hash = None
        if checksum_asset:
            try:
                with urlopen(checksum_asset["browser_download_url"], timeout=5) as resp:
                    text = resp.read().decode()
                for line in text.splitlines():
                    if "SHA-256:" in line and ".exe" in line:
                        expected_hash = line.split("SHA-256:")[1].strip().split()[0]
                        break
            except Exception:
                pass

        return {
            "version": remote_version,
            "tag": tag,
            "exe_url": exe_asset["browser_download_url"],
            "exe_name": exe_asset["name"],
            "exe_size": exe_asset["size"],
            "expected_hash": expected_hash,
            "notes": data.get("body", ""),
        }

    except (URLError, json.JSONDecodeError, KeyError, Exception):
        return None


def download_and_replace(update_info: dict, progress_callback=None) -> tuple[bool, str]:
    """Download the new exe, verify hash, and replace the current one.
    Returns (success, message).
    """
    current_exe = get_current_exe()
    if not current_exe:
        return False, "Not running as compiled exe"

    try:
        # Download to temp file
        tmp_dir = tempfile.mkdtemp(prefix="kenshi_update_")
        tmp_path = Path(tmp_dir) / update_info["exe_name"]

        req = Request(update_info["exe_url"])
        with urlopen(req, timeout=60) as resp:
            total = update_info["exe_size"]
            downloaded = 0
            hasher = hashlib.sha256()
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    hasher.update(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)

        # Verify hash
        actual_hash = hasher.hexdigest()
        expected = update_info.get("expected_hash")
        if expected and actual_hash != expected:
            tmp_path.unlink()
            return False, f"Hash mismatch!\nExpected: {expected}\nGot: {actual_hash}"

        # Replace: rename current → .old, move new → current, launch new, exit
        old_path = current_exe.with_suffix(".exe.old")
        if old_path.exists():
            old_path.unlink()

        # Write a small batch script that waits for us to exit, then swaps
        bat_path = Path(tmp_dir) / "_update.bat"
        bat_path.write_text(
            f'@echo off\n'
            f'echo Updating Kenshi Save Editor...\n'
            f'timeout /t 2 /nobreak >nul\n'
            f'move /Y "{current_exe}" "{old_path}"\n'
            f'move /Y "{tmp_path}" "{current_exe}"\n'
            f'start "" "{current_exe}"\n'
            f'del "{old_path}" 2>nul\n'
            f'rmdir /S /Q "{tmp_dir}" 2>nul\n',
            encoding="utf-8"
        )

        # Launch the updater script and exit
        subprocess.Popen(
            ["cmd", "/c", str(bat_path)],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        )
        return True, f"Updating to {update_info['version']}..."

    except Exception as e:
        return False, f"Download failed: {e}"
