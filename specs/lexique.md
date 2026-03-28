# Lexique — CYBER-VPT

**Règle observable :** un terme qui change de sens d'un document à l'autre détruit la traçabilité. Ce lexique fixe le vocabulaire minimal du projet.

## A
### Action observée
Événement élémentaire extrait d'un flux réseau, système ou applicatif, suffisamment structuré pour être vectorisé.

### ActionSemantics
Objet décrivant le sens opérationnel d'une action : `protocol`, `verb`, `permission`, `direction`.

### AlertEngine
Composant qui applique une politique de décision sur un `MatchResult`. Il ne calcule pas la distance ; il décide quoi en faire.

### AlertLevel
Niveau d'alerte produit par `AlertEngine`, par exemple `NONE`, `WATCH`, `CRITICAL`.

### ArchivedProfile
Résumé statistique d'une trajectoire inactive : `(μ, σ, n_points, first_seen, last_seen)`.

## B
### Baseline
Version déterministe du système, sans apprentissage, servant de référence avant toute IA.

### Bloom Filter
Structure probabiliste de test d'appartenance utilisée ici pour accélérer le lookup des empreintes connues. Accepte des faux positifs, pas des faux négatifs.

## C
### Calibration
Réglage des seuils, poids et paramètres à partir de données observées, et non d'une intuition seule.

### Commit
Unité élémentaire d'une trajectoire : `{ previous_hash, vector, timestamp, cumulative_score }`.

### Completion probability
Estimation du degré d'avancement d'une trajectoire observée par rapport à une trajectoire MITRE de référence. Ce n'est pas une preuve d'attaque.

### Contrat de domaine
Règle formelle imposée à la construction d'un objet métier. Exemple : `Vector5D ∈ [0,1]^5`.

### Convergence
Rapprochement progressif d'une trajectoire observée vers une trajectoire MITRE de référence.

### Count-Min Sketch
Structure de comptage approché utilisée pour estimer la fréquence d'apparition d'une empreinte ou d'une signature.

## D
### d1 — criticité
Dimension du vecteur mesurant l'importance opérationnelle de la ressource ou de la cible touchée.

### d2 — entropie
Dimension du vecteur mesurant le niveau de désordre informationnel du payload.

### d3 — dynamique temporelle
Dimension du vecteur mesurant le rythme d'enchaînement des actions à partir de `Δt` ou d'une fréquence locale.

### d4 — intensité
Dimension du vecteur mesurant la portée opérationnelle de l'action.

### d5 — rareté
Dimension du vecteur mesurant l'écart du porteur de l'action par rapport au comportement habituel du parc.

### Distance brute (`raw_distance`)
Distance produite directement par l'algorithme de matching. Elle n'est pas utilisée telle quelle pour la décision d'alerte.

### Distance normalisée (`normalized_distance`)
Distance ramenée dans `[0,1]`, seule exploitable côté décision.

### DTW — Dynamic Time Warping
Algorithme de comparaison de séquences tolérant des vitesses d'exécution différentes.

## E
### Empreinte
Signature technique stable ou semi-stable d'un porteur d'action. Dans le projet, elle est manipulée via `Fingerprint` et `id_emp`.

## F
### Fingerprint
Objet décrivant une empreinte technique, par exemple à partir de JA3, fingerprint OS, headers ou autres marqueurs.

### FingerprintResolver
Composant qui construit une `Fingerprint` à partir d'un `RawEvent`.

## G
### Ground truth
Jeu de vérité servant à évaluer ou calibrer le système. Dans ce projet, il est partiel et doit être construit avec prudence.

## H
### Hypothèse de mapping
Choix expliquant comment une phase MITRE a été transformée en `Vector5D`.

## I
### id_emp
Identifiant logique d'une empreinte. Il sert à rattacher plusieurs actions à un même porteur comportemental.

### Invariant
Propriété devant rester vraie dans tout état valide du système.

## J
### JA3
Empreinte de client TLS utilisée ici comme exemple de composante possible d'une `Fingerprint`.

## L
### Lexique
Référentiel de termes fixant le sens des mots utilisés dans les documents du projet.

## M
### Mahalanobis
Distance tenant compte de la covariance d'un nuage de points. Utilisée ici pour comparer un nouveau vecteur à un `ArchivedProfile`.

### MatchResult
Résultat produit par le moteur de matching. Il contient au minimum `normalized_distance`, `match_score`, `matched_stage`, `completion_probability`.

### Match score (`match_score`)
Score de rapprochement défini par `1 - normalized_distance`.

### Matrice de covariance (`σ`)
Résumé de la dispersion des points d'une trajectoire inactive autour de sa moyenne `μ`.

### Matcher
Composant qui compare une trajectoire observée à une trajectoire MITRE de référence et produit un `MatchResult`.

### MITRE ATT&CK
Base de connaissances documentant tactiques, techniques, sous-techniques, procédures et artefacts utiles à la modélisation du référentiel.

### Modèle de technique (`TechniqueModel`)
Représentation versionnée d'une technique MITRE dans le système : phases, vecteurs, hypothèses, niveau de confiance.

### Moyenne (`μ`)
Vecteur moyen d'un ensemble de points 5D.

## P
### Phase MITRE
Segment d'une technique ou d'une procédure MITRE vectorisé séparément pour former une trajectoire de référence.

### Préfixe d'attaque
Début observable d'une trajectoire d'attaque avant l'action terminale.

### Profil archivé
Voir `ArchivedProfile`.

## R
### Rareté
Voir `d5`.

### RawEvent
Événement brut minimal issu d'une source de logs avant transformation.

### Référentiel MITRE vectorisé
Ensemble versionné de trajectoires MITRE exprimées avec les mêmes règles de vectorisation que les événements observés.

## S
### Score cumulé
Valeur stockée dans un `Commit` pour conserver l'état de rapprochement à un instant donné.

### Seuil
Valeur de décision appliquée au `match_score` par `AlertEngine`.

### Signal faible
Action isolée ou peu marquée qui devient signifiante lorsqu'elle est replacée dans une trajectoire.

### Symétrie input / MITRE
Principe imposant que les actions observées et les phases MITRE soient vectorisées avec les mêmes définitions et les mêmes bornes.

## T
### Technique connue
Technique déjà documentée dans le référentiel MITRE vectorisé du projet.

### TechniqueModel
Voir `Modèle de technique`.

### Trajectory
Séquence ordonnée de `Commit` décrivant l'évolution d'une empreinte dans le temps.

### TrajectoryStore
Composant qui conserve les trajectoires actives et orchestre leur archivage.

### Trajectoire d'attaque
Séquence de phases ou d'actions caractérisant une attaque connue dans le référentiel.

### Trajectoire observée
Séquence d'actions réellement vues dans les logs et rattachées à une même empreinte.

### Traçabilité
Capacité à relier un score, un seuil ou un vecteur à une source, une règle et une version explicites.

## V
### Vector5D
Vecteur métier du projet : `[d1, d2, d3, d4, d5]`, avec chaque dimension dans `[0,1]`.

### Vectorisation
Transformation d'une action observée ou documentée en `Vector5D`.

### Vérité métrique canonique
Convention unique du projet pour exprimer la proximité : `raw_distance` -> `normalized_distance` -> `match_score`.