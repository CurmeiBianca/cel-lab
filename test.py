from core.simulation import Simulation

# Creeam o simulare cu Game of Life
sim = Simulation(width=5, height=5, rule="game_of_life")

# Populam lumea aleator
sim.randomize()

print("Starea initiala:")
print(sim.get_state())

# Avansam simularea cu un pas
sim.step()

print("\nDupa un pas:")
print(sim.get_state())
