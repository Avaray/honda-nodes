import shutil
from comfy_api.latest import io

class HondaDeleteDirectory(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_DeleteDirectory",
            display_name="📂 Delete Directory",
            category="⚡️ Honda Nodes/📂 File System",
            description="Deletes a directory and all its contents.",
            inputs=[
                io.String.Input(
                    "path",
                    default="",
                    display_name="Path",
                    tooltip="Absolute path to the directory to delete.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Deleted Path"),
            ],
        )

    @classmethod
    def execute(cls, path: str) -> io.NodeOutput:
        path = (path or "").strip()
        if path:
            shutil.rmtree(path, ignore_errors=True)
        return io.NodeOutput(path)
