"""
"Text Preview" - Schema V3 node definition.
"""

from comfy_api.latest import io, ui


class HondaTextPreview(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextPreview",
            display_name="🔤 Text Preview",
            category="⚡️ Honda Nodes/🔤 Text",
            description="Displays the input text directly on the node.",
            is_output_node=True,
            inputs=[
                io.String.Input(
                    "text_input",
                    force_input=True,
                    display_name="Text Input",
                    tooltip="The text you want to preview.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Text Pass-through"),
            ],
        )

    @classmethod
    def execute(
        cls,
        text_input: str,
    ) -> io.NodeOutput:
        text_input = text_input or ""
        # We rename the input socket from 'text' to 'text_input' so it doesn't collide
        # with ui.PreviewText which specifically targets a 'text' widget in the frontend.
        return io.NodeOutput(text_input, ui=ui.PreviewText(text_input))
