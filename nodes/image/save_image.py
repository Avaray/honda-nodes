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
                io.Image.Input("image", display_name="Image"),
                io.String.Input(
                    "metadata",
                    default="{}",
                    optional=True,
                    force_input=True,
                    display_name="Metadata",
                    tooltip="JSON object with metadata to inject via 'ime'.",
                ),
                io.String.Input(
                    "path_override",
                    default="",
                    optional=True,
                    force_input=True,
                    display_name="Path Override",
                    tooltip="Absolute path to a directory. If empty, uses the default ComfyUI output directory.",
                ),
                io.String.Input(
                    "format_override",
                    default="",
                    optional=True,
                    force_input=True,
                    display_name="Format Override",
                    tooltip="Provide 'png', 'jpg', or 'webp' to save ONLY in that format, ignoring the toggles above.",
                ),
                io.String.Input(
                    "filename",
                    default="HondaImage",
                    optional=True,
                    force_input=True,
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
                HondaWatermark.Input(
                    "watermark",
                    optional=True,
                    display_name="Watermark",
                    tooltip="Connect an 'Image Watermark' or 'Text Watermark' node.",
                ),
            ],
            outputs=[
                io.Array.Output(display_name="Saved Paths"),
                io.String.Output(display_name="PNG Path"),
                io.String.Output(display_name="JPG Path"),
                io.String.Output(display_name="WEBP Path"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image: torch.Tensor,
        metadata: str = "",
        path_override: str = "",
        format_override: str = "",
        filename: str = "",
        save_png: bool = True,
        save_jpg: bool = True,
        save_webp: bool = True,
        png_compress_level: int = 4,
        jpg_quality: int = 95,
        webp_quality: int = 95,
        webp_lossless: bool = False,
        watermark: dict | None = None,
    ) -> io.NodeOutput:
        filename = (filename or "ComfyUI").strip()
        save_dir = (path_override or folder_paths.get_output_directory()).strip()
        os.makedirs(save_dir, exist_ok=True)

        # Determine formats to save — format_override always wins
        fmt_ov = (format_override or "").strip().lower()
        if fmt_ov == "jpeg":
            fmt_ov = "jpg"

        if fmt_ov in ("png", "jpg", "webp"):
            formats_to_save = [fmt_ov]
        else:
            formats_to_save = []
            if save_png:
                formats_to_save.append("png")
            if save_jpg:
                formats_to_save.append("jpg")
            if save_webp:
                formats_to_save.append("webp")
            if not formats_to_save:
                # Fallback: at least save PNG if all toggles are off
                formats_to_save = ["png"]

        # Determine next counter across all enabled formats so numbering is consistent
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

        # Per-format tracking: first saved path for each format (last batch wins)
        png_path: str = ""
        jpg_path: str = ""
        webp_path: str = ""
        all_paths: list[str] = []

        for batch_index, img_tensor in enumerate(image):
            i = 255.0 * img_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            if watermark:
                img = apply_watermark(img, watermark)

            for fmt in formats_to_save:
                file_name = f"{filename}_{counter + batch_index:05d}.{fmt}"
                full_path = os.path.join(save_dir, file_name)

                clean_meta = sanitize_for_ime(meta_str, fmt) if meta_str not in ("", "{}") else ""

                if fmt == "png":
                    img.save(full_path, compress_level=png_compress_level)
                    if not png_path:
                        png_path = full_path
                elif fmt == "jpg":
                    save_img = img.convert("RGB") if img.mode in ("RGBA", "LA", "P") else img
                    save_img.save(full_path, quality=jpg_quality, optimize=True)
                    if not jpg_path:
                        jpg_path = full_path
                else:  # webp
                    img.save(full_path, quality=webp_quality, lossless=webp_lossless)
                    if not webp_path:
                        webp_path = full_path

                # Inject metadata via ime using a temp file
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
                            print(f"[HondaSaveImage] Warning: Failed to inject metadata: {e.stderr or e.stdout or str(e)}")
                        finally:
                            if tmp_path and os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                    else:
                        print("[HondaSaveImage] Warning: 'ime' CLI not found. Skipping metadata injection.")

                all_paths.append(full_path)

        preview = ui.PreviewImage(image)
        return io.NodeOutput(all_paths, png_path, jpg_path, webp_path, ui=preview)
