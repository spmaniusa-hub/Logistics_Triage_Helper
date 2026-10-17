# Deliverable 3: Bug Fix Package (`intake.py`)

This document packages the full developer workflow used to resolve the bug reported in `bug_report.txt`, applying the five developer patterns (**EXPLAIN**, **DEBUG**, **GENERATE**, **TEST**, and **DOCUMENT**).

---

## 1. EXPLAIN Pattern (Orientation)

### Prompt
```markdown
You are a senior Python engineer assisting a new team member at Northgate Logistics.
Explain the `intake.py` module below.
Break down:
1. The primary purpose and architecture of the module.
2. The data flow from raw complaint to final intake record.
3. The specific responsibilities of `normalize_text`, `can_auto_route`, and `build_record`.
4. Any assumptions the code makes about incoming triage data.
```

### AI Response
> **Summary & Architecture:**
> `intake.py` serves as the intake gateway for Northgate Logistics' complaint processing pipeline. It bridges raw customer text submissions with the structured output produced by the upstream triage classification model.
>
> **Data Flow:**
> 1. `Complaint`: A dataclass holding the raw customer submission (`complaint_id`, `text`, and optional pre-assigned category/priority).
> 2. `normalize_text`: Cleans up untrusted input by collapsing irregular whitespace and stripping leading/trailing spaces.
> 3. `can_auto_route`: Evaluates whether a triage record meets strict automated dispatch criteria without human intervention.
> 4. `build_record`: Assembles the finalized dictionary containing normalized text, triage fields, human escalation status, and the `auto_route` decision.
>
> **Assumptions & Observations:**
> - Assumes incoming triage records are Python dictionaries containing four specific keys: `category`, `priority`, `summary`, and `needs_human`.
> - Validates categories against `ALLOWED_CATEGORIES` and priorities against `ALLOWED_PRIORITIES`.
> - Evaluates auto-route eligibility based on key presence and allowed values.

---

## 2. DEBUG Pattern (Diagnosis & Ranked Causes)

### Prompt
```markdown
You are a software reliability engineer debugging an intake failure at Northgate Logistics.
Review:
1. The code in `intake.py`
2. The ticket in `bug_report.txt`:
   "Complaints flagged for human review are being auto-routed. Example: category 'damaged', priority 'P1', summary present, needs_human=true produced an intake record with auto_route=true."
3. Requirement 5 from `requirements.txt`:
   "Any record with needs_human=true must have auto_route=false."

Do NOT write code or provide a fix yet.
Instead:
1. Provide ranked potential root causes from most probable to least probable.
2. For each cause, specify concrete confirmation steps to verify or eliminate it without changing code.
3. Explain why this bug remained silent without throwing any runtime exceptions.
```

### AI Response
> ### Ranked Root Causes:
> 1. **Cause 1 (Definite / Primary Root Cause): Key Existence Checked, but Boolean Value Ignored in `can_auto_route`**
>    - *Analysis:* In `can_auto_route`, line 19 defines `required = {"category", "priority", "summary", "needs_human"}`. Line 20 checks `if set(record) != required: return False`. However, the function **never inspects the value of `record["needs_human"]`**.
>    - After checking categories and priorities, line 26 simply returns `bool(record["summary"])`. Because the summary is non-empty, `can_auto_route` evaluates to `True`, completely ignoring that `record["needs_human"] == True`.
>
> 2. **Cause 2 (Secondary / Unlikely): Type Coercion or Key Shadowing in `build_record`**
>    - *Analysis:* Could `build_record` be overwriting or passing wrong arguments to `can_auto_route`? Eliminated: `build_record` directly passes the `triage` dictionary into `can_auto_route(triage)`.
>
> ### Confirmation Steps:
> 1. In an interactive Python session or unit test, invoke:
>    ```python
>    can_auto_route({"category": "damaged", "priority": "P1", "summary": "Cracked screen", "needs_human": True})
>    ```
> 2. Observe the return value. If it returns `True`, Cause 1 is confirmed.
>
> ### Why No Exception Was Thrown:
> The logic is syntactically valid Python. The dictionary contains all expected keys, the set comparison succeeds, the set lookups succeed, and `bool("Cracked screen")` returns `True`. It is a pure business logic flaw.

---

## 3. GENERATE Pattern (Minimal Fix)

### Prompt
```markdown
Apply the GENERATE pattern. Produce the smallest, most minimal change to `intake.py` that fixes Cause 1.
Include a "done means" checklist with at least one happy path and one failure case.
Do not refactor unaffected functions.
```

### AI Response
> ### "Done Means" Checklist:
> - [x] When `record["needs_human"]` is `True`, `can_auto_route` returns `False`.
> - [x] When `record["needs_human"]` is anything other than `False` (e.g. missing, truthy, non-boolean), auto-routing is blocked.
> - [x] When `record["needs_human"]` is `False` with valid category, priority, and summary, `can_auto_route` returns `True`.
> - [x] Unaffected functions (`normalize_text`, `build_record`) and dataclasses remain untouched.
>
> ### Minimal Diff:
> ```diff
> --- a/intake.py
> +++ b/intake.py
> @@ -23,4 +23,6 @@ def can_auto_route(record: dict) -> bool:
>      if record["priority"] not in ALLOWED_PRIORITIES:
>          return False
> +    if record["needs_human"] is not False:
> +        return False
>      return bool(record["summary"])
> ```

---

## 4. TEST Pattern (Edge Cases & Pytest/Unittest Suite)

### Prompt
```markdown
You are a QA automation engineer using the TEST pattern.
Step 1: List all edge cases and boundary conditions based on `requirements.txt` (not just the code). Mark any edge cases that simple happy-path tests would miss.
Step 2: Generate a comprehensive test suite (`test_intake.py`) testing `can_auto_route`, `normalize_text`, and `build_record`.
```

### AI Response & Identified Edge Cases:
* **Edge Case 1 (The Reported Bug):** Record with valid category/priority and non-empty summary, but `needs_human=True`. Must return `False`.
* **Edge Case 2:** Record with `needs_human=False`, but empty summary string (`""`). Must return `False`.
* **Edge Case 3:** Missing or extraneous keys in dictionary. Must return `False`.
* **Edge Case 4:** Invalid enumerated values for category or priority. Must return `False`.
* **Edge Case 5:** Text normalization with irregular multiline whitespace, tabs, and padding.
* **Edge Case 6:** Full end-to-end integration via `build_record`.

### Generated Test Suite (`test_intake.py`)
```python
import unittest
from intake import Complaint, normalize_text, can_auto_route, build_record

class TestIntake(unittest.TestCase):
    def test_normalize_text(self):
        raw = "  Parcel   arrived    late\n  and damaged. \t "
        self.assertEqual(normalize_text(raw), "Parcel arrived late and damaged.")

    def test_can_auto_route_standard_eligible(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "Shipment delayed by two days.",
            "needs_human": False
        }
        self.assertTrue(can_auto_route(triage))

    def test_can_auto_route_bug_ticket_reproduction(self):
        """Requirement 5: Any record with needs_human=true must have auto_route=false"""
        triage = {
            "category": "damaged",
            "priority": "P1",
            "summary": "Screen cracked on monitor.",
            "needs_human": True
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_missing_key(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "Delayed"
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_extra_key(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "Delayed",
            "needs_human": False,
            "extra_field": "unexpected"
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_invalid_category(self):
        triage = {
            "category": "lost_forever",
            "priority": "P2",
            "summary": "Item lost",
            "needs_human": False
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_invalid_priority(self):
        triage = {
            "category": "delay",
            "priority": "URGENT",
            "summary": "Delayed",
            "needs_human": False
        }
        self.assertFalse(can_auto_route(triage))

    def test_can_auto_route_empty_summary(self):
        triage = {
            "category": "delay",
            "priority": "P3",
            "summary": "",
            "needs_human": False
        }
        self.assertFalse(can_auto_route(triage))

    def test_build_record_integration(self):
        c = Complaint(complaint_id="NGL-002", text="The monitor box was crushed.")
        triage = {
            "category": "damaged",
            "priority": "P1",
            "summary": "Monitor crushed.",
            "needs_human": True
        }
        rec = build_record(c, triage)
        self.assertEqual(rec["complaint_id"], "NGL-002")
        self.assertEqual(rec["original_text"], "The monitor box was crushed.")
        self.assertEqual(rec["category"], "damaged")
        self.assertEqual(rec["priority"], "P1")
        self.assertTrue(rec["needs_human"])
        self.assertFalse(rec["auto_route"])

if __name__ == "__main__":
    unittest.main()
```

---

## 5. DOCUMENT Pattern (Commit Message & Context)

### Generated Commit Message
```text
fix(intake): prevent auto-routing when needs_human is true

Verify that record["needs_human"] is explicitly False before allowing
auto_route to evaluate to True in can_auto_route(). Enforces Northgate
Triage Requirement 5.
```

### Sentence of "Why" the Model Could Not Have Known
> **Context:** In Northgate's production environment, auto-routing bypasses agent review by triggering automated customer acknowledgment emails and marking intake tickets as resolved; routing complaints with `needs_human: true` causes severe silent customer neglect and liability before human operators ever inspect the queue.

---

## 6. Corrected Code (`intake.py`)

```python
from dataclasses import dataclass

ALLOWED_CATEGORIES = {"delay", "damaged", "missing", "billing", "other"}
ALLOWED_PRIORITIES = {"P1", "P2", "P3", "P4"}

@dataclass
class Complaint:
    complaint_id: str
    text: str
    category: str | None = None
    priority: str | None = None


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def can_auto_route(record: dict) -> bool:
    required = {"category", "priority", "summary", "needs_human"}
    if set(record) != required:
        return False
    if record["category"] not in ALLOWED_CATEGORIES:
        return False
    if record["priority"] not in ALLOWED_PRIORITIES:
        return False
    if record["needs_human"] is not False:
        return False
    return bool(record["summary"])


def build_record(complaint: Complaint, triage: dict) -> dict:
    return {
        "complaint_id": complaint.complaint_id,
        "original_text": normalize_text(complaint.text),
        "category": triage.get("category", "other"),
        "priority": triage.get("priority", "P4"),
        "summary": triage.get("summary", ""),
        "needs_human": triage.get("needs_human", True),
        "auto_route": can_auto_route(triage),
    }
```
