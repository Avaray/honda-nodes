from comfy_api.latest import io


class HondaPrintToConsole(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_PrintToConsole",
            display_name="🛠️ Print to Console",
            category="⚡️ Honda Nodes/🛠️ Tools",
            description="Prints a value to the ComfyUI server console. Useful for debugging workflows.",
            is_output_node=True,
            inputs=[
                io.String.Input(
                    "value",
                    multiline=True,
                    force_input=True,
                    display_name="Value",
                    tooltip="The text to print to the server console.",
                ),
                io.String.Input(
                    "label",
                    default="",
                    display_name="Label",
                    tooltip="Optional label prepended to the output, e.g. '[DEBUG]'.",
                ),
                io.Boolean.Input(
                    "enabled",
                    default=True,
                    display_name="Enabled",
                    tooltip="When disabled, this node does nothing.",
                ),
            ],
            outputs=[],
        )

    @classmethod
    def execute(cls, value: str, label: str = "", enabled: bool = True) -> io.NodeOutput:
        if enabled:
            if label:
                print(f"[Honda] {label}: {value}")
            else:
                print(f"[Honda] {value}")
        return io.NodeOutput()
