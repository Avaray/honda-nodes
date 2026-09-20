"""
"Text Case Switch" - Schema V3 node definition.

Works like a switch statement in programming. Evaluates `match_text` against
several cases and returns the corresponding output, falling back to a default.
"""

from comfy_api.latest import io


class HondaTextCaseSwitch(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextCaseSwitch",
            display_name="🔤 Text Case Switch",
            category="⚡️ Honda Nodes/🔤 Text",
            description="Evaluates a text against multiple cases and returns the corresponding output.",
            inputs=[
                io.String.Input(
                    "match_text",
                    force_input=True,
                    display_name="Match Text",
                    tooltip="The base text to evaluate.",
                ),
                io.String.Input(
                    "default_output",
                    multiline=True,
                    display_name="Default Output",
                    tooltip="Output returned if none of the cases match.",
                ),
                io.Boolean.Input(
                    "ignore_case",
                    default=True,
                    display_name="Ignore Case",
                    tooltip="If enabled, ignores uppercase/lowercase differences when matching.",
                ),
                io.Boolean.Input(
                    "match_substring",
                    default=False,
                    display_name="Match Substring",
                    tooltip="If enabled, matches if 'Case X' is anywhere inside the Match Text (like 'contains'). If disabled, matches only exact string.",
                ),
                # Case 1
                io.String.Input("case_1", default="", display_name="Case 1"),
                io.String.Input("output_1", multiline=True, default="", display_name="Output 1"),
                # Case 2
                io.String.Input("case_2", default="", display_name="Case 2"),
                io.String.Input("output_2", multiline=True, default="", display_name="Output 2"),
                # Case 3
                io.String.Input("case_3", default="", display_name="Case 3"),
                io.String.Input("output_3", multiline=True, default="", display_name="Output 3"),
                # Case 4
                io.String.Input("case_4", default="", display_name="Case 4"),
                io.String.Input("output_4", multiline=True, default="", display_name="Output 4"),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(
        cls,
        match_text: str,
        default_output: str,
        ignore_case: bool,
        match_substring: bool,
        case_1: str,
        output_1: str,
        case_2: str,
        output_2: str,
        case_3: str,
        output_3: str,
        case_4: str,
        output_4: str,
    ) -> io.NodeOutput:
        match_text = match_text or ""
        default_output = default_output or ""
        
        # Prepare haystack
        haystack = match_text.lower() if ignore_case else match_text

        # Group cases into a list of tuples for easy iteration
        cases = [
            (case_1, output_1),
            (case_2, output_2),
            (case_3, output_3),
            (case_4, output_4),
        ]

        for case_val, out_val in cases:
            # Skip empty cases (so we don't accidentally match empty string)
            if not case_val:
                continue

            needle = case_val.lower() if ignore_case else case_val

            if match_substring:
                if needle in haystack:
                    return io.NodeOutput(out_val or "")
            else:
                if needle == haystack:
                    return io.NodeOutput(out_val or "")

        # If no cases matched, return default
        return io.NodeOutput(default_output)
