"""
honda-nodes
===========

Custom node pack for ComfyUI.

This package targets ComfyUI Nodes 2.0 (Schema V3) via `comfy_api.latest`.
"""

from comfy_api.latest import ComfyExtension, io
from .nodes.text.text_concatenate import HondaTextConcatenate
from .nodes.text.text_replace import HondaTextReplace
from .nodes.text.text_split import HondaTextSplit
from .nodes.text.text_switch import HondaTextSwitch
from .nodes.text.text_case_switch import HondaTextCaseSwitch
from .nodes.text.text_preview import HondaTextPreview
from .nodes.text.text import HondaText
from .nodes.text.text_match import HondaTextMatch
from .nodes.metadata.extract_metadata import HondaExtractMetadata
from .nodes.metadata.write_metadata import HondaWriteMetadata
from .nodes.image.load_image import HondaLoadImage
from .nodes.image.save_image import HondaSaveImage
from .nodes.json.json_get_value import HondaJSONGetValue
from .nodes.json.json_set_key import HondaJSONSetKey
from .nodes.json.json_delete_key import HondaJSONDeleteKey
from .nodes.json.json_merge import HondaJSONMerge
from .nodes.json.json_preview import HondaJSONPreview
from .nodes.json.json_validate import HondaJSONValidate

class HondaNodesExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            HondaText,
            HondaTextConcatenate,
            HondaTextMatch,
            HondaTextReplace,
            HondaTextSplit,
            HondaTextSwitch,
            HondaTextCaseSwitch,
            HondaTextPreview,
            HondaExtractMetadata,
            HondaWriteMetadata,
            HondaLoadImage,
            HondaSaveImage,
            HondaJSONGetValue,
            HondaJSONSetKey,
            HondaJSONDeleteKey,
            HondaJSONMerge,
            HondaJSONPreview,
            HondaJSONValidate,
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()

# Tell ComfyUI to serve files from ./web as /extensions/honda-nodes/
# This makes web/js/text_preview.js available to the frontend.
WEB_DIRECTORY = "./web"

__all__ = ["comfy_entrypoint", "WEB_DIRECTORY"]
