from typing import Any
from src.core.engine import Engine
from src.core.event import EventManager
from src.core.scene import SceneManager
from src.core.window import Window
from src.graphics.camera import Camera
from src.bootstrap.engine_builder import EngineBuilder


class Bootstrap:
    def __init__(self, builder: EngineBuilder) -> None:
        self.builder = builder

    def build(self) -> Engine:
        events = EventManager()

        window = Window(
            self.builder.window.get("width", 1280),
            self.builder.window.get("height", 720),
            self.builder.window.get("title", "Ashe of Heroes"),
            events
        )
        camera = Camera(
            self.builder.camera.get("width", 1280),
            self.builder.camera.get("height", 720),
            self.builder.camera.get("fov", 45.0),
            self.builder.camera.get("near", 0.1),
            self.builder.camera.get("far", 100.0),
        )
        services: dict[str, Any] = {
            "events": events,
            "window": window,
            "camera": camera,
        }

        for name, factory in self.builder.factories.items():
            if factory is None:
                continue
            try:
                services[name] = factory(services)
            except TypeError:
                services[name] = factory()

        scenes = SceneManager(events)
        services["scenes"] = scenes

        for key, scene_factory in self.builder.scenes.items():
            scenes.register(key, lambda sf=scene_factory: sf(services))

        if self.builder.initial_scene:
            scenes.push_by_key(self.builder.initial_scene)

        return Engine(
            window=window,
            events=events,
            scenes=scenes,
            camera=camera,
            services=services,
        )
