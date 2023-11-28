from diffusers import AutoPipelineForText2Image, AutoPipelineForImage2Image
from ai_render.core.base_render_engine import BaseRenderEngine
from PIL import Image
from typing import List, Union

class RenderEngine(BaseRenderEngine):
    def load_model(self) -> Union[AutoPipelineForText2Image, AutoPipelineForImage2Image]:
        """
        Load the AI model based on the configuration.
        """
        if self.config.render_mode=="img2img":
            self.model = AutoPipelineForImage2Image.from_pretrained(self.config.img2img_model)
        else:
            self.model = AutoPipelineForText2Image.from_pretrained(self.config.text2img_model)
        self.model.to(device=self.config.device, dtype=self.config.dtype)
        return self.model

    def render(self) -> List[Image.Image]:
        """
        Render the image based on the configuration..
        """
        self.set_seed(self.config.seed, self.config.randomize_seed)

        if self.config.render_mode=="img2img":
            print("Rendering image to image")
            return self._render_img2img()
        else:
            print("Rendering text to image")
            return self._render_txt2img()

    def _render_txt2img(self) -> List[Image.Image]:
        """
        Render method for text-to-image.
        """
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

    def _render_img2img(self) -> List[Image.Image]:
        """
        Render method for image-to-image.
        """
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
