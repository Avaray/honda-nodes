"""
"Text Case Switch" - Schema V3 node definition.

Works like a switch statement in programming. Evaluates `match_text` against
a user-defined list of cases (written one per line) and returns the
corresponding output, falling back to a default.

Each line in the 'Cases' field follows the format:
    <case_value> | <output_value>

Lines that do not contain the separator are silently ignored.
Empty lines are ignored too.

Example:
    photo | realistic photography, shot on Canon 5D
    anime | anime style illustration, cel shading
    painting | oil painting on canvas

The separator character can be changed in the 'Separator' field.
"""

from comfy_api.latest import io


class HondaTextCaseSwitch(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextCaseSwitch",
            display_name="🔤 Text Case Switch",
            category="⚡️ Honda Nodes/🔤 Text",
            description=(
                "Evaluates a text against a list of cases and returns the corresponding output. "
                "Write one case per line in the format: case | output. "
                "Falls back to 'Default Output' if no case matches."
            ),
            inputs=[
                io.String.Input(
                    "match_text",
                    force_input=True,
                    display_name="Match Text",
                    tooltip="The base text to evaluate against the cases.",
                ),
                io.String.Input(
                    "cases",
                    multiline=True,
                    default="photo | realistic photography\nanime | anime illustration style",
                    display_name="Cases",
                    tooltip=(
                        "One case per line, in the format: case | output\n"
                        "Example:\n"
                        "  photo | realistic photography\n"
                        "  anime | anime illustration style\n"
                        "Lines without the separator are ignored."
                    ),
                ),
                io.String.Input(
                    "default_output",
                    multiline=True,
                    default="",
                    display_name="Default Output",
                    tooltip="Output returned if none of the cases match.",
                ),
                io.String.Input(
                    "separator",
                    default="|",
                    display_name="Separator",
                    tooltip=(
                        "The character (or string) that divides the case value "
                        "from its output value in each line. Default is '|'."
                    ),
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
                    tooltip=(
                        "If enabled, a case matches whenever it appears anywhere inside the "
                        "Match Text (like 'contains'). If disabled, only exact matches count."
                    ),
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
                io.Boolean.Output(display_name="Matched"),
            ],
        )

    @classmethod
    def execute(
        cls,
        match_text: str,
        cases: str,
        default_output: str,
        separator: str,
        ignore_case: bool,
        match_substring: bool,
    ) -> io.NodeOutput:
        match_text = match_text or ""
        cases = cases or ""
        default_output = default_output or ""
        separator = separator or "|"

        haystack = match_text.lower() if ignore_case else match_text

        for raw_line in cases.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Skip lines that don't contain the separator
            sep_idx = line.find(separator)
            if sep_idx == -1:
                continue

            case_val = line[:sep_idx].strip()
            out_val = line[sep_idx + len(separator):].strip()

            if not case_val:
                continue

            needle = case_val.lower() if ignore_case else case_val

            if match_substring:
                matched = needle in haystack
            else:
                matched = needle == haystack

            if matched:
                return io.NodeOutput(out_val, True)

        return io.NodeOutput(default_output, False)
