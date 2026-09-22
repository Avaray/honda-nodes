import os
from comfy_api.latest import io

class HondaCreateDirectory(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_CreateDirectory",
            display_name="📂 Create Directory",
            category="⚡️ Honda Nodes/📂 File System",
            description="Creates a directory.",
            inputs=[
                io.String.Input(
                    "path",
                    default="",
                    display_name="Path",
                    tooltip="Absolute path to the directory to create.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Path"),
            ],
        )

    @classmethod
    def execute(cls, path: str) -> io.NodeOutput:
        path = (path or "").strip()
        if path:
            os.makedirs(path, exist_ok=True)
        return io.NodeOutput(path)
