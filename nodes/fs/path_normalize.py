"""
"Path Normalize" node.

Cleans up a raw path string so it is valid and consistent on the current OS:
- Expands ~ and environment variables
- Resolves redundant separators and . / .. components
- On Windows: converts forward slashes to backslashes
- On Linux/macOS: converts backslashes to forward slashes
- Strips surrounding whitespace
"""

import os
from comfy_api.latest import io


class HondaPathNormalize(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_PathNormalize",
            display_name="📂 Path Normalize",
            category="⚡️ Honda Nodes/📂 File System",
            description=(
                "Normalizes a path string for the current operating system. "
                "Fixes mixed separators (/ vs \\\\), expands ~ and environment variables, "
                "and resolves redundant . / .. components."
            ),
            inputs=[
                io.String.Input(
                    "path",
                    default="",
                    display_name="Path",
                    tooltip=(
                        "Raw path string to normalize. "
                        "Accepts forward slashes, backslashes, or mixed separators."
                    ),
                ),
            ],
            outputs=[
                io.String.Output(display_name="Normalized Path"),
            ],
        )

    @classmethod
    def execute(cls, path: str) -> io.NodeOutput:
        raw = (path or "").strip()

        if not raw:
            return io.NodeOutput("")

        # 1. Unify separators before expansion so os.path functions work cross-platform.
        #    Replace backslashes with forward slashes first; os.path.normpath will
        #    convert to the OS-native separator afterwards.
        unified = raw.replace("\\", "/")

        # 2. Expand ~ (home directory) and %VAR% / $VAR environment variables.
        expanded = os.path.expandvars(os.path.expanduser(unified))

        # 3. Normalize: collapse redundant separators and resolve . / .. segments.
        normalized = os.path.normpath(expanded)

        return io.NodeOutput(normalized)
