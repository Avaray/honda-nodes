import os
import fnmatch
from comfy_api.latest import io

class HondaListFiles(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Honda_ListFiles",
            display_name="📂 List Files",
            category="⚡️ Honda Nodes/📂 File System",
            description="Lists files in a directory matching a filter.",
            inputs=[
                io.String.Input(
                    "directory",
                    default="",
                    display_name="Directory",
                    tooltip="Absolute path to the directory.",
                ),
                io.Boolean.Input(
                    "recursive",
                    default=False,
                    display_name="Recursive",
                ),
                io.Int.Input(
                    "max_depth",
                    default=-1,
                    display_name="Max Depth",
                    tooltip="Maximum depth for recursive search. -1 for infinite.",
                ),
                io.String.Input(
                    "file_filter",
                    default="*",
                    display_name="Filter",
                    tooltip="Glob pattern to filter files (e.g., *.png).",
                ),
            ],
            outputs=[
                io.String.Output(display_name="Files"),
            ],
        )

    @classmethod
    def execute(cls, directory: str, recursive: bool, max_depth: int, file_filter: str) -> io.NodeOutput:
        directory = (directory or "").strip()
        file_filter = (file_filter or "*").strip()
        matched_files = []

        if directory and os.path.exists(directory):
            if not recursive:
                for entry in os.scandir(directory):
                    if entry.is_file() and fnmatch.fnmatch(entry.name, file_filter):
                        matched_files.append(entry.path)
            else:
                start_depth = directory.rstrip(os.path.sep).count(os.path.sep)
                for root, dirs, files in os.walk(directory):
                    current_depth = root.rstrip(os.path.sep).count(os.path.sep)
                    depth = current_depth - start_depth
                    if max_depth >= 0 and depth >= max_depth:
                        del dirs[:]  # Stop descending
                    for name in files:
                        if fnmatch.fnmatch(name, file_filter):
                            matched_files.append(os.path.join(root, name))

        # Return paths joined by newline
        out_str = "\n".join(matched_files)
        return io.NodeOutput(out_str)
