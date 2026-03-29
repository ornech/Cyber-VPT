# d4 Intensity Reference - Versioned Specification Data

This directory stores versioned documentation and data references for the d4
(intensite operatoire) dimension.

Scope is strictly documentary: no runtime loader behavior, no executable
implementation, no DTW policy, no MITRE detailed mapping policy, and no
alerting policy.

## Files

- `d4_intensity_spec.v1.md`: normative specification for d4 intensity.
- `action_semantics.v1.yaml`: versioned schema-and-examples table for
  `ActionSemantics` records.
- `protocol_mappings.v1.yaml`: initial versioned protocol-to-capability
  projection table.

## Update Rules

- Do not modify a released `v1` file in place for semantic changes.
- Create `vN` files for any structural or normative change.
- Record each new version in `CHANGELOG.md`.
- Add or update a decision entry in `DECISIONS.md` for structural choices.

## Mandatory Methodological Rules

- d4 must be calculable on observed input actions and on MITRE-side action
  descriptions, so the capability grid must remain portable across protocols.
- An action must be classified by observable operational effect on the target,
  not by native verb alone.
- A high d4 value does not mean "attack" by itself.

## Out of Scope

- Python code or executable implementation.
- Runtime loading or automation details.
- DTW internals, matching internals, MITRE internals, AlertEngine internals.
- Alert thresholds or operational policy decisions.
