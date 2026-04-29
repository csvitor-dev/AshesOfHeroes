from lib.types import CardClass
from src.logic.card.base import Card
from src.logic.card.entity_attributes import EntityAttributes


class Passive:
    def __init__(
        self,
        name: str,
        description: str,
        effects: dict[str, any],
    ) -> None:
        self.name = name
        self.description = description
        self.effects = effects


class Skill:
    def __init__(
        self,
        name: str,
        description: str,
        effects: dict[str, any],
        mana_cost: int,
        turn_cooldown: int,
        passive: Passive | None = None
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
        effects: dict[str, any],
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
        self.level = 1
        self.attributes = attributes
        self.skills = skills
        self.passive = passive
        self.items = []

    def level_up(self):
        if self.level == 5:
            return
        self.level += 1
        self.__increase_attributes()
        self.__increase_skills()

    def __increase_attributes(self):
        ...

    def __increase_skills(self):
        ...
