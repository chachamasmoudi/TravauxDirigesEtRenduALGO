# -*- coding: utf-8 -*-
"""
Un mouvement est identifié par l'ENSEMBLE des deux cases qui augmentent
(frozenset). Ainsi un même mouvement n'a qu'une seule écriture, et la liste
taboue reconnaît bien le retour en arrière.
"""

COUT = [[5, 3, 4],
        [6, 7, 2]]
STOCK = [8, 9]
DEMANDE = [4, 5, 8]


def cout_total(x):
    return sum(COUT[i][j] * x[i][j]
               for i in range(len(STOCK)) for j in range(len(DEMANDE)))


def solution_initiale():
    """Départ du coin la haut à gauche"""
    stock, dem = STOCK[:], DEMANDE[:]
    x = [[0] * len(DEMANDE) for _ in STOCK]
    i = j = 0
    while i < len(stock) and j < len(dem):
        q = min(stock[i], dem[j])
        x[i][j] += q
        stock[i] -= q
        dem[j] -= q
        if stock[i] == 0:
            i += 1
        else:
            j += 1
    return x


def voisins(x):
    """Génère (cases_augmentées, cases_diminuées, nouvelle_solution).

    Avec 2 dépôts, le mouvement est défini par deux colonnes (j1, j2) :
    +1 sur (D1,j1) et (D2,j2) ; -1 sur (D1,j2) et (D2,j1).
    Il faut au moins 1 container sur les cases qu'on diminue.
    """
    n = len(DEMANDE)
    for j1 in range(n):
        for j2 in range(n):
            if j1 == j2:
                continue
            if x[0][j2] >= 1 and x[1][j1] >= 1:
                y = [ligne[:] for ligne in x]
                y[0][j1] += 1
                y[1][j2] += 1
                y[0][j2] -= 1
                y[1][j1] -= 1
                aug = frozenset({(0, j1), (1, j2)})
                dim = frozenset({(0, j2), (1, j1)})
                yield aug, dim, y


def nom(cases):
    return "+" + " +".join(f"D{i + 1}M{j + 1}" for i, j in sorted(cases))


def recherche_taboue(max_iter=10, tenure=3):
    x = solution_initiale()
    best, best_cout = [l[:] for l in x], cout_total(x)
    tabou = {}  # mouvement interdit -> dernière itération où il reste interdit

    print("Solution initiale (coin Nord-Ouest) :", x, "coût =", best_cout)
    for it in range(1, max_iter + 1):
        choix = None
        for aug, dim, y in voisins(x):
            c = cout_total(y)
            est_tabou = tabou.get(aug, 0) >= it
            # critère d'aspiration : un mouvement tabou est accepté
            # s'il donne un coût meilleur que le meilleur global
            if est_tabou and c >= best_cout:
                continue
            if choix is None or c < choix[0]:
                choix = (c, y, aug, dim)
        if choix is None:
            print("Aucun voisin admissible : arrêt.")
            break
        c, x, aug, dim = choix
        # on interdit le mouvement inverse pendant 'tenure' itérations
        tabou[dim] = it + tenure
        if c < best_cout:
            best, best_cout = [l[:] for l in x], c
        print(f"Iter {it:2d} | mouvement {nom(aug)} | solution {x} | "
              f"coût = {c:3d} | meilleur = {best_cout}")
    return best, best_cout


if __name__ == "__main__":
    sol, c = recherche_taboue()
    print("\n=== Meilleure solution trouvée ===")
    for i, ligne in enumerate(sol, 1):
        for j, q in enumerate(ligne, 1):
            print(f"D{i} -> M{j} : {q} containers")
    print("Coût total minimal =", c)