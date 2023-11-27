from pydantic import BaseModel
from typing import Optional
from PIL import Image
import torch


class Config(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    lcm_model_name: str = "SimianLuo/LCM_Dreamshaper_v7"
    output_dir: str = ""
    torch_device: str = "mps"  # Adjust based on your hardware
    torch_dtype: str = "float16"  # "float16" if using FP16
    prompt: str = "A painting of a cat"  # Adjust this to closely describe the input image
    image: Optional[Image.Image] = None
    width: int = 512  # Match to input image
    height: int = 512  # Match to input image
    steps: int = 4
    seed: int = 0
    num_images_per_prompt: int = 1
    lcm_origin_steps: int = 50
    guidance_scale: float = 1.0  # Lower for closer resemblance
    output_type: str = "pil"
    strength: float = 0.6  # Lower for closer resemblance to input
    randomize_seed: bool = True
    image2image: bool = False  # Set to True for img2img
    use_fp16: bool = True  # Set to True if your hardware supports it

    @property
    def device(self) -> torch.device:
        return torch.device(self.torch_device)

    @property
    def dtype(self) -> torch.dtype:
        return torch.float32 if self.torch_dtype == "float32" else torch.float16
