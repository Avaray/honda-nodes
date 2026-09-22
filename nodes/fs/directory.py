from comfy_api.latest import io

class HondaDirectory(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_Directory",
            display_name="📂 Directory",
            category="⚡️ Honda Nodes/📂 File System",
            description="Specifies a directory path.",
            inputs=[
                io.String.Input(
                    "path",
                    default="",
                    display_name="Path",
                    tooltip="Absolute path to a directory.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Path"),
            ],
        )

    @classmethod
    def execute(cls, path: str) -> io.NodeOutput:
        return io.NodeOutput((path or "").strip())
