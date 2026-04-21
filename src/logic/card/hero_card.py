from lib.types import CardClass
from src.logic.card.base import Card


class Skill:
    def __init__(self, name: str, description: str, effects: dict[str, any]) -> None:
        self.name = name
        self.description = description
        self.effects = effects


class HeroCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        effects: dict[str, any],
        attributes: dict[str, any],
        skills: tuple[Skill, Skill]
    ) -> None:
        super().__init__(id, name, description, gold_cost, CardClass.HERO, effects)
        self.attributes = attributes
        self.skills = skills
        self.items = []
