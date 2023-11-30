from pydantic import BaseModel
from typing import Optional
import torch
from PIL import Image

class Config(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    text2img_model: str = "SimianLuo/LCM_Dreamshaper_v7"
    img2img_model: str = "SimianLuo/LCM_Dreamshaper_v7"
    inpainting_model: str = "runwayml/stable-diffusion-inpainting"
    
    output_dir: str = ""
    prompt: str = ""
    image: Optional[Image.Image] = None
    mask_image: Optional[Image.Image] = None
    width: int = 768
    height: int = 768
    steps: int = 10
    seed: int = 12345
    randomize_seed: bool = True
    num_images_per_prompt: int = 1
    guidance_scale: float = 1.0  # Lower for closer resemblance
    output_type: str = "pil"
    strength: float = 0.6  # Lower for closer resemblance to input
    torch_device: str = "mps"  #options: cpu, cuda, mps
    use_fp16: bool = False
    render_mode: str = "text2img"
    safety_checker: bool = True
    mask_path: str = "/Users/siva/devel/ai-render/data/mask.jpg"

    @property
    def render_mode(self) -> str:
        return self._render_mode

    @render_mode.setter
    def render_mode(self, value: str) -> None:
        if value not in ["text2img", "img2img", "inpainting"]:
            raise ValueError("Invalid render mode. Must be either 'text2img' or 'img2img' or 'inpainting'.")
        self._render_mode = value

    @property
    def device(self) -> torch.device:
        return torch.device(self.torch_device)

    @property
    def dtype(self) -> torch.dtype:
        return torch.float16 if self.use_fp16 and self.device.type == 'cuda' else torch.float32
