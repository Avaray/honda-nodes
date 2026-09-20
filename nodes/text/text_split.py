"""
"Text Split" - Schema V3 node definition.
"""

import re
import json
from comfy_api.latest import io

SPLIT_COMMA = "Comma (,)"
SPLIT_NEWLINE = "New Line (\\n)"
SPLIT_SPACE = "Space"
SPLIT_CUSTOM = "Custom String"
SPLIT_REGEX = "Custom Regex"

OUT_ARRAY = "Array / List"
OUT_CSV = "Comma-Separated (CSV)"
OUT_NEWLINE = "New Line Each"
OUT_JSON = "JSON Array"


class HondaTextSplit(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextSplit",
            display_name="🔤 Text Split",
            category="⚡️ Honda Nodes/🔤 Text",
            description="Splits a single text string and outputs it in various formats.",
            inputs=[
                io.String.Input(
                    "text",
                    force_input=True,
                    display_name="Text Input",
                    tooltip="The original text to split (must be connected from another node).",
                ),
                io.Combo.Input(
                    "split_by",
                    options=[SPLIT_COMMA, SPLIT_NEWLINE, SPLIT_SPACE, SPLIT_CUSTOM, SPLIT_REGEX],
                    default=SPLIT_COMMA,
                    display_name="Split By",
                    tooltip="What to use to split the text.",
                ),
                io.String.Input(
                    "custom_splitter",
                    default="",
                    display_name="Custom Splitter",
                    tooltip="Used only if 'Split By' is set to Custom String or Custom Regex.",
                ),
                io.Combo.Input(
                    "output_type",
                    options=[OUT_ARRAY, OUT_CSV, OUT_NEWLINE, OUT_JSON],
                    default=OUT_ARRAY,
                    display_name="Output Type",
                    tooltip="Format of the final output. Array is standard for batching. JSON is useful for API integrations.",
                ),
                io.Boolean.Input(
                    "skip_empty",
                    default=True,
                    display_name="Skip Empty Parts",
                    tooltip="If enabled, ignores any resulting text parts that are completely empty.",
                ),
                io.Boolean.Input(
                    "trim_whitespaces",
                    default=False,
                    display_name="Trim Whitespaces",
                    tooltip="If enabled, removes extra spaces from the beginning and end of each split part.",
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
        split_by: str,
        custom_splitter: str,
        output_type: str,
        skip_empty: bool,
        trim_whitespaces: bool,
    ) -> io.NodeOutput:
        text = text or ""
        is_regex = False
        splitter = ","
        
        if split_by == SPLIT_COMMA:
            splitter = ","
        elif split_by == SPLIT_NEWLINE:
            splitter = "\n"
        elif split_by == SPLIT_SPACE:
            splitter = " "
        elif split_by == SPLIT_CUSTOM:
            splitter = custom_splitter
        elif split_by == SPLIT_REGEX:
            splitter = custom_splitter
            is_regex = True
            
        if not splitter:
            parts = [text]
        else:
            if is_regex:
                try:
                    parts = re.split(splitter, text)
                except re.error as e:
                    print(f"[Honda Nodes] Invalid Regex in Text Split: {e}")
                    parts = [text]
            else:
                parts = text.split(splitter)
                
        result_parts = []
        for p in parts:
            if trim_whitespaces:
                p = p.strip()
            if skip_empty and not p:
                continue
            result_parts.append(p)
            
        if output_type == OUT_ARRAY:
            # ComfyUI natively supports python lists/tuples traversing through connections.
            final_output = result_parts
        elif output_type == OUT_CSV:
            final_output = ", ".join(result_parts)
        elif output_type == OUT_NEWLINE:
            final_output = "\n".join(result_parts)
        elif output_type == OUT_JSON:
            final_output = json.dumps(result_parts)
        else:
            final_output = result_parts
            
        return io.NodeOutput(final_output)
