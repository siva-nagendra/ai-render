from typing import Union
from ai_render.config.config import Config
from diffusers import LatentConsistencyModelPipeline, LatentConsistencyModelImg2ImgPipeline

PipelineType = Union[LatentConsistencyModelPipeline, LatentConsistencyModelImg2ImgPipeline]

class BaseRenderEngine:
    def __init__(self, config: Config):
        self.config = config
        self.model = self.load_model()

    def load_model(self) -> PipelineType:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def render(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")
