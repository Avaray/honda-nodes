"""
"Text Concatenate" - modern V3 (Schema) node definition.

This is the primary implementation, targeting the schema
that ComfyUI's upcoming "Nodes 2.0" (Vue-based) UI is built around.
"""

from comfy_api.latest import ComfyExtension, io

from .logic import (
    CASE_KEEP,
    CASE_MODES,
    MAX_TEXT_FIELDS,
    MIN_TEXT_FIELDS,
    concatenate_texts,
)


class HondaTextConcatenate(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        text_template = io.Autogrow.TemplateNames(
            input=io.String.Input("text", force_input=True),
            names=[f"Text Input {i:02d}" for i in range(1, MAX_TEXT_FIELDS + 1)],
        )
        return io.Schema(
            node_id="Honda_TextConcatenate",
            display_name="Text Concatenate",
            category="Honda Nodes/Text",
            description=(
                "Combines 1 to 99 connected text channels into one string "
                "using a chosen separator, with optional forced "
                "UPPERCASE/lowercase. Channels are plug-in sockets, not "
                "typed fields - connect a STRING output from another node "
                "to each channel you want to use."
            ),
            inputs=[
                io.Combo.Input(
                    "case_mode",
                    options=CASE_MODES,
                    default=CASE_KEEP,
                    display_name="Case Mode",
                    tooltip="Changes the capitalization of the entire final output. 'Capitalize Each Word' will make the first letter of every word uppercase.",
                ),
                io.String.Input(
                    "separator",
                    default="_",
                    display_name="Separator",
                    tooltip="Text inserted between each connected text channel (and also before the suffix and after the prefix).",
                ),
                io.String.Input(
                    "replace_whitespaces_with",
                    default="_",
                    display_name="Replace With",
                    tooltip="Symbol to replace whitespaces with. By default it uses an underscore. To disable this and keep spaces, type a single space here.",
                ),
                io.String.Input(
                    "global_prefix",
                    default="",
                    display_name="Global Prefix",
                    tooltip="Text added to the very beginning of the final string. The separator will be placed between this prefix and the first text channel.",
                ),
                io.String.Input(
                    "global_suffix",
                    default="",
                    display_name="Global Suffix",
                    tooltip="Text added to the very end of the final string. The separator will be placed between the last text channel and this suffix.",
                ),
                io.Boolean.Input(
                    "skip_empty",
                    default=True,
                    display_name="Skip Empty Inputs",
                    tooltip="If enabled, ignores any connected text channels that are completely empty so they don't produce extra separators.",
                ),
                io.Boolean.Input(
                    "trim_whitespaces",
                    default=False,
                    display_name="Trim Whitespaces",
                    tooltip="If enabled, automatically removes extra spaces from the beginning and end of each text channel, and collapses multiple spaces into a single space before joining them.",
                ),
                io.Autogrow.Input(
                    "texts",
                    template=text_template,
                    display_name="Texts",
                    tooltip="Connect text outputs to these slots. They will be combined in order.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(
        cls,
        case_mode,
        separator,
        replace_whitespaces_with,
        global_prefix,
        global_suffix,
        skip_empty,
        trim_whitespaces,
        texts,
    ) -> io.NodeOutput:
        # `texts` is a dict mapping the generated slot names (text0, text1, ...)
        # to their values, in slot order.
        values = list(texts.values())
        result = concatenate_texts(
            values,
            separator,
            case_mode,
            skip_empty,
            trim_whitespaces,
            replace_whitespaces_with,
            global_prefix,
            global_suffix,
        )
        return io.NodeOutput(result)


class HondaNodesExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            HondaTextConcatenate,
            # Add more Honda Nodes here as the pack grows.
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()
