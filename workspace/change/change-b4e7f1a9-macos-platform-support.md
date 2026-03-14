```yaml
# T02 Change Document
# macOS Full Platform Support

change_info:
  id: "change-b4e7f1a9"
  title: "macOS Full Platform Support"
  date: "2026-03-14"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b4e7f1a9"
    issue_iteration: 1

source:
  type: "enhancement"
  reference: "workspace/issues/issue-b4e7f1a9-macos-platform-support.md"
  description: >
    Extend deployment target to include macOS as a fully supported production
    platform. Approved proposal: workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md

scope:
  summary: >
    Add macOS support to install.sh via OS detection and platform-appropriate
    install path. Update requirements (AR-003, NFR-009) and master design
    (target_platform block). No Python source code changes required.
  affected_components:
    - name: "install.sh"
      file_path: "install.sh"
      change_type: "modify"
  affected_designs:
    - design_ref: "workspace/design/design-solax-modbus-master.md"
      sections:
        - "Target Platform"
        - "Development Environment"
    - design_ref: "workspace/requirements/requirements-solax-modbus-master.md"
      sections:
        - "AR-003"
        - "NFR-009"
  out_of_scope:
    - "Python source code (main.py, solax_emulator.py)"
    - "build.sh (already platform-agnostic)"
    - "macOS automatic launch (launchd)"
    - "Windows support"

rational:
  problem_statement: >
    install.sh targeted Linux-only paths (/opt/solax-monitor/) and registered
    a systemd service. Neither is valid on macOS. The application Python code
    is fully cross-platform but deployment was blocked on macOS.
  proposed_solution: >
    Added OS detection to install.sh. On macOS: use ~/.local/opt/solax-monitor/,
    skip service registration, print manual run instructions. Updated
    requirements and design documents to reflect macOS as a supported target.
  alternatives_considered:
    - option: "Separate install-macos.sh script"
      reason_rejected: "Duplication of logic; single script with OS detection is simpler to maintain"
    - option: "Homebrew formula"
      reason_rejected: "Out of scope; adds complexity beyond stated requirement"
  benefits:
    - "macOS workstations and Mac mini usable as production monitoring hosts"
    - "Development and production platform unified; reduced deployment friction"
    - "No-sudo installation on macOS"
  risks:
    - risk: "python3 not in PATH on fresh macOS"
      mitigation: "install.sh validates python3 availability with actionable error"
    - risk: "~/.local/opt/ directory absent"
      mitigation: "install.sh creates with mkdir -p"

technical_details:
  current_behavior: >
    install.sh hardcoded /opt/solax-monitor/ and registered a systemd service.
    Failed on macOS at both path creation and service registration.
  proposed_behavior: >
    install.sh detects OS via `uname -s`. On Linux: existing behaviour
    unchanged. On macOS: installs venv to ~/.local/opt/solax-monitor/,
    skips service registration, prints manual run command.
  implementation_approach: >
    1. OS detection block at top of install.sh via uname -s.
    2. INSTALL_DIR and VENV_DIR set based on detected OS.
    3. First-time venv creation uses sudo on Linux, no sudo on macOS.
    4. systemd block replaced with Linux-only conditional.
    5. macOS completion message with manual run instructions added.
    6. python3 availability check added for both platforms.
    7. AR-003 updated in requirements document.
    8. NFR-009 updated in requirements document.
    9. target_platforms block updated in master design.
  code_changes:
    - component: "install.sh"
      file: "install.sh"
      change_summary: >
        OS detection; platform-specific INSTALL_DIR/VENV_DIR; conditional
        venv creation (sudo Linux / no-sudo macOS); conditional systemd
        registration; python3 validation; macOS completion output.
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Manual execution of install.sh on macOS and Linux hosts"
  test_cases:
    - scenario: "Run install.sh on macOS with valid wheel"
      expected_result: "venv created at ~/.local/opt/solax-monitor/; no systemd operations; run command printed"
    - scenario: "Run install.sh on Linux with valid wheel"
      expected_result: "Existing behaviour unchanged; venv at /opt/solax-monitor/; systemd service registered"
    - scenario: "Run install.sh on macOS without python3 in PATH"
      expected_result: "Actionable error message; non-zero exit"
    - scenario: "Run solax-monitor manually on macOS after install"
      expected_result: "Monitor connects and displays telemetry normally"
  regression_scope:
    - "Linux install path and systemd registration unchanged"
    - "Monitor functional behaviour unchanged on both platforms"
  validation_criteria:
    - "install.sh exits 0 on macOS with valid wheel"
    - "venv present at ~/.local/opt/solax-monitor/ after macOS install"
    - "No systemd commands executed on macOS"
    - "AR-003 lists macOS as supported target"
    - "NFR-009 notes manual start on macOS"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Modify install.sh"
      owner: "Strategic Domain"
    - step: "Update AR-003 in requirements-solax-modbus-master.md"
      owner: "Strategic Domain"
    - step: "Update NFR-009 in requirements-solax-modbus-master.md"
      owner: "Strategic Domain"
    - step: "Update target_platforms block in design-solax-modbus-master.md"
      owner: "Strategic Domain"
  rollback_procedure: "Restore install.sh from git history"
  deployment_notes: "No deployment impact on existing Linux installations"

verification:
  implemented_date: "2026-03-14"
  implemented_by: "Strategic Domain"
  verification_date: ""
  verified_by: ""
  test_results: "Pending manual verification on macOS and Linux hosts"
  issues_found: []

traceability:
  design_updates:
    - design_ref: "workspace/design/design-solax-modbus-master.md"
      sections_updated:
        - "Target Platform"
        - "Development Environment"
      update_date: "2026-03-14"
    - design_ref: "workspace/requirements/requirements-solax-modbus-master.md"
      sections_updated:
        - "AR-003"
        - "NFR-009"
      update_date: "2026-03-14"
  related_changes: []
  related_issues:
    - issue_ref: "issue-b4e7f1a9"
      relationship: "source"

notes: "Approved proposal: workspace/proposal/proposal-b4e7f1a9-macos-platform-support.md"

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

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
