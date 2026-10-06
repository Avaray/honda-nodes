"""
"Array Is Empty" - Schema V3 node definition.

Returns True if the array contains no items (empty lines are ignored).
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
"""

from comfy_api.latest import io


class HondaArrayIsEmpty(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayIsEmpty",
            display_name="📋 Array Is Empty",
            category="⚡️ Honda Nodes/📋 Array",
            description="Returns True if the array contains no items (ignoring empty lines).",
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string.",
                ),
            ],
            outputs=[
                io.Boolean.Output(display_name="Result"),
                io.Int.Output(display_name="Count"),
            ],
        )

    @classmethod
    def execute(cls, array: str) -> io.NodeOutput:
        array = array or ""
        items = [item for item in array.split("\n") if item.strip()]
        return io.NodeOutput(len(items) == 0, len(items))
