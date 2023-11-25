import os
import torch
import time
from diffusers import DiffusionPipeline

class Predictor:
    def __init__(self):
        self.pipe = self._load_model()

    def _load_model(self) -> DiffusionPipeline:
        """
        Load the pre-trained model.
        Returns:
            DiffusionPipeline: The loaded model.
        """
        model = DiffusionPipeline.from_pretrained(
            "SimianLuo/LCM_Dreamshaper_v7",
        )
        model.to(torch_device="cpu", torch_dtype=torch.float32).to('mps:0')
        return model

    def predict(self, prompt: str, width: int, height: int, steps: int, seed: int = None) -> str:
        """
        Generate an image based on the given prompt.
        Args:
            prompt (str): The prompt for image generation.
            width (int): The width of the generated image.
            height (int): The height of the generated image.
            steps (int): The number of inference steps.
            seed (int, optional): The seed for random number generation. Defaults to None.
        Returns:
            str: The path to the saved output image.
        """
        seed = seed or int.from_bytes(os.urandom(2), "big")
        print(f"Using seed: {seed}")
        torch.manual_seed(seed)

        result = self.pipe(
            prompt=prompt, width=width, height=height,
            guidance_scale=8.0, num_inference_steps=steps,
            num_images_per_prompt=1, lcm_origin_steps=50,
            output_type="pil"
        ).images[0]

        return self._save_result(result)

    def predict_from_file(self, prompt_file: str, width: int, height: int, steps: int, seed: int = None, continuous: bool = False):
        """
        Generate images based on prompts from a file.
        Args:
            prompt_file (str): The path to the file containing prompts.
            width (int): The width of the generated images.
            height (int): The height of the generated images.
            steps (int): The number of inference steps.
            seed (int, optional): The seed for random number generation. Defaults to None.
            continuous (bool, optional): Whether to continuously generate images. Defaults to False.
        """
        with open(prompt_file, 'r') as file:
            prompts = file.readlines()

        while True:
            for prompt in prompts:
                prompt = prompt.strip()
                output_path = self.predict(prompt, width, height, steps, seed)
                print(f"Output image saved for '{prompt}' to: {output_path}")

            if not continuous:
                return

    def _save_result(self, result) -> str:
        """
        Save the generated image.
        Args:
            result: The generated image.
        Returns:
            str: The path to the saved image.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_dir = "/Users/sivanagendra/Documents/devel/houdini-lcm/output/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f"out-{timestamp}.png")
        result.save(output_path)
        return output_path

def main(prompt: str, prompts: str, width: int, height: int, steps: int, seed: int, continuous: bool):
    """
    The main function to run the image generation process.
    Args:
        prompt (str): The prompt for image generation.
        prompts (str): The path to the file containing prompts, or None.
        width (int): The width of the generated images.
        height (int): The height of the generated images.
        steps (int): The number of inference steps.
        seed (int): The seed for random number generation.
        continuous (bool): Whether to continuously generate images.
    """
    predictor = Predictor()

    if prompts:
        predictor.predict_from_file(prompts, width, height, steps, seed, continuous)
    else:
        output_path = predictor.predict(prompt, width, height, steps, seed)
        print(f"Output image saved to: {output_path}")

# if __name__ == "__main__":
prompt = "A painting of a dog"
prompts = None  # or "Your file path here"
width = 512
height = 512
steps = 8
seed = None  # or your seed here
continuous = False  # or True

main(prompt, prompts, width, height, steps, seed, continuous)