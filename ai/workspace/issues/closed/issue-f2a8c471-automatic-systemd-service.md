```yaml
# T03 Issue Document
# Automatic Systemd Service Registration

issue_info:
  id: "issue-f2a8c471"
  title: "Automatic Systemd Service Registration"
  date: "2026-07-02"
  reporter: "William Watson"
  status: "resolved"
  severity: "medium"
  type: "requirement_change"
  iteration: 1
  coupled_docs:
    change_ref: "change-f2a8c471"
    change_iteration: 1

source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Human-requested enhancement. install.sh should be capable of registering
    and starting a systemd service automatically at install time, rather than
    requiring the operator to create a unit file manually.

affected_scope:
  components:
    - name: "install.sh"
      file_path: "bin/install.sh"
  designs: []
  version: "0.1.0"

reproduction:
  prerequisites: "Run bin/install.sh on a Linux (Debian/Raspberry Pi) host"
  steps:
    - "Run ./install.sh [version|wheel-path]"
    - "Installation completes; symlink created"
    - "Script prints: 'To register as a systemd service, create a unit file manually.'"
  frequency: "always"
  reproducibility_conditions: "Any Linux host"
  preconditions: ""
  test_data: ""
  error_output: ""

behavior:
  expected: >
    install.sh, given the inverter IP and optional run parameters as
    command-line flags, generates and enables a systemd unit automatically,
    so the monitor starts on boot without manual unit-file authoring.
  actual: >
    install.sh performs no systemd operations. The operator must write the
    unit file by hand after installation.
  impact: "Manual, error-prone step required for unattended/boot-time deployment."
  workaround: "Operator writes a systemd unit file manually, as instructed."

environment:
  python_version: "3.9+"
  os: "Linux (Debian 12 / Raspberry Pi OS / trixie)"
  dependencies: []
  domain: "domain_1"

analysis:
  root_cause: >
    install.sh was never extended beyond package installation and PATH
    symlinking; service registration was left as an out-of-scope manual step.
  technical_notes: >
    Raised during review of issue-b4e7f1a9, which incorrectly assumed systemd
    registration already existed. Confirmed by source inspection that it does
    not. This issue is unrelated to macOS and does not depend on
    issue-b4e7f1a9's resolution.
  related_issues:
    - issue_ref: "issue-b4e7f1a9"
      relationship: "related"

resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    See change-f2a8c471 for full technical detail: new --ip/--port/--unit-id/
    --interval/--serve/--http-port/--allow flags on install.sh; systemd unit
    generated and enabled when --ip is supplied.
  change_ref: "change-f2a8c471"
  resolved_date: "2026-07-07"
  resolved_by: "William Watson"
  fix_description: >
    Confirmed present in bin/install.sh: --ip flag parsing, ExecStart
    construction, systemctl enable --now. Unit User directive superseded
    from root to monitor by change-d6b1f38a (least-privilege deployment).

verification:
  verified_date: "2026-07-07"
  verified_by: "William Watson"
  test_results: "Source-verified: bin/install.sh contains --ip parsing, unit generation, systemctl enable --now."
  closure_notes: "User=root superseded by User=monitor (change-d6b1f38a); flag parsing and unit generation otherwise as specified."

prevention:
  preventive_measures: "None specific; standard scope-definition practice applies."
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - "Run install.sh --ip <inverter-ip> on Linux; confirm unit file created and enabled"
    - "Run systemctl status solax-monitor; confirm active and correct ExecStart"
    - "Reboot host; confirm service starts after network is online"
    - "Run install.sh without --ip; confirm behavior unchanged from prior release"
  verification_results: "Confirmed by direct source inspection of bin/install.sh, 2026-07-07."

traceability:
  design_refs: []
  change_refs:
    - "change-f2a8c471"
  related_changes:
    - change_ref: "change-d6b1f38a"
      relationship: "supersedes the User=root unit directive with User=monitor"
  test_refs: []

notes: "Raised during review of issue-b4e7f1a9 (macOS support, rejected). This concern is independent."

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-02"
    author: "William Watson"
    changes:
      - "Initial issue document"
  - version: "1.1"
    date: "2026-07-07"
    author: "William Watson"
    changes:
      - "Status resolved; source-verified against bin/install.sh; noted User=root superseded by User=monitor (change-d6b1f38a); closed"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
