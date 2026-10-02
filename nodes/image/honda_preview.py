"""
honda_preview.py — Shared preview helper.

Wraps ui.PreviewImage to also embed original/preview dimensions in the
`as_dict()` output so the frontend can display resolution info under
the canvas thumbnail.
"""
import torch
import torch.nn.functional as F
from comfy_api.latest import ui


class HondaPreviewImage(ui.PreviewImage):
    """PreviewImage extended with orig/preview size metadata."""

    def __init__(self, preview_tensor: torch.Tensor, orig_h: int, orig_w: int):
        super().__init__(preview_tensor)
        _B, prev_H, prev_W, _C = preview_tensor.shape
        self.honda_dims = f"{prev_W}x{prev_H}|{orig_w}x{orig_h}"

    def as_dict(self) -> dict:
        d = super().as_dict()
        d["honda_dims"] = self.honda_dims
        return d


def make_preview(
    image_tensor: torch.Tensor,
    raw_image: bool,
    max_resolution: int,
) -> "HondaPreviewImage":
    """
    Downscale image_tensor for UI preview (unless raw_image=True), then
    return a HondaPreviewImage that carries both preview and original dims.
    """
    _B, orig_H, orig_W, _C = image_tensor.shape

    if not raw_image:
        max_dim = max(orig_H, orig_W)
        if max_dim > max_resolution:
            scale = max_resolution / max_dim
            new_H, new_W = int(orig_H * scale), int(orig_W * scale)
            img_c = image_tensor.permute(0, 3, 1, 2)
            img_c = F.interpolate(img_c, size=(new_H, new_W), mode="bicubic", align_corners=False)
            preview_tensor = img_c.permute(0, 2, 3, 1)
        else:
            preview_tensor = image_tensor
    else:
        preview_tensor = image_tensor

    return HondaPreviewImage(preview_tensor, orig_h=orig_H, orig_w=orig_W)
