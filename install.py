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
    # 2. Download `ime`
    # ---------------------------------------------------------
    # TODO: Update these URLs to point to your actual GitHub repository releases!
    ime_version = "v1.0.0" 
    ime_base_url = "https://github.com/YOUR_GITHUB_USERNAME/image-metadata-editor/releases/download"
    
    if system == "windows":
        ime_url = f"{ime_base_url}/{ime_version}/ime-windows.exe"
        ime_dest = os.path.join(BIN_DIR, "ime.exe")
    elif system == "darwin":
        ime_url = f"{ime_base_url}/{ime_version}/ime-macos"
        ime_dest = os.path.join(BIN_DIR, "ime")
    else:
        ime_url = f"{ime_base_url}/{ime_version}/ime-linux"
        ime_dest = os.path.join(BIN_DIR, "ime")

    if not os.path.exists(ime_dest):
        # UNCOMMENT the line below once you put your real repository URLs above
        # download_binary(ime_url, ime_dest)
        print("[Honda Nodes] Please configure the 'ime' GitHub URLs in install.py to enable automatic downloads.")
    else:
        print(f"[Honda Nodes] ime is already installed at {ime_dest}")

if __name__ == "__main__":
    print("[Honda Nodes] Running post-install setup...")
    install_dependencies()
