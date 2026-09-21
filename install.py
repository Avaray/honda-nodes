import os
import platform
import stat
import urllib.request

# Define the local bin directory
EXTENSION_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(EXTENSION_DIR, "bin")

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

def install_dependencies():
    os.makedirs(BIN_DIR, exist_ok=True)
    
    system = platform.system().lower() # 'windows', 'linux', 'darwin'
    arch = platform.machine().lower()  # e.g., 'x86_64', 'amd64', 'arm64', 'aarch64'
    
    # ---------------------------------------------------------
    # 1. Download `jq`
    # ---------------------------------------------------------
    jq_version = "jq-1.7.1"
    if system == "windows":
        jq_url = f"https://github.com/jqlang/jq/releases/download/{jq_version}/jq-windows-amd64.exe"
        jq_dest = os.path.join(BIN_DIR, "jq.exe")
    elif system == "darwin": # macOS
        is_arm = "arm" in arch or "aarch" in arch
        jq_url = f"https://github.com/jqlang/jq/releases/download/{jq_version}/jq-macos-{'arm64' if is_arm else 'amd64'}"
        jq_dest = os.path.join(BIN_DIR, "jq")
    else: # linux
        is_arm = "arm" in arch or "aarch" in arch
        jq_url = f"https://github.com/jqlang/jq/releases/download/{jq_version}/jq-linux-{'aarch64' if is_arm else 'amd64'}"
        jq_dest = os.path.join(BIN_DIR, "jq")
        
    if not os.path.exists(jq_dest):
        download_binary(jq_url, jq_dest)
    else:
        print(f"[Honda Nodes] jq is already installed at {jq_dest}")

    # ---------------------------------------------------------
    # 2. Download `mex`
    # ---------------------------------------------------------
    # TODO: Update these URLs to point to your actual GitHub repository releases!
    mex_version = "v1.0.0" 
    mex_base_url = "https://github.com/YOUR_GITHUB_USERNAME/mex/releases/download"
    
    if system == "windows":
        mex_url = f"{mex_base_url}/{mex_version}/mex-windows.exe"
        mex_dest = os.path.join(BIN_DIR, "mex.exe")
    elif system == "darwin":
        mex_url = f"{mex_base_url}/{mex_version}/mex-macos"
        mex_dest = os.path.join(BIN_DIR, "mex")
    else:
        mex_url = f"{mex_base_url}/{mex_version}/mex-linux"
        mex_dest = os.path.join(BIN_DIR, "mex")

    if not os.path.exists(mex_dest):
        # UNCOMMENT the line below once you put your real repository URLs above
        # download_binary(mex_url, mex_dest)
        print("[Honda Nodes] Please configure the 'mex' GitHub URLs in install.py to enable automatic downloads.")
    else:
        print(f"[Honda Nodes] mex is already installed at {mex_dest}")

if __name__ == "__main__":
    print("[Honda Nodes] Running post-install setup...")
    install_dependencies()
