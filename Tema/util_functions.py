zile_saptamana = []
intervale_orare = []
sali = {}
materii = {}
profesori = {}

lista_profi = []

ORAR = []
VARIANTE_ORAR_SOFT = []
VARIANTE_ORAR_HARD_HARD = []
PREFERAT = "Preferat"
NEPREFERAT = "Nepreferat"
MATERII = "Materii"
capacitate = {}
prof_nr_clase_orar = {}

RESPINS = []
MAX_DEPASIRE = 0

nr_zile = 0
nr_ore = 0

def count_aparitii_materie(materie, sali):
    count = 0
    for sala in sali.values():
        if materie in sala['Materii']:
            count += 1
    return count

def aranjare(materii, profi):
    # materile cu cei mai multi profi in fata
    sorted_materii = sorted(materii.items(), key=lambda x: (-x[1], x[0]))
    sorted_materii = sorted(sorted_materii, key=lambda x: (count_aparitii_materie(x[0], sali), x[0]))
    materii_ordine_descrescatoare = [materie[0] for materie in sorted_materii]

    # profesori cu cele mai putine materii si cei mai putini care apar in orar
    profesori_ordonati = sorted(profesori.items(), key=lambda x: (len(x[1]['Materii']), profi[x[0]]))
    nume_profesori_ordonati = [profesor[0] for profesor in profesori_ordonati]

    return materii_ordine_descrescatoare, nume_profesori_ordonati


def aparitii_profi(profi):
    return sorted(profi.keys(), key=lambda x: profi[x])