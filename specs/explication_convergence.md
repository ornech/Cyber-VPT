# Convergence et rapprochement vectoriel

**Point de départ observable :** une attaque documentée n'apparaît presque jamais d'un seul coup sous sa forme complète. Ce qui apparaît d'abord, ce sont des actions partielles, parfois faibles, qui commencent à dériver vers une forme connue.

Le rôle du moteur n'est donc de détecter précocement une attaque non par attribution de sa source, mais par convergence progressive d’une trajectoire d’actions observées vers une trajectoire d’attaque connue.

## 1. Espace commun de comparaison
Les deux objets comparés sont :
- `T_user` : trajectoire construite à partir des événements observés ;
- `T_mitre` : trajectoire de référence issue d'une technique MITRE vectorisée.

Les deux vivent dans le même espace :

$$[0,1]^5$$

Chaque point de la trajectoire est un `Vector5D` valide.

## 2. Nature du rapprochement
Le rapprochement porte sur des **séquences**, pas sur des points isolés.

Une seule action proche d'un modèle MITRE peut être bénigne. Une suite d'actions dont la forme, le rythme et l'intensité s'alignent progressivement sur une séquence MITRE devient beaucoup plus préoccupante.

## 3. Algorithme de matching
Le projet peut utiliser **DTW** pour comparer deux trajectoires exécutées à des vitesses différentes.

L'idée n'est pas de superposer les timestamps exacts, mais de comparer des dynamiques compatibles :
- attaque rapide ;
- attaque « low and slow » ;
- imitation incomplète d'une séquence connue.

## 4. Distance canonique
Le moteur doit distinguer deux niveaux de distance.

### 4.1. Distance brute
`raw_distance` est produite par l'algorithme de matching.

Cette distance dépend de la longueur des séquences et de la métrique locale. Elle ne doit pas servir directement à lever une alerte.

### 4.2. Distance normalisée
La seule distance exploitable côté décision est :

$$normalized\_distance \in [0,1]$$

Exemple de contrat :

$$normalized\_distance = min(\frac{raw\_distance}{distance_{max}}, 1.0)$$

puis :

$$match\_score = 1 - normalized\_distance$$

avec :

$$match\_score \in [0,1]$$

Ce point doit être figé. Tant qu'un document parle de `Distance < ε` et un autre de `1 - DTW / Distance_max`, le système n'a pas de vérité métrique unique.

## 5. Résultat de matching attendu
Le résultat du rapprochement doit au minimum contenir :
- `normalized_distance`
- `match_score`
- `matched_stage`
- `completion_probability`

### 5.1. `matched_stage`
Le moteur doit indiquer quelle étape de la trajectoire MITRE est la plus proche de la trajectoire observée.

### 5.2. `completion_probability`
Cette valeur n'est pas une certitude d'attaque. Elle exprime la proportion de trajectoire MITRE déjà mimée par la trajectoire observée.

Présenter cette probabilité comme une preuve serait méthodologiquement faible et juridiquement risqué.

## 6. Politique d'alerte
Le composant de décision applique une politique sur `match_score`.

Exemple :
- `match_score < 0.50` : bruit ou proximité insuffisante ;
- `0.50 <= match_score < 0.80` : surveillance renforcée ;
- `match_score >= 0.80` : alerte critique.

Le moteur de matching calcule ; le moteur d'alerte décide. Mélanger les deux revient à enfouir une politique de sécurité dans une formule mathématique, ce qui rend ensuite les réglages illisibles.

## 7. Rôle des signaux faibles
Les signaux faibles apparaissent quand :
- la criticité commence à monter ;
- le payload devient plus entropique ;
- le rythme change ;
- l'intensité des actions progresse ;
- l'empreinte porteuse est rare.

Pris séparément, chacun peut rester ambigu. Pris en trajectoire, ils peuvent déjà dessiner la forme initiale d'une technique MITRE.

## 8. Limites à garder visibles
Le système ne prédit pas l'avenir au sens fort. Il estime qu'une trajectoire observée devient **proche** d'une trajectoire d'attaque connue.

Il reste donc dépendant :
- de la qualité des règles de vectorisation ;
- de la qualité du référentiel MITRE vectorisé ;
- du calibrage des seuils ;
- de la couverture des comportements légitimes proches d'une attaque.

Une convergence forte vers MITRE sans base de comparaison sur le trafic légitime conduira simplement à industrialiser le faux positif.
