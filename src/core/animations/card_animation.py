from typing import Any
from src.core import AnimationCommand
from src.graphics.objects import ViewCard


class CardAnimation(AnimationCommand):
    def __init__(self, view_card: ViewCard, target_position: Any):
        self.view_card = view_card
        self.target_position = target_position

    def start(self) -> None: ...

    def update(self, dt: float) -> None: ...

    def is_finished(self) -> bool: ...
