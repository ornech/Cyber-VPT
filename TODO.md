# TODO — CYBER-VPT

**État observable :** le périmètre est désormais clair : détecter précocement une attaque par rapprochement de trajectoires vectorisées, et non attribuer une origine réseau.

## 0. Règle de travail
- Toute décision doit laisser une trace dans un fichier versionné.
- Toute formule doit être reliée à un terme du lexique.
- Toute hypothèse MITRE doit être justifiée, datée et révisable.
- Tout seuil doit être présenté comme provisoire tant qu'il n'a pas été calibré sur données observées.

## 1. Contrats de domaine à figer
### 1.1. Vector5D
- [ ] Créer le contrat `Vector5D ∈ [0,1]^5`.
- [ ] Définir les règles de rejet : `NaN`, `±inf`, dimension absente, valeur hors intervalle.
- [ ] Écrire les tests de contrat associés.
- [ ] Documenter les exemples valides et invalides.

### 1.2. MatchResult
- [ ] Figer la métrique canonique : `raw_distance`, `normalized_distance`, `match_score`.
- [ ] Interdire toute alerte basée directement sur `raw_distance`.
- [ ] Écrire le contrat : `normalized_distance ∈ [0,1]` et `match_score = 1 - normalized_distance`.
- [ ] Écrire les tests de cohérence associés.

### 1.3. ArchivedProfile
- [ ] Figer la structure : `(μ, σ, n_points, first_seen, last_seen)`.
- [ ] Définir les contraintes : `σ` symétrique positive semi-définie, `n_points >= 2`, bornes temporelles cohérentes.
- [ ] Écrire les tests de contrat associés.
- [ ] Interdire le terme « PCA » tant qu'aucun axe principal ni variance expliquée ne sont stockés.

## 2. Référentiel de vectorisation 5D
### 2.1. d1 — criticité
- [ ] Créer la table de pondération initiale des ressources/cibles.
- [ ] Versionner cette table.
- [ ] Associer chaque poids à une justification technique.

### 2.2. d2 — entropie
- [ ] Figer la formule retenue.
- [ ] Définir précisément ce qui entre dans `payload` selon le protocole.
- [ ] Documenter les limites : chiffrement légitime, compression, données binaires.

### 2.3. d3 — dynamique temporelle
- [ ] Choisir la fenêtre de calcul ou la méthode basée sur `Δt`.
- [ ] Figer la fonction de normalisation.
- [ ] Décrire les effets attendus sur rafale, exécution scriptée, low and slow.

### 2.4. d4 — intensité
- [ ] Définir `ActionSemantics` : `protocol`, `verb`, `permission`, `direction`.
- [ ] Construire un barème initial par protocole.
- [ ] Identifier les cas ambigus : lecture massive, écriture bénigne, suppression légitime.

### 2.5. d5 — rareté
- [ ] Définir le contenu exact d'une `Fingerprint`.
- [ ] Choisir le calcul de fréquence estimée.
- [ ] Figer la projection de cette fréquence dans `[0,1]`.
- [ ] Décrire les limites : nouvel équipement légitime, changement de navigateur, mise à jour système.

## 3. Référentiel MITRE vectorisé
- [ ] Définir le format d'un `TechniqueModel` versionné.
- [ ] Découper une technique en phases vectorisables.
- [ ] Définir une méthode de mapping MITRE -> `Vector5D` traçable.
- [ ] Associer à chaque phase : source, version ATT&CK, hypothèses, niveau de confiance.
- [ ] Interdire un « vecteur MITRE » sans justification documentaire.
- [ ] Créer les premières techniques pilotes pour validation méthodologique.

## 4. Chaîne de traitement cible
- [ ] Définir le schéma `RawEvent` minimal.
- [ ] Définir la construction de `Fingerprint`.
- [ ] Définir la résolution `id_emp <-> source courante`.
- [ ] Définir la structure `Commit`.
- [ ] Définir les règles d'ouverture, de mise à jour et de fermeture d'une `Trajectory`.
- [ ] Décrire les entrées et sorties de `Matcher`, `AlertEngine`, `ArchiveManager`.

## 5. Matching baseline sans IA
- [ ] Implémenter un baseline déterministe avant tout apprentissage.
- [ ] Choisir la métrique locale entre deux `Vector5D`.
- [ ] Implémenter DTW ou une alternative justifiée.
- [ ] Produire `MatchResult` complet : distance normalisée, score, phase rapprochée, complétion.
- [ ] Vérifier le comportement sur séquences courtes, longues, incomplètes, bruitées.

## 6. Corpus d'évaluation
### 6.1. Données bénignes
- [ ] Constituer un corpus minimal de comportements légitimes.
- [ ] Identifier les faux amis probables : scans internes, scripts d'administration, sauvegardes, mises à jour.

### 6.2. Données malveillantes ou rejouées
- [ ] Sélectionner quelques scénarios d'attaque documentés.
- [ ] Rejouer ou simuler des séquences partielles et complètes.
- [ ] Marquer les phases réellement observables dans les logs.

### 6.3. Jeu de vérité
- [ ] Définir ce qui constitue un préfixe d'attaque.
- [ ] Définir ce qui constitue une simple proximité bénigne.
- [ ] Séparer apprentissage, calibration et évaluation.

## 7. Calibration
- [ ] Définir les indicateurs : précision, rappel, délai d'alerte, taux de faux positifs.
- [ ] Mesurer la qualité du système sur préfixes d'attaque, pas seulement sur attaques complètes.
- [ ] Calibrer les seuils `WATCH` et `CRITICAL` sur données observées.
- [ ] Documenter les cas d'échec.

## 8. Archivage et cycle de vie
- [ ] Définir quand une trajectoire quitte la mémoire active.
- [ ] Définir la construction de `ArchivedProfile`.
- [ ] Définir la règle de réactivation via Mahalanobis.
- [ ] Mesurer l'impact mémoire et latence.

## 9. Traçabilité et révision
- [ ] Créer un `DECISIONS.md` pour les choix structurants.
- [ ] Créer un dossier `references/` pour les sources MITRE et hypothèses de mapping.
- [ ] Créer un `CHANGELOG.md` pour les modifications de règles et de seuils.
- [ ] Attribuer un identifiant à chaque hypothèse importante.

## 10. Apprentissage du modèle
- [ ] Ne démarrer l'apprentissage qu'après validation du baseline.
- [ ] Définir le rôle exact du modèle : calibration, pondération, estimation de zones probables.
- [ ] Interdire au modèle de produire une vérité non justifiée par des données observées.
- [ ] Évaluer si le modèle améliore réellement le délai de détection et non seulement le score apparent.

## 11. Livrables minimums du prochain jalon
- [ ] `TODO.md`
- [ ] `lexique.md`
- [ ] `contracts.md` ou dossier `contracts/`
- [ ] `TechniqueModel` de référence pour 2 à 3 techniques pilotes
- [ ] baseline de matching exécutable
- [ ] premiers tests de contrat et d'intégration

## 12. Critères de passage au jalon suivant
Le projet peut avancer vers l'entraînement seulement si :
- les invariants sont écrits et testés ;
- le référentiel MITRE initial est traçable ;
- le baseline fonctionne sur un petit corpus ;
- les faux positifs les plus évidents sont déjà visibles.

Sinon, l'apprentissage ne corrigera pas l'ambiguïté ; il l'automatisera.