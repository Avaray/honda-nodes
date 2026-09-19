"""
"Text Switch" - Schema V3 node definition.
"""

from comfy_api.latest import io


class HondaTextSwitch(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextSwitch",
            display_name="🔤 Text Switch (Conditional)",
            category="⚡️ Honda Nodes/🔤 Text",
            description="Outputs one of two text strings based on a boolean condition.",
            inputs=[
                io.Boolean.Input(
                    "condition",
                    default=True,
                    display_name="Condition",
                    tooltip="If True, outputs Text A. If False, outputs Text B.",
                ),
                io.String.Input(
                    "text_a",
                    multiline=True,
                    display_name="Text A (True)",
                    tooltip="The text to output if the condition is True.",
                ),
                io.String.Input(
                    "text_b",
                    multiline=True,
                    display_name="Text B (False)",
                    tooltip="The text to output if the condition is False.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(
        cls,
        condition: bool,
        text_a: str,
        text_b: str,
    ) -> io.NodeOutput:
        result = text_a if condition else text_b
        return io.NodeOutput(result or "")
