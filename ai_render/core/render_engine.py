from diffusers import AutoPipelineForText2Image, AutoPipelineForImage2Image, AutoPipelineForInpainting
from ai_render.core.base_render_engine import BaseRenderEngine
from PIL import Image
from typing import List, Union

class RenderEngine(BaseRenderEngine):
    def load_model(self) -> Union[AutoPipelineForText2Image, AutoPipelineForImage2Image, AutoPipelineForInpainting]:
        """
        Load the AI model based on the configuration.
        """
        if self.config.render_mode=="img2img":
            self.model = AutoPipelineForImage2Image.from_pretrained(self.config.img2img_model, requires_safety_checker=self.config.safety_checker)
        elif self.config.render_mode=="inpainting":
            self.model = AutoPipelineForInpainting.from_pretrained(self.config.inpainting_model, requires_safety_checker=self.config.safety_checker)
        else:
            self.model = AutoPipelineForText2Image.from_pretrained(self.config.text2img_model, requires_safety_checker=self.config.safety_checker)
        self.model.to(device=self.config.device, dtype=self.config.dtype)
        return self.model

    def render(self, model) -> List[Image.Image]:
        """
        Render the image based on the configuration.
        """
        self.model = model
        self.set_seed(self.config.seed, self.config.randomize_seed)

        if self.config.render_mode=="img2img":
            print("Rendering image to image")
            return self._render_img2img()
        if self.config.render_mode=="inpainting":
            print("Rendering inpainting")
            return self._render_inpainting()
        else:
            print("Rendering text to image")
            return self._render_txt2img()

    def _render_txt2img(self) -> List[Image.Image]:
        """
        Render method for text-to-image.
        """
        return self.model(
            prompt=self.config.prompt,
            width=self.config.width,
            height=self.config.height,
            guidance_scale=self.config.guidance_scale,
            num_inference_steps=self.config.steps,
            num_images_per_prompt=self.config.num_images_per_prompt,
            device=self.config.torch_device,
        ).images

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
    
    def _render_inpainting(self) -> List[Image.Image]:
        """
        Renders the image based on mask and image.
        """
        return self.model(
            prompt=self.config.prompt,
            image=self.config.image,
            mask_image=self.config.mask,
            strength=self.config.strength,
            width=self.config.width,
            height=self.config.height,
            guidance_scale=self.config.guidance_scale,
            num_inference_steps=self.config.steps,
            num_images_per_prompt=self.config.num_images_per_prompt,
            device=self.config.torch_device,
        ).images
