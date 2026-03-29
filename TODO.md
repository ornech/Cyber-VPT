# TODO — CYBER-VPT

**État observable :** le périmètre est fixé : détecter précocement une attaque par rapprochement de trajectoires vectorisées, et non attribuer une origine réseau.

## 0. Règle de travail
- Toute décision doit laisser une trace dans un fichier versionné.
- Toute formule doit être reliée à un terme du lexique.
- Toute hypothèse MITRE doit être justifiée, datée et révisable.
- Tout seuil doit être présenté comme provisoire tant qu'il n'a pas été calibré sur des données observées.
- Une sous-section `###` doit correspondre à une unité de travail transformable en issue.

## 1. Contrats de domaine à figer

### 1.1 — Vector5D
- [ ] Créer le contrat `Vector5D ∈ [0,1]^5`.
- [ ] Définir les règles de rejet : `NaN`, `±inf`, dimension absente, valeur hors intervalle.
- [ ] Écrire les tests de contrat associés.
- [ ] Documenter des exemples valides et invalides.

### 1.2 — MatchResult
- [ ] Figer la métrique canonique : `raw_distance`, `normalized_distance`, `match_score`.
- [ ] Interdire toute alerte basée directement sur `raw_distance`.
- [ ] Écrire le contrat : `normalized_distance ∈ [0,1]` et `match_score = 1 - normalized_distance`.
- [ ] Écrire les tests de cohérence associés.

### 1.3 — ArchivedProfile
- [ ] Figer la structure : `(μ, σ, n_points, first_seen, last_seen)`.
- [ ] Définir les contraintes : `σ` symétrique positive semi-définie, `n_points >= 2`, bornes temporelles cohérentes.
- [ ] Écrire les tests de contrat associés.
- [ ] Ne pas employer le terme `PCA` tant qu'aucun axe principal ni aucune variance expliquée ne sont stockés.

## 2. Référentiel de vectorisation 5D

### 2.1 — d1 criticité
- [ ] Créer la table initiale de pondération des ressources et des cibles.
- [ ] Versionner cette table.
- [ ] Associer chaque poids à une justification technique.

### 2.2 — d2 entropie
- [x] Figer la formule retenue.
- [x] Définir précisément ce qui entre dans `payload` selon le type d'événement ou de source.
- [x] Documenter les limites : chiffrement légitime, compression, données binaires.

### 2.3 — d3 dynamique temporelle
- [ ] Choisir la fenêtre de calcul ou la méthode basée sur `Δt`.
- [ ] Figer la fonction de normalisation.
- [ ] Décrire les effets attendus sur rafale, exécution scriptée et comportement low-and-slow.

### 2.4 — d4 intensité
- [ ] Définir `ActionSemantics` : `protocol`, `verb`, `permission`, `direction`.
- [ ] Construire un barème initial par protocole.
- [ ] Identifier les cas ambigus : lecture massive, écriture bénigne, suppression légitime.

### 2.5 — d5 rareté
- [ ] Définir le contenu exact d'une `Fingerprint`.
- [ ] Choisir le calcul de fréquence estimée.
- [ ] Figer la projection de cette fréquence dans `[0,1]`.
- [ ] Décrire les limites : nouvel équipement légitime, changement de navigateur, mise à jour système.

## 3. Référentiel MITRE vectorisé

### 3.1 — Format du TechniqueModel
- [ ] Définir le format d'un `TechniqueModel` versionné.
- [ ] Définir les champs minimaux : identifiant, version ATT&CK, phases, hypothèses, niveau de confiance, sources.

### 3.2 — Découpage en phases
- [ ] Décomposer une technique MITRE en phases vectorisables.
- [ ] Définir un critère explicite de séparation entre deux phases.

### 3.3 — Mapping MITRE vers Vector5D
- [ ] Définir une méthode de mapping `MITRE -> Vector5D` traçable.
- [ ] Associer à chaque phase : source, version ATT&CK, hypothèses, niveau de confiance.
- [ ] Interdire tout vecteur MITRE non justifié par une source documentaire.

### 3.4 — Techniques pilotes
- [ ] Créer les premières techniques pilotes pour validation méthodologique.
- [ ] Documenter pour chacune ce qui est théorique, ce qui est supposé et ce qui est observé.

## 4. Chaîne de traitement cible

### 4.1 — RawEvent
- [ ] Définir le schéma minimal de `RawEvent`.
- [ ] Identifier les champs obligatoires et facultatifs.

### 4.2 — Fingerprint et identité volatile
- [ ] Définir la construction de `Fingerprint`.
- [ ] Définir la résolution `id_emp <-> source courante`.
- [ ] Décrire les limites de cette résolution dans un contexte de brouillard réseau.

### 4.3 — Commit et Trajectory
- [ ] Définir la structure `Commit`.
- [ ] Définir les règles d'ouverture, de mise à jour et de fermeture d'une `Trajectory`.

### 4.4 — Composants de traitement
- [ ] Décrire les entrées et sorties de `Matcher`, `AlertEngine` et `ArchiveManager`.
- [ ] Décrire les invariants échangés entre ces composants.

## 5. Matching baseline sans IA

### 5.1 — Baseline déterministe
- [ ] Implémenter un baseline déterministe avant tout apprentissage.
- [ ] Choisir la métrique locale entre deux `Vector5D`.

### 5.2 — Alignement de trajectoires
- [ ] Implémenter DTW ou une alternative explicitement justifiée.
- [ ] Documenter les raisons du choix.

### 5.3 — Production du MatchResult
- [ ] Produire un `MatchResult` complet : distance normalisée, score, phase rapprochée, probabilité de complétion.
- [ ] Vérifier le comportement sur des séquences courtes, longues, incomplètes et bruitées.

## 6. Corpus d'évaluation

### 6.1 — Données bénignes
- [ ] Constituer un corpus minimal de comportements légitimes.
- [ ] Identifier les faux amis probables : scans internes, scripts d'administration, sauvegardes, mises à jour.

### 6.2 — Données malveillantes ou rejouées
- [ ] Sélectionner quelques scénarios d'attaque documentés.
- [ ] Rejouer ou simuler des séquences partielles et complètes.
- [ ] Marquer les phases réellement observables dans les logs.

### 6.3 — Jeu de vérité
- [ ] Définir ce qui constitue un préfixe d'attaque.
- [ ] Définir ce qui constitue une proximité bénigne.
- [ ] Séparer apprentissage, calibration et évaluation.

## 7. Calibration

### 7.1 — Indicateurs
- [ ] Définir les indicateurs : précision, rappel, délai d'alerte, taux de faux positifs.

### 7.2 — Mesure sur préfixes
- [ ] Mesurer la qualité du système sur des préfixes d'attaque, et non seulement sur des attaques complètes.

### 7.3 — Réglage des seuils
- [ ] Calibrer les seuils `WATCH` et `CRITICAL` sur des données observées.
- [ ] Documenter les cas d'échec.

## 8. Archivage et cycle de vie

### 8.1 — Sortie de la mémoire active
- [ ] Définir quand une trajectoire quitte la mémoire active.

### 8.2 — Construction du profil archivé
- [ ] Définir la construction de `ArchivedProfile`.

### 8.3 — Réactivation
- [ ] Définir la règle de réactivation via Mahalanobis.

### 8.4 — Coût système
- [ ] Mesurer l'impact mémoire et latence.

## 9. Traçabilité et révision

### 9.1 — Journal des décisions
- [ ] Créer un `DECISIONS.md` pour les choix structurants.

### 9.2 — Sources et hypothèses
- [ ] Créer un dossier `references/` pour les sources MITRE et les hypothèses de mapping.

### 9.3 — Historique des changements
- [ ] Créer un `CHANGELOG.md` pour les modifications de règles et de seuils.

### 9.4 — Identifiants d'hypothèses
- [ ] Attribuer un identifiant à chaque hypothèse importante.

## 10. Apprentissage du modèle

### 10.1 — Précondition
- [ ] Ne démarrer l'apprentissage qu'après validation du baseline.

### 10.2 — Rôle exact du modèle
- [ ] Définir le rôle exact du modèle : calibration, pondération, estimation de zones probables.

### 10.3 — Garde-fous
- [ ] Interdire au modèle de produire une vérité non justifiée par des données observées.

### 10.4 — Gain réel
- [ ] Évaluer si le modèle améliore réellement le délai de détection, et non seulement un score apparent.

## 11. Livrables minimums du prochain jalon

### 11.1 — Documents
- [ ] `TODO.md`
- [ ] `lexique.md`
- [ ] `contracts.md` ou dossier `contracts/`

### 11.2 — Référentiel initial
- [ ] `TechniqueModel` de référence pour 2 à 3 techniques pilotes

### 11.3 — Exécutable minimal
- [ ] baseline de matching exécutable
- [ ] premiers tests de contrat et d'intégration

## 12. Critères de passage au jalon suivant

### 12.1 — Invariants
- [ ] Les invariants sont écrits et testés.

### 12.2 — Référentiel MITRE
- [ ] Le référentiel MITRE initial est traçable.

### 12.3 — Baseline
- [ ] Le baseline fonctionne sur un petit corpus.

### 12.4 — Faux positifs initiaux
- [ ] Les faux positifs les plus évidents sont déjà visibles.

### 12.5 — Condition d'arrêt
- [ ] Tant qu'un des points précédents n'est pas satisfait, l'apprentissage est bloqué.

## 13. Rappel méthodologique
- Si le baseline reste ambigu, l'apprentissage ne corrigera pas l'ambiguïté ; il l'automatisera.