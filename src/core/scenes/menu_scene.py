from typing import Any
from lib.events import Events
from src.core.event import EventManager
from src.core.scene import Scene, SceneManager


class MenuScene(Scene):
    def __init__(self, event_manager: EventManager, scene_manager: SceneManager):
        super().__init__(event_manager, scene_manager)
        self.background_texture = None
        self.play_button_rect = [540, 300, 200, 80]  # x, y, width, height

    def on_enter(self, **params: Any) -> None:
        print("Entrando no Menu Principal...")
        self._events.subscribe(Events.RAW_INPUT_MOUSE, self._on_mouse_click)

    def on_exit(self) -> None:
        print("Saindo do Menu Principal...")
        self._events.unsubscribe(Events.RAW_INPUT_MOUSE, self._on_mouse_click)

    def _on_mouse_click(self, data: Any) -> None:
        x, y = data['x'], data['y']
        bx, by, bw, bh = self.play_button_rect

        if bx <= x <= bx + bw and by <= y <= by + bh:
            print("Botão Jogar clicado!")
            self._scenes.change_scene(
                "battle", player_deck_id="mage_01", enemy_deck_id="warrior_01")

    def update(self, dt: float) -> None:
        ...

    def render(self) -> None:
        ...
