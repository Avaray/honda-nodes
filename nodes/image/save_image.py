import os
import shutil
import subprocess
import tempfile
import torch
import numpy as np
from PIL import Image

import folder_paths
from comfy_api.latest import io, ui

from ..metadata.format_translation import sanitize_for_ime
from .watermark import HondaWatermark, apply_watermark


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
            description="Saves an image to disk in one or multiple formats, optionally with a watermark and injected JSON metadata.",
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
                io.Boolean.Input("save_png", default=True, display_name="Save PNG"),
                io.Boolean.Input("save_jpg", default=True, display_name="Save JPG"),
                io.Boolean.Input("save_webp", default=True, display_name="Save WEBP"),
                io.Int.Input("png_compress_level", default=4, min=0, max=9, display_name="PNG Compression", tooltip="0=fastest/largest, 9=slowest/smallest."),
                io.Int.Input("jpg_quality", default=95, min=1, max=100, display_name="JPG Quality"),
                io.Int.Input("webp_quality", default=95, min=1, max=100, display_name="WEBP Quality", tooltip="Only applies when WEBP Lossless is off."),
                io.Boolean.Input("webp_lossless", default=False, display_name="WEBP Lossless"),
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
                io.String.Input(
                    "format_override",
                    default="",
                    optional=True,
                    force_input=True,
                    display_name="Format Override",
                    tooltip="Provide 'png', 'jpg', or 'webp' to save ONLY in that format, ignoring the toggles above.",
                ),
                HondaWatermark.Input(
                    "watermark",
                    optional=True,
                    display_name="Watermark",
                    tooltip="Connect an 'Image Watermark' or 'Text Watermark' node.",
                ),
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
                io.String.Output(display_name="Saved Paths"),
            ],
        )

    @classmethod
    def execute(
        cls,
        images: torch.Tensor,
        filename: str = "",
        save_png: bool = True,
        save_jpg: bool = True,
        save_webp: bool = True,
        png_compress_level: int = 4,
        jpg_quality: int = 95,
        webp_quality: int = 95,
        webp_lossless: bool = False,
        save_path: str = "",
        metadata: str = "",
        format_override: str = "",
        watermark: dict | None = None,
        max_resolution: int = 1024,
        raw_image: bool = False,
    ) -> io.NodeOutput:
        filename = (filename or "HondaImage").strip()
        save_dir = (save_path or folder_paths.get_output_directory()).strip()
        os.makedirs(save_dir, exist_ok=True)

        # Determine formats to save
        format_override = (format_override or "").strip().lower()
        if format_override == "jpeg":
            format_override = "jpg"

        if format_override in ("png", "jpg", "webp"):
            formats_to_save = [format_override]
        else:
            formats_to_save = []
            if save_png:
                formats_to_save.append("png")
            if save_jpg:
                formats_to_save.append("jpg")
            if save_webp:
                formats_to_save.append("webp")
            if not formats_to_save:
                formats_to_save = ["png"]

        # Determine next counter across all enabled formats
        existing_files = []
        try:
            existing_files = os.listdir(save_dir)
        except OSError:
            pass

        counter = 1
        for fmt in formats_to_save:
            for f in existing_files:
                if f.startswith(filename) and f.endswith(f".{fmt}"):
                    try:
                        part = f[len(filename):].replace("_", "").replace(f".{fmt}", "")
                        if part.isdigit():
                            counter = max(counter, int(part) + 1)
                    except ValueError:
                        pass

        meta_str = (metadata or "").strip()
        saved_paths = []

        for batch_index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            # Apply watermark (shared helper)
            if watermark:
                img = apply_watermark(img, watermark)

            for fmt in formats_to_save:
                file_name = f"{filename}_{counter + batch_index:05d}.{fmt}"
                full_path = os.path.join(save_dir, file_name)

                clean_meta = sanitize_for_ime(meta_str, fmt) if meta_str not in ("", "{}") else ""

                if fmt == "png":
                    img.save(full_path, compress_level=png_compress_level)
                elif fmt == "jpg":
                    save_img = img.convert("RGB") if img.mode in ("RGBA", "LA", "P") else img
                    save_img.save(full_path, quality=jpg_quality, optimize=True)
                else:  # webp
                    img.save(full_path, quality=webp_quality, lossless=webp_lossless)

                # Inject metadata via ime using a temp file to avoid Windows cmdline length limit
                if clean_meta:
                    ime_path = _find_ime()
                    if ime_path:
                        tmp_path = None
                        try:
                            with tempfile.NamedTemporaryFile(
                                mode="w", suffix=".json", encoding="utf-8", delete=False
                            ) as tmp:
                                tmp.write(clean_meta)
                                tmp_path = tmp.name
                            cmd = [ime_path, full_path, "--set", f"@{tmp_path}"]
                            subprocess.run(
                                cmd, capture_output=True, text=True, check=True,
                                encoding="utf-8", errors="replace",
                            )
                        except subprocess.CalledProcessError as e:
                            print(f"[HondaSaveImage] Warning: Failed to inject metadata with ime: {e.stderr or e.stdout or str(e)}")
                        finally:
                            if tmp_path and os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                    else:
                        print("[HondaSaveImage] Warning: 'ime' CLI not found. Skipping metadata injection.")

                saved_paths.append(full_path)

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
        paths_str = "\n".join(saved_paths)
        return io.NodeOutput(paths_str, ui=preview)

