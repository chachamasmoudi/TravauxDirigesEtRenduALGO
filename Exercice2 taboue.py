# Exercice 2 : problème de transport avec la recherche taboue
#
#   demandes : 4  5  8   (4+5+8 = 17 = 8+9, donc tout le stock part)
#
# Idée : une solution c'est un tableau x 2x3 (x[i][j] = nb de containers
# envoyés de Di vers Mj). Il faut que :
#   - chaque ligne fasse le stock du dépôt
#   - chaque colonne fasse la demande du magasin
# et on veut le coût total le plus petit possible.
#
# Pour passer d'une solution à une autre (un "voisin") je fais un cycle 2x2 :
# +1 sur deux cases en diagonale et -1 sur les deux autres.
# Comme ça les sommes des lignes et des colonnes ne changent pas.

COUT = [[5, 3, 4],
        [6, 7, 2]]
STOCK = [8, 9]
DEMANDE = [4, 5, 8]


def cout_total(x):
    # somme de (quantité * coût unitaire) pour chaque case
    total = 0
    for i in range(len(STOCK)):
        for j in range(len(DEMANDE)):
            total += COUT[i][j] * x[i][j]
    return total


def solution_initiale():
    # méthode du coin Nord-Ouest : on part de la case en haut à gauche
    # et on met le max possible, puis on avance
    stock = STOCK[:]
    dem = DEMANDE[:]
    # tableau 2x3 rempli de zéros : une ligne par dépôt, une colonne par magasin
    # on utilise "for _ in STOCK" pour créer une nouvelle liste par ligne
    # (x[i][j] = nb de containers envoyés de Di vers Mj)
    x = [[0] * len(DEMANDE) for _ in STOCK]
    i = 0
    j = 0
    while i < len(stock) and j < len(dem):
        q = min(stock[i], dem[j])   # on livre le max possible
        x[i][j] += q
        stock[i] -= q
        dem[j] -= q
        if stock[i] == 0:           # le dépôt est vide -> dépôt suivant
            i += 1
        else:                       # sinon c'est le magasin qui est servi
            j += 1
    return x


def voisins(x):
    # on génère tous les voisins avec un cycle 2x2
    # (avec 2 dépôts il suffit de choisir 2 colonnes j1 et j2)
    # j1 et j2 = deux colonnes différentes, donc deux magasins (pas les stocks !)
    #   +1 sur (D1, j1) et (D2, j2)
    #   -1 sur (D1, j2) et (D2, j1)
    n = len(DEMANDE)
    for j1 in range(n):
        for j2 in range(n):
            if j1 == j2:
                continue
            # on ne peut retirer 1 que s'il y a au moins 1 container dans la case
            if x[0][j2] >= 1 and x[1][j1] >= 1:
                y = [ligne[:] for ligne in x]   # copie, sinon on modifie x
                y[0][j1] += 1
                y[1][j2] += 1
                y[0][j2] -= 1
                y[1][j1] -= 1
                # un mouvement = les deux cases qui augmentent
                # (comme ça le même mouvement s'écrit toujours pareil)
                aug = frozenset({(0, j1), (1, j2)})
                # et le mouvement inverse = les deux cases qui ont diminué
                dim = frozenset({(0, j2), (1, j1)})
                yield aug, dim, y


def nom(cases):
    # juste pour afficher joliment, ex : +D1M2 +D2M1
    return "+" + " +".join("D%dM%d" % (i + 1, j + 1) for i, j in sorted(cases))


def recherche_taboue(max_iter=10, tenure=3):
    x = solution_initiale()
    best = [ligne[:] for ligne in x]
    best_cout = cout_total(x)
    tabou = {}   # mouvement interdit -> jusqu'à quelle itération il est interdit

    print("Solution initiale (coin Nord-Ouest) :", x, "coût =", best_cout)

    for it in range(1, max_iter + 1):
        choix = None
        for aug, dim, y in voisins(x):
            c = cout_total(y)
            est_tabou = tabou.get(aug, 0) >= it
            # aspiration : si le mouvement est tabou mais qu'il bat le meilleur
            # coût qu'on a vu, on l'autorise quand même
            if est_tabou and c >= best_cout:
                continue
            # on garde le voisin le moins cher (même s'il est pire que x)
            if choix is None or c < choix[0]:
                choix = (c, y, aug, dim)

        if choix is None:
            print("Plus aucun voisin possible, on s'arrête.")
            break

        c, x, aug, dim = choix
        # on interdit le mouvement inverse pendant 'tenure' itérations
        # pour ne pas revenir directement en arrière
        tabou[dim] = it + tenure

        if c < best_cout:
            best = [ligne[:] for ligne in x]
            best_cout = c

        print("Iter %2d | mouvement %s | solution %s | coût = %3d | meilleur = %d"
              % (it, nom(aug), x, c, best_cout))

    return best, best_cout


if __name__ == "__main__":
    sol, c = recherche_taboue()
    print("\n=== Meilleure solution trouvée ===")
    for i, ligne in enumerate(sol, 1):
        for j, q in enumerate(ligne, 1):
            print("D%d -> M%d : %d containers" % (i, j, q))
    print("Coût total minimal =", c)