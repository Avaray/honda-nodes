"""
honda-nodes
===========

Custom node pack for ComfyUI.

This package targets ComfyUI Nodes 2.0 (Schema V3) via `comfy_api.latest`.
"""

from comfy_api.latest import ComfyExtension, io
from .nodes.text_concatenate import HondaTextConcatenate
from .nodes.text_replace import HondaTextReplace
from .nodes.text_split import HondaTextSplit
from .nodes.text_switch import HondaTextSwitch
from .nodes.text_preview import HondaTextPreview
from .nodes.text import HondaText


class HondaNodesExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            HondaText,
            HondaTextConcatenate,
            HondaTextReplace,
            HondaTextSplit,
            HondaTextSwitch,
            HondaTextPreview,
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()

# Tell ComfyUI to serve files from ./web as /extensions/honda-nodes/
# This makes web/js/text_preview.js available to the frontend.
WEB_DIRECTORY = "./web"

__all__ = ["comfy_entrypoint", "WEB_DIRECTORY"]
