# Test script for the render engine

from ai_render.core.render_engine import RenderEngine
from ai_render.config import Config
from ai_render.core.exporter import ImageExporter
import time
import warnings
from tabulate import tabulate
from ai_render.core.render_thread import RenderThread
from diffusers.utils import load_image, make_image_grid

warnings.filterwarnings("ignore", category=FutureWarning)

def post_render_tasks(rendered_images):
    rendered_images = [make_image_grid([cfg_instance.image, image], rows=1, cols=2) for image in rendered_images]
    image_exporter = ImageExporter(cfg_instance.output_dir)
    image_paths = [image_exporter.save_image(img) for img in rendered_images]
    
    end_time = time.perf_counter()
    render_time = end_time - start_time

    table = [["Render Time", f"{render_time:.4f} seconds"], ["Image Paths", ", ".join(image_paths)]]
    table_str = tabulate(table, headers=["Metric", "Value"], tablefmt="fancy_grid", numalign="center")

    # [make_image_grid([cfg_instance.image, image], rows=1, cols=2) for image in rendered_images]

    print(table_str)

start_time = time.perf_counter()

output_dir = "/Users/siva/devel/houdini"

img_path = "/Users/siva/devel/houdini/input/in-20231128-161915.jpg"

cfg_instance = Config(
    prompt="A blue grass field in the middle of a rainforest",
    image=load_image(img_path),
    output_dir=output_dir,
)

engine = RenderEngine(cfg_instance)


# model = engine.load_model()
# print(f"Model loaded: {model}")
# render = engine.render(model=model)
# print(f"Rendered image: {render}")
render_thread = RenderThread(engine=engine, config=cfg_instance, on_complete_callback=post_render_tasks)
render_thread.start()