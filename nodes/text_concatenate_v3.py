"""
"Text Concatenate" - modern V3 (Schema) node definition.

This is the primary, forward-looking implementation, targeting the schema
that ComfyUI's upcoming "Nodes 2.0" (Vue-based) UI is built around. It is
selected automatically whenever the running ComfyUI exposes
`comfy_api.latest` with `io.Autogrow` support (shipped since roughly
ComfyUI v0.6.0 / January 2026) - see the package's root __init__.py.

The numbered "channels" are implemented with `io.Autogrow.TemplatePrefix`
over a connection-only STRING input (`force_input=True` - no typed widget,
socket only). This is the same built-in mechanism ComfyUI's own
`AutogrowPrefixTestNode` reference/test node uses: it grows the number of
available sockets as the user connects wires to them, from MIN_TEXT_FIELDS
up to MAX_TEXT_FIELDS - like adding a new channel to a mixing console the
moment the previous one gets plugged in.
"""

from comfy_api.latest import ComfyExtension, io

from .logic import (
    CASE_KEEP,
    CASE_MODES,
    MAX_TEXT_FIELDS,
    MIN_TEXT_FIELDS,
    concatenate_texts,
)


class HondaTextConcatenateV3(io.ComfyNode):
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
            HondaTextConcatenateV3,
            # Add more Honda Nodes here as the pack grows.
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()
