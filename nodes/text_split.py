"""
"Text Split" - Schema V3 node definition.
"""

from comfy_api.latest import io

MAX_SPLIT_OUTPUTS = 10


class HondaTextSplit(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_TextSplit",
            display_name="🔤 Text Split",
            category="⚡️ Honda Nodes/🔤 Text",
            description="Splits a single text string into multiple text outputs based on a separator.",
            inputs=[
                io.String.Input(
                    "text",
                    force_input=True,
                    display_name="Text Input",
                    tooltip="The original text to split (must be connected from another node).",
                ),
                io.String.Input(
                    "separator",
                    default="_",
                    display_name="Separator",
                    tooltip="The character or sequence to split the text by.",
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
                io.String.Output(f"text_{i}", display_name=f"Text Output {i:02d}")
                for i in range(1, MAX_SPLIT_OUTPUTS + 1)
            ],
        )

    @classmethod
    def execute(
        cls,
        text: str,
        separator: str,
        skip_empty: bool,
        trim_whitespaces: bool,
    ) -> io.NodeOutput:
        text = text or ""
        separator = separator or "_"

        parts = text.split(separator)
        
        result_parts = []
        for p in parts:
            if trim_whitespaces:
                p = p.strip()
            if skip_empty and not p:
                continue
            result_parts.append(p)
            
        # Pad with empty strings if there are fewer parts than outputs
        while len(result_parts) < MAX_SPLIT_OUTPUTS:
            result_parts.append("")
            
        # Truncate if there are more parts than outputs
        result_parts = result_parts[:MAX_SPLIT_OUTPUTS]

        # In Schema V3, multiple outputs are usually passed positionally to NodeOutput
        return io.NodeOutput(*result_parts)
