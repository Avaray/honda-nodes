import os
import folder_paths
import shutil
import subprocess
import numpy as np
import torch
from PIL import Image, ImageOps

from comfy_api.latest import io, ui
from nodes import LoadImage

from ..metadata.format_translation import detect_format_from_file

class HondaLoadImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        
        return io.Schema(
            node_id="Honda_LoadImage",
            display_name="🖼 Load Image",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Loads an image from the input folder and outputs the image data, mask, file path, metadata as JSON, and its format.",
            inputs=[
                io.Combo.Input(
                    "image",
                    options=sorted(files) if files else [],
                    upload=io.UploadType.image,
                    image_folder=io.FolderType.input,
                    display_name="Image",
                ),
                io.String.Input(
                    "path_override",
                    default="",
                    optional=True,
                    force_input=True,
                    display_name="Path Override",
                    tooltip="Absolute path to an image file. If provided, this overrides the selected image in the dropdown.",
                ),
                io.Boolean.Input(
                    "lightweight_preview",
                    default=True,
                    display_name="Lightweight Preview",
                    tooltip="Automatically downscales the image if it is too large, saving VRAM and preventing UI lag.",
                ),
                io.Int.Input(
                    "max_resolution",
                    default=1024,
                    min=256,
                    max=8192,
                    step=64,
                    display_name="Max Resolution",
                    tooltip="Maximum dimension (width or height) when Lightweight Preview is enabled.",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Image"),
                io.Mask.Output(display_name="Mask"),
                io.String.Output(display_name="Path"),
                io.String.Output(display_name="Metadata"),
                io.String.Output(display_name="Format"),
            ],
        )

    @classmethod
    def execute(cls, image: str, path_override: str = "", lightweight_preview: bool = True, max_resolution: int = 1024) -> io.NodeOutput:
        path_override = (path_override or "").strip()
        
        if path_override and os.path.exists(path_override):
            image_path = path_override
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            img = i.convert("RGB")
            img = np.array(img).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(img)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - mask
            else:
                mask = np.zeros((64,64), dtype=np.float32)
            mask_tensor = torch.from_numpy(mask)[None,]
        else:
            # Use standard ComfyUI LoadImage node functionality
            image_tensor, mask_tensor = LoadImage().load_image(image)
            # Determine the absolute path of the loaded image
            image_path = folder_paths.get_annotated_filepath(image)
            
        if lightweight_preview:
            import torch.nn.functional as F
            B, H, W, C = image_tensor.shape
            max_dim = max(H, W)
            if max_dim > max_resolution:
                scale = max_resolution / max_dim
                new_H, new_W = int(H * scale), int(W * scale)
                # Downscale only for the UI preview — the output tensor stays full-res
                img_c = image_tensor.permute(0, 3, 1, 2)
                img_c = F.interpolate(img_c, size=(new_H, new_W), mode="bicubic", align_corners=False)
                preview_tensor = img_c.permute(0, 2, 3, 1)
            else:
                preview_tensor = image_tensor
        else:
            preview_tensor = image_tensor


        # Detect the original format
        img_format = detect_format_from_file(image_path)
        
        # Find the 'ime' executable
        ime_path = shutil.which("ime")
        if not ime_path:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_bin = os.path.join(current_dir, "bin")
            ime_exe = "ime.exe" if os.name == "nt" else "ime"
            local_ime = os.path.join(local_bin, ime_exe)
            if os.path.exists(local_ime):
                ime_path = local_ime

        metadata_text = ""
        if ime_path and os.path.exists(image_path):
            # ime outputs JSON natively
            cmd = [ime_path, image_path]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
                metadata_text = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                print(f"[Honda Nodes] Warning: Failed to extract metadata with ime: {e.stderr or e.stdout or str(e)}")
        elif not ime_path:
            print("[Honda Nodes] Warning: 'ime' CLI not found. Skipping metadata extraction.")
        
        # Use downscaled tensor for UI preview only; output stays full-resolution
        preview = ui.PreviewImage(preview_tensor)
        return io.NodeOutput(image_tensor, mask_tensor, image_path, metadata_text, img_format, ui=preview)
