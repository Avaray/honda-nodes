"""
Shared logic for the "Text Concatenate" node.
"""

from typing import Iterable, Optional

MIN_TEXT_FIELDS = 1
MAX_TEXT_FIELDS = 99

CASE_KEEP = "Keep Original"
CASE_UPPER = "UPPERCASE"
CASE_LOWER = "lowercase"
CASE_MODES = [CASE_KEEP, CASE_UPPER, CASE_LOWER]


def apply_case(text: str, mode: str) -> str:
    """Force the case of the final string, or leave it untouched."""
    if mode == CASE_UPPER:
        return text.upper()
    if mode == CASE_LOWER:
        return text.lower()
    return text


def concatenate_texts(
    texts: Iterable[Optional[str]],
    separator: str,
    case_mode: str,
    skip_empty: bool = True,
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
    if skip_empty:
        parts = [t for t in texts if t]
    else:
        parts = [t for t in texts if t is not None]

    joined = (separator or "").join(parts)
    return apply_case(joined, case_mode)
