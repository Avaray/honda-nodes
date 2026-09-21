import os
import folder_paths
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
            display_name="👁 Load Image",
            category="⚡️ Honda Nodes/👁 Image",
            description="Loads an image from the input folder and outputs the image data, mask, and file path.",
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
            ],
        )

    @classmethod
    def execute(cls, image: str) -> io.NodeOutput:
        # Use standard ComfyUI LoadImage node functionality
        image_tensor, mask_tensor = LoadImage().load_image(image)
        
        # Determine the absolute path of the loaded image
        image_path = folder_paths.get_annotated_filepath(image)
        
        return io.NodeOutput(image_tensor, mask_tensor, image_path)
