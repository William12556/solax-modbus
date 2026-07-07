```yaml
# T03 Issue Document
# macOS Full Platform Support

issue_info:
  id: "issue-b4e7f1a9"
  title: "macOS Full Platform Support"
  date: "2026-03-14"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "requirement_change"
  iteration: 2
  coupled_docs:
    change_ref: "change-b4e7f1a9"
    change_iteration: 2

source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Human-requested scope extension. macOS to be added as a fully supported
    production deployment target alongside Debian 12 / Raspberry Pi 4.
    Approved proposal: ai/workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md

affected_scope:
  components:
    - name: "install.sh"
      file_path: "install.sh"
  designs:
    - design_ref: "ai/workspace/design/design-solax-modbus-master.md"
  version: "0.1.0"

reproduction:
  prerequisites: "Deploy application on macOS"
  steps:
    - "Run install.sh on macOS"
    - "Script rejects unsupported OS (Linux-only)"
  frequency: "always"
  reproducibility_conditions: "Any macOS host"
  preconditions: ""
  test_data: ""
  error_output: "install.sh exits with 'Unsupported operating system' on macOS"

behavior:
  expected: >
    Original expectation (iteration 1): install.sh installs to
    ~/.local/opt/solax-monitor/ on macOS, no service registration performed.
  actual: >
    Iteration 2 correction: install.sh is Linux-only and contains no
    systemd registration code of any kind (confirmed by direct source
    inspection 2026-07-02). Iteration 1 of this document incorrectly
    described systemd registration as already existing prior to this
    change; that was false. No macOS branch was ever added.
  impact: "Application cannot be deployed on macOS without manual script modification."
  workaround: "Manually create venv at preferred path and run monitor directly."

environment:
  python_version: "3.9+"
  os: "macOS (any)"
  dependencies:
    - library: "pymodbus"
      version: "3.5.0+"
  domain: "domain_1"

analysis:
  root_cause: >
    Initial design scoped deployment exclusively to Debian 12 / Raspberry Pi 4.
    install.sh and requirements/design documents do not accommodate macOS paths
    or the absence of systemd.
  technical_notes: >
    Python application code is fully cross-platform; no source changes required
    for macOS support itself. This remains true, but macOS support is no longer
    pursued (see resolution).
  related_issues:
    - issue_ref: "issue-f2a8c471"
      relationship: "related"

resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    Rejected. Human decision (2026-07-02): macOS platform support will not be
    pursued. install.sh remains Linux-only. Separate concern raised during
    this review — automatic systemd service registration on Linux — is
    tracked independently under issue-f2a8c471 / change-f2a8c471, since it is
    unrelated to macOS and does not depend on this issue's resolution.
  change_ref: "change-b4e7f1a9"
  resolved_date: "2026-07-02"
  resolved_by: "William Watson"
  fix_description: "No implementation. Scope rejected; issue closed without code change."

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: >
    Closed as rejected. No macOS-specific code exists or will be added.
    install.sh continues to target Linux (Debian/Raspberry Pi) only.

prevention:
  preventive_measures: "Evaluate platform scope during initial requirements capture."
  process_improvements: >
    Change documents must be verified against actual source state before
    being marked implemented; iteration 1 of the coupled change document
    was marked implemented without corresponding code ever being written.

verification_enhanced:
  verification_steps: []
  verification_results: "Not applicable — rejected, no implementation performed."

traceability:
  design_refs:
    - "ai/workspace/design/design-solax-modbus-master.md"
  change_refs:
    - "change-b4e7f1a9"
  test_refs: []

notes: "Superseded proposal: ai/workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md. macOS support rejected 2026-07-02."

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-03-14"
    author: "William Watson"
    changes:
      - "Initial issue document"
  - version: "2.0"
    date: "2026-07-02"
    author: "William Watson"
    changes:
      - "Corrected reproduction/actual behavior: no systemd registration ever existed in source, contrary to iteration 1 text"
      - "Status changed to closed; resolution: macOS support rejected, will not be pursued"
      - "Cross-referenced new issue-f2a8c471 for the unrelated systemd automation concern"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
