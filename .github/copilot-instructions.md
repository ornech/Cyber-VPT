Copilot instructions for this repository
Project overview

This repository implements a system for predictive detection of cyber attacks by mapping sequences of events into a five‑dimensional vector space and comparing the resulting trajectories against MITRE ATT&CK reference models. The aim is to identify when an observed trajectory begins to converge toward a known attack pattern so that an alert can be raised before the final malicious step occurs.

Languages and frameworks

The project is written in Python 3.10. It uses commonly available libraries such as numpy, scipy and scikit‑learn for vector computations and dynamic time warping, as well as pandas for data manipulation. Unit tests are implemented with pytest. The development environment targets Ubuntu Linux.

How to build and validate changes

Always install dependencies before building, testing or running the project:

pip install -r requirements.txt

To run the unit tests:

pytest -q

If pytest is not installed, you can install it by running pip install pytest. Use this command to check code style:

pip install flake8
flake8 src/
Repository structure
README.md : description générale du projet.
src/ : code source, organisé par modules (vectorisation 5D, stockage des trajectoires, moteur de rapprochement, moteur d’alerte).
tests/ : tests unitaires.
.github/workflows/ : workflows GitHub Actions, dont copilot‑setup‑steps.yml.
.github/instructions/ : instructions ciblées (facultatif).
Coding guidelines
Respectez le style PEP 8 pour le code Python (utilisez flake8 ou black pour vérifier).
Écrivez des messages de commit clairs et concis en anglais.
Ajoutez des tests unitaires pour toute fonctionnalité nouvelle ou modifiée.
Lorsque vous utilisez des données MITRE ATT&CK, veillez à documenter la version et la source pour assurer la traçabilité.
Context for the agent

Vector 5D values must lie in the unit cube [0, 1]^5, normalized distances returned by the matching engine belong to [0, 1], and archived profiles consist of a mean vector μ, a covariance matrix σ, the number of points n, and timestamps for the first and last observations. The agent should preserve these invariants when creating or modifying code.

**_ End of instructions _**
