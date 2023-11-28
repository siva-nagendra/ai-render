from abc import ABC, abstractmethod
from ai_render.config import Config
import torch
from PIL import Image
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

class BaseRenderEngine(ABC):
    def __init__(self, config: Config):
        self.config = config
        self.model = None

    @abstractmethod
    def load_model(self):
        """Load the model specific to the render engine."""
        pass

    @abstractmethod
    def render(self, *args, **kwargs) -> Image.Image:
        """Render method to be implemented by subclasses."""
        pass

    def set_seed(self, seed: int, randomize_seed: bool):
        """Set the seed for reproducibility or randomization."""
        if randomize_seed:
            seed = torch.randint(high=torch.iinfo(torch.int32).max, size=(1,)).item()
        torch.manual_seed(seed)
        self.config.seed = seed