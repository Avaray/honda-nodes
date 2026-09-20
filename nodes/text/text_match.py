"""
"Text Match" - Schema V3 node definition.

Returns True if the pattern is found in the input text, False otherwise.
Supports both literal string matching and Python Regular Expressions.
"""

import re
from comfy_api.latest import io


class HondaTextMatch(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextMatch",
            display_name="🔤 Text Match",
            category="⚡️ Honda Nodes/🔤 Text",
            description=(
                "Checks whether a pattern exists in the input text and returns True or False. "
                "Supports both literal string matching and Python Regular Expressions."
            ),
            inputs=[
                io.String.Input(
                    "text_input",
                    force_input=True,
                    display_name="Text Input",
                    tooltip="The text to search within (must be connected from another node).",
                ),
                io.String.Input(
                    "pattern",
                    default="",
                    display_name="Pattern",
                    tooltip="The string or regex pattern to search for.",
                ),
                io.Boolean.Input(
                    "use_regex",
                    default=False,
                    display_name="Use Regex",
                    tooltip=(
                        "If enabled, treats the 'Pattern' field as a Python Regular Expression. "
                        "Uses Python's re module (re.search). "
                        "Example: r'\\d+' matches one or more digits."
                    ),
                ),
                io.Boolean.Input(
                    "ignore_case",
                    default=False,
                    display_name="Ignore Case",
                    tooltip="If enabled, the search will be case-insensitive.",
                ),
                io.Boolean.Input(
                    "full_match",
                    default=False,
                    display_name="Full Match",
                    tooltip=(
                        "If enabled, the pattern must match the entire text (re.fullmatch / exact equality). "
                        "If disabled, the pattern only needs to appear anywhere in the text (re.search / substring)."
                    ),
                ),
            ],
            outputs=[
                io.Boolean.Output(display_name="Match"),
                io.String.Output(display_name="Matched Text"),
            ],
        )

    @classmethod
    def execute(
        cls,
        text_input: str,
        pattern: str,
        use_regex: bool,
        ignore_case: bool,
        full_match: bool,
    ) -> io.NodeOutput:
        text_input = text_input or ""
        pattern = pattern or ""

        if not pattern:
            # No pattern — never matches
            return io.NodeOutput(False, "")

        matched = False
        matched_text = ""

        if use_regex:
            flags = re.IGNORECASE if ignore_case else 0
            try:
                fn = re.fullmatch if full_match else re.search
                m = fn(pattern, text_input, flags=flags)
                matched = m is not None
                matched_text = m.group(0) if m else ""
            except re.error as e:
                print(f"[Honda Nodes] Invalid Regex in Text Match: {e}")
                matched = False
                matched_text = ""
        else:
            # Literal string match
            haystack = text_input if not ignore_case else text_input.lower()
            needle = pattern if not ignore_case else pattern.lower()

            if full_match:
                matched = haystack == needle
                matched_text = text_input if matched else ""
            else:
                matched = needle in haystack
                # Find and return the original-case slice if case-insensitive
                if matched:
                    idx = haystack.find(needle)
                    matched_text = text_input[idx: idx + len(pattern)]
                else:
                    matched_text = ""

        return io.NodeOutput(matched, matched_text)
