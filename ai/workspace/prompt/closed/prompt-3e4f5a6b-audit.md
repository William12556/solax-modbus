Created: 2026 June 28

# T04 Audit Prompt — solax-modbus src/ Code Quality

---

## Table of Contents

[1.0 Prompt Info](<#1.0 prompt info>)
[2.0 Context](<#2.0 context>)
[3.0 Specification](<#3.0 specification>)
[4.0 Audit Scope](<#4.0 audit scope>)
[5.0 Deliverable](<#5.0 deliverable>)
[6.0 Success Criteria](<#6.0 success criteria>)
[7.0 Tactical Brief](<#7.0 tactical brief>)

---

## 1.0 Prompt Info

```yaml
prompt_info:
  id: "prompt-3e4f5a6b"
  task_type: "audit"
  source_ref: "P08 audit — solax-modbus src/ code quality"
  date: "2026-06-28"
  iteration: 1
  coupled_docs:
    change_ref: "N/A"
    change_iteration: 1
```

---

## 2.0 Context

```yaml
context:
  purpose: >
    Read-only code quality audit of src/solax_modbus/. No source files
    are written. Findings are accumulated in ai/state/ralph/audit-report.md.
  integration: >
    Audit proceeds item by item as listed in ai/state/ralph/audit-index.md.
    Worker marks each item [x] on completion. Reviewer checks coverage and
    finding quality before issuing SHIP.
  constraints:
    - "DO NOT write to any file under src/"
    - "audit-index.md item list must not be modified"
    - "Append findings only — do not overwrite audit-report.md"
```

---

## 3.0 Specification

```yaml
specification:
  description: >
    Per-item code quality audit of src/solax_modbus/ against six criteria.
    One audit-index.md item per AEL iteration.
  requirements:
    functional:
      - "Read each target function or class from source"
      - "Evaluate against all six audit criteria"
      - "Append findings to audit-report.md in the required format"
      - "Mark item [x] in audit-index.md on completion"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Read-only — no src/ writes"
        - "Append-only audit-report.md"
        - "One index item per iteration"
```

---

## 4.0 Audit Scope

Criteria applied to every item:

| Criterion | Description |
|---|---|
| style | PEP 8, naming conventions, docstrings, inline comments |
| complexity | Cyclomatic complexity, function length, nesting depth |
| error-handling | Exception coverage, logging, failure modes |
| security | Input validation, injection risk, unsafe operations |
| conformance | Consistency with design documents and register specification |
| dead-code | Unreachable branches, unused variables, imports |

Finding format required in `audit-report.md`:

```
---
## src/module.py :: ClassName.method_name  [iteration N]
- **Type:** <criterion>
- **Location:** line <N> (or range <N>–<M>)
- **Description:** <precise, actionable observation>
- **Severity:** <low | medium | high>
```

Items with no findings:

```
---
## src/module.py :: function_name  [iteration N]
- No findings.
```

---

## 5.0 Deliverable

```yaml
deliverable:
  files:
    - path: "ai/state/ralph/audit-report.md"
      content: "Append-only findings accumulator. Do not overwrite."
    - path: "ai/state/ralph/audit-index.md"
      content: "Mark completed items [x]. Do not add or remove items."
```

---

## 6.0 Success Criteria

```yaml
success_criteria:
  - "All 25 items in audit-index.md are marked [x]"
  - "audit-report.md contains an entry for every item"
  - "No src/ files written or modified"
```

---

## 7.0 Tactical Brief

```yaml
tactical_brief: |
  Read-only code quality audit of /Users/williamwatson/Documents/GitHub/solax-modbus/src/solax_modbus/.
  State directory: /Users/williamwatson/Documents/GitHub/solax-modbus/ai/state/ralph/
  DO NOT write to any file under src/.
  Audit criteria: style, complexity, error-handling, security, conformance, dead-code.
  Process one item per iteration from audit-index.md (most complex first).
  For each item: read the source, evaluate against all six criteria, append findings
  to audit-report.md in the required format, mark the item [x] in audit-index.md.
  Finding format:
    ---
    ## src/module.py :: ClassName.method  [iteration N]
    - **Type:** <criterion>
    - **Location:** line <N>
    - **Description:** <observation>
    - **Severity:** <low|medium|high>
  If no findings: record "- No findings." entry.
  Do not overwrite audit-report.md; append only.
  Do not add or remove items from audit-index.md.
```

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-28 | Initial audit prompt — solax-modbus src/ code quality |
| 1.1 | 2026-06-28 | Removed §7.0 Notes: recipe auto-selection is implemented in orchestrator.py (line 1512); manual swap instruction was incorrect |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
