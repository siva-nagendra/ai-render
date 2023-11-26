from pydantic import BaseModel

class Config(BaseModel):
    lcm_model_name: str = "SimianLuo/LCM_Dreamshaper_v7"
    output_dir: str = ""
    torch_device: str = "cpu"
    torch_dtype: str = "float32"
    prompt: str = "A painting of a cat"
    width: int = 512
    height: int = 512
    steps: int = 4
    seed: int = 0
    num_images_per_prompt: int = 1
    lcm_origin_steps: int = 50
    guidance_scale: float = 8.0
    output_type: str = "pil"