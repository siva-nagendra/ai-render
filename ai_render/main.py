# It's assumed that these are the correct paths to the modules. If not, adjust accordingly.
from ai_render.core.render_from_text import RenderFromText
from ai_render.core.utils.exporter import ImageExporter
from ai_render.config.config import Config
import time
from tabulate import tabulate
import warnings
import threading

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Define the function to perform rendering.
def render_in_thread(cfg, prompt, width, height, steps, seed):
    engine = RenderFromText(cfg)

    # Start the timer
    start_time = time.perf_counter()

    # Render the image, assuming `render` method only takes `prompt` as an argument.
    # If `render` accepts more arguments, you'll need to adjust the call accordingly.
    image = engine.render(prompt)

    # End the timer
    end_time = time.perf_counter()
    render_time = end_time - start_time

    # Export the image
    image_exporter = ImageExporter(cfg.output_dir)
    image_path = image_exporter.export(image)

    # Create a colorful logging table
    table = [["Render Time", f"{render_time:.4f} seconds"], ["Image Path", image_path]]
    table_str = tabulate(table, headers=["Metric", "Value"], tablefmt="fancy_grid", numalign="center")

    # Print the logging table in the main thread to avoid issues with threading.
    print_safe(table_str)

def print_safe(output):
    """
    This function ensures that the print statement is executed on the main thread.
    This is a placeholder for actual implementation that ensures thread safety.
    """
    print(output)

# Create a config instance with any required parameters
cfg_instance = Config()

# Parameters for the render
prompt = "A red sphere"
width = 512
height = 512
steps = 4
seed = 0

# Start rendering in a separate thread
render_thread = threading.Thread(target=render_in_thread, args=(cfg_instance, prompt, width, height, steps, seed))
render_thread.start()
