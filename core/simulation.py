from core.world import World
from core.automaton import Automaton

class Simulation:
    """
    Clasa care gestioneaza o simulare completa a automatului celular
    Leaga lumea (World) si automatul (Automaton)
    """

    def __init__(self, width=20, height=20, rule="game_of_life"):
        """
        Creeaza o lume noua si un automat cu regula selectata
        """
        self.world = World(width, height)
        self.automaton = Automaton(self.world, rule)

    def reset(self):
        """
        Reseteaza lumea la o stare goala (toate celulele moarte)
        """
        self.world = World(self.world.width, self.world.height)
        self.automaton.world = self.world

    def randomize(self):
        """
        Populeaza lumea cu valori aleatoare (0 sau 1)
        """
        import numpy as np
        self.world.grid = np.random.randint(0, 2, (self.world.height, self.world.width))

    def step(self):
        """
        Avanseaza simularea cu o generatie
        """
        self.automaton.step()

    def set_rule(self, rule):
        """
        Schimba regula automatului
        """
        self.automaton.rule = rule

    def get_state(self):
        """
        Returneaza grila curenta (pentru interfata)
        """
        return self.world.grid