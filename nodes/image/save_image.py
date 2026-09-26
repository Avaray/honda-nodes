import os
import shutil
import subprocess
import json
import torch
import numpy as np
from PIL import Image

import folder_paths
from comfy_api.latest import io, ui


def _find_ime() -> str | None:
    ime_path = shutil.which("ime")
    if ime_path:
        return ime_path

    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_bin = os.path.join(current_dir, "bin")
    ime_exe = "ime.exe" if os.name == "nt" else "ime"
    local_ime = os.path.join(local_bin, ime_exe)
    if os.path.exists(local_ime):
        return local_ime

    return None


class HondaSaveImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_SaveImage",
            display_name="🖼 Save Image",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Saves an image to disk, optionally injecting JSON metadata via 'ime', and displays a preview.",
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
                io.DynamicCombo.Input(
                    "image_format",
                    options=[
                        io.DynamicCombo.Option("png", [
                            io.Int.Input(
                                "compress_level",
                                default=4,
                                min=0,
                                max=9,
                                display_name="Compression Level",
                                tooltip="PNG is lossless — this only trades encode speed for file size (0 = fastest/biggest file, 9 = slowest/smallest file). It does not affect image quality.",
                            ),
                        ]),
                        io.DynamicCombo.Option("jpg", [
                            io.Int.Input(
                                "quality",
                                default=95,
                                min=1,
                                max=100,
                                display_name="Quality",
                                tooltip="JPEG quality (1-100). Higher = better quality, larger file.",
                            ),
                        ]),
                        io.DynamicCombo.Option("webp", [
                            io.Int.Input(
                                "quality",
                                default=95,
                                min=1,
                                max=100,
                                display_name="Quality",
                                tooltip="WEBP quality (1-100). Only applies when Lossless is off.",
                            ),
                            io.Boolean.Input(
                                "lossless",
                                default=False,
                                display_name="Lossless",
                                tooltip="Save WEBP losslessly instead of using lossy compression at the chosen Quality.",
                            ),
                        ]),
                    ],
                    display_name="Format",
                    tooltip="File format to save as. The quality controls below change depending on the selected format.",
                ),
                io.String.Input(
                    "save_path",
                    default="",
                    optional=True,
                    display_name="Save Path",
                    tooltip="Absolute path to a directory. If empty, uses the default ComfyUI output directory.",
                ),
                io.String.Input(
                    "metadata",
                    default="{}",
                    optional=True,
                    force_input=True,
                    display_name="Metadata (JSON)",
                    tooltip="JSON object with metadata to inject via 'ime'.",
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
        image_format: dict = None,
        save_path: str = "",
        metadata: str = ""
    ) -> io.NodeOutput:
        filename = (filename or "HondaImage").strip()
        save_dir = (save_path or folder_paths.get_output_directory()).strip()

        os.makedirs(save_dir, exist_ok=True)

        # image_format to teraz dict z DynamicCombo:
        # {"image_format": "png"/"jpg"/"webp", ...pola właściwe dla wybranej opcji}
        image_format = image_format or {}
        selected_format = str(image_format.get("image_format", "png")).strip().lower()
        if selected_format not in ("png", "jpg", "webp"):
            selected_format = "png"
        ext = selected_format

        existing_files = []
        try:
            existing_files = os.listdir(save_dir)
        except OSError:
            pass

        counter = 1
        for f in existing_files:
            if f.startswith(filename) and f.endswith(f".{ext}"):
                try:
                    part = f[len(filename):].replace("_", "").replace(f".{ext}", "")
                    if part.isdigit():
                        counter = max(counter, int(part) + 1)
                except ValueError:
                    pass

        saved_paths = []

        for batch_index, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            file_name = f"{filename}_{counter + batch_index:05d}.{ext}"
            full_path = os.path.join(save_dir, file_name)

            # Prepare metadata
            meta_str = (metadata or "").strip()
            meta_dict = None
            if meta_str and meta_str not in ("{}", ""):
                try:
                    meta_dict = json.loads(meta_str)
                except json.JSONDecodeError:
                    print(f"[HondaSaveImage] Invalid JSON in metadata — skipping metadata for {file_name}")

            if selected_format == "png":
                compress_level = image_format.get("compress_level", 4)
                pnginfo = None
                if isinstance(meta_dict, dict) and meta_dict:
                    from PIL.PngImagePlugin import PngInfo
                    pnginfo = PngInfo()
                    for k, v in meta_dict.items():
                        if isinstance(v, (dict, list)):
                            pnginfo.add_text(k, json.dumps(v, ensure_ascii=False))
                        else:
                            pnginfo.add_text(k, str(v))
                img.save(full_path, compress_level=compress_level, pnginfo=pnginfo)

            else:  # jpg or webp
                exif = None
                if isinstance(meta_dict, dict) and meta_dict:
                    exif = img.getexif()
                    exif_ifd = exif.get_ifd(34665)  # Exif IFD
                    # 37510 is UserComment
                    exif_ifd[37510] = json.dumps(meta_dict, ensure_ascii=False)

                if selected_format == "jpg":
                    quality = image_format.get("quality", 95)
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                    img.save(full_path, quality=quality, optimize=True, exif=exif)
                else:  # webp
                    quality = image_format.get("quality", 95)
                    lossless = bool(image_format.get("lossless", False))
                    img.save(full_path, quality=quality, lossless=lossless, exif=exif)

            saved_paths.append(full_path)

        preview = ui.PreviewImage(images)
        paths_str = "\n".join(saved_paths)
        return io.NodeOutput(paths_str, ui=preview)
