def valideaza_configurare(nume_automat, randuri, coloane, stare_initiala, densitate=None):
    if nume_automat == "Rule 30":
        randuri = 1
        
    if not (10 <= coloane <= 200):
        raise ValueError("Backend Error: Numărul de coloane trebuie să fie între 10 și 200.")
        
    if nume_automat != "Rule 30" and not (10 <= randuri <= 200):
        raise ValueError("Backend Error: Numărul de rânduri trebuie să fie între 10 și 200.")
    
    if stare_initiala == "Aleatoare":
        if densitate is None or not (0.0 <= densitate <= 1.0):
            raise ValueError("Backend Error: Densitatea trebuie să fie un număr între 0 și 1.")

    config = {
        "automat": nume_automat,
        "dimensiuni": {"randuri": randuri, "coloane": coloane},
        "stare_initiala": {"tip": stare_initiala, "densitate": densitate}
    }
    return config

def valideaza_fisier_salvat(date_json):
    chei_obligatorii = ["automat", "generatie", "stare"]
    for cheie in chei_obligatorii:
        if cheie not in date_json:
            raise ValueError(f"Fișier corupt: lipsește cheia obligatorie '{cheie}'.")
    return True