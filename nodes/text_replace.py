"""
"Text Replace" - Schema V3 node definition.
"""

import re
from comfy_api.latest import io


class HondaTextReplace(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextReplace",
            display_name="Text Replace",
            category="Honda Nodes/Text",
            description="Replaces occurrences of a string or regular expression in the input text.",
            inputs=[
                io.String.Input(
                    "text",
                    force_input=True,
                    display_name="Text Input",
                    tooltip="The original text to modify (must be connected from another node).",
                ),
                io.String.Input(
                    "find",
                    default="",
                    display_name="Find",
                    tooltip="The text or regex pattern to search for.",
                ),
                io.String.Input(
                    "replace_with",
                    default="",
                    display_name="Replace With",
                    tooltip="The text to replace matches with.",
                ),
                io.Boolean.Input(
                    "use_regex",
                    default=False,
                    display_name="Use Regex",
                    tooltip="If enabled, treats the 'Find' field as a Python Regular Expression.",
                ),
                io.Boolean.Input(
                    "ignore_case",
                    default=False,
                    display_name="Ignore Case",
                    tooltip="If enabled, the search will be case-insensitive.",
                ),
                io.Boolean.Input(
                    "replace_all",
                    default=True,
                    display_name="Replace All",
                    tooltip="If enabled, replaces all occurrences. If disabled, replaces only the first occurrence.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(
        cls,
        text: str,
        find: str,
        replace_with: str,
        use_regex: bool,
        ignore_case: bool,
        replace_all: bool,
    ) -> io.NodeOutput:
        if not find:
            return io.NodeOutput(text or "")

        count = 0 if replace_all else 1

        if use_regex:
            flags = re.IGNORECASE if ignore_case else 0
            try:
                result = re.sub(find, replace_with, text or "", count=count, flags=flags)
            except re.error as e:
                print(f"[Honda Nodes] Invalid Regex in Text Replace: {e}")
                result = text or ""
        else:
            if ignore_case:
                flags = re.IGNORECASE
                pattern = re.escape(find)
                # re.sub with escaped pattern behaves identically to case-insensitive literal replace,
                # but we must also escape the replacement string so things like \1 aren't parsed!
                # Or we can pass a lambda that just returns the literal replacement string.
                result = re.sub(pattern, lambda m: replace_with, text or "", count=count, flags=flags)
            else:
                if count == 0:
                    result = (text or "").replace(find, replace_with)
                else:
                    result = (text or "").replace(find, replace_with, count)

        return io.NodeOutput(result)
