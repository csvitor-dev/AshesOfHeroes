from src.bootstrap.bootstrap import Bootstrap
from src.bootstrap.engine_builder import EngineBuilder


def main():
    builder = EngineBuilder().add_window(
        width=800, height=800, title="Ashe of Heroes")

    engine = Bootstrap(builder).build()

    engine.run()


if __name__ == "__main__":
    main()
