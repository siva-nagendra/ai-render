from ai_render.core.base_render_engine import BaseRenderEngine
from ai_render.config.config import Config
from diffusers import LatentConsistencyModelImg2ImgPipeline
from PIL import Image
import torch
from typing import List, Tuple
import logging
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


class RenderFromImage(BaseRenderEngine):
    def load_model(self) -> LatentConsistencyModelImg2ImgPipeline:
        model = LatentConsistencyModelImg2ImgPipeline.from_pretrained(self.config.lcm_model_name)
        model.to(torch_device=self.config.torch_device, torch_dtype=self.config.torch_dtype)
        return model

    def render(self, frames: List[Image.Image], image_exporter) -> Tuple[List[str], int]:
        self._set_seed(self.config.seed, self.config.randomize_seed)
        results = []
        save_paths = []
        
        for frame in frames:
            result = self.model(
                prompt=self.config.prompt,
                image=frame,
                strength=self.config.strength,
                width=self.config.width,
                height=self.config.height,
                guidance_scale=self.config.guidance_scale,
                num_inference_steps=self.config.steps,
                num_images_per_prompt=self.config.num_images_per_prompt,
                output_type=self.config.output_type,
                device=self.config.torch_device,
            ).images
            paths = [image_exporter.export(img) for img in result]
            results.extend(result)
            save_paths.extend(paths)

        return save_paths, self.config.seed

    def _set_seed(self, seed: int, randomize_seed: bool):
        if randomize_seed:
            seed = torch.randint(high=torch.iinfo(torch.int32).max, size=(1,)).item()
        torch.manual_seed(seed)
        self.config.seed = seed