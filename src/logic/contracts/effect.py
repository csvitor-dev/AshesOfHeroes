from typing import Protocol


class Effect(Protocol):
    def apply(self) -> None: ...
