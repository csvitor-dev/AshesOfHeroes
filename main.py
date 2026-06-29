from src.bootstrap.bootstrap import Bootstrap
from src.bootstrap.engine_builder import EngineBuilder
from src.core.scenes.menu_scene import MenuScene
from src.core.scenes.battleground_scene import BattlegroundScene
from src.core.scenes.game_over_scene import GameOverScene
from src.graphics.rendering.renderer import Renderer
from src.graphics.texture_manager import TextureManager
from src.mechanics.match_logic import MatchLogic


def main():
    builder = (
        EngineBuilder()
        .init_game()
        .set_window(width=1280, height=720, title="Ashe of Heroes")
        .set_camera(fov=45.0, near=0.1, far=100.0)
        .use("renderer", lambda _: Renderer())
        .use("textures", lambda _: TextureManager())
        .use("match_logic", lambda s: MatchLogic(
            event_manager=s["events"],
            game_state=s["game_state"],
        ))
        .add_scene("menu", lambda s: MenuScene(
            event_manager=s["events"],
            scene_manager=s["scenes"],
            renderer=s["renderer"],
            camera=s["camera"],
        ))
        .add_scene("battle_ground", lambda s: BattlegroundScene(
            event_manager=s["events"],
            scene_manager=s["scenes"],
            renderer=s["renderer"],
            camera=s["camera"],
            game_state=s["game_state"],
            match_logic=s["match_logic"],
        ))
        .add_scene("game_over", lambda s: GameOverScene(
            event_manager=s["events"],
            scene_manager=s["scenes"],
            renderer=s["renderer"],
            camera=s["camera"],
            game_state=s["game_state"],
        ))
        .set_initial_scene("menu")
    )

    engine = Bootstrap(builder).build()
    engine.run()


if __name__ == "__main__":
    main()
