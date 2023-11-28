from pydantic import BaseModel
from typing import Optional
from PIL import Image
import torch

class Config(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    text2img_model: str = "SimianLuo/LCM_Dreamshaper_v7"
    img2img_model: str = "SimianLuo/LCM_Dreamshaper_v7"
    output_dir: str = ""
    prompt: str = ""
    image: Optional[Image.Image] = None
    width: int = 512
    height: int = 512
    steps: int = 4
    seed: int = 0
    randomize_seed: bool = False
    num_images_per_prompt: int = 1
    guidance_scale: float = 1.0  # Lower for closer resemblance
    output_type: str = "pil"
    strength: float = 0.6  # Lower for closer resemblance to input
    torch_device: str = "mps"  #options: cpu, cuda, mps
    use_fp16: bool = False
    render_mode: str = "text2img"

    @property
    def render_mode(self) -> str:
        return self._render_mode

    @render_mode.setter
    def render_mode(self, value: str) -> None:
        if value not in ["text2img", "img2img"]:
            raise ValueError("Invalid render mode. Must be either 'text2img' or 'img2img'.")
        self._render_mode = value

    @property
    def device(self) -> torch.device:
        return torch.device(self.torch_device)

    @property
    def dtype(self) -> torch.dtype:
        return torch.float16 if self.use_fp16 and self.device.type == 'cuda' else torch.float32
