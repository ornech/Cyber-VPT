"""Tests de contrat pour ArchivedProfile (C-003)."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pytest

from src.cyber_vpt.archived_profile import ArchivedProfile
from src.cyber_vpt.vector5d import Vector5D


def _valid_mu() -> Vector5D:
    return Vector5D(0.2, 0.3, 0.4, 0.5, 0.6)


def _valid_sigma() -> np.ndarray:
    return np.diag([0.5, 0.4, 0.3, 0.2, 0.1])


def _valid_profile(**overrides) -> ArchivedProfile:
    first = datetime(2026, 1, 1, 10, 0, 0)
    last = datetime(2026, 1, 1, 10, 5, 0)
    defaults = dict(
        mu=_valid_mu(),
        sigma=_valid_sigma(),
        n_points=3,
        first_seen=first,
        last_seen=last,
    )
    defaults.update(overrides)
    return ArchivedProfile(**defaults)


class TestArchivedProfileValidCases:
    def test_accepts_valid_profile(self):
        profile = _valid_profile()
        assert isinstance(profile.mu, Vector5D)
        assert profile.sigma.shape == (5, 5)
        assert profile.n_points == 3
        assert profile.first_seen <= profile.last_seen

    def test_accepts_psd_with_zero_eigenvalue(self):
        sigma = np.diag([1.0, 0.5, 0.1, 0.0, 0.0])
        profile = _valid_profile(sigma=sigma)
        assert np.min(np.linalg.eigvalsh(profile.sigma)) == pytest.approx(0.0)

    def test_accepts_equal_temporal_bounds(self):
        t = datetime(2026, 1, 1, 10, 0, 0)
        profile = _valid_profile(first_seen=t, last_seen=t)
        assert profile.first_seen == profile.last_seen


class TestArchivedProfileSigmaValidation:
    def test_rejects_non_5x5_sigma(self):
        with pytest.raises(ValueError, match="5x5"):
            _valid_profile(sigma=np.eye(4))

    def test_rejects_non_finite_sigma_nan(self):
        sigma = _valid_sigma().copy()
        sigma[0, 0] = np.nan
        with pytest.raises(ValueError, match="finie"):
            _valid_profile(sigma=sigma)

    def test_rejects_non_finite_sigma_inf(self):
        sigma = _valid_sigma().copy()
        sigma[0, 1] = np.inf
        sigma[1, 0] = np.inf
        with pytest.raises(ValueError, match="finie"):
            _valid_profile(sigma=sigma)

    def test_rejects_non_symmetric_sigma(self):
        sigma = _valid_sigma().copy()
        sigma[0, 1] = 0.3
        sigma[1, 0] = 0.0
        with pytest.raises(ValueError, match="symetrique"):
            _valid_profile(sigma=sigma)

    def test_rejects_non_psd_sigma(self):
        sigma = np.eye(5)
        sigma[0, 0] = -0.1
        with pytest.raises(ValueError, match="positive semi-definie"):
            _valid_profile(sigma=sigma)


class TestArchivedProfileFieldValidation:
    def test_rejects_mu_not_vector5d(self):
        with pytest.raises(TypeError, match="Vector5D"):
            _valid_profile(mu=(0.2, 0.3, 0.4, 0.5, 0.6))

    def test_rejects_n_points_below_two(self):
        with pytest.raises(ValueError, match="n_points"):
            _valid_profile(n_points=1)

    def test_rejects_n_points_not_int(self):
        with pytest.raises(TypeError, match="entier"):
            _valid_profile(n_points=2.5)

    def test_rejects_n_points_bool(self):
        with pytest.raises(TypeError, match="entier"):
            _valid_profile(n_points=True)

    def test_rejects_inverted_temporal_bounds(self):
        first = datetime(2026, 1, 1, 10, 0, 1)
        last = datetime(2026, 1, 1, 10, 0, 0)
        with pytest.raises(ValueError, match="first_seen > last_seen"):
            _valid_profile(first_seen=first, last_seen=last)

    def test_rejects_first_seen_not_datetime(self):
        with pytest.raises(TypeError, match="first_seen"):
            _valid_profile(first_seen="2026-01-01T10:00:00")

    def test_rejects_last_seen_not_datetime(self):
        with pytest.raises(TypeError, match="last_seen"):
            _valid_profile(last_seen=123)


class TestArchivedProfileImmutability:
    def test_is_immutable(self):
        profile = _valid_profile()
        with pytest.raises(AttributeError):
            profile.n_points = 4  # type: ignore[misc]

    def test_equality_works(self):
        profile_a = _valid_profile()
        profile_b = _valid_profile()
        assert profile_a == profile_b

    def test_inequality_works(self):
        profile_a = _valid_profile()
        profile_b = _valid_profile(n_points=5)
        assert profile_a != profile_b
