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
            ],
            outputs=[
                io.Image.Output(display_name="Images"),
            ],
        )

    @classmethod
    def execute(cls, images: torch.Tensor) -> io.NodeOutput:
        preview = ui.PreviewImage(images)
        return io.NodeOutput(images, ui=preview)
