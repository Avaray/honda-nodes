"""
"JSON Set Key" - Schema V3 node definition.

Sets or updates a key in a JSON object using the 'jq' CLI tool.
"""

import subprocess
from comfy_api.latest import io
from .utils import find_jq


class HondaJSONSetKey(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_JSONSetKey",
            display_name="JSON Set Key",
            category="⚡️ Honda Nodes/🔣 JSON",
            description="Sets or updates a value at a specific key path in a JSON string.",
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
                    default=".new_key",
                    display_name="Key Path",
                    tooltip="The jq path for the key, e.g., '.metadata.title' or '.name'.",
                ),
                io.String.Input(
                    "value",
                    default="my value",
                    multiline=True,
                    display_name="Value",
                    tooltip="The value to set.",
                ),
                io.Boolean.Input(
                    "is_json_value",
                    default=False,
                    display_name="Is JSON/Number?",
                    tooltip="Enable if the value is a number, boolean, or raw JSON object instead of a string.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Result"),
            ],
        )

    @classmethod
    def execute(cls, json_data: str, key_path: str, value: str, is_json_value: bool) -> io.NodeOutput:
        json_data = json_data or "{}"
        if not json_data.strip():
            json_data = "{}"
            
        key_path = (key_path or ".").strip()
        value = value or ""

        jq_path = find_jq()
        if not jq_path:
            raise FileNotFoundError(
                "The 'jq' CLI tool was not found in the system PATH or the extension's 'bin' folder."
            )

        # Build jq command: jq --arg val "value" '.key = $val'
        # or jq --argjson val '123' '.key = $val'
        arg_flag = "--argjson" if is_json_value else "--arg"
        
        # If is_json_value is True, we must ensure value is valid JSON to pass to --argjson. 
        # If it's empty, we'll default to "null"
        if is_json_value and not value.strip():
            value = "null"
            
        cmd = [
            jq_path,
            arg_flag, "val", value,
            f"{key_path} = $val"
        ]

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
