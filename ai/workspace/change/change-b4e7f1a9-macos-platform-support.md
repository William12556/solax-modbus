```yaml
# T02 Change Document
# macOS Full Platform Support

change_info:
  id: "change-b4e7f1a9"
  title: "macOS Full Platform Support"
  date: "2026-03-14"
  author: "William Watson"
  status: "rejected"
  priority: "medium"
  iteration: 2
  coupled_docs:
    issue_ref: "issue-b4e7f1a9"
    issue_iteration: 2

source:
  type: "enhancement"
  reference: "ai/workspace/issues/issue-b4e7f1a9-macos-platform-support.md"
  description: >
    Extend deployment target to include macOS as a fully supported production
    platform. Approved proposal: ai/workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md

scope:
  summary: >
    Rejected 2026-07-02. macOS is not pursued as a deployment target.
    install.sh remains Linux-only. No code changes made under this document.
  affected_components: []
  affected_designs: []
  out_of_scope:
    - "macOS install path handling"
    - "macOS service/launchd registration"
    - "Windows support"

rational:
  problem_statement: >
    Iteration 1 stated install.sh "hardcoded /opt/solax-monitor/ and registered
    a systemd service" as current behavior, and described the macOS change as
    already implemented. Direct source inspection (2026-07-02) found neither
    claim true: install.sh performs no systemd operations of any kind, on any
    platform, and no macOS branch was ever added. The iteration 1 status field
    ("implemented") was incorrect.
  proposed_solution: >
    Reject macOS support. Correct the false "implemented" status. Close the
    coupled issue. Do not implement any macOS-specific logic in install.sh.
  alternatives_considered:
    - option: "Retrofit this document to cover Linux systemd automation instead"
      reason_rejected: >
        This document's identity and full history concern macOS support
        specifically. Repurposing it for an unrelated Linux-only feature would
        misrepresent its provenance. See change-f2a8c471 instead.
  benefits: []
  risks: []

technical_details:
  current_behavior: >
    install.sh is Linux-only (rejects all other OS via uname -s check).
    Performs no systemd registration; symlinks the binary into
    /usr/local/bin/ and prints manual instructions for service creation.
    This has been true throughout; iteration 1's description of pre-existing
    systemd registration was inaccurate.
  proposed_behavior: >
    No change. install.sh remains Linux-only. This document is closed without
    implementation.
  implementation_approach: "None — rejected."
  code_changes: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Not applicable — no implementation."
  test_cases: []
  regression_scope: []
  validation_criteria: []

implementation:
  effort_estimate: ""
  implementation_steps: []
  rollback_procedure: "Not applicable — no code changed under this document."
  deployment_notes: "None."

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: "2026-07-02"
  verified_by: "William Watson"
  test_results: "Not applicable — rejected."
  issues_found:
    - issue_ref: "issue-b4e7f1a9"

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-f2a8c471"
      relationship: "related, unrelated concern raised during same review"
  related_issues:
    - issue_ref: "issue-b4e7f1a9"
      relationship: "source"

notes: >
  Superseded proposal: ai/workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md.
  The separate, unrelated request for automatic Linux systemd service
  registration is tracked under change-f2a8c471.

version_history:
  - version: "1.0"
    date: "2026-03-14"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-03-14"
    author: "William Watson"
    changes:
      - "Status updated to implemented"
      - "implementation_steps owner updated to Strategic Domain"
      - "verification.implemented_date and implemented_by populated"
      - "traceability.design_updates update_date populated"
  - version: "2.0"
    date: "2026-07-02"
    author: "William Watson"
    changes:
      - "Corrected false 'implemented' status to 'rejected'"
      - "Corrected technical_details.current_behavior to match actual source (no systemd code, no macOS branch)"
      - "Cleared code_changes, affected_components, and testing sections — no implementation performed"
      - "Cross-referenced change-f2a8c471 for the unrelated systemd automation work"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
