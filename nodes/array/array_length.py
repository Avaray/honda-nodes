"""
"Array Length" - Schema V3 node definition.

Returns the number of items in a newline-separated array.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
"""

from comfy_api.latest import io


class HondaArrayLength(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayLength",
            display_name="📋 Array Length",
            category="⚡️ Honda Nodes/📋 Array",
            description="Returns the number of items in a newline-separated array.",
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string.",
                ),
                io.Boolean.Input(
                    "count_empty",
                    default=False,
                    display_name="Count Empty",
                    tooltip="If disabled, empty lines are not counted.",
                ),
            ],
            outputs=[
                io.Int.Output(display_name="Count"),
            ],
        )

    @classmethod
    def execute(cls, array: str, count_empty: bool) -> io.NodeOutput:
        array = array or ""
        items = array.split("\n")
        if not count_empty:
            items = [item for item in items if item.strip()]
        return io.NodeOutput(len(items))
