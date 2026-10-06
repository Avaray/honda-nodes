"""
"Array To Text" - Schema V3 node definition.

Joins a newline-separated array into a single text string using a configurable separator.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
"""

from comfy_api.latest import io


class HondaArrayToText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayToText",
            display_name="📋 Array To Text",
            category="⚡️ Honda Nodes/📋 Array",
            description="Joins a newline-separated array into a single text string using a configurable separator.",
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string to join.",
                ),
                io.String.Input(
                    "separator",
                    default=", ",
                    display_name="Separator",
                    tooltip="Separator placed between each item in the output text.",
                ),
                io.Boolean.Input(
                    "trim_items",
                    default=True,
                    display_name="Trim Items",
                    tooltip="Strip leading and trailing whitespace from each item before joining.",
                ),
                io.Boolean.Input(
                    "remove_empty",
                    default=True,
                    display_name="Remove Empty",
                    tooltip="Drop empty lines before joining.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Text"),
                io.Int.Output(display_name="Count"),
            ],
        )

    @classmethod
    def execute(cls, array: str, separator: str, trim_items: bool, remove_empty: bool) -> io.NodeOutput:
        array = array or ""
        separator = separator if separator is not None else ", "
        items = array.split("\n")
        if trim_items:
            items = [item.strip() for item in items]
        if remove_empty:
            items = [item for item in items if item]
        return io.NodeOutput(separator.join(items), len(items))
