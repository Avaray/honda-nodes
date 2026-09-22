import json
import os
import platform
import stat
import urllib.error
import urllib.request

# Define the local bin directory
EXTENSION_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(EXTENSION_DIR, "bin")


def get_latest_tag(repo: str, fallback: str) -> str:
    """
    Query the GitHub API for the latest release tag of `repo` (e.g. 'jqlang/jq').
    Returns the tag_name string on success, or `fallback` if the request fails.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "honda-nodes-installer"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            tag = data.get("tag_name", "").strip()
            if tag:
                print(f"[Honda Nodes] Latest release of {repo}: {tag}")
                return tag
    except Exception as e:
        print(f"[Honda Nodes] WARNING: Could not fetch latest release for {repo}: {e}")
    print(f"[Honda Nodes] Falling back to hardcoded version: {fallback}")
    return fallback


def download_binary(url: str, dest_path: str):
    print(f"[Honda Nodes] Downloading {url} ...")
    try:
        urllib.request.urlretrieve(url, dest_path)

        # Make the file executable on Linux and macOS
        if platform.system() != "Windows":
            st = os.stat(dest_path)
            os.chmod(dest_path, st.st_mode | stat.S_IEXEC)

        print(f"[Honda Nodes] Successfully installed to {dest_path}")
    except Exception as e:
        print(f"[Honda Nodes] ERROR: Failed to download {url}\n{e}")


def _jq_filename(system: str, arch: str) -> str:
    """
    Return the exact filename used in jq GitHub releases for the given
    platform.system().lower() and platform.machine().lower() values.

    Reference: https://github.com/jqlang/jq/releases
    """
    # ---- Windows ----
    if system == "windows":
        if "arm" in arch or "aarch" in arch:
            return "jq-windows-arm64.exe"
        if arch in ("i386", "i686", "x86"):
            return "jq-windows-i386.exe"
        return "jq-windows-amd64.exe"  # x86_64 / amd64 (default)

    # ---- macOS ----
    if system == "darwin":
        if "arm" in arch or "aarch" in arch:
            return "jq-macos-arm64"
        return "jq-macos-amd64"

    # ---- Linux (everything else) ----
    if arch in ("x86_64", "amd64"):
        return "jq-linux-amd64"
    if arch in ("aarch64", "arm64"):
        return "jq-linux-arm64"
    if arch in ("armv7l", "armhf"):
        return "jq-linux-armhf"
    if arch in ("armv6l", "armel"):
        return "jq-linux-armel"
    if arch in ("i386", "i686", "x86"):
        return "jq-linux-i386"
    if arch == "riscv64":
        return "jq-linux-riscv64"
    if arch == "s390x":
        return "jq-linux-s390x"
    if arch in ("ppc64le", "ppc64el"):
        return "jq-linux-ppc64el"
    if arch == "mips64el":
        return "jq-linux-mips64el"
    if arch == "mips64":
        return "jq-linux-mips64"
    if arch == "mipsel":
        return "jq-linux-mipsel"
    if arch == "mips":
        return "jq-linux-mips"
    # Generic fallback: amd64
    print(f"[Honda Nodes] WARNING: Unknown arch '{arch}', defaulting to jq-linux-amd64")
    return "jq-linux-amd64"


def install_dependencies():
    os.makedirs(BIN_DIR, exist_ok=True)

    system = platform.system().lower()  # 'windows', 'linux', 'darwin'
    arch = platform.machine().lower()   # e.g. 'x86_64', 'amd64', 'arm64', 'aarch64'

    # ---------------------------------------------------------
    # 1. Download `jq`
    # ---------------------------------------------------------
    jq_tag = get_latest_tag("jqlang/jq", fallback="jq-1.8.2")
    jq_filename = _jq_filename(system, arch)
    jq_url = f"https://github.com/jqlang/jq/releases/download/{jq_tag}/{jq_filename}"
    jq_dest = os.path.join(BIN_DIR, "jq.exe" if system == "windows" else "jq")

    if not os.path.exists(jq_dest):
        download_binary(jq_url, jq_dest)
    else:
        print(f"[Honda Nodes] jq is already installed at {jq_dest}")

    # ---------------------------------------------------------
    # 2. Download `ime`
    # ---------------------------------------------------------
    ime_tag = get_latest_tag("Avaray/image-metadata-editor", fallback="v1.0.0")
    ime_base = f"https://github.com/Avaray/image-metadata-editor/releases/download/{ime_tag}"

    if system == "windows":
        ime_url = f"{ime_base}/ime-windows-amd64.exe"
        ime_dest = os.path.join(BIN_DIR, "ime.exe")
    elif system == "darwin":
        is_arm = "arm" in arch or "aarch" in arch
        ime_url = f"{ime_base}/ime-darwin-{'arm64' if is_arm else 'amd64'}"
        ime_dest = os.path.join(BIN_DIR, "ime")
    else:  # linux
        is_arm = "arm" in arch or "aarch" in arch
        ime_url = f"{ime_base}/ime-linux-{'arm64' if is_arm else 'amd64'}"
        ime_dest = os.path.join(BIN_DIR, "ime")

    if not os.path.exists(ime_dest):
        download_binary(ime_url, ime_dest)
    else:
        print(f"[Honda Nodes] ime is already installed at {ime_dest}")


if __name__ == "__main__":
    print("[Honda Nodes] Running post-install setup...")
    install_dependencies()
