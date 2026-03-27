# Spécification d'Homogénéisation des Vecteurs (CYBER-PATH)

L'objectif est de garantir que $V_{input} \in [0, 1]^5$ et $V_{mitre} \in [0, 1]^5$.

## 1. Protocole de Normalisation des Inputs ($V_{input}$)
Chaque donnée brute doit passer par une fonction de transformation avant vectorisation :

* **d1 (Criticité) :** Utilisation d'une table de correspondance (Lookup Table).
    * *Règle :* $d1 = \frac{Poids(Ressource)}{Max(Poids)}$.
* **d2 (Entropie) :** Normalisation de Shannon.
    * *Règle :* $d2 = \frac{H(payload)}{H_{max}}$ (où $H_{max} = 8$ pour de l'octet pur).
* **d3 (Fréquence) :** Fonction Sigmoïde pour gérer les rafales.
    * *Règle :* $d3 = \frac{1}{1 + e^{-k(f - f_0)}}$.
* **d4 (Intensité) :** Mapping linéaire des permissions.
    * *Règle :* `READ=0.2`, `WRITE=0.6`, `EXEC/DELETE=1.0`.
* **d5 (Rareté) :** Score probabiliste via Count-Min Sketch.
    * *Règle :* $1 - P(UA_{connu})$.

## 2. Protocole de Scoring des MITRE ($V_{mitre}$)
Pour chaque technique MITRE (TID), un expert ou un modèle de NLP définit un "Vecteur Idéal" :
* Le vecteur représente l'**empreinte théorique** de la technique.
* Exemple T1190 : $[0.9, 0.8, 1.0, 0.7, 0.9]$.
