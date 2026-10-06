import os
import hashlib
from comfy_api.latest import io

class HondaFileHash(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_FileHash",
            display_name="📂 File Hash",
            category="⚡️ Honda Nodes/📂 File System",
            description="Calculates the MD5 or SHA-256 hash of a file.",
            inputs=[
                io.String.Input(
                    "path",
                    default="",
                    force_input=True,
                    display_name="Path",
                    tooltip="Absolute path to the file.",
                ),
                io.Combo.Input(
                    "algorithm",
                    options=["SHA-256", "MD5"],
                    default="SHA-256",
                    display_name="Algorithm",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Hash"),
            ],
        )

    @classmethod
    def execute(cls, path: str, algorithm: str) -> io.NodeOutput:
        path = (path or "").strip()
        if not path or not os.path.isfile(path):
            raise RuntimeError(f"File not found: {path}")

        if algorithm == "MD5":
            h = hashlib.md5()
        else:
            h = hashlib.sha256()
            
        try:
            with open(path, "rb") as f:
                # Read in 8MB chunks to avoid high memory usage for very large files
                for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
                    h.update(chunk)
            return io.NodeOutput(h.hexdigest())
        except Exception as e:
            raise RuntimeError(f"Failed to calculate hash for {path}: {str(e)}")
