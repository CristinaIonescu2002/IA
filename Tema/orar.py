import utils as u
import check_constraints as cc
import sys
import random
import numpy as np
import os
import math
import copy

zile_saptamana = []
intervale_orare = []
lista_profi = []
sali = {}
materii = {}
profesori = {}
capacitate = {}
prof_nr_clase_orar = {}
nr_zile = 0
nr_ore = 0

ORAR = []
RESPINS = []
VARIANTE_ORAR = []
WRONG_PLACEMENTS = []
PREFERAT = "Preferat"
NEPREFERAT = "Nepreferat"
MATERII = "Materii"
MAX_DEPASIRE = 0



def evaluate_for_first(schedule):
    total_score = 0
    copie_nr_studenti = materii.copy()
    prof_nr_clase_orar = {nume_prof: 0 for nume_prof in continut['Profesori']}
    check = True
  
    for i, ora in enumerate(intervale_orare):
        for j, zi in enumerate(zile_saptamana):
            for sala, valoare in schedule[i][j].items():
                if valoare != (None, None):
                    for sala_k, valoare_k in schedule[i][j].items():
                        if sala != sala_k:
                            if (valoare[0] == valoare_k[0]):
                                check = False
                    if prof_nr_clase_orar[valoare[0]] > 7:
                        check = False

                    copie_nr_studenti[valoare[1]] = copie_nr_studenti[valoare[1]] - capacitate[sala]
                    total_score += capacitate[sala]
                    prof_nr_clase_orar[valoare[0]] += 1

                    for elem in profesori[valoare[0]][NEPREFERAT] or elem[0] is None:
                        if ora == elem or zi == elem:
                            if (i, j, sala, valoare[0], valoare[1]) not in WRONG_PLACEMENTS:
                                group = (i, j, sala, valoare[0], valoare[1])
                                WRONG_PLACEMENTS.append(group)

    for _, nr in copie_nr_studenti.items():
        if nr > 0:
            check = False
    
    return check

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

def generate_first_table():
    if len(profesori) % len(sali) > len(sali) / 2:
        max_profs_on_interval = 7 - len(profesori) % len(sali) + len(sali) - len(profesori) % len(sali)
    else:
        max_profs_on_interval = 7 - len(profesori) % len(sali)

    ORAR = [[{} for _ in range(nr_zile)] for _ in range(nr_ore)]
    used_profs_matrix = [[[] for _ in range(nr_zile)] for _ in range(nr_ore)]

    copie_nr_studenti_materii = materii.copy()
    prof_nr_clase_orar = {nume_prof: 0 for nume_prof in continut['Profesori']}

    materii_ordine_descrescatoare, aparitii_profi_asc = aranjare(copie_nr_studenti_materii, prof_nr_clase_orar)

    # salile cu cea mai mare capacitate in fata
    sali_sortate = sorted(sali.items(), key=lambda x: x[1]['Capacitate'], reverse=True)
    salile_ordine_descrescatoare = [sala[0] for sala in sali_sortate]

    for clasa in salile_ordine_descrescatoare:
        for i, _ in enumerate(intervale_orare):
            for j, _ in enumerate(zile_saptamana):
                alegere_facuta = False
                for materie in materii_ordine_descrescatoare:
                    if copie_nr_studenti_materii[materie] <= 0:
                        continue
                    for prof in aparitii_profi_asc:
                        if prof_nr_clase_orar[prof] == max_profs_on_interval or prof in used_profs_matrix[i][j]:
                            continue
                        for elem in VARIANTE_ORAR[i][j][clasa]:
                            if elem == (prof, materie):
                                ORAR[i][j][clasa] = elem
                                prof_nr_clase_orar[prof] = prof_nr_clase_orar[prof] + 1
                                copie_nr_studenti_materii[materie] = copie_nr_studenti_materii[materie] - sali[clasa]['Capacitate']

                                materii_ordine_descrescatoare, aparitii_profi_asc = aranjare(copie_nr_studenti_materii, prof_nr_clase_orar)
                                alegere_facuta = True
                                break
                        if alegere_facuta:
                            used_profs_matrix[i][j].append(prof)
                            break
                    if alegere_facuta:
                        break
                if not alegere_facuta:
                    ORAR[i][j][clasa] = (None, None)

    check = evaluate_for_first(ORAR)

    if not check:
        print("Ceva a mers prost in generarea Orarului!")
    
    return ORAR

def evaluate_schedule(schedule):
    total_score = 0
    prof_nr_clase_orar = {nume_prof: 0 for nume_prof in continut['Profesori']}
    check = True
    contor_not_soft = 0

    for i in range(nr_ore):
        for j in range(nr_zile):
            for sala, valoare in schedule[i][j].items():
                if valoare != (None, None):
                    for sala_k, valoare_k in schedule[i][j].items():
                        if sala != sala_k:
                            if (valoare[0] == valoare_k[0]):
                                total_score = total_score - 20
                                check = False
                    if prof_nr_clase_orar[valoare[0]] > 7:
                        total_score = total_score - 20
                        check = False
                    incalcat = 0
                    for elem in profesori[valoare[0]][NEPREFERAT]:
                        if intervale_orare[i] == elem:
                            total_score = total_score - 5
                            contor_not_soft = contor_not_soft + 1
                            incalcat = incalcat + 1
                        if zile_saptamana[j] == elem:
                            total_score = total_score - 10
                            contor_not_soft = contor_not_soft + 1
                            incalcat = incalcat + 1

    # comentariu lasat pentru a se observa avansarea pe care o face
    print(f"total-evaluare:{total_score}")

    return total_score, check

def generate_neighbor(current_state):

    new_state_evaluation = -10000
    new_state = current_state
    new_state_check = False

    # swap intre intervale orare pe aceeasi clasa
    for elem in WRONG_PLACEMENTS:
        sala = elem[2]
        for i in range(nr_ore):
            for j in range(nr_zile):
                valoare = current_state[i][j][sala]

                if (i, j, sala, valoare[0], valoare[1]) != elem:           
                    aux_state = copy.deepcopy(current_state)

                    aux_state[elem[0]][elem[1]][elem[2]] = current_state[i][j][sala]
                    aux_state[i][j][sala] = current_state[elem[0]][elem[1]][elem[2]]

                    aux_evaluation, check = evaluate_schedule(aux_state)

                    if (aux_evaluation > new_state_evaluation):
                        new_state = copy.deepcopy(aux_state)
                        new_state_evaluation = aux_evaluation
                        new_state_check = check

    # swap intre profi
    for elem in WRONG_PLACEMENTS:
        for i in range(nr_ore):
            for j in range(nr_zile):
                for sala, valoare in current_state[i][j].items():
                    if valoare[0] == elem[3]:
                        continue
                    if valoare[1] in profesori[elem[3]][MATERII] and elem[4] in profesori[valoare[0]][MATERII]:
                        if (i, j, sala, valoare[0], valoare[1]) != elem:           
                            aux_state = copy.deepcopy(current_state)
                            nume1, materie1 = current_state[i][j][sala]
                            nume2, materie2 = current_state[elem[0]][elem[1]][elem[2]]

                            aux_state[elem[0]][elem[1]][elem[2]] = (nume1, materie2)
                            aux_state[i][j][sala] = (nume2, materie1)

                            aux_evaluation, check = evaluate_schedule(aux_state)

                            if (aux_evaluation > new_state_evaluation):
                                new_state = copy.deepcopy(aux_state)
                                new_state_evaluation = aux_evaluation
                                new_state_check = check

    return new_state, new_state_evaluation, new_state_check

def hc(current_state):
    print("hc\n")
    if current_state is None:
        current_state = generate_first_table()
        current_score, check = evaluate_schedule(current_state)

    while True:
        neighbor, neighbor_score, check = generate_neighbor(current_state)

        if neighbor_score > current_score:
            WRONG_PLACEMENTS.clear()
            _ = evaluate_for_first(neighbor)
            current_state = neighbor
            current_score = neighbor_score
        elif check:
            break

    return current_state

def add_element_to_list(pref):
    if pref[0] != "1" and pref[0] != "8":
        return pref, False

    ore = pref.split('-')

    ora_inceput = int(ore[0])
    ora_sfarsit = int(ore[1])

    if ora_sfarsit - ora_inceput == 2:
        return ("(" + str(ora_inceput) + ", " + str(ora_sfarsit) + ")"), False
    else:
        lista = []
        for i in range(2, ora_sfarsit-ora_inceput+2, 2):
            ora_final = ora_inceput + i
            lista.append("(" + str(ora_inceput+i-2) + ", " + str(ora_final) + ")")
        return lista, True

def gestionare_profesori():
    for nume_prof, detalii in continut['Profesori'].items():
        lista_profi.append(nume_prof)
        list_pref = []
        list_nepref = []
        for pref in detalii['Constrangeri']:
            if pref[0] == "!":
                pref = pref[1:]

                elemente, ext = add_element_to_list(pref)

                if ext:
                    list_nepref.extend(elemente)
                else:
                    list_nepref.append(elemente)
            else:
                elemente, ext = add_element_to_list(pref)
                if ext:
                    list_pref.extend(elemente)
                else:
                    list_pref.append(elemente)
        d = {
            PREFERAT: list_pref,
            NEPREFERAT: list_nepref,
            MATERII: detalii[MATERII]
        }

        profesori[nume_prof] = d

class Node:
    def __init__(self, state, parent=None):
        self.state = copy.deepcopy(state)
        self.visits = 0
        self.score = -1000
        self.children = []
        self.parent = parent

def select(node):
    while node.children:
        if not all(child.visits > 0 for child in node.children):
            return expand(node)
        else:
            total_visits = sum(child.visits for child in node.children)
            child = max(node.children, key=lambda child: child.score / child.visits + math.sqrt(2 * math.log(total_visits) / child.visits))
            node = child
    return node

def evaluate_schedule_mcts(schedule):
    total_score = 0
    prof_nr_clase_orar = {nume_prof: 0 for nume_prof in continut['Profesori']}
    contor_not_soft = 0

    for i in range(nr_ore):
        for j in range(nr_zile):
            for sala, valoare in schedule[i][j].items():
                if valoare != (None, None):
                    for sala_k, valoare_k in schedule[i][j].items():
                        if sala != sala_k:
                            if (valoare[0] == valoare_k[0]):
                                total_score = total_score - 20
                    if prof_nr_clase_orar[valoare[0]] > 7:
                        total_score = total_score - 20
                    incalcat = 0
                    for elem in profesori[valoare[0]][NEPREFERAT]:
                        if intervale_orare[i] == elem:
                            total_score = total_score - 5
                            contor_not_soft = contor_not_soft + 1
                            incalcat = incalcat + 1
                        if zile_saptamana[j] == elem:
                            total_score = total_score - 10
                            contor_not_soft = contor_not_soft + 1
                            incalcat = incalcat + 1

    return total_score

def expand(node):
    WRONG_PLACEMENTS.clear()
    _ = evaluate_for_first(node.state)
    child_state = get_possible_states(node.state)
    child_node = Node(child_state, node)
    node.children.append(child_node)
    return child_node

def get_possible_states(state):

    new_state_evaluation = -10000
    new_state = state
    lista_elemente = []

    # swap intre intervale orare pe aceeasi clasa
    for elem in WRONG_PLACEMENTS:
        sala = elem[2]
        for i in range(nr_ore):
            for j in range(nr_zile):
                valoare = state[i][j][sala]

                if (i, j, sala, valoare[0], valoare[1]) != elem:           
                    aux_state = copy.deepcopy(state)

                    aux_state[elem[0]][elem[1]][elem[2]] = state[i][j][sala]
                    aux_state[i][j][sala] = state[elem[0]][elem[1]][elem[2]]

                    aux_evaluation = evaluate_schedule_mcts(aux_state)

                    if (aux_evaluation > new_state_evaluation):
                        new_state = copy.deepcopy(aux_state)
                        new_state_evaluation = aux_evaluation
                        if new_state not in lista_elemente:
                            lista_elemente.append(new_state)

    # swap intre profi
    for elem in WRONG_PLACEMENTS:
        for i in range(nr_ore):
            for j in range(nr_zile):
                for sala, valoare in state[i][j].items():
                    if valoare[0] == elem[3]:
                        continue
                    if valoare[1] in profesori[elem[3]][MATERII] and elem[4] in profesori[valoare[0]][MATERII]:
                        if (i, j, sala, valoare[0], valoare[1]) != elem:           
                            aux_state = copy.deepcopy(state)
                            nume1, materie1 = state[i][j][sala]
                            nume2, materie2 = state[elem[0]][elem[1]][elem[2]]

                            aux_state[elem[0]][elem[1]][elem[2]] = (nume1, materie2)
                            aux_state[i][j][sala] = (nume2, materie1)

                            aux_evaluation = evaluate_schedule_mcts(aux_state)

                            if (aux_evaluation > new_state_evaluation):
                                new_state = copy.deepcopy(aux_state)
                                new_state_evaluation = aux_evaluation
                                if new_state not in lista_elemente:
                                    lista_elemente.append(new_state)

    state_ales = random.choice(lista_elemente) if lista_elemente else state

    return state_ales

def backpropagate(node, score):
    while node:
        node.visits += 1
        node.score = score
        node = node.parent

def mcts(root_state, num_iterations):
    print("mtsc\n")

    root_node = Node(root_state)
    best_child_state = None
    best_child_score = float('-inf')
    for i in range(num_iterations):
        print(f"iteratie:{i}")

        node = select(root_node)
        if not node.children:
            child_node = expand(node)
            score = evaluate_schedule_mcts(child_node.state)
            child_node.score = score
            backpropagate(child_node, score)
            if score > best_child_score:
                    best_child_score = score
                    best_child_state = copy.deepcopy(child_node.state)
        else:
            sampled_children = random.sample(node.children, k=len(node.children))
            for child_node in sampled_children:
                score = evaluate_schedule_mcts(child_node.state)
                child_node.score = score
                backpropagate(child_node, score)
                if score > best_child_score:
                    best_child_score = score
                    best_child_state = copy.deepcopy(child_node.state)

    return best_child_state

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print('\nSe rulează de exemplu:\n\npython3 orar.py mcts/hc nume_fisier_intrare\n')
        sys.exit(0)

    alg_type = sys.argv[1]
    file_name = sys.argv[2]

    path = f'inputs/{file_name}.yaml'

    continut = u.read_yaml_file(path)

    intervale_orare = continut['Intervale']
    zile_saptamana = continut['Zile']
    materii = continut['Materii']
    sali = continut['Sali']

    nr_zile = len(zile_saptamana)
    nr_ore = len(intervale_orare)

    for nume, key in sali.items():
        capacitate[nume] = key['Capacitate']
        if MAX_DEPASIRE < key['Capacitate']:
            MAX_DEPASIRE = key['Capacitate']

    gestionare_profesori()

    VARIANTE_SALI = {}
    for nume_sala, valoare_sala in sali.items():
        for materie in valoare_sala['Materii']:
            for nume_prof, valoare_prof in profesori.items():
                if materie in valoare_prof['Materii']:
                    if nume_sala not in VARIANTE_SALI:
                        VARIANTE_SALI[nume_sala] = [(nume_prof, materie)]
                    else:
                        VARIANTE_SALI[nume_sala].append((nume_prof, materie))

    VARIANTE_ORAR = [[{} for _ in range(nr_zile)] for _ in range(nr_ore)]
    for i, ora in enumerate(intervale_orare):
        for j, zi in enumerate(zile_saptamana):
            d = {}
            for nume_sala, valori in VARIANTE_SALI.items():
                lista_pe_sala = []
                for prof in valori:
                    if (str(ora) in profesori[prof[0]][NEPREFERAT] and str(zi) in profesori[prof[0]][NEPREFERAT]) \
                            or (str(ora) in profesori[prof[0]][PREFERAT] and str(zi) in profesori[prof[0]][PREFERAT]):
                        lista_pe_sala.append((prof[0], prof[1]))

                lista_pe_sala.append((None, None))
                d[nume_sala] = lista_pe_sala
            
            VARIANTE_ORAR[i][j] = d

    final_schedule = []

    if alg_type == "mcts":
        root_state = generate_first_table()
        num_iterations = 500
        final_schedule = mcts(root_state, num_iterations)
    elif alg_type == "hc":
        final_schedule = hc(None)
    else:
        print("Wrong algoritm type!\n")
        sys.exit(0)

    result = {}
    initiale_profi, _ = u.get_profs_initials(lista_profi)
    if final_schedule != []:
        for j, zi in enumerate(zile_saptamana):
            result[zi] = {}
            for i, ora in enumerate(intervale_orare):
                ore_str = ora.strip('()').replace(',', ' ')
                ore = ore_str.split()

                ora_inceput = int(ore[0])
                ora_sfarsit = int(ore[1])

                valori_sali = {}
                for sala, valori in final_schedule[i][j].items():
                    if valori[0] == None:
                        valori_sali[sala] = None
                    else:
                        valori_sali[sala] = valori
                result[zi][(ora_inceput, ora_sfarsit)] = valori_sali

    folder_name = f"results-{alg_type}"
    file = f'{file_name}.txt'
    input_name = f'inputs/{file_name}.yaml'

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    cale_fisier = os.path.join(folder_name, file)

    print(u.pretty_print_timetable(result, input_name))

    data = u.read_yaml_file(input_name)
    print("...Hard:................... ")
    hard_result = cc.check_mandatory_constraints(result, data)
    print(hard_result)
    print("...Soft:................... ")
    soft_result = cc.check_optional_constraints(result, data)
    print(soft_result)
    print(".............................")

    with open(cale_fisier, "w") as f:
        f.write(u.pretty_print_timetable(result, input_name))
        f.write(f"Incalca {hard_result} constrangeri hard!\n")
        f.write(f"Incalca {soft_result} constrangeri soft!\n")
        f.write(f"Pentru mai multe detalii se pot vedea in terminal la rulare!")
