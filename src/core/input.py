from typing import Any, Optional
from lib.events import Events
from src.core.event import EventManager
from src.core.scene import SceneManager
from src.logic.contracts import Card


class Input:
    def __init__(self, event_manager: EventManager, scene_manager: SceneManager):
        self.__events = event_manager
        self.__scenes = scene_manager

        self.__is_dragging = False
        self.__dragged_object: Optional[Card] = None

        self.__events.subscribe(
            Events.RAW_INPUT_MOUSE, self.__handle_mouse_click)

    def __handle_mouse_click(self, data: Any):
        x, y = data['x'], data['y']
        clicked_entity = self.__pick_entity(x, y)

        if clicked_entity:
            self.__events.emit(Events.ENTITY_SELECTED,
                               entity_id=clicked_entity.id)

            self.__is_dragging = True
            self.__dragged_object = clicked_entity

    def __pick_entity(self, x: float, y: float) -> Optional[Card]:
        for card in self.__scenes.get_renderable_cards():
            if card.is_point_inside(x, y):
                return card
        return None

    def update(self):
        if self.__is_dragging:
            ...
