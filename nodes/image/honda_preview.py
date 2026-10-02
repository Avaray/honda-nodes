"""
honda_preview.py - Shared preview helper.

Downscales the image for UI preview and returns a UI dictionary
containing the temp image paths plus the `honda_dims` metadata.
"""
import torch
import torch.nn.functional as F
from comfy_api.latest import ui

def make_preview(
    image_tensor: torch.Tensor,
    raw_image: bool,
    max_resolution: int,
) -> dict:
    """
    Downscale image_tensor for UI preview (unless raw_image=True), then
    return a UI dictionary that carries both preview and original dims.
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

    # Generate the standard PreviewImage (saves to temp folder)
    preview = ui.PreviewImage(preview_tensor)
    ui_dict = preview.as_dict()
    
    _B, prev_H, prev_W, _C = preview_tensor.shape
    ui_dict["honda_dims"] = f"{prev_W}x{prev_H}|{orig_W}x{orig_H}"
    
    return ui_dict
