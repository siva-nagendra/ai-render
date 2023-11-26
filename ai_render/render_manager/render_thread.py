import threading
import logging
import warnings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

class RenderThread(threading.Thread):
    def __init__(self, engine, on_complete_callback):
        super().__init__()
        self.engine = engine
        self.on_complete = on_complete_callback
        self.rendered_image = None

    def run(self):
        try:
            logging.info("Rendering...")
            self.rendered_image = self.engine.render()
            logging.info("Rendering completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during rendering: {e}")
        finally:
            self.on_complete(self.rendered_image)