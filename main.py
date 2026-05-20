from src.core import EngineBuilder


def main():
    builder = EngineBuilder()

    engine = builder.add_window(width=800, height=800).build()

    engine.run()


if __name__ == "__main__":
    main()
