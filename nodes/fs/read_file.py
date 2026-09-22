import os
from comfy_api.latest import io

class HondaReadFile(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ReadFile",
            display_name="📂 Read File",
            category="⚡️ Honda Nodes/📂 File System",
            description="Reads text content from a file.",
            inputs=[
                io.String.Input(
                    "file_path",
                    default="",
                    display_name="File Path",
                    tooltip="Absolute path to the text file to read.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Text"),
            ],
        )

    @classmethod
    def execute(cls, file_path: str) -> io.NodeOutput:
        file_path = (file_path or "").strip()
        if not file_path:
            raise ValueError("File path cannot be empty.")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fallback to replace invalid characters if it's not strict UTF-8
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}")
            
        return io.NodeOutput(text)
