from ai_render.core.render_engine import RenderEngine
from ai_render.config.config import Config
from ai_render.core.utils.exporter import ImageExporter
from PIL import Image
import time
import warnings
from tabulate import tabulate
from ai_render.render_manager.render_thread import RenderThread

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Define the post-render callback function
def post_render_tasks(rendered_images):
    image_exporter = ImageExporter(cfg_instance.output_dir)
    image_paths = [image_exporter.export(img) for img in rendered_images]
    
    # End the timer and calculate render time
    end_time = time.perf_counter()
    render_time = end_time - start_time

    # Create a colorful logging table
    table = [["Render Time", f"{render_time:.4f} seconds"], ["Image Paths", ", ".join(image_paths)]]
    table_str = tabulate(table, headers=["Metric", "Value"], tablefmt="fancy_grid", numalign="center")

    # Print the logging table in the main thread
    print(table_str)

start_time = time.perf_counter()

output_dir = "/Users/siva/devel/houdini"

# Create a config instance
cfg_instance = Config(
    prompt="In the clouds piggy bank with hair",
    output_dir=output_dir,
)
# If using image-to-image rendering, set the image in the config
img2img = False  # Set to True for image-to-image rendering
if img2img:
    img_path = "/Users/siva/devel/ai-render/data/input1.png"
    cfg_instance.image = Image.open(img_path)
    cfg_instance.image2image = True

engine = RenderEngine(cfg_instance)

# a = engine.load_model()
# print(a)
# engine.render()

# Start rendering in a separate thread using RenderThread
render_thread = RenderThread(engine=engine, on_complete_callback=post_render_tasks)
render_thread.start()