from diffusers import LatentConsistencyModelPipeline
import torch
from PIL import Image
import os
from ai_render.core.base_render_engine import BaseRenderEngine
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

class RenderFromText(BaseRenderEngine):
    def load_model(self) -> LatentConsistencyModelPipeline:
        model = LatentConsistencyModelPipeline.from_pretrained(self.config.lcm_model_name)
        model.to(torch_device=self.config.torch_device, torch_dtype=torch.float32)
        return model

    def render(self) -> Image.Image:
        seed = self.config.seed or int.from_bytes(os.urandom(2), "big")
        torch.manual_seed(seed)

        result = self.model(
            prompt=self.config.prompt, width=self.config.width, height=self.config.height,
            guidance_scale=self.config.guidance_scale, num_inference_steps=self.config.steps,
            num_images_per_prompt=self.config.num_images_per_prompt, 
            lcm_origin_steps=self.config.lcm_origin_steps,
            output_type=self.config.output_type,
        ).images[0]

        return result
