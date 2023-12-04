import threading
import logging
import warnings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

class RenderThread(threading.Thread):
    def __init__(self, engine, config, on_complete_callback):
        super().__init__()
        self.engine = engine
        self.config = config
        self.on_complete = on_complete_callback
        self._stop_event = threading.Event()
        self.is_running = True

    def run(self):
        logging.info("Starting rendering loop...")
        while not self._stop_event.is_set():
            try:
                self.rendered_image = self.engine.render(self.config)
                if self.rendered_image:
                    logging.info("Rendering completed for one image.")
                    self.on_complete(self.rendered_image)
                else:
                    logging.error("Rendering failed for one image.")
            except Exception as e:
                logging.error(f"Exception during rendering: {e}")
                break
        logging.info("Rendering loop stopped.")

    def stop_rendering(self):
        self._stop_event.set()
        logging.info("Stop signal sent to rendering thread.")
