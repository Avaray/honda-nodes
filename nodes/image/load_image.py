import os
import folder_paths
import shutil
import subprocess
from comfy_api.latest import io
from nodes import LoadImage

class HondaLoadImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        
        return io.Schema(
            node_id="Honda_LoadImage",
            display_name="🖼 Load Image",
            category="⚡️ Honda Nodes/🖼 Image",
            description="Loads an image from the input folder and outputs the image data, mask, file path, and metadata as JSON.",
            inputs=[
                io.Combo.Input(
                    "image",
                    options=sorted(files) if files else [],
                    upload=io.UploadType.image,
                    image_folder=io.FolderType.input,
                    display_name="Image",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Image"),
                io.Mask.Output(display_name="Mask"),
                io.String.Output(display_name="Path"),
                io.String.Output(display_name="Metadata"),
            ],
        )

    @classmethod
    def execute(cls, image: str) -> io.NodeOutput:
        # Use standard ComfyUI LoadImage node functionality
        image_tensor, mask_tensor = LoadImage().load_image(image)
        
        # Determine the absolute path of the loaded image
        image_path = folder_paths.get_annotated_filepath(image)
        
        # Find the 'mex' executable
        mex_path = shutil.which("mex")
        if not mex_path:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_bin = os.path.join(current_dir, "bin")
            mex_exe = "mex.exe" if os.name == "nt" else "mex"
            local_mex = os.path.join(local_bin, mex_exe)
            if os.path.exists(local_mex):
                mex_path = local_mex

        metadata_text = ""
        if mex_path and os.path.exists(image_path):
            # Always output JSON format
            cmd = [mex_path, image_path, "-j"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
                metadata_text = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                print(f"[Honda Nodes] Warning: Failed to extract metadata with mex: {e.stderr or e.stdout or str(e)}")
        elif not mex_path:
            print("[Honda Nodes] Warning: 'mex' CLI not found. Skipping metadata extraction.")
        
        return io.NodeOutput(image_tensor, mask_tensor, image_path, metadata_text)
