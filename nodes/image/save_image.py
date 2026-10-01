import os
import shutil
import subprocess
import json
import tempfile
import torch
import numpy as np
from PIL import Image

import folder_paths
from comfy_api.latest import io, ui

from ..metadata.format_translation import sanitize_for_ime


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
            description="Saves an image to disk in one or multiple formats, optionally adding a watermark and injecting JSON metadata via 'ime'.",
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
                io.Int.Input("png_compress_level", default=4, min=0, max=9, display_name="PNG Compression", tooltip="0=fastest/largest, 9=slowest/smallest. PNG is lossless — only affects file size."),
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
                io.String.Input(
                    "watermark_text",
                    default="",
                    optional=True,
                    display_name="Watermark Text",
                    tooltip="Text to overlay on the image. Leave empty for no watermark.",
                ),
                io.Int.Input(
                    "watermark_size",
                    default=24,
                    min=8,
                    max=256,
                    display_name="Watermark Size",
                ),
                io.Float.Input(
                    "watermark_opacity",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.1,
                    display_name="Watermark Opacity",
                ),
                io.Combo.Input(
                    "watermark_position",
                    options=["bottom_right", "bottom_left", "top_right", "top_left", "center"],
                    default="bottom_right",
                    display_name="Watermark Position",
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
        watermark_text: str = "",
        watermark_size: int = 24,
        watermark_opacity: float = 0.5,
        watermark_position: str = "bottom_right",
    ) -> io.NodeOutput:
        from PIL import ImageDraw, ImageFont

        filename = (filename or "HondaImage").strip()
        save_dir = (save_path or folder_paths.get_output_directory()).strip()
        os.makedirs(save_dir, exist_ok=True)

        # Format override: force a single format if given
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

        def _apply_watermark(img: Image.Image) -> Image.Image:
            text = (watermark_text or "").strip()
            if not text:
                return img
            base = img.convert("RGBA")
            overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            try:
                font = ImageFont.truetype("arial.ttf", watermark_size)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            margin = 16
            W, H = base.size
            positions = {
                "bottom_right": (W - tw - margin, H - th - margin),
                "bottom_left":  (margin, H - th - margin),
                "top_right":    (W - tw - margin, margin),
                "top_left":     (margin, margin),
                "center":       ((W - tw) // 2, (H - th) // 2),
            }
            x, y = positions.get(watermark_position, positions["bottom_right"])
            alpha = int(255 * max(0.0, min(1.0, watermark_opacity)))
            # Draw subtle shadow first for readability
            draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, alpha // 2))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))
            composited = Image.alpha_composite(base, overlay)
            return composited.convert("RGB") if img.mode != "RGBA" else composited

        saved_paths = []

        for batch_index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            img = _apply_watermark(img)

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

        preview = ui.PreviewImage(images)
        paths_str = "\n".join(saved_paths)
        return io.NodeOutput(paths_str, ui=preview)
