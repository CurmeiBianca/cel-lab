import numpy as np

class World:
    """
    Reprezinta grila automatului celular
    Contine dimensiunile si starea curenta a celulelor
    """

    def __init__(self, width, height, initial_state=None):
        """
        Creeaza o grila de dimensiuni (height x width)
        Daca nu se ofera o stare initiala, se genereaza automat una random
        """

        self.width = width
        self.height = height

        if initial_state is None:
            # Grila random cu valori 0/1 (utila pentru Game of Life)
            self.grid = np.random.randint(0, 2, size=(height, width))
        else:
            # Convertim starea initiala intr-un array NumPy
            self.grid = np.array(initial_state)

    def get_neighbors(self, x, y):
        """
        Returneaza vecinii celulei (x, y) folosind vecinatatea Moore
        Moore = 8 vecini (sus, jos, stanga, dreapta, diagonale)
        """

        neighbors = []

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:

                # Sarim peste celula curenta
                if dx == 0 and dy == 0:
                    continue

                nx, ny = x + dx, y + dy

                # Verificam daca vecinul este in interiorul grilei
                if 0 <= nx < self.height and 0 <= ny < self.width:
                    neighbors.append(self.grid[nx][ny])

        return neighbors

    def count_neighbors(self, x, y, value=1):
        """
        Numara cati vecini ai celulei (x, y) au valoarea 'value'
        Folosit in regulile automatului (ex: celule vii in Game of Life)
        """

        neighbors = self.get_neighbors(x, y)
        return sum(1 for n in neighbors if n == value)

    def copy(self):
        """
        Creeaza o copie a lumii
        Util pentru generarea unei noi generatii fara a modifica grila curenta
        """
        return World(self.width, self.height, initial_state=self.grid.copy())