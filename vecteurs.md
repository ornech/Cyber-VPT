# Les vecteurs
## Spécification technique de la vectorisation 5D

**Point de départ observable :** deux événements peuvent avoir des signatures textuelles très différentes tout en participant à la même logique d'attaque. Le projet ne compare donc pas des chaînes, mais des actions ramenées dans un même espace vectoriel.

## 1. Invariant du vecteur
Chaque action observée ou documentée est représentée par :

$$V_a = [d_1, d_2, d_3, d_4, d_5]$$

avec l'invariant :

$$V_a \in [0,1]^5$$

Un vecteur est **invalide** si une composante est absente, non finie, négative ou supérieure à `1`.

## 2. Entrées nécessaires à la vectorisation
La vectorisation ne doit pas dépendre d'un timestamp brut uniquement. Elle a besoin au minimum de trois objets :
- `RawEvent` : événement brut ;
- `Fingerprint` : porteur de l'action ;
- `ActionSemantics` : sens opérationnel de l'action.

### 2.1. RawEvent
Exemples de champs utiles :
- `timestamp`
- `protocol`
- `resource`
- `payload`
- `source`

### 2.2. Fingerprint
Exemples de composantes :
- JA3 ;
- fingerprint OS ;
- entropie ou structure des headers ;
- marqueurs stables de session ou de client.

### 2.3. ActionSemantics
`d4` ne doit pas dépendre d'un simple nom de méthode. Il faut au moins :
- `protocol`
- `verb`
- `permission`
- `direction`

Sans cela, un `POST`, un `DELETE SQL`, un `scp` ou un `chmod` seraient forcés dans le même moule lexical, ce qui fabrique une belle abstraction et un mauvais score.

## 3. Définition des dimensions
| Dimension | Nom                  | Entrée principale                                         | Règle de normalisation                  | Finalité                                                                  |
| :-------- | :------------------- | :-------------------------------------------------------- | :-------------------------------------- | :------------------------------------------------------------------------ |
| `d1`      | Criticité            | ressource ou cible                                        | table de pondération puis normalisation | distinguer une cible sensible d'un bruit de fond                          |
| `d2`      | Entropie             | champs observés retenus par type d'événement ou de source | `H(payload_bytes) / 8`                  | repérer une densité informationnelle inhabituelle dans le contenu observé |
| `d3`      | Dynamique temporelle | `Δt`, fréquence locale                                    | sigmoïde bornée dans `[0,1]`            | capturer rafale, script ou accélération d'exécution                       |
| `d4`      | Intensité            | sémantique de l'action                                    | barème borné par protocole/permission   | distinguer lecture, écriture, exécution, destruction                      |
| `d5`      | Rareté               | empreinte                                                 | score estimé par fréquence d'apparition | renforcer un signal porté par un acteur atypique                          |

## 4. Règles détaillées par dimension
### 4.1. `d1` — criticité
`d1` mesure l'importance de la cible touchée.

Exemple de principe :

$$d1 = \frac{W(resource)}{W_{max}}$$

La table de pondération doit être versionnée. Une valeur de criticité non tracée rend le score discutable.

### 4.2. `d2` — entropie
`d2` mesure le désordre informationnel d'un ensemble fermé de champs observés,
déterminé mécaniquement par le type d'événement ou de source.

Formule canonique :

$$d2 = \frac{H(payload\_bytes)}{8}$$

où `H` est l'entropie de Shannon calculée sur des octets, et `payload_bytes`
désigne la concaténation ordonnée des seuls champs inclus par la règle
normative du type d'événement considéré.

Règle ferme de calcul :
- si le contenu utile n'est pas observable dans la source ou reste chiffré,
	`d2` est **non calculable** ;
- si un contenu applicatif est déjà observé en clair dans la source, `d2` est
	calculé sur ce contenu observé uniquement ;
- aucun décodage implicite, aucune décompression implicite et aucun
	déchiffrement implicite ne sont autorisés ;
- la spécification raisonne toujours sur la forme effectivement observée dans
	la source.

Tableau normatif de composition de `payload_bytes` :

| Type d'événement ou de source          | Champs inclus dans `payload_bytes`      | Champs exclus par défaut                                                                                                                       | Condition de non-calculabilité                        |
| :------------------------------------- | :-------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| Requête HTTP applicative journalisée   | `cible`, `query_string`, `body`         | `methode`, tous les en-têtes, cookies, version HTTP, adresse source, ports, timestamps, identifiants techniques, métadonnées de transport      | aucun des champs inclus n'est observé en clair        |
| Réponse HTTP applicative journalisée   | `body`                                  | status code, tous les en-têtes, cookies, version HTTP, adresse source, ports, timestamps, identifiants techniques, métadonnées de transport    | `body` n'est pas observé en clair                     |
| Événement DNS journalisé               | `query_name`                            | `record_type`, identifiant de transaction, flags, compteurs, adresses, ports, sérialisation binaire non exposée en clair                       | `query_name` n'est pas observé en clair               |
| Événement de commande système ou shell | `command`, `arguments`                  | PID, UID, horodatage, code retour, hôte, métadonnées de session                                                                                | ni `command` ni `arguments` ne sont observés en clair |
| Événement applicatif générique         | `message`, `body`, `content`, `payload` | level, logger, thread, timestamp, identifiants techniques, champs de contexte non textuels, tout champ non explicitement nommé dans ce tableau | aucun des champs inclus n'est observé en clair        |
| Événement de messagerie journalisé     | `subject`, `body`                       | enveloppe SMTP, routing headers, métadonnées de transport, pièces jointes non exposées en clair                                                | ni `subject` ni `body` ne sont observés en clair      |

Ordre de concaténation pour `payload_bytes` :
- Requête HTTP : `cible`, puis `query_string`, puis `body`.
- Réponse HTTP : `body`.
- DNS : `query_name`.
- Commande système ou shell : `command`, puis `arguments`.
- Événement applicatif générique : `message`, puis `body`, puis `content`, puis
	`payload`.
- Messagerie : `subject`, puis `body`.

Le choix DNS est volontairement fermé sur `query_name`. `record_type` reste
exclu car il constitue un champ structurel de qualification de requête et non un
contenu applicatif manipulé.

Une entropie élevée n'est pas un aveu d'attaque. Elle signale seulement une
forte densité informationnelle dans la forme observée : contenu binaire,
encodé, compressé, chiffré ou autrement atypique.

Limites documentées :
- un flux légitimement chiffré reste hors calcul si aucun contenu clair n'est
	présent dans la source ;
- une compression ou un encodage visibles dans la source sont évalués tels
	qu'observés, sans transformation préalable ;
- des données binaires observées en clair peuvent produire une entropie élevée
	sans indiquer à elles seules une action malveillante ;
- un contenu très court ou un log partiel réduit fortement la portée
	interprétative de `d2`.

### 4.3. `d3` — dynamique temporelle
`d3` ne doit pas être calculé à partir du seul timestamp absolu.

Le moteur doit dériver :
- `Δt` depuis le dernier commit de la même empreinte ;
- une fréquence locale ou une densité d'événements sur fenêtre glissante.

Exemple de mise à l'échelle :

$$d3 = \frac{1}{1 + e^{-k(f - f_0)}}$$

Cette forme borne `d3` dans `[0,1]` et évite qu'une rafale écrase toutes les autres dimensions.

### 4.4. `d4` — intensité
`d4` mesure la portée opérationnelle de l'action.

Exemple de barème générique :
- lecture : `0.2`
- écriture : `0.6`
- exécution / suppression / action destructive : `1.0`

Le barème doit être décliné par protocole. Une lecture SQL et un `GET /health` n'ont pas la même surface de risque, même si l'étiquette « READ » rassure un instant.

### 4.5. `d5` — rareté
`d5` mesure l'écart entre l'empreinte observée et le comportement habituel du parc.

Le calcul s'appuie sur une estimation de fréquence, par exemple via **Count-Min Sketch**, afin d'éviter un stockage exhaustif.

Exemple de comportement attendu :
- signature ubiquitaire : `d5 -> 0`
- signature rare ou nouvelle : `d5 -> 1`

`d5` agit comme amplificateur de signal faible. Une action modérément suspecte portée par une empreinte très rare doit compter davantage qu'un bruit de fond produit mille fois par jour.

## 5. Contrat de construction
Un `Vector5D` valide doit satisfaire les trois points suivants :
- les cinq dimensions existent ;
- chaque dimension est finie ;
- chaque dimension appartient à `[0,1]`.

La validation doit être faite **au constructeur**, puis vérifiée en test. Une validation seulement documentaire ne protège rien.

## 6. Usage côté trajectoire
Chaque vecteur est inséré dans un commit :

`{ previous_hash, vector, timestamp, cumulative_score }`

La trajectoire résultante reste une **séquence ordonnée**. Le système ne cherche pas un mot-clé final ; il cherche une dérive progressive vers une forme déjà connue.

## 7. Usage côté MITRE
Les actions MITRE doivent être vectorisées avec les mêmes règles que les actions observées.

Conséquence directe :
- même définition de `d1` à `d5` ;
- mêmes bornes ;
- mêmes tables de correspondance ;
- même sémantique de `d3` et `d4`.

Sinon `V_input` et `V_mitre` n'ont que l'apparence d'être comparables.
