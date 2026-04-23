class EntityAttributes:
    def __init__(
        self,
        health: int,
        mana: int,
        attack_damage: int,
        magic_damage: int,
        armor: int,
        magic_resistence: int,
        turn_cooldown: int,
    ) -> None:
        self.health = health
        self.mana = mana
        self.attack_damage = attack_damage
        self.magic_damage = magic_damage
        self.armor = armor
        self.magic_resistence = magic_resistence
        self.turn_cooldown = turn_cooldown
