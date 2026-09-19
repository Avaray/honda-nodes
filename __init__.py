"""
honda-nodes
===========

Custom node pack for ComfyUI.

This package auto-detects which node API the running ComfyUI supports:

* If `comfy_api.latest` is available AND exposes `io.Autogrow` (this has
  shipped in mainline ComfyUI since roughly v0.6.0 / January 2026, and is
  the schema the upcoming "Nodes 2.0" Vue-based UI is built around), the
  modern V3 Schema node is used (honda_nodes/text_concatenate_v3.py).
  This is the primary, forward-looking implementation.

* Otherwise, a fully self-contained legacy V1 node is used instead
  (honda_nodes/text_concatenate_v1.py), paired with a JS extension that
  reproduces the dynamic/reorderable text-field UI by hand. This keeps
  the pack usable on older ComfyUI installs.

Either way, the node ends up registered under the same id
("Honda_TextConcatenate") and display name ("Text Concatenate"), so the
choice is invisible to the end user.
"""

WEB_DIRECTORY = "./web"

try:
    from comfy_api.latest import io as _io

    _HAS_V3 = hasattr(_io, "Autogrow")
except ImportError:
    _HAS_V3 = False

if _HAS_V3:
    from .nodes.text_concatenate_v3 import comfy_entrypoint  # noqa: F401

    __all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]
else:
    from .nodes.text_concatenate_v1 import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )

    __all__ = ["WEB_DIRECTORY", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
