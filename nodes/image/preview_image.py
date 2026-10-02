import torch
from comfy_api.latest import io, ui
from .honda_preview import make_preview

class HondaPreviewImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_PreviewImage",
            display_name="🖼 Preview Image",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Displays an image on the canvas and passes it through for further processing.",
            is_output_node=True,
            inputs=[
                io.Image.Input("images", display_name="Images"),
                io.Int.Input(
                    "max_resolution",
                    default=1024,
                    min=256,
                    max=8192,
                    step=256,
                    display_name="Max Resolution",
                    tooltip="Maximum dimension for preview. Hidden in UI.",
                ),
                io.Boolean.Input(
                    "raw_image",
                    default=False,
                    display_name="RAW Image",
                    tooltip="If enabled, shows the preview in true original quality and dimensions, skipping any UI downscaling.",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Images"),
            ],
        )

    @classmethod
    def execute(cls, images: torch.Tensor, max_resolution: int = 1024, raw_image: bool = False) -> io.NodeOutput:
        preview = make_preview(images, raw_image=raw_image, max_resolution=max_resolution)
        # Always pass through full-resolution images as output
        return io.NodeOutput(images, ui=preview)
