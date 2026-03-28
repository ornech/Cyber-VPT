"""
ArchivedProfile — contrat de domaine C-003 du projet CYBER-VPT.

Invariants fondamentaux
-----------------------
- mu est un Vector5D valide.
- sigma est une matrice 5x5 finie.
- sigma est symetrique.
- sigma est positive semi-definie (les valeurs propres nulles sont autorisees).
- n_points est un entier >= 2.
- first_seen et last_seen sont des datetime coherents (first_seen <= last_seen).
"""

from __future__ import annotations

from datetime import datetime

import numpy as np

from .vector5d import Vector5D

_SYMMETRY_TOLERANCE = 1e-12
_PSD_TOLERANCE = 1e-12


class ArchivedProfile:
    """Profil archive statistique conforme au contrat C-003."""

    __slots__ = ("mu", "sigma", "n_points", "first_seen", "last_seen")

    def __init__(
        self,
        mu: Vector5D,
        sigma: np.ndarray,
        n_points: int,
        first_seen: datetime,
        last_seen: datetime,
    ) -> None:
        _validate_mu(mu)
        sigma_array = _validate_sigma(sigma)
        _validate_n_points(n_points)
        _validate_datetimes(first_seen, last_seen)

        object.__setattr__(self, "mu", mu)
        object.__setattr__(self, "sigma", sigma_array)
        object.__setattr__(self, "n_points", int(n_points))
        object.__setattr__(self, "first_seen", first_seen)
        object.__setattr__(self, "last_seen", last_seen)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(
            "ArchivedProfile est immuable : les champs ne peuvent pas etre modifies "
            "apres construction."
        )

    def __repr__(self) -> str:
        return (
            "ArchivedProfile("
            f"mu={self.mu!r}, "
            f"sigma={self.sigma!r}, "
            f"n_points={self.n_points!r}, "
            f"first_seen={self.first_seen!r}, "
            f"last_seen={self.last_seen!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArchivedProfile):
            return NotImplemented
        return (
            self.mu == other.mu
            and np.array_equal(self.sigma, other.sigma)
            and self.n_points == other.n_points
            and self.first_seen == other.first_seen
            and self.last_seen == other.last_seen
        )


def _validate_mu(value: object) -> None:
    if not isinstance(value, Vector5D):
        raise TypeError(
            f"mu doit etre une instance de Vector5D, recu : {type(value).__name__!r}."
        )


def _validate_sigma(value: object) -> np.ndarray:
    sigma = np.asarray(value, dtype=float)

    if sigma.shape != (5, 5):
        raise ValueError(
            f"sigma doit etre une matrice 5x5, recu shape={sigma.shape!r}."
        )

    if not np.isfinite(sigma).all():
        raise ValueError("sigma doit etre finie (sans NaN, +inf, -inf).")

    if not np.allclose(sigma, sigma.T, atol=_SYMMETRY_TOLERANCE, rtol=0.0):
        raise ValueError("sigma doit etre symetrique.")

    eigenvalues = np.linalg.eigvalsh(sigma)
    if np.min(eigenvalues) < -_PSD_TOLERANCE:
        raise ValueError(
            "sigma doit etre positive semi-definie (valeurs propres >= 0)."
        )

    return sigma


def _validate_n_points(value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(
            f"n_points doit etre un entier, recu : {type(value).__name__!r}."
        )

    if value < 2:
        raise ValueError(f"n_points vaut {value!r} : n_points doit etre >= 2.")


def _validate_datetimes(first_seen: object, last_seen: object) -> None:
    if not isinstance(first_seen, datetime):
        raise TypeError(
            "first_seen doit etre un datetime, "
            f"recu : {type(first_seen).__name__!r}."
        )
    if not isinstance(last_seen, datetime):
        raise TypeError(
            "last_seen doit etre un datetime, "
            f"recu : {type(last_seen).__name__!r}."
        )
    if first_seen > last_seen:
        raise ValueError("Bornes temporelles invalides : first_seen > last_seen.")
