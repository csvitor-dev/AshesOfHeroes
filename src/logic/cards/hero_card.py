from collections import deque
from typing import Optional
from lib.types import CardClass
from src.logic.card_cell import CardCell
from src.logic.contracts.card import Card
from src.logic.cards.item_card import ItemCard
from src.logic.contracts.entity_attributes import EntityAttributes
from src.logic.contracts.effect import Effect


class Passive:
    def __init__(
        self,
        name: str,
        description: str,
        effects: deque[Effect],
    ) -> None:
        self.name = name
        self.description = description
        self.effects = effects


class Skill:
    def __init__(
        self,
        name: str,
        description: str,
        effects: deque[Effect],
        mana_cost: int,
        turn_cooldown: int,
        passive: Optional[Passive] = None
    ) -> None:
        self.name = name
        self.description = description
        self.effects = effects
        self.mana_cost = mana_cost
        self.turn_cooldown = turn_cooldown
        self.passive = passive


class HeroCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        effects: deque[Effect],
        attributes: EntityAttributes,
        skills: tuple[Skill, Skill],
        passive: Passive
    ) -> None:
        super().__init__(
            id,
            name,
            description,
            gold_cost,
            gold_profit,
            CardClass.HERO,
            effects
        )
        self.__level = 1
        self.__attributes = attributes
        self.__skills = skills
        self.__passive = passive
        self.__items = (CardCell(), CardCell(), CardCell())

    def level_up(self):
        if self.__level == 5:
            return
        self.__level += 1
        self.__increase_attributes()
        self.__increase_skills()

    def __increase_attributes(self):
        ...

    def __increase_skills(self):
        ...
        
    @property
    def current_health(self) -> int:
        return self.__attributes.health

    def add_item(self, item_card: ItemCard) -> bool:
        for cell in self.__items:
            if cell.occupied is False:
                cell.set_card(item_card)
                return True
        return False
