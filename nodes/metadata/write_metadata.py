"""
"Write Metadata" - Schema V3 node definition.

Uses the 'mex' CLI tool to inject metadata (key=value pairs) into an image file.
"""

import os
import shutil
import subprocess
from comfy_api.latest import io


def _find_mex() -> str | None:
    """Look for the 'mex' executable in PATH or in the extension's own bin/ folder."""
    mex_path = shutil.which("mex")
    if mex_path:
        return mex_path

    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_bin = os.path.join(current_dir, "bin")
    mex_exe = "mex.exe" if os.name == "nt" else "mex"
    local_mex = os.path.join(local_bin, mex_exe)
    if os.path.exists(local_mex):
        return local_mex

    return None


class HondaWriteMetadata(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_WriteMetadata",
            display_name="🏷️ Write Metadata",
            category="⚡️ Honda Nodes/🏷️ Metadata",
            description=(
                "Injects metadata tags into an image file using the 'mex' CLI tool. "
                "Accepts a JSON object string where each key-value pair is written as metadata. "
                "Operates in-place by default; provide an Output Path to leave the original untouched."
            ),
            inputs=[
                io.String.Input(
                    "file_path",
                    default="",
                    display_name="File Path",
                    tooltip="Absolute path to the target JPEG or PNG file.",
                ),
                io.String.Input(
                    "metadata",
                    default="{}",
                    multiline=True,
                    display_name="Metadata (JSON)",
                    tooltip=(
                        "A JSON object whose keys and string values will be written as metadata tags.\n"
                        "Example: {\"ImageDescription\": \"My photo\", \"Artist\": \"John\"}\n"
                        "Nested objects and arrays are serialized to strings."
                    ),
                ),
                io.String.Input(
                    "output_path",
                    default="",
                    optional=True,
                    display_name="Output Path (optional)",
                    tooltip=(
                        "If provided, mex writes the result to this path instead of modifying "
                        "the source file in-place. Leave empty to edit in-place."
                    ),
                ),
            ],
            outputs=[
                io.String.Output(display_name="Result Path"),
            ],
        )

    @classmethod
    def execute(cls, file_path: str, metadata: str, output_path: str = "") -> io.NodeOutput:
        import json

        file_path = (file_path or "").strip()
        if not file_path:
            raise ValueError("File Path is empty. Please provide a valid path.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse the JSON input
        metadata = (metadata or "{}").strip()
        try:
            data = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Metadata input: {e}")

        if not isinstance(data, dict):
            raise ValueError("Metadata must be a JSON object (dict), not an array or scalar.")

        # Flatten: nested values are serialized to JSON strings
        pairs: list[tuple[str, str]] = []
        for key, value in data.items():
            key = str(key).strip()
            if not key:
                continue
            if isinstance(value, (dict, list)):
                str_value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                str_value = "true" if value else "false"
            else:
                str_value = str(value)
            pairs.append((key, str_value))

        if not pairs:
            raise ValueError("No metadata pairs found. The JSON object must not be empty.")

        mex_path = _find_mex()
        if not mex_path:
            raise FileNotFoundError(
                "The 'mex' CLI tool was not found in the system PATH or the extension's 'bin' folder. "
                "Download it and place the executable in your PATH or in the honda-nodes/bin/ folder."
            )

        cmd = [mex_path, file_path]
        for key, value in pairs:
            cmd += ["--set", f"{key}={value}"]

        out = (output_path or "").strip()
        if out:
            cmd += ["--output", out]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"mex failed (exit code {e.returncode}): {e.stderr or e.stdout or str(e)}"
            )

        result_path = out if out else file_path
        return io.NodeOutput(result_path)
