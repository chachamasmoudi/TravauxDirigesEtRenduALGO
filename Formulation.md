# Ordonnancement de la maintenance de centrales électriques — Formulation pour AG

## 1. Données
- 7 unités, capacités (MW) : C = [20, 15, 35, 40, 15, 15, 10] → capacité totale = 150 MW
- Intervalles de maintenance requis : d = [2, 2, 1, 1, 1, 1, 1]
- 4 intervalles dans l'année, demande (MW) : D = [80, 90, 65, 70]

## 2. Variables de décision
x(u,t) ∈ {0,1} : 1 si l'unité u est en maintenance pendant l'intervalle t (u = 1..7, t = 1..4).

## 3. Contraintes
1. Chaque unité u est en maintenance exactement d(u) intervalles : Σ_t x(u,t) = d(u).
2. La maintenance est continue (commence au début d'un intervalle, finit à la fin d'un intervalle) :
   - unités 1 et 2 : 1100, 0110, 0011
   - unités 3 à 7 : 1000, 0100, 0010, 0001
3. Réserve strictement positive à chaque intervalle : R(t) > 0 (la réserve doit dépasser la demande).

## 4. Fonction objectif
Réserve de l'intervalle t :

R(t) = Σ_u C(u) − Σ_u C(u)·x(u,t) − D(t) = 150 − P_maint(t) − D(t)

Objectif : maximiser la plus petite réserve de l'année

**max  f(x) = min_t R(t)**

## 5. Codage
- Chromosome = 7 gènes × 4 bits = 28 bits ; 

  gène u = motif de maintenance de l'unité u,

  bit t = intervalle t.
- Espace de recherche valide : 3 × 3 × 4⁵ = 9 216 cédules.
- Les gènes sont toujours des motifs valides (les contraintes 1 et 2 sont satisfaites par construction).

## 6. Fonction d'évaluation (fitness)
fitness = max(0, min_t R(t)) → une réserve négative donne une performance de 0 (contrainte 3 gérée par pénalité).

## 7. Opérateurs génétiques
- **Sélection par loterie (roulette)** : probabilité de choisir l'individu i = f_i / Σ f_j.
- **Croisement à 1 point**, coupure uniquement entre deux gènes (blocs de 4 bits), probabilité pc = 0,8.
- **Mutation par inversion** : pour chaque gène, avec probabilité pm = 0,15, on inverse (miroir) l'ordre de ses 4 bits :
  1100↔0011, 1000↔0001, 0100↔0010 ; 0110 reste inchangé. Le résultat est toujours un motif valide.
- **Mutation par remplacement** (variante testée) : le gène est remplacé par un autre motif valide tiré au hasard (comme dans le cours).
- Élitisme : le meilleur individu est conservé à chaque génération.

## 8. Paramètres utilisés
Population = 40 (≈ 6 × le nombre de gènes), 60 générations, pc = 0,8, pm = 0,15.

## 9. Résultats (voir ga_maintenance.py)
- Optimum exact par force brute : **25 MW** (ex. 1100 1100 0010 0001 0010 0001 1000).
- AG avec inversion : optimum atteint dans 19 exécutions sur 20 (moyenne 24,75).
- AG avec remplacement : optimum atteint dans 20 exécutions sur 20.
- Remarque : l'inversion ne peut pas changer le gène 0110 et n'explore que les motifs « symétriques » ; elle est donc moins diversifiante que le remplacement, d'où un taux de réussite un peu plus faible.