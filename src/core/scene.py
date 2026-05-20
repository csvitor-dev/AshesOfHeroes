from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Callable
from src.core.event import EventManager


class SceneManager:
    def __init__(self, event_manager: EventManager):
        self.__events = event_manager
        self.__stack: deque[Scene] = deque()
        self.__registry: dict[str,  Callable[..., Scene]] = {}

    def register(self, key: str, factory: Callable[..., Scene]) -> None:
        self.__registry[key] = factory

    def push_by_key(self, key: str) -> None:
        if key not in self.__registry:
            raise KeyError(f"Cena '{key}' não registrada.")
        self.push_scene(self.__registry[key]())

    def push_scene(self, scene: Scene) -> None:
        if self.__stack:
            self.__stack[-1].on_pause()
        self.__stack.append(scene)
        scene.on_enter()

    def change_scene(self, name: str, **params: Any):
        while self.__stack:
            old_scene = self.__stack.pop()
            old_scene.on_exit()

        new_scene = self.__registry[name](self.__events, self)
        self.__stack.append(new_scene)
        new_scene.on_enter(**params)

    def pop_scene(self):
        if self.__stack:
            self.__stack.pop().on_exit()

        if self.__stack:
            self.__stack[-1].on_resume()

    def replace_scene(self, scene: Scene) -> None:
        if self.__stack:
            self.__stack.pop().on_exit()

        self.__stack.append(scene)
        scene.on_enter()

    def update(self, dt: float) -> None:
        if self.__stack:
            self.__stack[-1].update(dt)

    def render(self) -> None:
        if self.__stack:
            self.__stack[-1].render()

    def clear(self) -> None:
        while self.__stack:
            self.__stack.pop().on_exit()

    @property
    def current(self) -> Scene | None:
        return self.__stack[-1] if self.__stack else None


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
