"""
"JSON Preview" - Schema V3 node definition.

Displays a JSON string as a collapsible tree in the UI.
"""

from comfy_api.latest import io


class HondaJSONPreview(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_JSONPreview",
            display_name="👀 JSON Preview",
            category="⚡️ Honda Nodes/🔣 JSON",
            description="Displays the input JSON as an interactive, collapsible tree on the node body.",
            is_output_node=True,
            inputs=[
                io.String.Input(
                    "json_input",
                    force_input=True,
                    display_name="JSON String",
                    tooltip="The JSON string you want to preview.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="JSON Pass-through"),
            ],
        )

    @classmethod
    def execute(cls, json_input: str) -> io.NodeOutput:
        json_input = json_input or "{}"
        
        # We pass it to the UI inside a dictionary, which our frontend JS will intercept.
        # "json_tree" is the key we'll look for in message.json_tree
        return io.NodeOutput(json_input, ui={"json_tree": (json_input,)})
