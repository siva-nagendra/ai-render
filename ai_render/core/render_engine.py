from diffusers import AutoPipelineForImage2Image
from PIL import Image
from typing import List

class RenderEngine():
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.model = self.load_model()

    def load_model(self) -> AutoPipelineForImage2Image:
        """
        Load the AI model based on the configuration.
        """
        self.model = AutoPipelineForImage2Image.from_pretrained(self.config.img2img_model, requires_safety_checker=self.config.safety_checker)
        return self.model

    def render(self, config) -> List[Image.Image]:
        """
        Render the image based on the configuration.
        """
        self.config = config
        return self._render_img2img()

    def _render_img2img(self) -> List[Image.Image]:
        """
        Render method for image-to-image.
        """
        return self.model(
            prompt=self.config.prompt,
            image=self.config.image,
            strength=self.config.strength,
            width=self.config.width,
            height=self.config.height,
            guidance_scale=self.config.guidance_scale,
            num_inference_steps=self.config.steps,
            num_images_per_prompt=self.config.num_images_per_prompt,
            device=self.config.torch_device,
        ).images
