import os
import shutil
import subprocess
from comfy_api.latest import io

class HondaExtractMetadata(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ExtractMetadata",
            display_name="🏷️ Extract Metadata",
            category="⚡️ Honda Nodes/🏷️ Metadata",
            description="Extracts metadata from image and video files using the 'mex' CLI tool.",
            inputs=[
                io.String.Input(
                    "file_path",
                    default="",
                    display_name="File Path",
                    tooltip="Path to the image or video file.",
                ),
                io.Boolean.Input(
                    "as_json",
                    default=False,
                    display_name="As JSON",
                    tooltip="If True, outputs the metadata as JSON format (-j flag).",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(cls, file_path: str, as_json: bool) -> io.NodeOutput:
        if not file_path:
            raise ValueError("File path is empty. Please provide a valid file path.")
            
        file_path = file_path.strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Find the 'mex' executable
        mex_path = shutil.which("mex")
        
        # Also check local 'bin' folder in the extension directory
        if not mex_path:
            # Go up from nodes/metadata/extract_metadata.py -> nodes/metadata -> nodes -> honda-nodes
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_bin = os.path.join(current_dir, "bin")
            mex_exe = "mex.exe" if os.name == "nt" else "mex"
            local_mex = os.path.join(local_bin, mex_exe)
            if os.path.exists(local_mex):
                mex_path = local_mex

        if not mex_path:
            raise FileNotFoundError(
                "The 'mex' CLI tool was not found in the system PATH or the extension's 'bin' folder. "
                "Please download it from its repository and either add it to your PATH or place the executable "
                "in a 'bin' folder inside the honda-nodes extension directory."
            )

        cmd = [mex_path, file_path]
        if as_json:
            cmd.append("-j")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
            return io.NodeOutput(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error executing mex (exit code {e.returncode}): {e.stderr or e.stdout or str(e)}")
