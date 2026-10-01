"""
Watermark nodes for Honda Nodes.

Defines a shared HONDA_WATERMARK custom type used by:
  - HondaWatermarkLoad  (image-based watermark from a PNG file)
  - HondaWatermarkText  (text-based watermark with font selection)

The watermark dict is consumed by HondaSaveImage.
"""

import os
import sys
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, field
from typing import Any

from comfy_api.latest import io


# ---------------------------------------------------------------------------
# Custom IO type
# ---------------------------------------------------------------------------
HondaWatermark = io.Custom("HONDA_WATERMARK")


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------
def _get_font_dirs() -> list[str]:
    dirs = []
    if sys.platform == "win32":
        win = os.environ.get("WINDIR", "C:\\Windows")
        dirs.append(os.path.join(win, "Fonts"))
    elif sys.platform == "darwin":
        dirs += ["/Library/Fonts", "/System/Library/Fonts",
                 os.path.expanduser("~/Library/Fonts")]
    else:
        dirs += ["/usr/share/fonts", "/usr/local/share/fonts",
                 os.path.expanduser("~/.fonts")]
    return dirs


def _list_fonts() -> list[str]:
    seen: dict[str, str] = {}  # display_name → full_path
    for d in _get_font_dirs():
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.lower().endswith((".ttf", ".otf")):
                name = os.path.splitext(fn)[0]
                seen[name] = os.path.join(d, fn)
    if not seen:
        return ["[default]"]
    return sorted(seen.keys())


def _resolve_font(font_name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_name == "[default]":
        return ImageFont.load_default()
    for d in _get_font_dirs():
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            name = os.path.splitext(fn)[0]
            if name == font_name:
                try:
                    return ImageFont.truetype(os.path.join(d, fn), size)
                except Exception:
                    pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Shared watermark application
# ---------------------------------------------------------------------------
_POSITIONS = ["bottom_right", "bottom_left", "top_right", "top_left", "center"]


def apply_watermark(img: Image.Image, wm: dict) -> Image.Image:
    """Apply a watermark dict to a PIL Image, returning a new Image."""
    if not wm:
        return img

    wm_type = wm.get("type")
    position = wm.get("position", "bottom_right")
    opacity = max(0.0, min(1.0, float(wm.get("opacity", 0.5))))
    margin = int(wm.get("margin", 16))

    base = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))

    if wm_type == "image":
        wm_img: Image.Image = wm["image"].convert("RGBA")
        # Scale relative to canvas if scale provided
        scale = float(wm.get("scale", 1.0))
        if scale != 1.0:
            new_w = int(wm_img.width * scale)
            new_h = int(wm_img.height * scale)
            wm_img = wm_img.resize((new_w, new_h), Image.LANCZOS)
        # Apply opacity to alpha channel
        r, g, b, a = wm_img.split()
        a = a.point(lambda x: int(x * opacity))
        wm_img = Image.merge("RGBA", (r, g, b, a))
        W, H = base.size
        tw, th = wm_img.size
        x, y = _calc_pos(position, W, H, tw, th, margin)
        overlay.paste(wm_img, (x, y), wm_img)

    elif wm_type == "text":
        text = wm.get("text", "")
        if not text:
            return img
        font_name = wm.get("font", "[default]")
        font_size = int(wm.get("size", 24))
        color_hex = wm.get("color", "#FFFFFF")
        shadow = bool(wm.get("shadow", True))
        font = _resolve_font(font_name, font_size)
        draw = ImageDraw.Draw(overlay)
        W, H = base.size
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = _calc_pos(position, W, H, tw, th, margin)
        alpha = int(255 * opacity)
        r, g, b = _hex_to_rgb(color_hex)
        if shadow:
            draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, alpha // 2))
        draw.text((x, y), text, font=font, fill=(r, g, b, alpha))

    composited = Image.alpha_composite(base, overlay)
    return composited.convert("RGBA") if img.mode == "RGBA" else composited.convert("RGB")


def _calc_pos(position: str, W: int, H: int, tw: int, th: int, margin: int) -> tuple[int, int]:
    if position == "bottom_right":
        return W - tw - margin, H - th - margin
    if position == "bottom_left":
        return margin, H - th - margin
    if position == "top_right":
        return W - tw - margin, margin
    if position == "top_left":
        return margin, margin
    # center
    return (W - tw) // 2, (H - th) // 2


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return (255, 255, 255)


# ---------------------------------------------------------------------------
# Node: Image Watermark
# ---------------------------------------------------------------------------
class HondaWatermarkLoad(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_WatermarkLoad",
            display_name="🖼 Image Watermark",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Creates a watermark from a PNG/image file (supports transparency). Connect to Save Image.",
            inputs=[
                io.String.Input(
                    "image_path",
                    default="",
                    force_input=True,
                    display_name="Image Path",
                    tooltip="Absolute path to a PNG (or any image with transparency) to use as the watermark.",
                ),
                io.Float.Input(
                    "opacity",
                    default=0.7,
                    min=0.0,
                    max=1.0,
                    step=0.05,
                    display_name="Opacity",
                ),
                io.Float.Input(
                    "scale",
                    default=1.0,
                    min=0.01,
                    max=10.0,
                    step=0.05,
                    display_name="Scale",
                    tooltip="Scaling factor applied to the watermark image before compositing.",
                ),
                io.Combo.Input(
                    "position",
                    options=_POSITIONS,
                    default="bottom_right",
                    display_name="Position",
                ),
                io.Int.Input(
                    "margin",
                    default=16,
                    min=0,
                    max=512,
                    display_name="Margin (px)",
                ),
            ],
            outputs=[
                HondaWatermark.Output(display_name="Watermark"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image_path: str,
        opacity: float = 0.7,
        scale: float = 1.0,
        position: str = "bottom_right",
        margin: int = 16,
    ) -> io.NodeOutput:
        image_path = (image_path or "").strip()
        if not image_path or not os.path.exists(image_path):
            raise FileNotFoundError(f"[Honda WatermarkLoad] Image not found: {image_path!r}")
        wm_img = Image.open(image_path)
        wm_dict = {
            "type": "image",
            "image": wm_img,
            "opacity": opacity,
            "scale": scale,
            "position": position,
            "margin": margin,
        }
        return io.NodeOutput(wm_dict)


# ---------------------------------------------------------------------------
# Node: Text Watermark
# ---------------------------------------------------------------------------
_FONTS_LIST = _list_fonts()

_COLOR_PRESETS = [
    "#FFFFFF",  # White
    "#000000",  # Black
    "#FF0000",  # Red
    "#00FF00",  # Green
    "#0000FF",  # Blue
    "#FFFF00",  # Yellow
    "#FF8800",  # Orange
    "#FF00FF",  # Magenta
    "#00FFFF",  # Cyan
]


class HondaWatermarkText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_WatermarkText",
            display_name="✏️ Text Watermark",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Creates a text watermark with full font and style control. Connect to Save Image.",
            inputs=[
                io.String.Input(
                    "text",
                    default="© My Name",
                    display_name="Text",
                    tooltip="Text to render as watermark. Use \\n for newlines.",
                ),
                io.Combo.Input(
                    "font",
                    options=_FONTS_LIST,
                    default=_FONTS_LIST[0],
                    display_name="Font",
                ),
                io.Int.Input(
                    "size",
                    default=32,
                    min=6,
                    max=512,
                    display_name="Font Size",
                ),
                io.Combo.Input(
                    "color",
                    options=_COLOR_PRESETS,
                    default="#FFFFFF",
                    display_name="Color",
                    tooltip="Color as a hex code. You can type a custom hex directly.",
                ),
                io.Float.Input(
                    "opacity",
                    default=0.7,
                    min=0.0,
                    max=1.0,
                    step=0.05,
                    display_name="Opacity",
                ),
                io.Boolean.Input(
                    "shadow",
                    default=True,
                    display_name="Drop Shadow",
                    tooltip="Adds a subtle black shadow under the text for readability on bright backgrounds.",
                ),
                io.Combo.Input(
                    "position",
                    options=_POSITIONS,
                    default="bottom_right",
                    display_name="Position",
                ),
                io.Int.Input(
                    "margin",
                    default=16,
                    min=0,
                    max=512,
                    display_name="Margin (px)",
                ),
            ],
            outputs=[
                HondaWatermark.Output(display_name="Watermark"),
            ],
        )

    @classmethod
    def execute(
        cls,
        text: str,
        font: str = "[default]",
        size: int = 32,
        color: str = "#FFFFFF",
        opacity: float = 0.7,
        shadow: bool = True,
        position: str = "bottom_right",
        margin: int = 16,
    ) -> io.NodeOutput:
        wm_dict = {
            "type": "text",
            "text": text,
            "font": font,
            "size": size,
            "color": color,
            "opacity": opacity,
            "shadow": shadow,
            "position": position,
            "margin": margin,
        }
        return io.NodeOutput(wm_dict)
