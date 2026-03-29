# d4 Intensity Specification v1

- `spec_id`: `d4_intensity_spec.v1`
- `version`: `v1`
- `status`: `provisional`
- `scope`: `CYBER-VPT d4 operational intensity`
- `owner`: `CYBER-VPT`

## 1. Role of d4 in the 5D Vector

`d4` captures observable operational capability of an action to transform,
control, or destroy target state, normalized in `[0,1]`.

`d4` is one dimension among five and must not be treated as a standalone
verdict.

## 2. Normative Definition of Intensity

Retained definition:
- `d4` does not measure danger, intent, or malignity.
- `d4` measures only observable operational capability on the target state.

Operational capability means what the action can concretely do to target state,
from read-only observation to control/execution-level effect.

## 3. What d4 Does Not Measure

`d4` does not encode:
- attacker intent,
- legal legitimacy,
- business criticality,
- data sensitivity,
- confidence of malicious attribution.

A high `d4` score is not sufficient to conclude an attack.

## 4. Portability and Symmetry Requirements

Methodological constraints for v1:
- `d4` must be calculable from an observed input action and from an action
  represented in MITRE-side references.
- Therefore, `d4` must stay portable across protocols and action vocabularies.
- The same capability grid must be used for both sides.

## 5. Common Cross-Protocol Operational Capability Grid

Retained stable grid for v1:
- `OBSERVE_READ`: observation / read without target state modification.
- `CREATE_DEPOSIT`: creation / deposit of new artifact or record.
- `MODIFY_WRITE`: modification / write of existing state.
- `DELETE_STRONG_ALTER`: deletion or strong alteration with durable impact.
- `CONTROL_EXECUTE`: control change, execution, or active steering capability.

## 6. Protocol-to-Capability Projection Rules

Normative rule:
- classify by observable operational effect on the target,
- not by native protocol verb alone.

Mandatory examples:
- an HTTP `GET` with application-side effects must not be automatically mapped
  to `OBSERVE_READ`;
- a permission/rights change must be mapped according to actually observed
  control capability effect.

Additional methodological constraints:
- sensitive read remains a read in `d4` terms;
- benign write remains a modification in `d4` terms;
- context can influence interpretation but must not rewrite capability nature.

## 7. Ambiguous Cases (Documented as Ambiguous)

The following cases are intentionally marked context-dependent in v1:
- massive read,
- benign write,
- legitimate deletion,
- legitimate automatic creation,
- normal administrative execution,
- expected maintenance permission change.

Method rule:
- these cases must be documented as ambiguous,
- they must not be artificially over-interpreted into attack conclusions.

## 8. d4_hint in Mapping Tables

`d4_hint` is defined as:
- provisional,
- ordinal,
- documentary,
- not empirically calibrated in v1,
- not sufficient by itself to conclude an attack.

`d4_hint` values provide ordering guidance for capability classes only.
They are not a runtime scoring algorithm.

## 9. Interpretation Limits

This specification does not define:
- executable d4 computation code,
- runtime loading behavior,
- DTW behavior,
- MITRE detailed modeling,
- alert thresholds or decision policy.

## 10. Open Points for Future Calibration

Intentionally left open in v1:
- corpus-based calibration of numerical anchors associated with capability
  classes,
- protocol-family coverage extension,
- tie-breaking rules when multiple effects are observed in one action record,
- confidence metadata associated with mapping quality.

Any normative evolution must create new versioned files (`v2`, `v3`, ...), not
silent edits of `v1`.
