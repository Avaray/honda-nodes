"""
"Text" - Schema V3 node definition.
"""

from comfy_api.latest import io


class HondaText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_Text",
            display_name="🔤 Text",
            category="⚡️ Honda Nodes/🔤 Text",
            description="A simple multiline text input node that outputs its content as a string.",
            inputs=[
                io.String.Input(
                    "text",
                    default="",
                    multiline=True,
                    display_name="",
                    tooltip="Enter any text here. The content will be passed to the Output socket.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(cls, text: str) -> io.NodeOutput:
        return io.NodeOutput(text or "")
