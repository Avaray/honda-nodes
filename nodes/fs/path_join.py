"""
"Path Join" node.

Joins multiple path segments into one well-formed path for the current OS.
Works correctly on Windows, Linux, and macOS:
- Each segment is stripped of surrounding whitespace
- Empty segments are skipped
- Mixed separators (/ and \\) are accepted and normalized
- The final result is passed through os.path.normpath so separators,
  redundant dots, and double slashes are cleaned up
- A segment that is an absolute path resets the join (standard os.path.join behaviour)
"""

import os
from comfy_api.latest import io


_EMPTY = ""


class HondaPathJoin(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_PathJoin",
            display_name="📂 Path Join",
            category="⚡️ Honda Nodes/📂 File System",
            description=(
                "Joins up to 5 path segments into a single, OS-correct path. "
                "Empty segments are ignored. Mixed separators are normalized automatically. "
                "Behaves like os.path.join: an absolute segment resets the result."
            ),
            inputs=[
                io.String.Input(
                    "segment_1",
                    default="",
                    display_name="Segment 1",
                    tooltip="First path segment (e.g. a base directory).",
                ),
                io.String.Input(
                    "segment_2",
                    default="",
                    display_name="Segment 2",
                    optional=True,
                ),
                io.String.Input(
                    "segment_3",
                    default="",
                    display_name="Segment 3",
                    optional=True,
                ),
                io.String.Input(
                    "segment_4",
                    default="",
                    display_name="Segment 4",
                    optional=True,
                ),
                io.String.Input(
                    "segment_5",
                    default="",
                    display_name="Segment 5",
                    optional=True,
                ),
            ],
            outputs=[
                io.String.Output(display_name="Path"),
            ],
        )

    @classmethod
    def execute(
        cls,
        segment_1: str,
        segment_2: str = _EMPTY,
        segment_3: str = _EMPTY,
        segment_4: str = _EMPTY,
        segment_5: str = _EMPTY,
    ) -> io.NodeOutput:
        raw_segments = [segment_1, segment_2, segment_3, segment_4, segment_5]

        # Normalize each segment: strip whitespace and unify separators so that
        # both "/" and "\\" are treated the same before os.path.join processes them.
        segments = []
        for seg in raw_segments:
            cleaned = (seg or "").strip().replace("\\", "/")
            if cleaned:
                segments.append(cleaned)

        if not segments:
            return io.NodeOutput("")

        joined = os.path.join(*segments)
        normalized = os.path.normpath(joined)

        return io.NodeOutput(normalized)
