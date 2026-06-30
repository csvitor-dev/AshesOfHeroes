from collections import deque
from lib.types import CardClass
from src.logic.contracts.card import Card
from src.logic.contracts.effect import Effect
from src.logic.contracts.entity_attributes import EntityAttributes


class TurretCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        effects: deque[Effect],
        attributes: EntityAttributes,
        turn_cooldown: int,
    ) -> None:
        super().__init__(
            id, name, description, gold_cost, gold_profit,
            CardClass.TURRET, effects,
        )
        self.__attr = attributes
        self.__turn_cooldown = turn_cooldown
        self._has_attacked = False

    def attack(self, target: "TurretCard") -> None:
        if not self.can_attack:
            return
        target.take_damage(self.__attr.attack_damage)
        self._has_attacked = True

    def take_damage(self, amount: int) -> int:
        effective = max(0, amount - self.__attr.armor)
        self.__attr.health = max(0, self.__attr.health - effective)
        return self.__attr.health

    def heal(self, amount: int) -> int:
        self.__attr.health = min(self.__attr.health + amount, self.__attr.health)
        return self.__attr.health

    def reset_turn_state(self) -> None:
        self._has_attacked = False

    @property
    def can_attack(self) -> bool:
        return not self._has_attacked and self.is_alive

    @property
    def has_attacked(self) -> bool:
        return self._has_attacked

    @property
    def is_alive(self) -> bool:
        return self.__attr.health > 0

    @property
    def current_health(self) -> int:
        return self.__attr.health

    @property
    def attack_damage(self) -> int:
        return self.__attr.attack_damage

    @property
    def gold_profit(self) -> int:
        return self._gold_profit
