"""
honda-nodes
===========

Custom node pack for ComfyUI.

This package targets ComfyUI Nodes 2.0 (Schema V3) via `comfy_api.latest`.
"""

from comfy_api.latest import ComfyExtension, io
from .nodes.text_concatenate import HondaTextConcatenate
from .nodes.text_replace import HondaTextReplace


class HondaNodesExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            HondaTextConcatenate,
            HondaTextReplace,
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()

__all__ = ["comfy_entrypoint"]
