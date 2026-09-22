import shutil
import os
from comfy_api.latest import io

class HondaMoveFile(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_MoveFile",
            display_name="📂 Move File",
            category="⚡️ Honda Nodes/📂 File System",
            description="Moves a file to a new destination.",
            inputs=[
                io.String.Input(
                    "source_path",
                    default="",
                    display_name="Source Path",
                ),
                io.String.Input(
                    "destination_path",
                    default="",
                    display_name="Destination Path",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Destination Path"),
            ],
        )

    @classmethod
    def execute(cls, source_path: str, destination_path: str) -> io.NodeOutput:
        source_path = (source_path or "").strip()
        destination_path = (destination_path or "").strip()
        
        if source_path and destination_path and os.path.exists(source_path):
            dest_dir = os.path.dirname(destination_path)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            shutil.move(source_path, destination_path)
            
        return io.NodeOutput(destination_path)
