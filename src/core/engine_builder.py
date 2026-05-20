from typing import Callable, Any
from src.core import Engine


class EngineBuilder:

    def __init__(self):
        self.window: dict[str, Any] = {}
        self.factories: dict[str, Callable[..., Any]] = {}
        self.scene_reg: dict[str, Callable[..., Any]] = {}
        self.initial_scene: str | None = None

    def add_window(self, width: int, height: int, title: str = "Ashe of Heroes") -> EngineBuilder:
        self.window = {"width": width, "height": height, "title": title}
        return self

    def add_renderer(self, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories["renderer"] = factory
        return self

    def add_textures(self, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories["textures"] = factory
        return self

    def add_camera(self, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories["camera"] = factory
        return self

    def add_animation_queue(self, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories["animation_queue"] = factory
        return self

    def use(self, name: str, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories[name] = factory
        return self

    def add_scene(self, key: str, factory: Callable[..., Any]) -> EngineBuilder:
        self.scene_reg[key] = factory
        return self

    def set_initial_scene(self, key: str) -> EngineBuilder:
        self.initial_scene = key
        return self

    def build(self) -> Engine:
        return Engine.from_builder(self)
