"""
"Write Metadata" - Schema V3 node definition.

Uses the 'ime' CLI tool to inject metadata (key=value pairs) into an image file.
"""

import os
import shutil
import subprocess
from comfy_api.latest import io


def _find_ime() -> str | None:
    """Look for the 'ime' executable in PATH or in the extension's own bin/ folder."""
    ime_path = shutil.which("ime")
    if ime_path:
        return ime_path

    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_bin = os.path.join(current_dir, "bin")
    ime_exe = "ime.exe" if os.name == "nt" else "ime"
    local_ime = os.path.join(local_bin, ime_exe)
    if os.path.exists(local_ime):
        return local_ime

    return None


class HondaWriteMetadata(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_WriteMetadata",
            display_name="🏷️ Write Metadata",
            category="⚡️ Honda Nodes/🏷️ Metadata",
            description=(
                "Injects metadata tags into an image file using the 'ime' CLI tool. "
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
                        "A JSON object to merge into the metadata via 'ime'.\n"
                        "Example: {\"exif\": {\"Artist\": \"John\"}, \"custom\": {\"UserComment\": {\"rating\": 5}}}\n"
                        "Use the correct structure for the image format (e.g. PngText for PNGs)."
                    ),
                ),
                io.String.Input(
                    "output_path",
                    default="",
                    optional=True,
                    display_name="Output Path (optional)",
                    tooltip=(
                        "If provided, ime writes the result to this path instead of modifying "
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
        import tempfile

        file_path = (file_path or "").strip()
        if not file_path:
            raise ValueError("File Path is empty. Please provide a valid path.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse the JSON input early to validate it
        metadata = (metadata or "{}").strip()
        try:
            data = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Metadata input: {e}")

        if not isinstance(data, dict):
            raise ValueError("Metadata must be a JSON object (dict), not an array or scalar.")

        if not data:
            raise ValueError("The JSON object must not be empty.")

        from .format_translation import detect_format_from_file, sanitize_for_ime

        target_format = detect_format_from_file(file_path)
        clean_meta = sanitize_for_ime(metadata, target_format if target_format != "unknown" else "jpg")

        if not clean_meta:
            raise ValueError("Metadata contains no valid 'exif' or 'custom' keys after sanitization.")

        ime_path = _find_ime()
        if not ime_path:
            raise FileNotFoundError(
                "The 'ime' CLI tool was not found in the system PATH or the extension's 'bin' folder. "
                "Download it and place the executable in your PATH or in the honda-nodes/bin/ folder."
            )

        out = (output_path or "").strip()

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", encoding="utf-8", delete=False
            ) as tmp:
                tmp.write(clean_meta)
                tmp_path = tmp.name

            cmd = [ime_path, file_path, "--set", f"@{tmp_path}"]
            if out:
                cmd += ["--output", out]

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
                f"ime failed (exit code {e.returncode}): {e.stderr or e.stdout or str(e)}"
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

        result_path = out if out else file_path
        return io.NodeOutput(result_path)

