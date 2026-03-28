# Cahier des charges fonctionnel et technique
## Projet : CYBER-VPT — Cyber Vector Predictive Trajectory

**Constat observable :** un log isolé dit peu de chose. Une suite d'actions faibles, rapprochées d'une trajectoire MITRE documentée, peut en revanche annoncer une attaque avant son effet final.

## 1. Objet du projet
Le projet vise à **détecter précocement une attaque** en repérant, dès l'apparition de signaux faibles, qu'une suite d'actions observées commence à ressembler à une séquence d'actions déjà documentée dans **MITRE ATT&CK**.

Le moteur doit donc faire deux travaux symétriques :
1. **vectoriser les actions observées** dans les flux réseau, système ou applicatifs ;
2. **vectoriser les actions documentées dans MITRE** avec le même vocabulaire mathématique ;
3. comparer les deux dans un même espace afin d'estimer un **degré de rapprochement**.

L'hypothèse de travail est simple : si les actions observées et les actions MITRE ne vivent pas dans le même espace métrique, la comparaison est décorative.

## 2. Espace vectoriel commun
Chaque action est représentée par un vecteur :

$$V_a = [d_1, d_2, d_3, d_4, d_5]$$

avec l'invariant suivant :

$$V_a \in [0,1]^5$$

Aucune composante ne doit sortir de l'intervalle `[0,1]`. Une valeur hors intervalle rend la comparaison invalide.

### 2.1. Dimensions retenues
| Dimension | Nom | Rôle |
| :-- | :-- | :-- |
| `d1` | Criticité de la ressource | Mesure l'importance opérationnelle de la cible touchée |
| `d2` | Entropie du payload | Mesure le niveau d'obfuscation ou de complexité du contenu |
| `d3` | Dynamique temporelle | Mesure le rythme d'enchaînement des actions |
| `d4` | Intensité de l'action | Mesure la portée opérationnelle de l'action réalisée |
| `d5` | Rareté de l'empreinte | Mesure l'écart du porteur de l'action par rapport au parc habituel |

## 3. Chaîne de traitement cible
Le traitement attendu est le suivant :

`RawEvent -> FingerprintResolver -> Vectorizer -> TrajectoryStore -> Matcher -> AlertEngine -> ArchiveManager`

### 3.1. Identité de l'empreinte
Chaque événement est rattaché à une empreinte `id_emp`, dérivée d'éléments tels que :
- JA3 ou signature TLS ;
- fingerprint OS ;
- caractéristiques de headers ou de contexte protocolaire.

Une table volatile assure la correspondance temps réel :

$$id_{emp} \leftrightarrow source_{courante}$$

Cette liaison est opérationnelle, pas identitaire au sens juridique. La confusion entre les deux ferait monter les faux positifs autant que les prétentions.

### 3.2. Trajectoire active
Une trajectoire active est une séquence ordonnée de commits :

`{ previous_hash, vector, timestamp, cumulative_score }`

Chaque commit ajoute une action vectorisée à l'historique d'une même empreinte.

## 4. Référentiel MITRE vectorisé
Une technique MITRE n'est pas stockée comme un simple identifiant `Txxxx`, mais comme un **modèle de technique** constitué d'une ou plusieurs séquences de vecteurs idéaux.

Exemple de forme attendue :
- phase 1 : reconnaissance ;
- phase 2 : exploitation ;
- phase 3 : action sur objectif.

Chaque séquence MITRE doit être produite avec **les mêmes règles de vectorisation** que les événements observés. Si `d3` ou `d4` ne signifient pas la même chose côté input et côté MITRE, le score de rapprochement devient arbitraire.

## 5. Matching et décision d'alerte
Le moteur de matching calcule une distance de trajectoire, par exemple via **DTW** pour tolérer des vitesses d'exécution différentes.

Le système distingue impérativement :
- `raw_distance` : distance brute calculée par l'algorithme ;
- `normalized_distance ∈ [0,1]` : distance exploitable par la politique d'alerte ;
- `match_score = 1 - normalized_distance`.

### 5.1. Invariant de matching
L'invariant suivant est obligatoire :

$$0 \le normalized\_distance \le 1$$

et :

$$match\_score = 1 - normalized\_distance$$

L'alerte ne doit jamais être déclenchée directement sur la distance brute.

### 5.2. Politique d'alerte
La décision d'alerte appartient à un composant distinct du matcher.

Exemple de politique :
- `match_score < 0.50` : aucune alerte ;
- `0.50 <= match_score < 0.80` : surveillance renforcée ;
- `match_score >= 0.80` : alerte critique.

Ces seuils sont des hypothèses initiales. Sans campagne de calibration sur jeux de données sains et malveillants, ils n'ont aucune valeur démontrée.

## 6. Archivage et cycle de vie
Les trajectoires actives sont conservées en mémoire vive tant qu'elles restent utiles au calcul temps réel.

Une trajectoire inactive n'est pas résumée par une « PCA » tant qu'aucun axe principal ni variance expliquée ne sont stockés. Le projet retient ici un **résumé statistique gaussien** :

`ArchivedProfile = (μ, σ, n_points, first_seen, last_seen)`

avec :
- `μ` : vecteur moyen 5D ;
- `σ` : matrice de covariance `5x5` ;
- `n_points` : nombre d'observations agrégées ;
- `first_seen`, `last_seen` : bornes temporelles.

### 6.1. Invariants d'archive
Un profil archivé valide doit respecter :
- `μ ∈ [0,1]^5` ;
- `σ` symétrique positive semi-définie ;
- `n_points >= 2` ;
- `first_seen <= last_seen`.

La réactivation d'une empreinte archivée peut alors s'appuyer sur une distance de Mahalanobis pour distinguer la continuité d'une rupture comportementale.

## 7. Contraintes techniques
- **Temps de vectorisation cible** : `< 2 ms / événement` ;
- **Latence de corrélation cible** : `< 500 ms` entre réception et score ;
- **lookup des empreintes** : filtre de Bloom pour éviter des accès inutiles ;
- **rareté dynamique** : Count-Min Sketch pour estimer les fréquences sans stocker toutes les signatures.

## 8. Contrats à figer dès le début
Le projet repose sur trois contrats non négociables :
1. `Vector5D ∈ [0,1]^5` ;
2. `MatchResult.normalized_distance ∈ [0,1]` ;
3. `ArchivedProfile = (μ, σ, n_points, first_seen, last_seen)`.

Tant que ces contrats ne sont ni écrits, ni testés, ni imposés à la construction des objets, le projet reste un prototype conceptuel.
