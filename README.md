# Northgate Logistics - AI-Assisted Triage Helper Prototype

Final Project submission for *Basics of Prompting for Developers and AI Introduction*.

## Documentation

- **[System Design Document](DESIGN_DOCUMENT.md)**: System architecture, component breakdowns, data models, threat modeling, and queue routing matrix.
- **[User Guide & Operations Manual](USER_GUIDE.md)**: Setup instructions, step-by-step workflow, verification commands, prompt library quick reference, and FAQ.

## Six Deliverables (Index)

1. **Deliverable 1 (Prompt Library):** [`deliverable_1_prompt_library.md`](deliverable_1_prompt_library.md) (also available as `prompt_library.md`)
2. **Deliverable 2 (Triage Prompt & Validation Evidence):** [`deliverable_2_triage.md`](deliverable_2_triage.md)
3. **Deliverable 3 (Bug Fix Package):** [`deliverable_3_bug_fix_package.md`](deliverable_3_bug_fix_package.md)
4. **Deliverable 4 (Four-Step Verification Report):** [`deliverable_4_verification_report.md`](deliverable_4_verification_report.md)
5. **Deliverable 5 (Improvement Log):** [`deliverable_5_improvement_log.md`](deliverable_5_improvement_log.md)
6. **Deliverable 6 (One-Page Reflection):** [`deliverable_6_reflection.md`](deliverable_6_reflection.md) (also available as `reflection.md`)

## Code & Test Runners

- `intake.py`: Corrected intake module with bug fix applied.
- `test_intake.py`: Unit test suite verifying `intake.py` (`python3 test_intake.py`).
- `test_triage_runner.py`: Validation script verifying V1 and V2 outputs against `validation.py` (`python3 test_triage_runner.py`).
- `validation.py`: Starter validator script.
- `submission_checklist.md`: Completed submission checklist.
