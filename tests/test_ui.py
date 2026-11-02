"""
Teste automate end-to-end pentru interfața CelLab (app/ui.py).

Pornire (din folderul cel-lab, cu venv activ, aplicația oprită):
    pip install pytest
    pytest tests/test_ui.py -v

Streamlit are un "robot" (AppTest) care pornește aplicația fără browser,
apasă butoane, trage de slidere și citește ce apare pe ecran. Testele urmează
aceiași pași ca testarea manuală din ghid (numerele din paranteze).
Ce nu poate verifica robotul: desenul grilei și editarea manuală -> manual.
"""

import os

import numpy as np
from streamlit.testing.v1 import AppTest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALE_UI = os.path.join(RADACINA, "app", "ui.py")
DOSAR_SALVARI = os.path.join(RADACINA, "data", "saved_states")


# ---------------------------------------------------------------- ajutoare
def porneste_aplicatia():
    at = AppTest.from_file(CALE_UI, default_timeout=60).run()
    verifica_fara_erori(at)
    return at


def verifica_fara_erori(at):
    assert not at.exception, at.exception


def apasa(at, text):
    """Apasă butonul al cărui text conține `text`."""
    buton = next(b for b in at.button if text in b.label)
    buton.click().run()
    verifica_fara_erori(at)


def seteaza_numar(at, eticheta, valoare):
    camp = next(x for x in at.number_input if x.label == eticheta)
    camp.set_value(valoare).run()
    verifica_fara_erori(at)


def alege_automatul(at, nume):
    at.selectbox(key="nume_automat").select(nume).run()
    verifica_fara_erori(at)


def valoare_afisata(at, eticheta):
    """Citește numărul afișat într-un contor (st.metric)."""
    return next(m for m in at.metric if m.label == eticheta).value


def mesaje_verzi(at):
    return [m.value for m in at.success]


def generatia_curenta(at):
    s = at.session_state
    return s.gen_start + len(s.istoric) - 1


# ---------------------------------------------------------------- teste
def test_01_aplicatia_porneste_cu_glider():
    at = porneste_aplicatia()
    assert at.session_state.automat == "Game of Life"
    assert valoare_afisata(at, "Generația afișată") == "0"
    assert int(at.session_state.istoric[0].sum()) == 5


def test_02_game_of_life_glider_se_misca():
    at = porneste_aplicatia()
    inainte = at.session_state.istoric[0].copy()
    for _ in range(4):
        apasa(at, "Pas următor")
    asteptat = np.roll(np.roll(inainte, 1, axis=0), 1, axis=1)
    assert np.array_equal(at.session_state.istoric[-1], asteptat)
    assert valoare_afisata(at, "Generația afișată") == "4"


def test_03_stare_stabila_si_04_slider():
    at = porneste_aplicatia()
    seteaza_numar(at, "Număr de generații N", 110)
    apasa(at, "Rulează N")
    assert valoare_afisata(at, "Generația afișată") == "110"
    assert any("generația 107" in m for m in mesaje_verzi(at))
    assert int(at.session_state.istoric[-1].sum()) == 4

    # (4) sliderul schimbă generația afișată
    at.slider(key="slider_gen").set_value(50).run()
    verifica_fara_erori(at)
    assert valoare_afisata(at, "Generația afișată") == "50"
    at.slider(key="slider_gen").set_value(0).run()
    assert valoare_afisata(at, "Generația afișată") == "0"


def test_05_fara_generatii_intermediare():
    at = porneste_aplicatia()
    next(c for c in at.checkbox if "intermediare" in c.label).uncheck().run()
    apasa(at, "Reset")
    apasa(at, "Rulează N")                       # N = 20 implicit
    assert valoare_afisata(at, "Generații în memorie") == "1"
    assert valoare_afisata(at, "Generația afișată") == "20"


def test_06_acelasi_seed_aceeasi_grila():
    at = porneste_aplicatia()
    next(r for r in at.radio if r.label == "Stare inițială").set_value("Aleatoare").run()
    apasa(at, "Generează starea inițială")
    prima = at.session_state.istoric[0].copy()
    apasa(at, "Generează starea inițială")
    assert np.array_equal(at.session_state.istoric[0], prima)

    seteaza_numar(at, "Seed", 7)
    apasa(at, "Generează starea inițială")
    assert not np.array_equal(at.session_state.istoric[0], prima)


def test_07_brians_brain_starile_avanseaza():
    at = porneste_aplicatia()
    alege_automatul(at, "Brian's Brain")
    inainte = at.session_state.istoric[-1].copy()
    apasa(at, "Pas următor")
    dupa = at.session_state.istoric[-1]
    # FIRING (1) -> DYING (2), DYING (2) -> OFF (0)
    assert np.all(dupa[inainte == 1] == 2)
    assert np.all(dupa[inainte == 2] == 0)


def test_09_rule_30_primele_randuri():
    at = porneste_aplicatia()
    alege_automatul(at, "Rule 30")
    apasa(at, "Rulează N")
    istoric = at.session_state.istoric
    centru = len(istoric[0]) // 2
    randuri = ["".join(map(str, r[centru - 3: centru + 4])) for r in istoric[:4]]
    assert randuri == ["0001000", "0011100", "0110010", "1101111"]
    assert len(istoric) == 21


def test_10_salvare_si_incarcare():
    at = porneste_aplicatia()
    for _ in range(3):
        apasa(at, "Pas următor")
    stare_salvata = at.session_state.istoric[-1].copy()

    inainte = set(os.listdir(DOSAR_SALVARI)) if os.path.isdir(DOSAR_SALVARI) else set()
    apasa(at, "Salvează starea")
    fisier_nou = (set(os.listdir(DOSAR_SALVARI)) - inainte).pop()

    try:
        alege_automatul(at, "Rule 30")
        at.selectbox(key="fisier_ales").select(fisier_nou).run()
        apasa(at, "Încarcă")

        assert at.session_state.automat == "Game of Life"
        assert np.array_equal(at.session_state.istoric[-1], stare_salvata)
        assert valoare_afisata(at, "Generația afișată") == "3"

        apasa(at, "Pas următor")                  # continuă de unde a rămas
        assert generatia_curenta(at) == 4
    finally:
        os.remove(os.path.join(DOSAR_SALVARI, fisier_nou))
