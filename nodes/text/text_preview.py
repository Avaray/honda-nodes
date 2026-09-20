"""
"Text Preview" - Schema V3 node definition.

NOTE: Text preview rendering on the node body relies on ComfyUI's built-in
textPreviewWidgets frontend extension, which listens for {"text": (value,)}
in the UI output of any output node and dynamically renders it.
"""

from comfy_api.latest import io, ui


class HondaTextPreview(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextPreview",
            display_name="🔤 Text Preview",
            category="⚡️ Honda Nodes/🔤 Text",
            description="Displays the input text directly on the node body and passes it through.",
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
        # ui.PreviewText.as_dict() returns {"text": (text_input,)}.
        # ComfyUI's textPreviewWidgets frontend extension intercepts this
        # and renders the text directly on the node body for any is_output_node=True node.
        return io.NodeOutput(text_input, ui=ui.PreviewText(text_input))
