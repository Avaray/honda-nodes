"""
"Text Concatenate" - legacy V1 node definition.

Used automatically as a fallback when the running ComfyUI does not expose
`comfy_api.latest` (i.e. no V3 schema / Autogrow support yet). See the
package's root __init__.py for the selection logic.

The numbered "channels" are plain connection-only STRING inputs
(`forceInput: True` - no typed widget, socket only), declared as a fixed
pool of MAX_TEXT_FIELDS optional inputs (text_1 .. text_99). The companion
JS extension (web/js/text_concatenate.js) trims the node down to a single
empty channel on creation and then grows/shrinks the visible sockets as
the user plugs/unplugs wires, so it behaves like a mixing console: connect
something to the last empty channel and a fresh one appears next to it.
"""

from .logic import (
    CASE_KEEP,
    CASE_MODES,
    MAX_TEXT_FIELDS,
    concatenate_texts,
)


class HondaTextConcatenate:
    """Combines 1-99 connected text strings into a single string."""

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            f"text_{i}": ("STRING", {"forceInput": True})
            for i in range(1, MAX_TEXT_FIELDS + 1)
        }
        return {
            "required": {
                "case_mode": (CASE_MODES, {"default": CASE_KEEP}),
                "separator": ("STRING", {"multiline": False, "default": "_"}),
                "skip_empty": ("BOOLEAN", {"default": True}),
            },
            "optional": optional,
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"
    CATEGORY = "Honda Nodes/Text"
    DESCRIPTION = (
        "Combines 1 to 99 connected text channels into one string using a "
        "chosen separator, with optional forced UPPERCASE/lowercase. "
        "Channels are plug-in sockets, not typed fields - connect a STRING "
        "output from another node to each channel you want to use."
    )

    def execute(self, case_mode, separator, skip_empty, **kwargs):
        # None = channel not connected at all; "" = connected but empty.
        # concatenate_texts() tells these apart (see logic.py).
        texts = [kwargs.get(f"text_{i}", None) for i in range(1, MAX_TEXT_FIELDS + 1)]
        result = concatenate_texts(texts, separator, case_mode, skip_empty)
        return (result,)


NODE_CLASS_MAPPINGS = {
    "Honda_TextConcatenate": HondaTextConcatenate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Honda_TextConcatenate": "Text Concatenate",
}
