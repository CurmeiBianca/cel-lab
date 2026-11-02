"""
Contine regulile pentru diferite automate celulare:
- Game of Life
- Brian's Brain
- Rule 30
"""

def apply_game_of_life(cell, alive_neighbors):
    """
    Regula pentru Game of Life
    - O celula vie ramane vie daca are 2 sau 3 vecini vii
    - O celula moarta devine vie daca are exact 3 vecini vii
    """

    if cell == 1:
        return 1 if alive_neighbors in (2, 3) else 0
    else:
        return 1 if alive_neighbors == 3 else 0

def apply_brians_brain(cell, alive_neighbors):
    """
    Regula pentru Brian's Brain
    Stari:
    - 0 = moarta
    - 1 = vie
    - 2 = in stare de "firing"

    Reguli:
    - Celulele moarte devin vii daca au exact 2 vecini vii
    - Celulele vii trec in starea 2
    - Celulele in starea 2 devin moarte
    """

    if cell == 0:
        return 1 if alive_neighbors == 2 else 0
    elif cell == 1:
        return 2
    else:
        return 0

def apply_rule_30(left, center, right):
    """
    Regula pentru Rule 30 (automat 1D)
    Combinatiile sunt definite de regula 30 in binar
    """

    pattern = (left, center, right)

    rule_30 = {
        (1, 1, 1): 0,
        (1, 1, 0): 0,
        (1, 0, 1): 0,
        (1, 0, 0): 1,
        (0, 1, 1): 1,
        (0, 1, 0): 1,
        (0, 0, 1): 1,
        (0, 0, 0): 0
    }

    return rule_30[pattern]