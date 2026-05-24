from typing import Callable, Any
from src.logic.card_deck import CardDeck
from src.logic.game_state import GameState


class EngineBuilder:

    def __init__(self):
        self.window: dict[str, Any] = {}
        self.camera: dict[str, Any] = {}
        self.factories: dict[str, Callable[..., Any]] = {}
        self.scenes: dict[str, Callable[..., Any]] = {}
        self.initial_scene: str | None = None
        self.game_state = None

    def init_game(self):
        self.game_state = GameState()
        return self

    def set_window(self, width: int, height: int, title: str) -> EngineBuilder:
        self.window = {"width": width, "height": height, "title": title}
        return self

    def set_camera(self, fov: float, near: float, far: float) -> EngineBuilder:
        self.camera = {
            "width": self.window.get("width"),
            "height": self.window.get("height"),
            "fov": fov,
            "near": near,
            "far": far,
        }
        return self

    def use_animation_queue(self, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories["animation_queue"] = factory
        return self

    def use(self, name: str, factory: Callable[..., Any]) -> EngineBuilder:
        self.factories[name] = factory
        return self

    def add_scene(self, key: str, factory: Callable[..., Any]) -> EngineBuilder:
        self.scenes[key] = factory
        return self

    def set_initial_scene(self, key: str) -> EngineBuilder:
        self.initial_scene = key
        return self
