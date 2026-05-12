from OpenGL.GL import *

from src.core.animation import AnimationQueue
from src.core.event import EventManager
from src.core.animations.card_animation import CardAnimation
from lib.events import EventType
from typing import Any


class VisualBoard:
    def __init__(self, event_manager: EventManager, animation_queue: AnimationQueue):
        self.events = event_manager
        self.animation_queue = animation_queue

        self.visual_cards: dict[Any, Any] = {}

        self.events.subscribe(EventType.LOGIC_COMBAT_RESOLVED,
                              self._on_combat_resolved)

    def load_assets(self) -> None: ...

    def unload_assets(self) -> None: ...

    def _on_combat_resolved(self, data: Any) -> None:
        attacker_vis = self.visual_cards.get(data["attacker_id"])
        target_vis = self.visual_cards.get(data["target_id"])

        if attacker_vis and target_vis:
            self.animation_queue.enqueue(
                CardAnimation(attacker_vis, target_vis.position))

    def update(self, dt: float) -> None:
        for card_vis in self.visual_cards.values():
            card_vis.update_lerp(dt)

    def render(self) -> None:
        for card_vis in self.visual_cards.values():
            card_vis.draw()
