# Spécification d'homogénéisation des vecteurs

**Constat observable :** si les événements observés et les actions MITRE ne sont pas projetés avec les mêmes règles, le matching produit un score numérique, mais pas une preuve de proximité.

L'objectif de ce document est donc de garantir :

$$V_{input} \in [0,1]^5 \quad et \quad V_{mitre} \in [0,1]^5$$

avec **la même sémantique** pour chaque dimension.

## 1. Règle générale
Pour toute dimension `d_i` :
- même définition métier côté input et côté MITRE ;
- même intervalle `[0,1]` ;
- même méthode de normalisation ;
- même jeu de tables ou de barèmes de référence.

Si cette symétrie n'est pas tenue, la comparaison devient rhétorique.

## 2. Protocole de normalisation des actions observées
### 2.1. `d1` — criticité
Entrée : ressource, service, cible ou objet touché.

Règle :

$$d1 = \frac{W(resource)}{W_{max}}$$

La table `W` doit être versionnée et justifiable.

### 2.2. `d2` — entropie
Entrée : concaténation ordonnée de champs explicitement retenus par type
d'événement ou de source.

Règle :

$$d2 = \frac{H(payload\_bytes)}{8}$$

où `payload_bytes` est calculé uniquement à partir des champs observés en clair
et explicitement nommés ci-dessous.

Règle ferme :
- si le contenu utile n'est pas observable dans la source ou reste chiffré,
	`d2` est **non calculable** ;
- si un contenu applicatif est déjà observé en clair dans la source, `d2` est
	calculé sur ce contenu observé uniquement ;
- aucun décodage implicite, aucune décompression implicite et aucun
	déchiffrement implicite ne sont autorisés.

Tableau normatif :

| Type d'événement ou de source          | Champs inclus                           | Champs exclus                                                                                                                                  | Condition de non-calculabilité                        |
| :------------------------------------- | :-------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| Requête HTTP applicative journalisée   | `cible`, `query_string`, `body`         | `methode`, tous les en-têtes, cookies, version HTTP, adresses, ports, timestamps, identifiants techniques, métadonnées de transport            | aucun champ inclus n'est observé en clair             |
| Réponse HTTP applicative journalisée   | `body`                                  | status code, tous les en-têtes, cookies, version HTTP, adresses, ports, timestamps, identifiants techniques, métadonnées de transport          | `body` n'est pas observé en clair                     |
| Événement DNS journalisé               | `query_name`                            | `record_type`, identifiant de transaction, flags, compteurs, adresses, ports, sérialisation binaire non exposée en clair                       | `query_name` n'est pas observé en clair               |
| Événement de commande système ou shell | `command`, `arguments`                  | PID, UID, horodatage, code retour, hôte, métadonnées de session                                                                                | ni `command` ni `arguments` ne sont observés en clair |
| Événement applicatif générique         | `message`, `body`, `content`, `payload` | level, logger, thread, timestamp, identifiants techniques, champs de contexte non textuels, tout champ non explicitement nommé dans ce tableau | aucun champ inclus n'est observé en clair             |
| Événement de messagerie journalisé     | `subject`, `body`                       | enveloppe SMTP, routing headers, métadonnées de transport, pièces jointes non exposées en clair                                                | ni `subject` ni `body` ne sont observés en clair      |

Ordre de concaténation :
- Requête HTTP : `cible`, puis `query_string`, puis `body`.
- Réponse HTTP : `body`.
- DNS : `query_name`.
- Commande système ou shell : `command`, puis `arguments`.
- Événement applicatif générique : `message`, puis `body`, puis `content`, puis
	`payload`.
- Messagerie : `subject`, puis `body`.

Le champ DNS `record_type` est explicitement exclu. Il reste un attribut
structurel de qualification de requête et n'entre pas dans le contenu retenu
pour `d2`.

### 2.3. `d3` — dynamique temporelle
Entrée : fréquence locale dérivée d'un `Δt` ou d'une fenêtre glissante.

Règle type :

$$d3 = \frac{1}{1 + e^{-k(f - f_0)}}$$

La fréquence doit être calculée à partir de l'historique de la même empreinte. Un timestamp brut ne suffit pas.

### 2.4. `d4` — intensité
Entrée : sémantique de l'action (`protocol`, `verb`, `permission`, `direction`).

Exemple de barème générique :
- lecture : `0.2`
- écriture : `0.6`
- exécution, suppression, action destructrice : `1.0`

### 2.5. `d5` — rareté
Entrée : empreinte ou signature de porteur.

Règle : score borné croissant avec la rareté observée.

Exemple de mise en œuvre : estimation de fréquence par **Count-Min Sketch**, puis projection dans `[0,1]`.

## 3. Protocole de vectorisation du référentiel MITRE
Le référentiel MITRE ne doit pas être réduit à un seul vecteur idéal par technique tant qu'une technique comporte plusieurs phases.

Chaque technique est modélisée comme une **séquence de phases vectorisées**.

Exemple de structure logique :
- `phase_1` : préparation / reconnaissance ;
- `phase_2` : accès / exploitation ;
- `phase_3` : action sur objectif.

Chaque phase produit son propre `Vector5D` avec les mêmes règles que les inputs observés.

## 4. Règle de symétrie input / MITRE
Pour toute comparaison, il doit être possible d'affirmer :
- `d1_input` et `d1_mitre` parlent de la même notion ;
- `d2_input` et `d2_mitre` parlent de la même notion ;
- `d3_input` et `d3_mitre` utilisent la même échelle temporelle ;
- `d4_input` et `d4_mitre` utilisent le même barème d'intensité ;
- `d5_input` et `d5_mitre` expriment la même idée de rareté ou d'anomalie de porteur.

Sans cette règle, le moteur compare des nombres, pas des comportements.

## 5. Contrôles obligatoires
### 5.1. Contrôle de validité du vecteur
Tout vecteur construit doit vérifier :
- 5 composantes présentes ;
- aucune composante `NaN` ou infinie ;
- chaque composante dans `[0,1]`.

### 5.2. Contrôle de cohérence du référentiel
Toute séquence MITRE vectorisée doit être accompagnée :
- de sa source ;
- de sa version ;
- de l'hypothèse de mapping retenue ;
- de la justification des poids utilisés.

Un modèle MITRE sans traçabilité n'est pas un référentiel ; c'est une intuition.

## 6. Invariant final
L'homogénéisation est jugée correcte uniquement si :
1. les événements observés et les modèles MITRE produisent des `Vector5D` valides ;
2. les deux côtés utilisent les mêmes conventions ;
3. le moteur de matching peut travailler sans conversion ad hoc spécifique à une source.
