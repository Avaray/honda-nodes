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
            description="Extracts metadata from image and video files using the 'ime' CLI tool.",
            # Output node: runs even when nothing is connected to "Output",
            # so the in-node preview always works.
            is_output_node=True,
            inputs=[
                io.String.Input(
                    "file_path",
                    default="",
                    display_name="File Path",
                    tooltip="Path to the image or video file.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(cls, file_path: str, **kwargs) -> io.NodeOutput:
        if not file_path:
            raise ValueError("File path is empty. Please provide a valid file path.")
            
        file_path = file_path.strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Find the 'ime' executable
        ime_path = shutil.which("ime")
        
        # Also check local 'bin' folder in the extension directory
        if not ime_path:
            # Go up from nodes/metadata/extract_metadata.py -> nodes/metadata -> nodes -> honda-nodes
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_bin = os.path.join(current_dir, "bin")
            ime_exe = "ime.exe" if os.name == "nt" else "ime"
            local_ime = os.path.join(local_bin, ime_exe)
            if os.path.exists(local_ime):
                ime_path = local_ime

        if not ime_path:
            raise FileNotFoundError(
                "The 'ime' CLI tool was not found in the system PATH or the extension's 'bin' folder. "
                "Please download it from its repository and either add it to your PATH or place the executable "
                "in a 'bin' folder inside the honda-nodes extension directory."
            )

        cmd = [ime_path, file_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error executing ime (exit code {e.returncode}): {e.stderr or e.stdout or str(e)}")

        text = result.stdout.strip()

        # The frontend (extract_metadata.js) reads these keys in onExecuted():
        #   resolved_path  -> the path this run actually used (also when it came from a link)
        #   metadata_text  -> what goes into the preview box
        return io.NodeOutput(
            text,
            ui={
                "resolved_path": (file_path,),
                "metadata_text": (text,),
            },
        )
