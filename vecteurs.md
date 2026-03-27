# Les vecteurs
## 📑 Spécifications Techniques : Métriques et Vectorisation

L'objectif de cette section est de transformer l'activité brute en un espace vectoriel $\mathbb{R}^5$ où chaque action $V_a$ est un point géométrique.

### 1. Définition du Vecteur d'Action ($V_a$)
Chaque événement réseau ou applicatif est projeté dans un espace à 5 dimensions. Le vecteur est défini par $V_a = [d_1, d_2, d_3, d_4, d_5]$.

| Dimension | Nom | Indicateur (Calcul) | Plage $[0,1]$ |
| :--- | :--- | :--- | :--- |
| **$d_1$** | **Criticité Ressource** | Poids assigné à l'URL/Service ($W_{res}$). Ex: `/login` = 0.9, `/static/` = 0.1. | Normalisé par $Max(W)$ |
| **$d_2$** | **Entropie Payload** | Calcul de l'entropie de Shannon sur le corps de la requête (Détection d'obfuscation). | $H(x) / H_{max}$ |
| **$d_3$** | **Fréquence Temporelle** | $1 / \Delta t$ où $\Delta t$ est le délai depuis le dernier commit de l'empreinte. | Sigmoïde de la fréquence |
| **$d_4$** | **Intensité Méthode** | Score selon le verbe HTTP et les permissions (GET=0.2, POST=0.6, DELETE=1.0). | Barème fixe |
| **$d_5$** | **Score de Rareté** | Poids inverse de la récurrence des marqueurs de l'empreinte (JA3, UA). | $\log(\frac{N}{n+1})$ |



---

### 2. Indicateur de Rareté Dynamique ($d_5$)
C'est l'indicateur "sentinel". Il permet de pondérer l'importance d'un événement non pas sur ce qu'il fait, mais sur **qui** le fait par rapport à la norme du parc.

* **Calcul de l'Unicité :** Utilisation d'un **Count-Min Sketch** pour estimer la fréquence $n$ d'une signature sans stocker toutes les signatures en RAM.
* **Comportement :**
    * Si la signature est ubiquitaire (ex: Windows Update), $d_5 \to 0$.
    * Si la signature est unique ou nouvelle, $d_5 \to 1$.
* **Effet de levier :** En cas de signal faible (ex: une seule requête avec une entropie moyenne), un $d_5$ élevé va "étirer" le vecteur, facilitant le dépassement du seuil de similarité $\epsilon$ avec une trajectoire MITRE.

---

### 3. Structure de la Trajectoire ($T_{user}$)
La trajectoire n'est pas une simple liste, mais un **graphe linéaire de commits**.

* **Structure du Commit :** `{ Hash_Précédent, Vecteur_Va, Timestamp, Score_Cumulé }`.
* **Indicateur de Convergence :** Calculé à chaque nouveau commit par la distance DTW :
    $$\text{Score}_{match} = 1 - \frac{DTW(T_{user}, T_{atk})}{Distance_{max}}$$
* **Seuil d'Alerte ($\epsilon$) :** * **$\epsilon > 0.8$ :** Alerte Critique (Mimétisme avéré d'une technique MITRE).
    * **$0.5 < \epsilon < 0.8$ :** Surveillance accrue (Transfert prioritaire en New List).



---

### 4. Gestion du Cycle de Vie (Politique LRU-SACP)
Pour maintenir la performance (32 Go RAM), le système applique une réduction de données basée sur la pertinence mathématique.

#### A. New List (Active)
* **Stockage :** Vecteurs complets $\mathbb{R}^5$ en RAM.
* **Indicateur de sortie :** Temps d'inactivité > $T_{threshold}$ OU dépassement de capacité mémoire.

#### B. Old List (Archive Statistique)
Avant le passage en Old List, la trajectoire subit une **Compression par Centroïde** :
1.  Calcul du **Vecteur Moyen** ($\mu$) de la trajectoire.
2.  Calcul de la **Matrice de Covariance** (résumé de la dispersion des actions).
3.  Stockage du résumé : la trajectoire n'est plus une suite de points, mais un "nuage" statistique défini par $(\mu, \sigma)$.

> **Note technique :** Si une empreinte en Old List redevient active, le système compare le nouveau vecteur $V_{new}$ à la distance de Mahalanobis du centroïde pour décider s'il s'agit d'une suite logique ou d'une rupture de comportement.

---

### 5. Indicateurs de Performance Système (KPI)
| Indicateur | Cible | Méthode de mesure |
| :--- | :--- | :--- |
| **Temps de Vectorisation** | < 2ms / log | Mesure CPU cycle par thread |
| **Précision du Filtre de Bloom** | Faux Positifs < 1% | Dimensionnement de la fonction de hachage |
| **Délai de Corrélation** | Temps Réel (< 500ms) | Latence entre réception INPUT et calcul DTW |
