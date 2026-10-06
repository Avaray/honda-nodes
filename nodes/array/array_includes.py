"""
"Array Includes" - Schema V3 node definition.

Checks whether a value exists in a newline-separated array.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
"""

from comfy_api.latest import io


class HondaArrayIncludes(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayIncludes",
            display_name="📋 Array Includes",
            category="⚡️ Honda Nodes/📋 Array",
            description="Checks whether a value exists in a newline-separated array.",
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string.",
                ),
                io.String.Input(
                    "value",
                    force_input=True,
                    display_name="Value",
                    tooltip="The value to search for in the array.",
                ),
                io.Boolean.Input(
                    "case_sensitive",
                    default=True,
                    display_name="Case Sensitive",
                    tooltip="If disabled, comparison is case-insensitive.",
                ),
                io.Boolean.Input(
                    "trim_items",
                    default=True,
                    display_name="Trim Items",
                    tooltip="Strip leading and trailing whitespace from each item before comparing.",
                ),
            ],
            outputs=[
                io.Boolean.Output(display_name="Result"),
            ],
        )

    @classmethod
    def execute(cls, array: str, value: str, case_sensitive: bool, trim_items: bool) -> io.NodeOutput:
        array = array or ""
        value = value or ""
        items = array.split("\n")
        if trim_items:
            items = [item.strip() for item in items]
        if case_sensitive:
            result = value in items
        else:
            value_lower = value.lower()
            result = any(item.lower() == value_lower for item in items)
        return io.NodeOutput(result)
