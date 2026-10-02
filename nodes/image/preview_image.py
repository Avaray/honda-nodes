import torch
from comfy_api.latest import io, ui

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
        if not raw_image:
            import torch.nn.functional as F
            B, H, W, C = images.shape
            max_dim = max(H, W)
            if max_dim > max_resolution:
                scale = max_resolution / max_dim
                new_H, new_W = int(H * scale), int(W * scale)
                img_c = images.permute(0, 3, 1, 2)
                img_c = F.interpolate(img_c, size=(new_H, new_W), mode="bicubic", align_corners=False)
                preview_tensor = img_c.permute(0, 2, 3, 1)
            else:
                preview_tensor = images
        else:
            preview_tensor = images

        preview = ui.PreviewImage(preview_tensor)
        # We simply pass the original images through as output, and attach the UI preview.
        return io.NodeOutput(images, ui=preview)
