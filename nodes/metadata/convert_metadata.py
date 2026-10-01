from comfy_api.latest import io
from .format_translation import translate_metadata

class HondaConvertMetadataFormat(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ConvertMetadataFormat",
            display_name="🔀 Convert Metadata Format",
            category="⚡️ Honda Nodes/🏷️ Metadata",
            description="Translates the internal structure of metadata JSON to match a target file format (e.g. converting PngText to UserComment and vice versa).",
            inputs=[
                io.String.Input(
                    "metadata",
                    default="{}",
                    multiline=True,
                    display_name="Metadata (JSON)",
                    tooltip="The input metadata JSON string to be converted.",
                ),
                io.Combo.Input(
                    "target_format",
                    options=["png", "jpg", "webp"],
                    display_name="Target Format",
                    tooltip="The image format you intend to save this metadata into.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Converted Metadata"),
            ],
        )

    @classmethod
    def execute(cls, metadata: str, target_format: str) -> io.NodeOutput:
        result = translate_metadata(metadata, target_format)
        return io.NodeOutput(result)
