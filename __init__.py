"""
honda-nodes
===========

Custom node pack for ComfyUI.

This package targets ComfyUI Nodes 2.0 (Schema V3) via `comfy_api.latest`.
"""

from .nodes.text_concatenate import comfy_entrypoint

__all__ = ["comfy_entrypoint"]
