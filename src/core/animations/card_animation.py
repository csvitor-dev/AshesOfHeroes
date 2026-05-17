from typing import Any
from src.core.animation import AnimationCommand


class CardAnimation(AnimationCommand):
    def __init__(self, card_visual: Any, target_position: Any):
        self.card_visual = card_visual
        self.target_position = target_position
