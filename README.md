# CelLab - Cellular Automata Simulation Platform

CelLab este o aplicatie interactiva pentru definirea, simularea si analiza automatelor celulare.
Utilizatorul poate descrie un automat celular in limbaj natural, sistemul il valideaza, il simuleaza si raspunde la intrebari despre evolutia sa.

Acest repository contine implementarea proiectului pentru disciplina *Inteligenta Artificiala*.

---

## Echipa

| Membru | Rol | Responsabilitati |
|--------|-----|------------------|
| **Curmei Bianca-Gabriela** | Motorul de simulare | Logica de tranzitie, stari, matrice NumPy, Game of Life, Brian's Brain, Rule 30 |
| **Preutu-Grigore Diana-Smaranda** | Interfata grafica | Streamlit UI, input utilizator, vizualizare generatii |
| **Dughila Miruna** | NLP & Validare | Parsare limbaj natural, validare reguli, gestionare erori |
| **Ursache David** | Analiza & AI | Detectare cicluri, stabilitate, numar celule, dataset, experiment ML |

---

## Scopul proiectului

CelLab permite:
- definirea unui automat celular in limbaj natural,
- validarea rehulilor si a starilor, 
- simularea generatiilor succesive,
- vizualizarea evolutiei,
- salvarea starilor,
- analiza comportamentului automatului, 
- construirea unui dataset si rularea unui experiment de invatare automata

---

## Arhitectura proiectului

Proiectul este organizat in module:

- **Interfata garfica (Stremlit)** - input, configurare, vizualizare
- **Parser NLP** - interpretarea descrierii naturale
- **Motor de simulare (NumPy)** - calculul generatiilor
- **Analiza** - stabilitate, cicluri, numar celule, configuratii
- **Stocare & AI** - salvare JSON/SQLite, dataset, experiment ML

---

## Tehnologii utilizate

- Python
- Streamlit
- NumPy
- SQLite / JSON
- scikit-learn
- pytest
- Git & GitHub

---