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
        return io.Schema(
            node_id="Honda_LoadImage",
            display_name="🖼 Load Image",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Loads an image from the input folder and outputs the image data, mask, file path, metadata as JSON, and its format.",
            inputs=[
                io.String.Input(
                    "image_file",
                    default="",
                    socketless=True,
                    display_name="File Name",
                    tooltip="Name of the image file in the input directory.",
                ),
                io.String.Input(
                    "path_override",
                    default="",
                    optional=True,
                    force_input=True,
                    display_name="Path Override",
                    tooltip="Absolute path to an image file. If provided, this overrides the selected image.",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Image"),
                io.String.Output(display_name="Path"),
                io.String.Output(display_name="Metadata"),
                io.String.Output(display_name="Format"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image_file: str,
        path_override: str = "",
    ) -> io.NodeOutput:
        path_override = (path_override or "").strip()

        if path_override:
            if not os.path.exists(path_override):
                return io.NodeOutput(block_execution=f"Path Override: file not found at '{path_override}'")
            image_path = path_override
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            img = i.convert("RGB")
            img_np = np.array(img).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(img_np).clone()[None,]
            # Copy the external file into the input folder so the frontend
            # can display a preview via the /view API endpoint.
            input_dir = folder_paths.get_input_directory()
            dest_name = os.path.basename(path_override)
            dest_path = os.path.join(input_dir, dest_name)
            if not os.path.exists(dest_path):
                shutil.copy2(path_override, dest_path)
            preview_name = dest_name
        else:
            if not image_file:
                return io.NodeOutput(block_execution="Please select an image or provide a path_override.")
            image_tensor, _ = LoadImage().load_image(image_file)
            image_path = folder_paths.get_annotated_filepath(image_file)
            preview_name = image_file

        img_format = detect_format_from_file(image_path)

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
            cmd = [ime_path, image_path]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
                metadata_text = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                print(f"[Honda Nodes] Warning: Failed to extract metadata with ime: {e.stderr or e.stdout or str(e)}")
        elif not ime_path:
            print("[Honda Nodes] Warning: 'ime' CLI not found. Skipping metadata extraction.")

        preview = ui.PreviewImage(image_tensor)
        return io.NodeOutput(image_tensor, image_path, metadata_text, img_format, ui=preview)

