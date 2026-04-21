from lib.types import CardClass
from src.logic.card.base import Card
from src.logic.card.entity_attributes import EntityAttributes


class Skill:
    def __init__(
        self,
        name: str,
        description: str,
        effects: dict[str, any],
        mana_cost: int,
        turn_cooldown: int,
    ) -> None:
        self.name = name
        self.description = description
        self.effects = effects
        self.mana_cost = mana_cost
        self.turn_cooldown = turn_cooldown


class HeroCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        effects: dict[str, any],
        attributes: EntityAttributes,
        skills: tuple[Skill, Skill]
    ) -> None:
        super().__init__(id, name, description, gold_cost, CardClass.HERO, effects)
        self.level = 1
        self.attributes = attributes
        self.skills = skills
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
