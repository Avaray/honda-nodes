"""
"JSON Merge" - Schema V3 node definition.

Merges two JSON objects together deeply using the 'jq' CLI tool.
"""

import subprocess
from comfy_api.latest import io
from .utils import find_jq


class HondaJSONMerge(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_JSONMerge",
            display_name="JSON Merge",
            category="⚡️ Honda Nodes/🔣 JSON",
            description="Merges two JSON objects deeply.",
            inputs=[
                io.String.Input(
                    "json_a",
                    default="{}",
                    multiline=True,
                    display_name="JSON A",
                    tooltip="The first JSON object.",
                ),
                io.String.Input(
                    "json_b",
                    default="{}",
                    multiline=True,
                    display_name="JSON B",
                    tooltip="The second JSON object. Its keys will overwrite keys in JSON A.",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Result"),
            ],
        )

    @classmethod
    def execute(cls, json_a: str, json_b: str) -> io.NodeOutput:
        json_a = json_a or "{}"
        json_b = json_b or "{}"
        
        if not json_a.strip(): json_a = "{}"
        if not json_b.strip(): json_b = "{}"

        jq_path = find_jq()
        if not jq_path:
            raise FileNotFoundError(
                "The 'jq' CLI tool was not found in the system PATH or the extension's 'bin' folder."
            )

        # Build jq command: jq -s '.[0] * .[1]'
        # -s (slurp) reads multiple JSON objects into a single array
        cmd = [jq_path, "-s", ".[0] * .[1]"]
        
        # Combine the two JSON objects with a newline so jq slurps them as an array of two elements
        combined_input = f"{json_a}\n{json_b}"

        try:
            result = subprocess.run(
                cmd,
                input=combined_input,
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
