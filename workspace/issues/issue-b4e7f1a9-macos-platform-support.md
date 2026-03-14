```yaml
# T03 Issue Document
# macOS Full Platform Support

issue_info:
  id: "issue-b4e7f1a9"
  title: "macOS Full Platform Support"
  date: "2026-03-14"
  reporter: "William Watson"
  status: "open"
  severity: "medium"
  type: "requirement_change"
  iteration: 1
  coupled_docs:
    change_ref: "change-b4e7f1a9"
    change_iteration: 1

source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Human-requested scope extension. macOS to be added as a fully supported
    production deployment target alongside Debian 12 / Raspberry Pi 4.
    Approved proposal: workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md

affected_scope:
  components:
    - name: "install.sh"
      file_path: "install.sh"
  designs:
    - design_ref: "workspace/design/design-solax-modbus-master.md"
  version: "0.1.0"

reproduction:
  prerequisites: "Deploy application on macOS"
  steps:
    - "Run install.sh on macOS"
    - "Script assumes /opt/solax-monitor/ (Linux path)"
    - "Script registers systemd service (not available on macOS)"
  frequency: "always"
  reproducibility_conditions: "Any macOS host"
  preconditions: ""
  test_data: ""
  error_output: "install.sh fails on macOS due to Linux-specific paths and systemd dependency"

behavior:
  expected: >
    install.sh installs package to ~/.local/opt/solax-monitor/ on macOS.
    No service registration performed on macOS (manual start only).
    Requirements and design documents reflect macOS as a supported target.
  actual: >
    install.sh targets /opt/solax-monitor/ and registers a systemd service.
    Neither is valid on macOS. Requirements and design documents list only
    Debian 12 / Raspberry Pi 4 as the target platform.
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
    Python application code is fully cross-platform; no source changes required.
    Changes confined to: install.sh (OS detection, macOS path, skip service
    registration), AR-003 (add macOS target), NFR-009 (manual start note),
    master design target_platform block.
  related_issues: []

resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    Implement per approved proposal b4e7f1a9. See change document
    change-b4e7f1a9-macos-platform-support.md for full technical detail.
  change_ref: "change-b4e7f1a9"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: "Evaluate platform scope during initial requirements capture."
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - "Run install.sh on macOS; confirm venv created at ~/.local/opt/solax-monitor/"
    - "Confirm no systemd or launchd operations attempted"
    - "Run solax-monitor manually on macOS; confirm normal operation"
    - "Verify AR-003 and NFR-009 updated in requirements document"
    - "Verify master design target_platform block updated"
  verification_results: ""

traceability:
  design_refs:
    - "workspace/design/design-solax-modbus-master.md"
  change_refs:
    - "change-b4e7f1a9"
  test_refs: []

notes: "Approved proposal: workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md"

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

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
