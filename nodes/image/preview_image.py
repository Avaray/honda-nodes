import os
import uuid
import numpy as np
import torch
from PIL import Image

import folder_paths
from comfy_api.latest import io


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
                io.Image.Input("images", display_name="Image"),
            ],
            outputs=[
                io.Image.Output(display_name="Image"),
            ],
        )

    @classmethod
    def execute(cls, images: torch.Tensor) -> io.NodeOutput:
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)

        preview_files = []
        for img_tensor in images:
            i = 255.0 * img_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            fname = f"honda_preview_{uuid.uuid4().hex[:12]}.png"
            fpath = os.path.join(temp_dir, fname)
            img.save(fpath, compress_level=1)
            preview_files.append({"filename": fname, "type": "temp", "subfolder": ""})

        return io.NodeOutput(images, ui={"honda_preview_image": preview_files})
