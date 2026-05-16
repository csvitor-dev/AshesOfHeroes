from collections import deque
from typing import Optional, Protocol


class AnimationCommand(Protocol):
    def start(self) -> None: ...

    def update(self, dt: float) -> None: ...

    def is_finished(self) -> bool: ...


class AnimationQueue:
    def __init__(self):
        self.__queue: deque[AnimationCommand] = deque()
        self.__current_animation: Optional[AnimationCommand] = None

    def enqueue(self, animation_command: AnimationCommand) -> None:
        self.__queue.append(animation_command)

    def update(self, dt: float) -> None:
        if self.__current_animation is None:
            if not self.__queue:
                return
            self.__current_animation = self.__queue.popleft()
            self.__current_animation.start()
        self.__current_animation.update(dt)

        if self.__current_animation.is_finished():
            self.__current_animation = None

    def is_busy(self) -> bool:
        return self.__current_animation is not None or len(self.__queue) > 0
