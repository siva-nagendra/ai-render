# Test script for the render engine

from ai_render.core.render_engine import RenderEngine
from ai_render.config import Config
from ai_render.core.exporter import ImageExporter
from PIL import Image
import time
import warnings
from tabulate import tabulate
from ai_render.core.render_thread import RenderThread

warnings.filterwarnings("ignore", category=FutureWarning)

def post_render_tasks(rendered_images):
    image_exporter = ImageExporter(cfg_instance.output_dir)
    image_paths = [image_exporter.export(img) for img in rendered_images]
    
    end_time = time.perf_counter()
    render_time = end_time - start_time

    table = [["Render Time", f"{render_time:.4f} seconds"], ["Image Paths", ", ".join(image_paths)]]
    table_str = tabulate(table, headers=["Metric", "Value"], tablefmt="fancy_grid", numalign="center")

    print(table_str)

start_time = time.perf_counter()

output_dir = "/Users/siva/devel/houdini"

cfg_instance = Config(
    prompt="In the clouds piggy bank with hair",
    output_dir=output_dir,
)

cfg_instance.render_mode = "img2img"
engine_test = False

if cfg_instance.render_mode == "img2img":
    img_path = "/Users/siva/devel/ai-render/data/input1.png"
    cfg_instance.image = Image.open(img_path)
    cfg_instance.render_mode = "img2img"

engine = RenderEngine(cfg_instance)


if engine_test:
    model = engine.load_model()
    print(f"Model loaded: {model}")
    render = engine.render()
    print(f"Rendered image: {render}")
else:
    render_thread = RenderThread(engine=engine, on_complete_callback=post_render_tasks)
    render_thread.start()