# Exercice 3 : voyageur de commerce (8 villes)
# 3 méthodes : 1) recherche taboue
# 2) recuit simulé
# 3) algorithme génétique
# La solution initiale pour la taboue et le recuit est 1-2-3-4-5-6-7-8-1.

import math
import random

# Dans le tableau, un "-" veut dire qu'il n'y a pas de route directe.
# Je mets un coût énorme (100) pour ces arêtes-là, comme ça une tournée qui
# les utilise n'est jamais intéressante.
INF = 100

# Le tableau ne donne que la moitié du haut, donc je suppose que les
# distances sont symétriques (d(a,b) = d(b,a)).
ARETES = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}
N = 8

# matrice des distances (je laisse la ligne 0 et la colonne 0 vides
# pour que les villes soient numérotées de 1 à 8)
D = [[INF] * (N + 1) for _ in range(N + 1)]
for (a, b), c in ARETES.items():
    D[a][b] = c
    D[b][a] = c


def cout(tour):
    # somme des 8 arêtes, la dernière ville revient à la première
    total = 0
    for k in range(N):
        total += D[tour[k]][tour[(k + 1) % N]]
    return total


def fmt(tour):
    # pour afficher la tournée avec le retour à la ville de départ
    return "-".join(map(str, tour + [tour[0]]))


def deux_opt(t, i, j):
    # voisin 2-opt : on inverse le morceau de la tournée entre i et j
    # (la ville 1 reste en position 0 donc i commence à 1)
    return t[:i] + t[i:j + 1][::-1] + t[j + 1:]


# ------------------------------------------------------------------
# 1) Recherche taboue
# ------------------------------------------------------------------
def recherche_taboue(max_iter=15, tenure=3):
    print("=" * 60)
    print("1) RECHERCHE TABOUE")
    print("=" * 60)
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    best = x[:]
    best_c = cout(x)
    tabou = {}   # (ville, ville) interdite -> itération où l'interdiction finit
    print("Solution initiale : %s  coût = %d" % (fmt(x), best_c))

    for it in range(1, max_iter + 1):
        cand = None
        # on teste toutes les inversions possibles
        for i in range(1, N - 1):
            for j in range(i + 1, N):
                y = deux_opt(x, i, j)
                c = cout(y)
                mv = (x[i], x[j])
                # mouvement tabou et qui ne bat pas le meilleur -> on le saute
                if tabou.get(mv, 0) >= it and c >= best_c:
                    continue
                if cand is None or c < cand[0]:
                    cand = (c, y, mv)
        if cand is None:
            break
        c, x, mv = cand
        # on interdit ce mouvement (dans les deux sens) pendant 'tenure' itérations
        tabou[mv] = it + tenure
        tabou[(mv[1], mv[0])] = it + tenure
        if c < best_c:
            best = x[:]
            best_c = c
        print("Iter %2d | 2-opt %s | %s | coût = %d | meilleur = %d"
              % (it, mv, fmt(x), c, best_c))

    print("--> Meilleure tournée : %s  coût = %d\n" % (fmt(best), best_c))
    return best, best_c


# ------------------------------------------------------------------
# 2) Recuit simulé
# ------------------------------------------------------------------
def recuit_simule(n_iter=5, T0=30.0, alpha=0.7, seed=3):
    # T0 et alpha je les ai choisis un peu au feeling (empirique) :
    # la température commence à 30 et elle est multipliée par 0.7 à chaque tour
    print("=" * 60)
    print("2) RECUIT SIMULE (5 itérations)")
    print("=" * 60)
    random.seed(seed)
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    c = cout(x)
    best = x[:]
    best_c = c
    T = T0
    print("Départ : %s  coût = %d  T0 = %s, T <- %s*T" % (fmt(x), c, T0, alpha))

    for it in range(1, n_iter + 1):
        # voisin au hasard (2-opt)
        i, j = sorted(random.sample(range(1, N), 2))
        y = deux_opt(x, i, j)
        cy = cout(y)
        delta = cy - c

        if delta < 0:
            # meilleur -> on accepte toujours
            accepte = True
            p = 1.0
        else:
            # moins bon -> on accepte quand même avec la probabilité e^(-delta/T)
            p = math.exp(-delta / T)
            accepte = random.random() < p

        print("Iter %d | T=%6.2f | voisin %s coût=%d | delta=%+d | p=%.4f | %s"
              % (it, T, fmt(y), cy, delta, p, "ACCEPTE" if accepte else "refuse"))

        if accepte:
            x = y
            c = cy
            if c < best_c:
                best = x[:]
                best_c = c
        T = T * alpha   # on refroidit

    print("--> Meilleure tournée : %s  coût = %d\n" % (fmt(best), best_c))
    return best, best_c


# ------------------------------------------------------------------
# 3) Algorithme génétique
# ------------------------------------------------------------------
def croisement_ox(p1, p2):
    # croisement OX : on garde un morceau du parent 1 et on complète
    # avec les villes qui manquent dans l'ordre du parent 2
    # (comme ça l'enfant est toujours une permutation valide)
    a, b = sorted(random.sample(range(N), 2))
    enfant = [None] * N
    enfant[a:b + 1] = p1[a:b + 1]
    reste = [v for v in p2 if v not in enfant]
    k = 0
    for i in range(N):
        if enfant[i] is None:
            enfant[i] = reste[k]
            k += 1
    return enfant


def mutation(t, pm=0.2):
    # avec une probabilité de 20% on échange 2 villes au hasard
    t = t[:]
    if random.random() < pm:
        i, j = random.sample(range(N), 2)
        t[i], t[j] = t[j], t[i]
    return t


def selection_tournoi(pop, k=3):
    # on tire 3 individus au hasard et on garde le meilleur (coût le plus petit)
    return min(random.sample(pop, k), key=cout)


def algo_genetique(taille=30, generations=40, seed=5):
    print("=" * 60)
    print("3) ALGORITHME GENETIQUE")
    print("=" * 60)
    random.seed(seed)

    # population de départ : 30 tournées mélangées au hasard
    pop = []
    for _ in range(taille):
        t = list(range(1, N + 1))
        random.shuffle(t)
        pop.append(t)
    best = min(pop, key=cout)

    for g in range(1, generations + 1):
        nouvelle = [best[:]]   # élitisme : on garde toujours le meilleur
        while len(nouvelle) < taille:
            e = croisement_ox(selection_tournoi(pop), selection_tournoi(pop))
            nouvelle.append(mutation(e))
        pop = nouvelle
        cand = min(pop, key=cout)
        if cout(cand) < cout(best):
            best = cand[:]
        if g % 5 == 0 or g == 1:
            print("Génération %2d | meilleur = %s | coût = %d"
                  % (g, fmt(best), cout(best)))

    # on remet la tournée pour qu'elle commence à la ville 1
    k = best.index(1)
    best = best[k:] + best[:k]
    print("--> Meilleure tournée : %s  coût = %d\n" % (fmt(best), cout(best)))
    return best, cout(best)


if __name__ == "__main__":
    recherche_taboue()
    recuit_simule()
    algo_genetique()