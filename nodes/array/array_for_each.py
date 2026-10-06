"""
"Array For Each" - Schema V3 node definition.

Given a newline-separated array and a zero-based index, outputs the item at that index.
Use with a counter or loop controller to iterate through all items.
Also outputs the total count and whether the current index is the last one.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
"""

from comfy_api.latest import io


class HondaArrayForEach(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayForEach",
            display_name="📋 Array For Each",
            category="⚡️ Honda Nodes/📋 Array",
            description=(
                "Given a newline-separated array and a zero-based index, outputs the item at that index. "
                "Use with a counter or loop controller to iterate through all items. "
                "Also outputs the total count and whether the index is the last one."
            ),
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
                    tooltip="Zero-based index of the current iteration.",
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
                io.Boolean.Output(display_name="Is Last"),
            ],
        )

    @classmethod
    def execute(cls, array: str, index: int, trim_items: bool) -> io.NodeOutput:
        array = array or ""
        items = array.split("\n")
        if trim_items:
            items = [item.strip() for item in items]
        count = len(items)
        if index < 0 or index >= count:
            raise RuntimeError(
                f"Index {index} is out of range for array of length {count}."
            )
        is_last = index == count - 1
        return io.NodeOutput(items[index], count, is_last)
