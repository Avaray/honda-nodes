import os
import shutil
import subprocess
import json
import torch
import numpy as np
from PIL import Image

import folder_paths
from comfy_api.latest import io, ui


def _find_mex() -> str | None:
    mex_path = shutil.which("mex")
    if mex_path:
        return mex_path

    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_bin = os.path.join(current_dir, "bin")
    mex_exe = "mex.exe" if os.name == "nt" else "mex"
    local_mex = os.path.join(local_bin, mex_exe)
    if os.path.exists(local_mex):
        return local_mex

    return None


class HondaSaveImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_SaveImage",
            display_name="Save Image",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Saves an image to disk, optionally injecting metadata via 'mex', and displays a preview in the UI.",
            is_output_node=True,
            inputs=[
                io.Image.Input("images", display_name="Images"),
                io.String.Input(
                    "filename",
                    default="HondaImage",
                    optional=True,
                    display_name="Filename",
                    tooltip="Base filename. A counter will be appended automatically.",
                ),
                io.String.Input(
                    "save_path",
                    default="",
                    optional=True,
                    display_name="Save Path",
                    tooltip="Absolute path to a directory where the image should be saved. If empty, uses the default ComfyUI output directory.",
                ),
                io.String.Input(
                    "metadata",
                    default="",
                    multiline=True,
                    optional=True,
                    display_name="Metadata",
                    tooltip="Metadata to write via 'mex'. One Key=Value pair per line.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Saved Paths"),
            ],
        )

    @classmethod
    def execute(
        cls,
        images: torch.Tensor,
        filename: str = "",
        save_path: str = "",
        metadata: str = ""
    ) -> io.NodeOutput:
        filename = (filename or "HondaImage").strip()
        save_dir = (save_path or folder_paths.get_output_directory()).strip()
        
        # Ensure the directory exists
        os.makedirs(save_dir, exist_ok=True)
        
        # We need a counter so we don't overwrite files
        # Let's find the next available counter for this prefix
        existing_files = []
        try:
            existing_files = os.listdir(save_dir)
        except OSError:
            pass
            
        counter = 1
        for f in existing_files:
            if f.startswith(filename) and f.endswith(".png"):
                try:
                    # extract counter if format is prefix_XXXXX_.png or prefix_XXXXX.png
                    part = f[len(filename):].replace("_", "").replace(".png", "")
                    if part.isdigit():
                        counter = max(counter, int(part) + 1)
                except ValueError:
                    pass

        saved_paths = []
        
        for batch_index, image in enumerate(images):
            # Convert tensor back to PIL Image
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Format filename
            current_counter = counter + batch_index
            file_name = f"{filename}_{current_counter:05d}.png"
            full_path = os.path.join(save_dir, file_name)
            
            # Save raw PNG first
            img.save(full_path, compress_level=4)
            saved_paths.append(full_path)
            
            # Apply mex if metadata is provided
            if metadata.strip():
                pairs = []
                for raw_line in metadata.splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, _, v = line.partition("=")
                        pairs.append((k.strip(), v.strip()))
                
                if pairs:
                    mex_path = _find_mex()
                    if mex_path:
                        cmd = [mex_path, full_path]
                        for k, v in pairs:
                            cmd += ["--set", f"{k}={v}"]
                        try:
                            subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                check=True,
                                encoding="utf-8",
                                errors="replace",
                            )
                        except subprocess.CalledProcessError as e:
                            print(f"[HondaSaveImage] Error running mex on {full_path}: {e.stderr or e.stdout}")
                    else:
                        print(f"[HondaSaveImage] Warning: metadata provided but 'mex' not found!")
        
        # Create a preview of the images
        # comfy_api.latest.ui.PreviewImage handles generating temporary files to display in the frontend
        preview = ui.PreviewImage(images)
        
        # Output the saved absolute paths (joined by newline if multiple)
        paths_str = "\n".join(saved_paths)
        return io.NodeOutput(paths_str, ui=preview)
