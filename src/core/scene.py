from abc import ABC, abstractmethod
from collections import deque
from typing import Any
from src.core.event import EventManager


class Scene(ABC):
    def __init__(self, event_manager: EventManager, scene_manager: SceneManager):
        self._events = event_manager
        self._scenes = scene_manager

    @abstractmethod
    def on_enter(self, **params: Any) -> None: ...

    @abstractmethod
    def on_exit(self) -> None: ...

    @abstractmethod
    def on_pause(self) -> None: ...

    @abstractmethod
    def on_resume(self) -> None: ...

    @abstractmethod
    def handle_input(self) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def render(self) -> None: ...


class SceneManager:
    def __init__(self, event_manager: EventManager):
        self.__events = event_manager
        self.__stack: deque[Scene] = deque()
        self.__registered_scenes: dict[str, type[Scene]] = {}

    def register(self, name: str, scene_class: type[Scene]):
        self.__registered_scenes[name] = scene_class

    def change_scene(self, name: str, **params: Any):
        while self.__stack:
            old_scene = self.__stack.pop()
            old_scene.on_exit()

        new_scene = self.__registered_scenes[name](self.__events, self)
        self.__stack.append(new_scene)
        new_scene.on_enter(**params)

    def push_scene(self, name: str, **params: Any):
        if self.__stack:
            self.__stack[-1].on_pause()

        new_scene = self.__registered_scenes[name](self.__events, self)
        self.__stack.append(new_scene)
        new_scene.on_enter(**params)

    def pop_scene(self):
        if self.__stack:
            old_scene = self.__stack.pop()
            old_scene.on_exit()

        if self.__stack:
            self.__stack[-1].on_resume()

    def update(self, dt: float):
        if self.__stack:
            self.__stack[-1].update(dt)

    def render(self):
        for scene in self.__stack:
            scene.render()
