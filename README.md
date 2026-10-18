Dans ce TD, j'ai utilisé des métaheuristiques pour résoudre deux problèmes : un problème de transport (exercice 2) et un problème de voyageur de commerce (exercice 3).
 
Pour l'exercice 2, la recherche taboue a trouvé un coût de 52, qui est la meilleure solution possible. Ce qui m'a le plus aidé à comprendre, c'est la liste taboue : elle empêche de revenir en arrière et oblige l'algorithme à essayer d'autres solutions, même un peu moins bonnes.
 
Pour l'exercice 3, la recherche taboue et l'algorithme génétique ont tous les deux trouvé la tournée 1-2-4-5-6-7-3-8-1 de coût 98. J'ai testé toutes les tournées possibles et 98 est bien le minimum. La recherche taboue y est arrivée plus vite (dès la 4ème itération). Le recuit simulé est resté à 103, mais je pense que c'est surtout parce qu'on ne faisait que 5 itérations, ce qui est trop peu pour juger la méthode.

J'ai aussi retenu que le choix du voisinage et des paramètres (température, taille de la population, etc.) compte beaucoup dans le résultat.
