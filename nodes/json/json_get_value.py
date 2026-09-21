"""
"JSON Get Value" - Schema V3 node definition.

Uses the 'jq' CLI tool to extract values from JSON strings.
"""

import subprocess
from comfy_api.latest import io
from .utils import find_jq


class HondaJSONGetValue(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_JSONGetValue",
            display_name="JSON Get Value",
            category="⚡️ Honda Nodes/🔣 JSON",
            description="Extracts a value from a JSON string using the 'jq' CLI tool.",
            inputs=[
                io.String.Input(
                    "json_data",
                    default="{}",
                    multiline=True,
                    display_name="JSON Data",
                    tooltip="The JSON string to process.",
                ),
                io.String.Input(
                    "jq_filter",
                    default=".",
                    display_name="jq Filter",
                    tooltip="The jq filter to apply, e.g., '.data[0].id' or '.name'.",
                ),
                io.Boolean.Input(
                    "raw_output",
                    default=True,
                    display_name="Raw Output (-r)",
                    tooltip="If enabled, outputs raw strings instead of JSON-encoded strings (adds -r flag).",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Result"),
            ],
        )

    @classmethod
    def execute(cls, json_data: str, jq_filter: str, raw_output: bool) -> io.NodeOutput:
        json_data = json_data or ""
        if not json_data.strip():
            return io.NodeOutput("")
            
        jq_filter = (jq_filter or ".").strip()

        jq_path = find_jq()
        if not jq_path:
            raise FileNotFoundError(
                "The 'jq' CLI tool was not found in the system PATH or the extension's 'bin' folder. "
                "Download it and place the executable in your PATH or in the honda-nodes/bin/ folder."
            )

        cmd = [jq_path]
        if raw_output:
            cmd.append("-r")
        cmd.append(jq_filter)

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
