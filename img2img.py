from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional
import uuid
from diffusers.pipelines import LatentConsistencyModelImg2ImgPipeline
from utils.imgs2gif import images_to_gif, load_images_from_folder
from diffusers.image_processor import PipelineImageInput
import os
import random
import time
import numpy as np
from PIL import Image, PngImagePlugin
import torch
import os
from PIL import Image

MAX_SEED = np.iinfo(np.int32).max

# dreamshaper_model = "Lykon/dreamshaper-7"
dreamshaper_model = "SimianLuo/LCM_Dreamshaper_v7"

def randomize_seed_fn(seed: int, randomize_seed: bool) -> int:
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    return seed


def save_image(img, metadata: dict, save_dir: str = None):
    
    Path(save_dir).mkdir(exist_ok=True, parents=True)
    seed = metadata["seed"]
    unique_id = uuid.uuid4()
    filename = save_dir + f"{unique_id}-{seed}" + ".png"

    meta_tuples = [(k, str(v)) for k, v in metadata.items()]
    png_info = PngImagePlugin.PngInfo()
    for k, v in meta_tuples:
        png_info.add_text(k, v)
    img.save(filename, pnginfo=png_info)

    return filename


def save_images(image_array, metadata: dict, save_dir: str = None):
    paths = []
    with ThreadPoolExecutor() as executor:
        paths = list(executor.map(lambda img: save_image(img, metadata, save_dir=save_dir), image_array))
    return paths


def generate_i2i(
    prompt: str,
    frames: list[PipelineImageInput] = None,
    strength: float = 0.6,
    seed: int = 0,
    guidance_scale: float = 1,
    num_inference_steps: int = 4,
    num_images: int = 1,
    randomize_seed: bool = True,
    use_fp16: bool = False,
    use_torch_compile: bool = False,
    use_cpu: bool = False,
    save_dir: str = None,
    width: Optional[int] = 512,
    height: Optional[int] = 512,
) -> Image.Image:
    seed = randomize_seed_fn(seed, randomize_seed)
    torch.manual_seed(seed)

    selected_device = "mps" # Change it later

    if use_cpu:
        selected_device = "cpu"
        if use_fp16:
            use_fp16 = False
            print("LCM warning: running on CPU, overrode FP16 with FP32")

    pipe = LatentConsistencyModelImg2ImgPipeline.from_pretrained(dreamshaper_model)

    if use_fp16:
        pipe.to(torch_device=selected_device, torch_dtype=torch.float16)
    else:
        pipe.to(torch_device=selected_device, torch_dtype=torch.float32)

    start_time = time.time()
    results = []
    for frame in frames:
        width, height = frame.size
        result = pipe(
            prompt=prompt,
            image=frame,
            strength=strength,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            num_images_per_prompt=1,
            original_inference_steps=50,
            output_type="pil",
            device = selected_device
        ).images
        paths = save_images(result, metadata={"prompt": prompt, "seed": seed, "width": width,
                            "height": height, "guidance_scale": guidance_scale, "num_inference_steps": num_inference_steps}, 
                            save_dir=save_dir)
        results.extend(result)

    elapsed_time = time.time() - start_time
    print("LCM inference time: ", elapsed_time, "seconds")
    return paths, seed


# prompt = "A wedding cake delicious and colorful in bright pink and white"
prompt = "A furry black and white cat with a red bow tie in matrix movie"

folder_path = "/Users/siva/devel/houdini-lcm/input/img2img/lucifer/render/"
seq = os.listdir(folder_path)
# frames = [Image.open(os.path.join(folder_path, x)) for x in seq]
frames = [Image.open(os.path.join(folder_path, seq[5]))]

save_dir = "/Users/siva/devel/houdini-lcm/output/img2img/lucifer_01/"

output_path, seed = generate_i2i(prompt=prompt, frames=frames, save_dir=save_dir)
print("success")
print(output_path, seed)


# # make gif
# folder_path, file_name = os.path.split(output_path[0])
# print("Generating gif")
# images = load_images_from_folder(folder_path)
# images_to_gif(images, 5, output_filename=)

# print("Gif success")

