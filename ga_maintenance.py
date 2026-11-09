"""
Ordonnancement de la maintenance de centrales électriques par algorithme génétique.

- Codage      : 7 gènes de 4 bits (1 gène = 1 unité, 1 bit = 1 intervalle)
- Fitness     : plus petite réserve sur les 4 intervalles (0 si négative)
- Sélection   : loterie (roulette proportionnelle à la fitness)
- Croisement  : à 1 point, uniquement aux frontières de gènes (blocs de 4 bits)
- Mutation    : par inversion (miroir du bloc de 4 bits d'un gène) ;
                variante "remplacement" par un motif valide au choix.
"""
import random
import itertools
import argparse

# ----------------------------- Données du problème -----------------------------
CAPACITE = [20, 15, 35, 40, 15, 15, 10]      # MW par unité
NB_INTERV_MAINT = [2, 2, 1, 1, 1, 1, 1]      # intervalles requis par unité
DEMANDE = [80, 90, 65, 70]                   # MW par intervalle
N_UNITES = len(CAPACITE)
N_INTERV = len(DEMANDE)
CAP_TOTALE = sum(CAPACITE)                   # 150 MW


def motifs_possibles(k, n=N_INTERV):
    res = []
    for debut in range(n - k + 1):
        bits = [0] * n
        for i in range(debut, debut + k):
            bits[i] = 1
        res.append(tuple(bits))
    return res


MOTIFS = [motifs_possibles(k) for k in NB_INTERV_MAINT]
# Unités 1,2 : 1100, 0110, 0011 ; unités 3..7 : 1000, 0100, 0010, 0001


# ----------------------------- Chromosome & fitness ----------------------------
def chromosome_aleatoire():
    """Liste de 7 gènes ; chaque gène est un tuple de 4 bits valide."""
    return [random.choice(MOTIFS[u]) for u in range(N_UNITES)]


def reserves(chrom):
    """Réserve de chaque intervalle = Cap_totale - P_maintenance - demande."""
    res = []
    for t in range(N_INTERV):
        p_maint = sum(CAPACITE[u] * chrom[u][t] for u in range(N_UNITES))
        res.append(CAP_TOTALE - p_maint - DEMANDE[t])
    return res


def fitness(chrom):
    """Performance = plus petite réserve ; 0 si une réserve est négative."""
    return max(0, min(reserves(chrom)))


def en_str(chrom):
    return " ".join("".join(map(str, g)) for g in chrom)


# ----------------------------- Opérateurs génétiques ---------------------------
def selection_loterie(pop, fits):
    """Roulette : probabilité de sélection proportionnelle à la fitness."""
    total = sum(fits)
    if total == 0:                      # tous nuls -> tirage uniforme
        return random.choice(pop)
    r = random.uniform(0, total)
    cumul = 0.0
    for ind, f in zip(pop, fits):
        cumul += f
        if r <= cumul:
            return ind
    return pop[-1]


def croisement(p1, p2, pc):
    """Croisement à 1 point, coupure entre deux gènes (blocs de 4 bits)."""
    if random.random() < pc:
        pt = random.randint(1, N_UNITES - 1)
        return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]
    return list(p1), list(p2)


def mutation_inversion(chrom, pm):
    """Pour chaque gène, avec proba pm : inversion (miroir) des 4 bits.
    1100 <-> 0011, 1000 <-> 0001, 0100 <-> 0010 ; 0110 reste 0110.
    Le résultat est toujours un motif valide."""
    return [g[::-1] if random.random() < pm else g for g in chrom]


def mutation_remplacement(chrom, pm):
    """Variante : le gène est remplacé par un autre motif valide (cf. cours)."""
    return [random.choice(MOTIFS[u]) if random.random() < pm else g
            for u, g in enumerate(chrom)]


MUTATIONS = {"inversion": mutation_inversion, "remplacement": mutation_remplacement}


# ----------------------------- Boucle de l'AG ----------------------------------
def algo_genetique(taille_pop=40, generations=60, pc=0.8, pm=0.15,
                   mutation="inversion", elitisme=True, graine=None, verbose=True):
    if graine is not None:
        random.seed(graine)
    mut = MUTATIONS[mutation]
    pop = [chromosome_aleatoire() for _ in range(taille_pop)]
    meilleur, hist = None, []

    for gen in range(generations + 1):
        fits = [fitness(c) for c in pop]
        i_best = max(range(len(pop)), key=lambda i: fits[i])
        if meilleur is None or fits[i_best] > fitness(meilleur):
            meilleur = list(pop[i_best])
        hist.append((max(fits), sum(fits) / len(fits)))
        if verbose and gen % 10 == 0:
            print(f"Gén {gen:3d} | meilleure = {hist[-1][0]:3d} | moyenne = {hist[-1][1]:6.2f}")
        if gen == generations:
            break

        nouvelle = [list(meilleur)] if elitisme else []
        while len(nouvelle) < taille_pop:
            p1 = selection_loterie(pop, fits)
            p2 = selection_loterie(pop, fits)
            e1, e2 = croisement(p1, p2, pc)
            nouvelle.append(mut(e1, pm))
            if len(nouvelle) < taille_pop:
                nouvelle.append(mut(e2, pm))
        pop = nouvelle
    return meilleur, hist


def force_brute():
    """Vérification : énumération exhaustive (3*3*4^5 = 9216 cédules)."""
    best, best_c = -1, None
    for combo in itertools.product(*MOTIFS):
        f = fitness(list(combo))
        if f > best:
            best, best_c = f, list(combo)
    return best, best_c


def afficher(chrom):
    print("Chromosome :", en_str(chrom))
    print("Réserves par intervalle :", reserves(chrom))
    print("Fitness (plus petite réserve) :", fitness(chrom))
    for u, g in enumerate(chrom, 1):
        ints = [i + 1 for i, b in enumerate(g) if b]
        print(f"  Unité {u} ({CAPACITE[u-1]} MW) : maintenance aux intervalles {ints}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", type=int, default=40)
    ap.add_argument("--gen", type=int, default=60)
    ap.add_argument("--pc", type=float, default=0.8)
    ap.add_argument("--pm", type=float, default=0.15)
    ap.add_argument("--mutation", choices=MUTATIONS, default="inversion")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    print(f"=== AG : sélection loterie + mutation '{a.mutation}' ===")
    best, hist = algo_genetique(a.pop, a.gen, a.pc, a.pm, a.mutation, graine=a.seed)
    print("\n--- Meilleure cédule trouvée par l'AG ---")
    afficher(best)
    opt, opt_c = force_brute()
    print(f"\n--- Optimum exact (force brute) : {opt} MW ---")
    print("Chromosome :", en_str(opt_c))

    # Comparaison des deux mutations sur 20 exécutions
    print("\n--- Comparaison sur 20 exécutions (graines 0..19) ---")
    for m in MUTATIONS:
        res = [fitness(algo_genetique(a.pop, a.gen, a.pc, a.pm, m, graine=s, verbose=False)[0])
               for s in range(20)]
        print(f"{m:13s}: moyenne={sum(res)/20:5.2f}  min={min(res)}  max={max(res)}  "
              f"optimum atteint {sum(r == opt for r in res)}/20")