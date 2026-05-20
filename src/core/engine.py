from OpenGL.GL import *
import time
from typing import Any
from src.core import EngineBuilder, EventManager, SceneManager, Window
from src.graphics.rendering import Renderer
from src.core.animation import AnimationQueue
from src.graphics.objects import ViewBoard


class Engine:

    def __init__(
        self,
        window: Window,
        events: EventManager,
        scenes: SceneManager,
        services: dict[str, Any],
    ):

        self.__window = window
        self.__events = events
        self.__scenes = scenes
        self.__services = services

        self.__is_running = True
        self.__last_frame_time = time.time()

    @classmethod
    def from_builder(cls, builder: EngineBuilder) -> Engine:
        events = EventManager()

        window = Window(
            builder.window.get("width", 1280),
            builder.window.get("height", 720),
            events
        )
        services: dict[str, Any] = {"events": events, "window": window}

        for name, factory in builder.factories.items():
            if factory is None:
                continue
            try:
                services[name] = factory(services)
            except TypeError:
                services[name] = factory()

        if "camera" not in services and "camera" in builder.factories:
            ...
        scenes = SceneManager(events)
        services["scenes"] = scenes

        for key, scene_factory in builder.scene_reg.items():
            scenes.register(key, lambda sf=scene_factory: sf(services))

        if builder.initial_scene:
            scenes.push_by_key(builder.initial_scene)

        return cls(
            window=window,
            events=events,
            scenes=scenes,
            services=services,
        )

    def run(self) -> None:
        while self.__is_running and not self.__window.should_close():
            dt = self.__tick()

            self.__window.poll_events()

            self.__update(dt)
            self.__render()
        self.__shutdown()

    def __update(self, dt: float) -> None:
        self.__scenes.update(dt)

    def __render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.__scenes.render()
        self.__window.swap_buffers()

    def __tick(self) -> float:
        now = time.time()
        dt = now - self.__last_frame_time

        self.__last_frame_time = now
        return dt

    def __shutdown(self) -> None:
        self.__scenes.clear()
        self.__window.shutdown()

    def get_service(self, name: str):
        return self.__services.get(name)

# renderer = GenericRenderer()
# textures = TextureManager()
# camera   = BoardCamera(width=1280, height=720)

# # 2. ViewBoard — conhece eventos e estado
# view_board = ViewBoard(
#     event_manager   = event_manager,
#     animation_queue = animation_queue,
#     renderer        = renderer,
#     textures        = textures,
#     camera          = camera,
# )
# view_board.load_assets()   # compila shaders de slot/card

# # 3. HUD — independente do ViewBoard
# hud = HUDRenderer(renderer)

# # 4. BoardRenderer — recebe tudo pronto, só orquestra
# board_renderer = BoardRenderer(
#     renderer   = renderer,
#     textures   = textures,
#     camera     = camera,
#     view_board = view_board,   # injetado
#     hud        = hud,
# )

# # game loop
# while running:
#     dt = clock.tick()
#     board_renderer.update(dt)
#     board_renderer.render(game_state)
#     window.swap_buffers()