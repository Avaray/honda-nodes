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
                "Injects metadata tags into an image file (JPEG or PNG) using the 'mex' CLI tool. "
                "Each line of the Metadata input must be in Key=Value format. "
                "Lines that are empty or start with '#' are ignored. "
                "Operates in-place by default; enable 'Write to new file' to leave the original untouched."
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
                    default="",
                    multiline=True,
                    display_name="Metadata",
                    tooltip=(
                        "Metadata to write. One Key=Value pair per line.\n"
                        "Standard EXIF keys: ImageDescription, Make, Model, Software, "
                        "Artist, Copyright, DateTimeOriginal, UserComment.\n"
                        "Any other key is treated as a custom tag."
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
        file_path = (file_path or "").strip()
        if not file_path:
            raise ValueError("File Path is empty. Please provide a valid path.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse Key=Value pairs — skip blank lines and comments
        pairs: list[tuple[str, str]] = []
        for raw_line in metadata.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Invalid metadata line (missing '='): {raw_line!r}\n"
                    "Each line must be in Key=Value format."
                )
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError(f"Empty key in line: {raw_line!r}")
            pairs.append((key, value))

        if not pairs:
            raise ValueError(
                "No metadata pairs found. "
                "Provide at least one Key=Value line in the Metadata input."
            )

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
            result = subprocess.run(
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
