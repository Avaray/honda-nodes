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
                # This widget MUST be named "text" — ui.PreviewText.as_dict() returns
                # {"text": (value,)} and the Vue frontend looks for a widget with this exact name
                # to render the text preview on the node body.
                # It is readonly (the user should not type here), it only receives values from
                # the backend via the ui output dictionary after execution.
                io.String.Input(
                    "text",
                    default="",
                    multiline=True,
                    display_name="",
                    tooltip="Preview of the connected text. Updated automatically after execution.",
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
        text: str,
    ) -> io.NodeOutput:
        text_input = text_input or ""
        # ui.PreviewText serializes to {"text": (text_input,)}, which the frontend maps
        # to the "text" widget declared above, updating it reactively after execution.
        return io.NodeOutput(text_input, ui=ui.PreviewText(text_input))
