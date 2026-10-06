"""
"Array Get Item" - Schema V3 node definition.

Returns the element at a given index from a newline-separated array.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
Supports negative indices (e.g. -1 for last item).
"""

from comfy_api.latest import io


class HondaArrayGetItem(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayGetItem",
            display_name="📋 Array Get Item",
            category="⚡️ Honda Nodes/📋 Array",
            description="Returns the element at a given index from a newline-separated array. Supports negative indices (e.g. -1 for last).",
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string.",
                ),
                io.Int.Input(
                    "index",
                    default=0,
                    display_name="Index",
                    tooltip="Zero-based index of the item to retrieve. Negative indices count from the end.",
                ),
                io.Boolean.Input(
                    "trim_items",
                    default=True,
                    display_name="Trim Items",
                    tooltip="Strip leading and trailing whitespace from each item.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Item"),
                io.Int.Output(display_name="Count"),
            ],
        )

    @classmethod
    def execute(cls, array: str, index: int, trim_items: bool) -> io.NodeOutput:
        array = array or ""
        items = array.split("\n")
        if trim_items:
            items = [item.strip() for item in items]
        count = len(items)
        if index < -count or index >= count:
            raise RuntimeError(
                f"Index {index} is out of range for array of length {count}."
            )
        return io.NodeOutput(items[index], count)
