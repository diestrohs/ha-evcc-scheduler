# EVCC Scheduler v0.1.4

Release Date: 2026-01-25

## Changes

- Fix: Correct `precondition` semantics to enum values 0/1/2
  - `0` = no precondition
  - `1` = PV surplus only
  - `2` = cheap prices only (if tariffs enabled)
- Services validation updated in `services.py` (booleans explicitly rejected for `precondition`)
- `services.yaml` selector switched to numeric range (0–2) with clearer description
- README (DE/EN) and Documentation (DE/EN) updated to reflect enum meanings and examples
- Version bumped to 0.1.4 in manifest and CHANGELOG updated

## Compatibility

- Home Assistant: 2025.12.0+
- EVCC: 0.210.2+

## Notes

- No changes to data flow or entity IDs; this release strictly improves validation and documentation.

## Previous (v0.1.3)

- Stricter service input validation for `time`, `weekdays`, `soc`, `active`
- Coordinator presence checks with clear ServiceValidationError messages
- README (DE/EN) updates with input validation and `tz` examples