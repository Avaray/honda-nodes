"""
"Array From Text" - Schema V3 node definition.

Splits a text string into a newline-separated array using a configurable separator.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
"""

from comfy_api.latest import io


class HondaArrayFromText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayFromText",
            display_name="📋 Array From Text",
            category="⚡️ Honda Nodes/📋 Array",
            description="Splits a text string into an array (newline-separated) using a configurable separator.",
            inputs=[
                io.String.Input(
                    "text",
                    multiline=True,
                    force_input=True,
                    display_name="Text",
                    tooltip="The text to split into array items.",
                ),
                io.String.Input(
                    "separator",
                    default=",",
                    display_name="Separator",
                    tooltip="Separator character(s) used to split the text.",
                ),
                io.Boolean.Input(
                    "trim_items",
                    default=True,
                    display_name="Trim Items",
                    tooltip="Strip leading and trailing whitespace from each item.",
                ),
                io.Boolean.Input(
                    "remove_empty",
                    default=True,
                    display_name="Remove Empty",
                    tooltip="Drop empty items after splitting.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Array"),
                io.Int.Output(display_name="Count"),
            ],
        )

    @classmethod
    def execute(cls, text: str, separator: str, trim_items: bool, remove_empty: bool) -> io.NodeOutput:
        text = text or ""
        separator = separator or ","
        items = text.split(separator)
        if trim_items:
            items = [item.strip() for item in items]
        if remove_empty:
            items = [item for item in items if item]
        return io.NodeOutput("\n".join(items), len(items))
