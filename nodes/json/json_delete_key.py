"""
"JSON Delete Key" - Schema V3 node definition.

Deletes a key from a JSON object using the 'jq' CLI tool.
"""

import subprocess
from comfy_api.latest import io
from .utils import find_jq


class HondaJSONDeleteKey(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_JSONDeleteKey",
            display_name="JSON Delete Key",
            category="⚡️ Honda Nodes/🔣 JSON",
            description="Removes a specific key from a JSON object.",
            inputs=[
                io.String.Input(
                    "json_data",
                    default="{}",
                    multiline=True,
                    display_name="JSON Data",
                    tooltip="The JSON string to modify.",
                ),
                io.String.Input(
                    "key_path",
                    default=".key_to_delete",
                    display_name="Key Path",
                    tooltip="The jq path for the key to remove, e.g., '.metadata.unwanted_tag'.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Result"),
            ],
        )

    @classmethod
    def execute(cls, json_data: str, key_path: str) -> io.NodeOutput:
        json_data = json_data or "{}"
        if not json_data.strip():
            return io.NodeOutput("{}")
            
        key_path = (key_path or "").strip()
        if not key_path:
            return io.NodeOutput(json_data)

        jq_path = find_jq()
        if not jq_path:
            raise FileNotFoundError(
                "The 'jq' CLI tool was not found in the system PATH or the extension's 'bin' folder."
            )

        # Build jq command: jq 'del(.key)'
        filter_expr = f"del({key_path})"
        cmd = [jq_path, filter_expr]

        try:
            result = subprocess.run(
                cmd,
                input=json_data,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            return io.NodeOutput(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"jq failed (exit code {e.returncode}): {e.stderr or e.stdout or str(e)}"
            )
