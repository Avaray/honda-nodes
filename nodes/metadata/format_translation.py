import json

def translate_metadata(meta_str: str, target_format: str) -> str:
    """
    Translates the structure of a metadata JSON string to match the target format
    (e.g., converting PngText <-> UserComment).
    Returns the modified JSON string, or the original if no changes were needed/possible.
    """
    meta_str = (meta_str or "").strip()
    if not meta_str or meta_str == "{}":
        return meta_str

    try:
        meta_dict = json.loads(meta_str)
    except json.JSONDecodeError:
        return meta_str

    if not isinstance(meta_dict, dict):
        return meta_str

    custom = meta_dict.get("custom", {})
    if not isinstance(custom, dict):
        return meta_str

    target_format = target_format.strip().lower()
    
    # We create a new custom dictionary to not mutate in place unexpectedly
    new_custom = dict(custom)
    changed = False
    
    if target_format == "png":
        # PNG stores text chunks in PngText. It does not use UserComment.
        if "UserComment" in new_custom:
            user_comment = new_custom.pop("UserComment")
            png_text = new_custom.get("PngText", {})
            if not isinstance(png_text, dict):
                png_text = {}
            else:
                png_text = dict(png_text)
                
            if isinstance(user_comment, dict):
                png_text.update(user_comment)
            else:
                png_text["UserComment"] = user_comment
                
            new_custom["PngText"] = png_text
            changed = True
            
    elif target_format in ("jpg", "jpeg", "webp"):
        # JPEG/WebP store everything in a single UserComment field.
        if "PngText" in new_custom:
            png_text = new_custom.pop("PngText")
            user_comment = new_custom.get("UserComment", {})
            if not isinstance(user_comment, dict):
                user_comment = {"original_comment": user_comment}
            else:
                user_comment = dict(user_comment)
                
            if isinstance(png_text, dict):
                user_comment.update(png_text)
            else:
                user_comment["PngText"] = png_text
                
            new_custom["UserComment"] = user_comment
            changed = True

    if changed:
        meta_dict["custom"] = new_custom
        return json.dumps(meta_dict, ensure_ascii=False)
        
    return meta_str

def detect_format_from_file(path: str) -> str:
    """Safely detects image format from file magic bytes."""
    try:
        with open(path, "rb") as f:
            header = f.read(12)
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                return "png"
            if header.startswith(b'\xff\xd8\xff'):
                return "jpg"
            if header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WEBP':
                return "webp"
    except Exception:
        pass
    return "unknown"
