from src.logic.card_cell import CardCell

type StageCell = tuple[CardCell, bool]
""" A stage cell is a tuple of a card cell and a boolean indicating whether the card is revealed or not. """


class Stage:
    def __init__(self):
        self.__red_side: tuple[StageCell, StageCell, StageCell] = (
            (CardCell(), False) for _ in range(3))
        self.__blue_side: tuple[StageCell, StageCell,
                                StageCell] = ((CardCell(), False) for _ in range(3))

    def is_revealed_in_red_side(self, index: int) -> bool:
        return self.__red_side[index][1]

    def is_revealed_in_blue_side(self, index: int) -> bool:
        return self.__blue_side[index][1]
