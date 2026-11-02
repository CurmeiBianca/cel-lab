from core.world import World
from core.rules import apply_game_of_life, apply_brians_brain, apply_rule_30

class Automaton:
    """
    Clasa care gestioneaza evolutia automatului celular
    Foloseste o lume (World) si o regula specifica
    """

    def __init__(self, world, rule="game_of_life"):
        """
        Initializeaza automatul cu o lume si o regula
        rule poate fi: game_of_life, brians_brain, rule_30
        """
        self.world = world
        self.rule = rule

    def apply_rule(self, x, y):
        """
        Aplica regula selectata asupra celulei (x, y)
        """

        cell = self.world.grid[x][y]

        if self.rule == "game_of_life":
            alive_neighbors = self.world.count_neighbors(x, y, value=1)
            return apply_game_of_life(cell, alive_neighbors)

        elif self.rule == "brians_brain":
            alive_neighbors = self.world.count_neighbors(x, y, value=1)
            return apply_brians_brain(cell, alive_neighbors)

        elif self.rule == "rule_30":
            # Automat 1D -> folosim doar vecinii stanga, centru, dreapta
            left = self.world.grid[x][y - 1] if y > 0 else 0
            center = cell
            right = self.world.grid[x][y + 1] if y < self.world.width - 1 else 0
            return apply_rule_30(left, center, right)

        else:
            raise ValueError("Regula necunoscuta!")

    def step(self):
        """
        Genereaza o noua generatie a automatului
        Creeaza o copie a lumii si aplica regulile pe fiecare celula
        """

        new_world = self.world.copy()

        for x in range(self.world.height):
            for y in range(self.world.width):
                new_world.grid[x][y] = self.apply_rule(x, y)

        self.world = new_world
