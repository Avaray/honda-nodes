from comfy_api.latest import io
import torch

class HondaImageSize(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ImageSize",
            display_name="🖼 Image Size",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Outputs the width and height of an image in pixels.",
            inputs=[
                io.Image.Input("image", display_name="Image"),
            ],
            outputs=[
                io.Int.Output(display_name="Width"),
                io.Int.Output(display_name="Height"),
            ],
        )

    @classmethod
    def execute(cls, image: torch.Tensor) -> io.NodeOutput:
        # image shape is [batch, height, width, channels]
        height = int(image.shape[1])
        width = int(image.shape[2])
        return io.NodeOutput(width, height)
