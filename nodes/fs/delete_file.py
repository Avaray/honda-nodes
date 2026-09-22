import os
from comfy_api.latest import io

class HondaDeleteFile(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_DeleteFile",
            display_name="📂 Delete File",
            category="⚡️ Honda Nodes/📂 File System",
            description="Deletes a file.",
            inputs=[
                io.String.Input(
                    "file_path",
                    default="",
                    display_name="File Path",
                    tooltip="Absolute path to the file to delete.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Deleted Path"),
            ],
        )

    @classmethod
    def execute(cls, file_path: str) -> io.NodeOutput:
        file_path = (file_path or "").strip()
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        return io.NodeOutput(file_path)
