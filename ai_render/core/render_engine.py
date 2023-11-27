from diffusers import LatentConsistencyModelPipeline, LatentConsistencyModelImg2ImgPipeline
from typing import Union, List
from ai_render.core.base_render_engine import BaseRenderEngine
from PIL import Image
import torch

class RenderEngine(BaseRenderEngine):
    def load_model(self) -> Union[LatentConsistencyModelPipeline, LatentConsistencyModelImg2ImgPipeline]:
        """Load the appropriate model based on the rendering type."""
        if self.config.image2image:
            self.model = LatentConsistencyModelImg2ImgPipeline.from_pretrained(self.config.lcm_model_name)
        else:
            self.model = LatentConsistencyModelPipeline.from_pretrained(self.config.lcm_model_name)
        
        # Set the device and dtype
        device = torch.device(self.config.torch_device)
        dtype = torch.float16 if self.config.use_fp16 and device.type == 'cuda' else torch.float32

        self.model.to(device=device, dtype=dtype)
        return self.model

    def render(self) -> Union[Image.Image, List[Image.Image]]:
        """Render images based on the configuration."""
        self.set_seed(self.config.seed, self.config.randomize_seed)
        if self.config.image2image:
            return self._render_image_to_image()
        else:
            return self._render_text_to_image()


    def _render_text_to_image(self) -> List[Image.Image]:
        """Render method for text-to-image."""
        self.model = self.load_model()
        return self.model(
            prompt=self.config.prompt,
            width=self.config.width,
            height=self.config.height,
            guidance_scale=self.config.guidance_scale,
            num_inference_steps=self.config.steps,
            num_images_per_prompt=self.config.num_images_per_prompt,
            output_type=self.config.output_type,
            device=self.config.torch_device,
        ).images

    def _render_image_to_image(self) -> List[Image.Image]:
        """Render method for image-to-image."""
        self.model = self.load_model()
        return self.model(
            prompt=self.config.prompt,
            image=self.config.image,
            strength=self.config.strength,
            width=self.config.width,
            height=self.config.height,
            guidance_scale=self.config.guidance_scale,
            num_inference_steps=self.config.steps,
            num_images_per_prompt=self.config.num_images_per_prompt,
            output_type=self.config.output_type,
            device=self.config.torch_device,
        ).images
