import os
import shutil

def find_jq() -> str | None:
    """Look for the 'jq' executable in PATH or in the extension's own bin/ folder."""
    jq_path = shutil.which("jq")
    if jq_path:
        return jq_path

    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_bin = os.path.join(current_dir, "bin")
    jq_exe = "jq.exe" if os.name == "nt" else "jq"
    local_jq = os.path.join(local_bin, jq_exe)
    if os.path.exists(local_jq):
        return local_jq

    return None
