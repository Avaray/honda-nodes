"""
"Text Preview" - Schema V3 node definition.
"""

from comfy_api.latest import io


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
                    "text",
                    force_input=True,
                    display_name="Text Input",
                    tooltip="The text you want to preview.",
                ),
                io.String.Input(
                    "text_preview",
                    default="",
                    multiline=True,
                    display_name="Preview",
                    tooltip="The previewed text will appear here after execution.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Text Pass-through"),
            ],
        )

    @classmethod
    def execute(
        cls,
        text: str,
        text_preview: str,
    ) -> io.NodeOutput:
        text = text or ""
        # In Schema V3, returning the value for a widget in the 'ui' dict updates it in the Vue frontend.
        return io.NodeOutput(text, ui={"text_preview": [text]})
