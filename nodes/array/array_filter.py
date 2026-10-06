"""
"Array Filter" - Schema V3 node definition.

Filters a newline-separated array by removing empty items, duplicates, and/or items
matching (or not matching) a glob pattern.
Arrays in this pack are represented as newline-separated strings (e.g. "item1\nitem2\nitem3").
Filters are applied in order: trim → remove_empty → remove_duplicates → pattern.
"""

import fnmatch
from comfy_api.latest import io


class HondaArrayFilter(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ArrayFilter",
            display_name="📋 Array Filter",
            category="⚡️ Honda Nodes/📋 Array",
            description=(
                "Filters a newline-separated array. Can remove empty items, duplicates, "
                "and items matching or not matching a pattern."
            ),
            inputs=[
                io.String.Input(
                    "array",
                    multiline=True,
                    force_input=True,
                    display_name="Array",
                    tooltip="Newline-separated array string.",
                ),
                io.Boolean.Input(
                    "remove_empty",
                    default=True,
                    display_name="Remove Empty",
                    tooltip="Remove empty lines from the array.",
                ),
                io.Boolean.Input(
                    "remove_duplicates",
                    default=False,
                    display_name="Remove Duplicates",
                    tooltip="Remove duplicate items, keeping the first occurrence.",
                ),
                io.String.Input(
                    "pattern",
                    default="",
                    display_name="Pattern",
                    tooltip=(
                        "Optional glob pattern. Items matching the pattern are kept "
                        "(or removed if Invert Pattern is enabled)."
                    ),
                ),
                io.Boolean.Input(
                    "invert_pattern",
                    default=False,
                    display_name="Invert Pattern",
                    tooltip="If enabled, items matching the pattern are removed instead of kept.",
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
    def execute(
        cls,
        array: str,
        remove_empty: bool,
        remove_duplicates: bool,
        pattern: str,
        invert_pattern: bool,
        trim_items: bool,
    ) -> io.NodeOutput:
        array = array or ""
        items = array.split("\n")

        # 1. Trim
        if trim_items:
            items = [item.strip() for item in items]

        # 2. Remove empty
        if remove_empty:
            items = [item for item in items if item]

        # 3. Remove duplicates (preserve order)
        if remove_duplicates:
            seen = set()
            deduped = []
            for item in items:
                if item not in seen:
                    seen.add(item)
                    deduped.append(item)
            items = deduped

        # 4. Pattern filter
        pattern = (pattern or "").strip()
        if pattern:
            if invert_pattern:
                items = [item for item in items if not fnmatch.fnmatch(item, pattern)]
            else:
                items = [item for item in items if fnmatch.fnmatch(item, pattern)]

        return io.NodeOutput("\n".join(items), len(items))
