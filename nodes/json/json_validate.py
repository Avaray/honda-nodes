import json
from comfy_api.latest import io

class HondaJSONValidate(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_JSONValidate",
            display_name="📑 JSON Validate",
            category="⚡️ Honda Nodes/📑 JSON",
            description="Validates whether a given string is valid JSON format.",
            inputs=[
                io.String.Input(
                    "json_data",
                    default="{}",
                    multiline=True,
                    force_input=True,
                    display_name="JSON Data",
                    tooltip="The JSON string to validate.",
                ),
            ],
            outputs=[
                io.Boolean.Output(display_name="Is Valid"),
            ],
        )

    @classmethod
    def execute(cls, json_data: str) -> io.NodeOutput:
        json_data = json_data or ""
        is_valid = False
        
        if json_data.strip():
            try:
                json.loads(json_data)
                is_valid = True
            except ValueError:
                is_valid = False
                
        return io.NodeOutput(is_valid)
