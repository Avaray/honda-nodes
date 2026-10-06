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
from .nodes.metadata.convert_metadata import HondaConvertMetadataFormat
from .nodes.image.load_image import HondaLoadImage
from .nodes.image.save_image import HondaSaveImage
from .nodes.image.preview_image import HondaPreviewImage
from .nodes.image.watermark import HondaWatermarkLoad, HondaWatermarkText
from .nodes.image.image_size import HondaImageSize
from .nodes.json.json_get_value import HondaJSONGetValue
from .nodes.json.json_set_key import HondaJSONSetKey
from .nodes.json.json_delete_key import HondaJSONDeleteKey
from .nodes.json.json_merge import HondaJSONMerge
from .nodes.json.json_preview import HondaJSONPreview
from .nodes.json.json_validate import HondaJSONValidate

# File System nodes
from .nodes.fs.directory import HondaDirectory
from .nodes.fs.create_directory import HondaCreateDirectory
from .nodes.fs.delete_directory import HondaDeleteDirectory
from .nodes.fs.list_files import HondaListFiles
from .nodes.fs.move_file import HondaMoveFile
from .nodes.fs.rename_file import HondaRenameFile
from .nodes.fs.delete_file import HondaDeleteFile
from .nodes.fs.read_file import HondaReadFile
from .nodes.fs.path_normalize import HondaPathNormalize
from .nodes.fs.path_join import HondaPathJoin

# Tools nodes
from .nodes.tools.download_files import HondaDownloadFiles
from .nodes.tools.print_to_console import HondaPrintToConsole

# Array nodes
from .nodes.array.array_from_text import HondaArrayFromText
from .nodes.array.array_to_text import HondaArrayToText
from .nodes.array.array_get_item import HondaArrayGetItem
from .nodes.array.array_slice import HondaArraySlice
from .nodes.array.array_length import HondaArrayLength
from .nodes.array.array_filter import HondaArrayFilter
from .nodes.array.array_includes import HondaArrayIncludes
from .nodes.array.array_is_empty import HondaArrayIsEmpty
from .nodes.array.array_for_each import HondaArrayForEach

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
            HondaConvertMetadataFormat,
            HondaLoadImage,
            HondaSaveImage,
            HondaPreviewImage,
            HondaWatermarkLoad,
            HondaWatermarkText,
            HondaImageSize,
            HondaJSONGetValue,
            HondaJSONSetKey,
            HondaJSONDeleteKey,
            HondaJSONMerge,
            HondaJSONPreview,
            HondaJSONValidate,
            HondaDirectory,
            HondaCreateDirectory,
            HondaDeleteDirectory,
            HondaListFiles,
            HondaMoveFile,
            HondaRenameFile,
            HondaDeleteFile,
            HondaReadFile,
            HondaPathNormalize,
            HondaPathJoin,
            HondaDownloadFiles,
            HondaPrintToConsole,
            HondaArrayFromText,
            HondaArrayToText,
            HondaArrayGetItem,
            HondaArraySlice,
            HondaArrayLength,
            HondaArrayFilter,
            HondaArrayIncludes,
            HondaArrayIsEmpty,
            HondaArrayForEach,
        ]


async def comfy_entrypoint() -> HondaNodesExtension:
    return HondaNodesExtension()

# Tell ComfyUI to serve files from ./web as /extensions/honda-nodes/
# This makes web/js/text_preview.js available to the frontend.
WEB_DIRECTORY = "./web"

__all__ = ["comfy_entrypoint", "WEB_DIRECTORY"]
