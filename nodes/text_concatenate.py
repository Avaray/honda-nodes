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
                io.Combo.Input("case_mode", options=CASE_MODES, default=CASE_KEEP),
                io.String.Input("separator", default="_"),
                io.Boolean.Input("skip_empty", default=True),
                io.Autogrow.Input("texts", template=text_template),
            ],
            outputs=[
                io.String.Output(display_name="Output"),
            ],
        )

    @classmethod
    def execute(cls, case_mode, separator, skip_empty, texts) -> io.NodeOutput:
        # `texts` is a dict mapping the generated slot names (text0, text1, ...)
        # to their values, in slot order.
        values = list(texts.values())
        result = concatenate_texts(values, separator, case_mode, skip_empty)
        return io.NodeOutput(result)


class HondaNodesExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            HondaTextConcatenate,
            # Add more Honda Nodes here as the pack grows.
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()
