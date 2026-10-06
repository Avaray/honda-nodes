"""
"Array Slice" - Schema V3 node definition.

Returns a slice of a newline-separated array.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
Supports negative indices. When end == -1, slices to the end of the array.
"""

from comfy_api.latest import io


class HondaArraySlice(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArraySlice",
            display_name="📋 Array Slice",
            category="⚡️ Honda Nodes/📋 Array",
            description="Returns a slice of a newline-separated array. Supports negative indices.",
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string.",
                ),
                io.Int.Input(
                    "start",
                    default=0,
                    display_name="Start",
                    tooltip="Inclusive start index. Supports negative indices.",
                ),
                io.Int.Input(
                    "end",
                    default=-1,
                    display_name="End",
                    tooltip="Exclusive end index. Use -1 for the end of the array.",
                ),
                io.Int.Input(
                    "step",
                    default=1,
                    display_name="Step",
                    tooltip="Step between items in the slice.",
                ),
                io.Boolean.Input(
                    "trim_items",
                    default=True,
                    display_name="Trim Items",
                    tooltip="Strip leading and trailing whitespace from each item.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Array"),
                io.Int.Output(display_name="Count"),
            ],
        )

    @classmethod
    def execute(cls, array: str, start: int, end: int, step: int, trim_items: bool) -> io.NodeOutput:
        array = array or ""
        items = array.split("\n")
        if trim_items:
            items = [item.strip() for item in items]
        # Treat end == -1 as None (slice to end of array)
        slice_end = None if end == -1 else end
        sliced = items[start:slice_end:step]
        return io.NodeOutput("\n".join(sliced), len(sliced))
