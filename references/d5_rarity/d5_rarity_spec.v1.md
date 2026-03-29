# d5 Rarity Specification v1

- `spec_id`: `d5_rarity_spec.v1`
- `version`: `v1`
- `status`: `accepted`
- `scope`: `CYBER-VPT d5 rarity`
- `owner`: `CYBER-VPT`

## 1. Role of d5 in 5D vectorization

`d5` represents the rarity of an observed fingerprint in the 5D vector and is
bounded in `[0,1]`.

`d5` is one dimension among five and must not be treated as a standalone
verdict.

## 2. Normative minimal definition of observed fingerprint rarity

Retained `v1` definition:

- `d5` measures rarity of an observed fingerprint relative to a documentary
  counting universe.
- The full transverse definition and construction of `Fingerprint` are out of
  scope for this specification.

## 3. Retained counting universe

The counting universe is fixed for `v1` as:

- by source family or protocol.

Rarity is always interpreted relative to that retained universe.

## 4. Retained counting granularity

The counting granularity is fixed for `v1` as:

- observed action occurrence.

## 5. Normative treatment of `never_seen`

For `v1`, `never_seen` is represented as the maximum value of the scalar rarity
continuum in `[0,1]`.

No hidden flag, side channel, or out-of-range state is introduced.

## 6. Canonical ordinal projection in `[0,1]`

The retained projection is:

- ordinal documentary projection with fixed anchors.

This specification defines an ordinal documentary class mapping, bounded in
`[0,1]`, without imposing a runtime estimator law.

## 7. Semantic input/MITRE symmetry rule

For `d5`, retained symmetry is semantic and documentary:

- observed input side and MITRE side must use the same documentary rarity
  vocabulary and correspondence table;
- this does not require empirical frequency symmetry between input and MITRE.

## 8. Interpretation limits

Methodological limits for `v1`:

- d5 alone is not sufficient to conclude an attack.
- Rarity can have legitimate causes of fingerprint renewal, including:
  - browser change,
  - system update,
  - legitimate new equipment,
  - other observable legitimate renewals.

## 9. What d5 does not measure

d5 does not measure:

- attacker intent,
- legal legitimacy,
- business criticality,
- attack certainty,
- alert policy decisions.

## 10. Elements explicitly out of v1

The following are intentionally out of `v1`:

- temporal horizon policy,
- forgetting/aging policy,
- runtime estimator selection,
- implementation and execution behavior.

## 11. Traceability link to `rarity_projection.v1.yaml`

The authoritative documentary table for ordinal classes, fixed anchors,
`never_seen` policy, and semantic input/MITRE correspondence is versioned in:

`references/d5_rarity/rarity_projection.v1.yaml`
