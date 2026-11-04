"""
CelLab - Interfața grafică (prototip pentru Livrabilul 2)

Pornire (din folderul cel-lab):   streamlit run app/ui.py

Ce face:
  - alegi un automat (Game of Life, Brian's Brain, Rule 30)
  - setezi parametrii (dimensiune, stare inițială, nr. generații)
  - aplici regula pas cu pas sau de N ori
  - vezi grila și derulezi prin generațiile salvate
  - salvezi starea în JSON și o încarci înapoi (continuă simularea)

Regulile vin din motorul de simulare (core/world.py, core/automaton.py, core/rules.py).
Salvarea din secțiunea "MOCK" e provizorie și va fi înlocuită
cu modulul de stocare din data/.
"""

import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import streamlit as st

# ui.py stă în app/, iar motorul în core/ -> adăugăm folderul proiectului
# în calea de căutare, ca să meargă "from core... import ..."
RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADACINA not in sys.path:
    sys.path.insert(0, RADACINA)

from core.world import World          # grila
from core.automaton import Automaton  # aplicarea regulilor
from nlp.parser import valideaza_configurare, valideaza_fisier_salvat


# ======================================================================
# 1. DESCRIEREA AUTOMATELOR (stări + culori)
# ======================================================================
AUTOMATE = {
    "Game of Life": {
        "stari": ["Moartă", "Vie"],
        "culori": ["#ffffff", "#1f2937"],
        "dim": 2,  # grilă 2D
    },
    "Brian's Brain": {
        "stari": ["OFF", "FIRING", "DYING"],
        "culori": ["#111827", "#facc15", "#3b82f6"],
        "dim": 2,
    },
    "Rule 30": {
        "stari": ["0", "1"],
        "culori": ["#ffffff", "#1f2937"],
        "dim": 1,  # un singur rând; generațiile se afișează una sub alta
    },
}


# ======================================================================
# 2. REGULILE - folosesc motorul de simulare din core/ (World + Automaton)
# ======================================================================
# Numele din interfață -> numele regulii din core/automaton.py
REGULI_CORE = {
    "Game of Life": "game_of_life",
    "Brian's Brain": "brians_brain",
    "Rule 30": "rule_30",
}


def pas_urmator(nume, grila):
    """Primește generația curentă, o dă motorului de simulare și întoarce generația nouă.
    Rule 30 e un singur rând; motorul lucrează pe grile 2D, așa că îl facem
    temporar o grilă cu 1 rând și apoi îl desfacem la loc."""
    este_1d = grila.ndim == 1
    grila_2d = grila.reshape(1, -1) if este_1d else grila
    inaltime, latime = grila_2d.shape

    lume = World(latime, inaltime, initial_state=grila_2d.copy())
    automat = Automaton(lume, rule=REGULI_CORE[nume])
    automat.step()

    noua = automat.world.grid.astype(np.int8)
    return noua.reshape(-1) if este_1d else noua


# ======================================================================
# 3. STAREA INIȚIALĂ
# ======================================================================
def stare_initiala(nume, randuri, coloane, mod, densitate, seed):
    rng = np.random.default_rng(seed)

    if AUTOMATE[nume]["dim"] == 1:
        if mod == "Aleatoare":
            return (rng.random(coloane) < densitate).astype(np.int8)
        rand = np.zeros(coloane, dtype=np.int8)
        rand[coloane // 2] = 1                       # o singură celulă vie în centru
        return rand

    if mod == "Aleatoare":
        return (rng.random((randuri, coloane)) < densitate).astype(np.int8)

    grila = np.zeros((randuri, coloane), dtype=np.int8)
    if nume == "Game of Life":
        # glider în colțul stânga-sus
        for r, c in [(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)]:
            grila[r, c] = 1
    else:
        # Brian's Brain: "glider" (2 celule FIRING cu 2 DYING în spate) - urcă în sus
        r0, c0 = randuri // 2, coloane // 2
        grila[r0, c0] = grila[r0, c0 + 1] = 1        # FIRING
        grila[r0 + 1, c0] = grila[r0 + 1, c0 + 1] = 2  # DYING
    return grila


# ======================================================================
# 4. MOCK - SALVARE / ÎNCĂRCARE (provizoriu, va fi înlocuit cu modulul din data/)
# ======================================================================
DOSAR_SALVARI = os.path.join(RADACINA, "data", "saved_states")


def salveaza_stare(s):
    os.makedirs(DOSAR_SALVARI, exist_ok=True)
    generatie = s.gen_start + len(s.istoric) - 1
    date = {
        "automat": s.automat,
        "generatie": generatie,
        "stare": s.istoric[-1].tolist(),
        "istoric": [x.tolist() for x in s.istoric] if s.pastreaza else None,
        "gen_start": s.gen_start,
        "salvat_la": datetime.now().isoformat(timespec="seconds"),
    }
    nume = s.automat.replace(" ", "_").replace("'", "")
    cale = os.path.join(DOSAR_SALVARI, f"{nume}_gen{generatie}_{datetime.now():%H%M%S}.json")
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(date, f)
    return cale


def incarca_stare(cale):
    with open(cale, encoding="utf-8") as f:
        return json.load(f)


# ======================================================================
# 5. STAREA APLICAȚIEI (Streamlit rerulează tot scriptul la fiecare click,
#    așa că tot ce trebuie păstrat stă în st.session_state)
# ======================================================================
def reseteaza(nume, randuri, coloane, mod, densitate, seed):
    s = st.session_state
    s.automat = nume
    s.istoric = [stare_initiala(nume, randuri, coloane, mod, densitate, seed)]
    s.gen_start = 0          # numărul generației pentru istoric[0]
    s.vizualizat = 0         # ce index din istoric e afișat
    s.gen_stabila = None     # prima generație după care nu se mai schimbă nimic


def avanseaza(n):
    s = st.session_state
    curent = s.istoric[-1]
    for _ in range(n):
        generatie = s.gen_start + len(s.istoric) - 1
        nou = pas_urmator(s.automat, curent)
        if s.get("gen_stabila") is None and np.array_equal(nou, curent):
            s.gen_stabila = generatie
        curent = nou
        if s.pastreaza:
            s.istoric.append(curent)
        else:
            s.istoric = [curent]
            s.gen_start += 1
    s.vizualizat = len(s.istoric) - 1


def incarca_in_aplicatie():
    """Rulează la click pe 'Încarcă', înainte de redesenarea paginii."""
    s = st.session_state
    date = incarca_stare(os.path.join(DOSAR_SALVARI, s.fisier_ales))

    #adaugat functie valideaza_fisier_salvat, trece datele citite prin filtru inainte de a le baga in memorie
    try:
        valideaza_fisier_salvat(date)
        s.automat = date["automat"]
        s.nume_automat = date["automat"]     # mută și selectorul din bara laterală
        if date["istoric"]:
            s.istoric = [np.array(x, dtype=np.int8) for x in date["istoric"]]
            s.gen_start = date["gen_start"]
        else:
            s.istoric = [np.array(date["stare"], dtype=np.int8)]
            s.gen_start = date["generatie"]
        s.vizualizat = len(s.istoric) - 1
        s.gen_stabila = None
    except ValueError as eroare:
        st.error(f"Nu se poate încărca salvarea: {eroare}")


def muta_sliderul():
    """Rulează când utilizatorul trage de sliderul de generații."""
    st.session_state.vizualizat = st.session_state.slider_gen


# ======================================================================
# 6. DESENAREA
# ======================================================================
def deseneaza(nume, imagine):
    culori = AUTOMATE[nume]["culori"]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(imagine, cmap=ListedColormap(culori), vmin=0, vmax=len(culori) - 1,
              interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


# ======================================================================
# 7. INTERFAȚA
# ======================================================================
st.set_page_config(page_title="CelLab", layout="wide")
st.title("CelLab – simulator de automate celulare")

# ---------- Bara laterală: parametri ----------
with st.sidebar:
    st.header("1. Automat")
    nume = st.selectbox("Alege automatul", list(AUTOMATE.keys()), key="nume_automat")

    st.text_area("Descriere în limbaj natural",
                 placeholder="Disponibil la Livrabilul 4 (L13)", disabled=True)

    st.header("2. Parametri")
    if AUTOMATE[nume]["dim"] == 2:
        randuri = st.number_input("Rânduri", 10, 200, 30)
    else:
        randuri = 1
    coloane = st.number_input("Coloane", 10, 400, 30 if AUTOMATE[nume]["dim"] == 2 else 81)
    mod = st.radio("Stare inițială", ["Preset", "Aleatoare"], horizontal=True)
    densitate = st.slider("Densitate (pentru aleatoare)", 0.0, 1.0, 0.3)
    seed = st.number_input("Seed", 0, 99999, 42)
    st.session_state.pastreaza = st.checkbox("Salvează generațiile intermediare", value=True)

    #adaugat functie valideaza_configurare pt verificarea datelor(validarea)
    if st.button("Generează starea inițială", type="primary", use_container_width=True):
        try:
            config = valideaza_configurare(nume, randuri, coloane, mod, densitate)
            randuri_sigure = config["dimensiuni"]["randuri"]
            coloane_sigure = config["dimensiuni"]["coloane"]
            reseteaza(nume, randuri_sigure, coloane_sigure, mod, densitate, seed)
        except ValueError as eroare:
            st.error(f"Eroare de validare: {eroare}")

# prima rulare sau automat schimbat -> reinițializare
if "istoric" not in st.session_state or st.session_state.automat != nume:
    reseteaza(nume, randuri, coloane, mod, densitate, seed)

s = st.session_state

# ---------- Controale de simulare ----------
st.subheader("3. Simulare")
c1, c2, c3 = st.columns([1, 2, 1])
c1.button("Pas următor ▶", on_click=avanseaza, args=(1,), use_container_width=True)
with c2:
    n_gen = st.number_input("Număr de generații N", 1, 1000, 20, label_visibility="collapsed")
    st.button(f"Rulează N generații ⏩", on_click=avanseaza, args=(int(n_gen),),
              use_container_width=True)
c3.button("Reset ↺", on_click=reseteaza,
          args=(nume, randuri, coloane, mod, densitate, seed), use_container_width=True)

# ---------- Afișare ----------
col_grila, col_info = st.columns([3, 1])

with col_info:
    if len(s.istoric) > 1:
        # sliderul are cheia lui; înainte de desenare îl aliniem cu generația afișată
        s.slider_gen = s.vizualizat
        st.slider("Derulează generațiile", 0, len(s.istoric) - 1,
                  key="slider_gen", on_change=muta_sliderul)
    generatie_afisata = s.gen_start + s.vizualizat
    st.metric("Generația afișată", generatie_afisata)
    st.metric("Generații în memorie", len(s.istoric))

    stare = s.istoric[s.vizualizat]
    st.write("**Celule pe tip:**")
    for i, eticheta in enumerate(AUTOMATE[s.automat]["stari"]):
        st.write(f"{eticheta}: {int((stare == i).sum())}")

    if s.get("gen_stabila") is not None:
        st.success(f"Stare stabilă de la generația {s.gen_stabila}: "
                   "grila nu se mai schimbă.")

with col_grila:
    if AUTOMATE[s.automat]["dim"] == 1:
        # Rule 30: fiecare rând e o generație, de sus în jos
        imagine = np.array(s.istoric[: s.vizualizat + 1])
        if not s.pastreaza:
            st.info("Pentru imaginea completă a Rule 30 bifează "
                    "„Salvează generațiile intermediare”.")
    else:
        imagine = stare
    figura = deseneaza(s.automat, imagine)
    st.pyplot(figura)
    plt.close(figura)

# ---------- Editare manuală (doar 2D, grile mici) ----------
if AUTOMATE[s.automat]["dim"] == 2 and stare.shape[0] <= 40 and stare.shape[1] <= 40:
    with st.expander("✏️ Editează manual ultima generație"):
        legenda = ", ".join(f"{i} = {e}" for i, e in enumerate(AUTOMATE[s.automat]["stari"]))
        st.caption(f"Valori: {legenda}")
        tabel = st.data_editor(pd.DataFrame(s.istoric[-1]),
                               key=f"editor_{s.automat}_{s.gen_start + len(s.istoric)}")
        if st.button("Aplică modificările"):
            maxim = len(AUTOMATE[s.automat]["stari"]) - 1
            noua = np.clip(tabel.fillna(0).to_numpy(dtype=int), 0, maxim).astype(np.int8)
            s.istoric[-1] = noua
            s.vizualizat = len(s.istoric) - 1
            s.gen_stabila = None
            st.rerun()

# ---------- Salvare / încărcare ----------
st.subheader("4. Salvare și încărcare")
cs, ci = st.columns(2)
with cs:
    if st.button("💾 Salvează starea curentă", use_container_width=True):
        cale = salveaza_stare(s)
        st.success(f"Salvat: {os.path.basename(cale)}")
with ci:
    fisiere = sorted(os.listdir(DOSAR_SALVARI)) if os.path.isdir(DOSAR_SALVARI) else []
    if fisiere:
        st.selectbox("Fișier salvat", fisiere, key="fisier_ales")
        st.button("📂 Încarcă și continuă", on_click=incarca_in_aplicatie,
                  use_container_width=True)
    else:
        st.caption("Nicio stare salvată încă.")
