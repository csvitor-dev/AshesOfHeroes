from typing import Any
from lib.events import EventType
from src.core.scene import Scene, SceneManager
from src.core.event import EventManager
from mechanics.match_logic import MatchLogic
from src.graphics.objects.view_board import ViewBoard
from src.core.animation import AnimationQueue


class BattleFieldScene(Scene):
    def __init__(self, event_manager: EventManager, scene_manager: SceneManager):
        super().__init__(event_manager, scene_manager)

        self.__animation_queue = AnimationQueue()
        self.__match_logic = MatchLogic(self._events)
        self.__board = ViewBoard(self._events, self.__animation_queue)

    def on_enter(self, **params: Any) -> None:
        print(
            f"Iniciando Batalha! Decks: {params.get('player_deck_id')} vs {params.get('enemy_deck_id')}")
        self.__board.load_assets()

        self.__match_logic.setup_match(params.get(
            'player_deck_id'), params.get('enemy_deck_id'))

        self._events.subscribe(
            EventType.ACTION_PAUSE_GAME, self._on_pause_requested)

        self.__match_logic.start_game()

    def on_exit(self) -> None:
        print("Encerrando Batalha e limpando memória GPU...")
        self.__board.unload_assets()

    def on_pause(self):
        print("Batalha pausada (outra cena sobreposta).")

    def _on_pause_requested(self, data: Any) -> None:
        # Empilha a cena de pausa sem destruir a batalha
        self._scenes.push_scene("pause")

    def handle_input(self):
        ...

    def update(self, dt: float) -> None:
        self.__animation_queue.update(dt)

        if not self.__animation_queue.is_busy():
            self.__match_logic.update(dt)
        self.__board.update(dt)

    def render(self):
        self.__board.render()
