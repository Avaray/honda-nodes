import os
from comfy_api.latest import io

class HondaRenameFile(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_RenameFile",
            display_name="📂 Rename File",
            category="⚡️ Honda Nodes/📂 File System",
            description="Renames a file in its current directory.",
            inputs=[
                io.String.Input(
                    "file_path",
                    default="",
                    display_name="File Path",
                    tooltip="Absolute path to the file.",
                ),
                io.String.Input(
                    "new_name",
                    default="",
                    display_name="New Name",
                    tooltip="New file name (with extension).",
                ),
            ],
            outputs=[
                io.String.Output(display_name="New File Path"),
            ],
        )

    @classmethod
    def execute(cls, file_path: str, new_name: str) -> io.NodeOutput:
        file_path = (file_path or "").strip()
        new_name = (new_name or "").strip()
        new_path = ""
        
        if file_path and new_name and os.path.exists(file_path):
            directory = os.path.dirname(file_path)
            new_path = os.path.join(directory, new_name)
            os.rename(file_path, new_path)
            
        return io.NodeOutput(new_path)
