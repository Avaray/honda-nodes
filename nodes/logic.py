"""
Shared logic for the "Text Concatenate" node.
"""

import re
from typing import Iterable, Optional

MIN_TEXT_FIELDS = 1
MAX_TEXT_FIELDS = 99

CASE_KEEP = "Keep Original"
CASE_UPPER = "UPPERCASE"
CASE_LOWER = "lowercase"
CASE_CAPITALIZE = "Capitalize Each Word"
CASE_MODES = [CASE_KEEP, CASE_UPPER, CASE_LOWER, CASE_CAPITALIZE]


def apply_case(text: str, mode: str) -> str:
    """Force the case of the final string, or leave it untouched."""
    if mode == CASE_UPPER:
        return text.upper()
    if mode == CASE_LOWER:
        return text.lower()
    if mode == CASE_CAPITALIZE:
        return text.title()
    return text


def concatenate_texts(
    texts: Iterable[Optional[str]],
    separator: str,
    case_mode: str,
    skip_empty: bool = True,
    trim_whitespaces: bool = False,
    replace_whitespaces: bool = False,
    replace_whitespaces_with: str = "_",
    global_prefix: str = "",
    global_suffix: str = "",
) -> str:
    """
    Join an ordered sequence of text values with `separator`, then apply
    the requested case transform to the final result.

    Each item in `texts` should be `None` for a channel that isn't
    connected at all (always excluded, regardless of skip_empty), or a
    string (possibly "") for a channel that *is* connected.

    skip_empty=True (default) additionally drops connected-but-empty
    channels, so unused channels don't inject extra separators into the
    output. skip_empty=False keeps a connected empty string as a literal
    empty segment, while still ignoring unconnected channels.
    """
    parts = []
    if global_prefix:
        parts.append(global_prefix)

    for t in texts:
        if t is None:
            continue
        if trim_whitespaces:
            t = re.sub(r'\s+', ' ', t).strip()
        if replace_whitespaces:
            t = re.sub(r'\s', replace_whitespaces_with, t)
        if skip_empty and not t:
            continue
        parts.append(t)

    if global_suffix:
        parts.append(global_suffix)

    joined = (separator or "").join(parts)
    return apply_case(joined, case_mode)
