# d5 Rarity Reference - Versioned Documentary Reference

This directory stores the versioned documentary reference for the d5 (rarity)
dimension.

Scope is strictly documentary: no runtime loader behavior, no executable
implementation, no benchmark/calibration workflow, no test execution policy,
no DTW logic, and no alerting policy logic.

`d5` remains a scalar dimension in `[0,1]`. The `never_seen` case remains
inside the same scalar continuum and is represented by the maximum anchor.
The projection is ordinal and documentary, with fixed anchors.

This reference does not define `Fingerprint` as a transverse object. It only
covers the minimal relation "rarity of an observed fingerprint" for d5.

Temporal horizon and forgetting/aging policy are explicitly out of v1.

## Files

- `d5_rarity_spec.v1.md`: normative documentary specification for d5.
- `rarity_projection.v1.yaml`: versioned documentary table for ordinal classes,
  anchors, and input/MITRE semantic correspondence.

## Update Rules

- Do not modify released `v1` files in place for semantic changes.
- Create `vN` files for any structural or normative change.
- Record each new version in `CHANGELOG.md`.
- Add or update a decision entry in `DECISIONS.md` for structural choices.

## Mandatory Methodological Rules

- d5 must remain scalar and bounded in `[0,1]`.
- `never_seen` must remain in the same scalar continuum.
- Projection must remain ordinal, documentary, and bounded with fixed anchors.
- Counting universe must remain explicit and unique for v1.
- Counting granularity must remain explicit and unique for v1.
- Input/MITRE symmetry for d5 must remain semantic and documentary.
- d5 alone is not sufficient to conclude an attack.

## Out of Scope

- Full transverse definition of `Fingerprint`.
- Runtime estimator design and implementation.
- Empirical calibration workflow and benchmark logic.
- Execution-time validation/test procedures.
- DTW internals, matching internals, AlertEngine internals.
- Temporal horizon policy details (out of v1).
- Forgetting/aging policy details (out of v1).
