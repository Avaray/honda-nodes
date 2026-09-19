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
            ],
            outputs=[
                io.String.Output(display_name="Text Pass-through"),
            ],
        )

    @classmethod
    def execute(
        cls,
        text: str,
    ) -> io.NodeOutput:
        text = text or ""
        # Returning ui={"text": [text]} tells the frontend to display the text.
        # We also pass the text through as an output so it can still be chained to other nodes.
        return io.NodeOutput(text, ui={"text": [text], "string": [text]})
