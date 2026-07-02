```yaml
# T02 Change Document
# Automatic Systemd Service Registration

change_info:
  id: "change-f2a8c471"
  title: "Automatic Systemd Service Registration"
  date: "2026-07-02"
  author: "William Watson"
  status: "approved"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f2a8c471"
    issue_iteration: 1

source:
  type: "issue"
  reference: "ai/workspace/issues/issue-f2a8c471-automatic-systemd-service.md"
  description: >
    Extend install.sh to generate, enable, and start a systemd unit
    automatically when the operator supplies the inverter IP and optional
    run parameters as command-line flags.

scope:
  summary: >
    Add command-line flags to install.sh for inverter IP and run parameters.
    When --ip is supplied, generate a systemd unit, register it with
    network-boot ordering, and enable/start it. Linux only; no macOS scope.
  affected_components:
    - name: "install.sh"
      file_path: "bin/install.sh"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "macOS support (see issue-b4e7f1a9, rejected)"
    - "launchd or any non-systemd init system"
    - "Interactive prompting for parameters"
    - "Config-file-based parameter loading in main.py"
    - "Changes to main.py or solax_emulator.py (neither requires modification)"

rational:
  problem_statement: >
    install.sh installs the package and a PATH symlink but performs no
    systemd operations. Unattended/boot-time deployment requires a manually
    authored unit file.
  proposed_solution: >
    Add flags --ip (required to trigger service creation), --port,
    --unit-id, --interval, --serve, --http-port, --allow (repeatable) to
    install.sh. When --ip is present, generate
    /etc/systemd/system/solax-monitor.service with ExecStart built from the
    supplied flags, run daemon-reload and enable --now. Omitting --ip
    preserves current behavior unchanged (manual-instruction path).
  alternatives_considered:
    - option: "Interactive prompts during install"
      reason_rejected: "Human declined; CLI flags preferred for scriptability and non-interactive deployment."
    - option: "Config file consumed by main.py"
      reason_rejected: "Human declined; out of scope. Parameters are baked into ExecStart instead, keeping main.py unchanged."
  benefits:
    - "Unattended Linux deployment without manual unit-file authoring"
    - "No main.py or emulator source changes required"
  risks:
    - risk: "Service runs as User=root"
      mitigation: "Accepted by human decision (2026-07-02). Not mitigated further in this iteration."
    - risk: "Unit file is regenerated unconditionally on every install run with --ip, overwriting any manual edits to the unit file"
      mitigation: "Accepted by human decision (2026-07-02); documented behavior, not silently avoided."

technical_details:
  current_behavior: >
    install.sh performs no systemd operations on any platform. It symlinks
    the installed binary into /usr/local/bin/ and prints a message instructing
    manual unit-file creation.
  proposed_behavior: >
    install.sh accepts new optional flags alongside the existing positional
    version/wheel-path argument: --ip IP, --port PORT, --unit-id ID,
    --interval SECONDS, --serve, --http-port PORT, --allow CIDR (repeatable).
    When --ip is supplied: install.sh writes
    /etc/systemd/system/solax-monitor.service with:
      - ExecStart=<venv>/bin/solax-monitor <ip> [--port P] [--unit-id U]
        [--interval N] [--serve] [--http-port P] [--allow C ...]
      - User=root
      - Restart=on-failure
      - After=network-online.target
      - Wants=network-online.target
    then runs `systemctl daemon-reload` and `systemctl enable --now
    solax-monitor`. This is unconditional and idempotent: re-running
    install.sh with --ip regenerates and overwrites the unit file and
    restarts the service. When --ip is omitted, no systemd operations occur;
    existing manual-instruction output is unchanged.
  implementation_approach: >
    1. Add flag parser to install.sh, coexisting with the existing positional
       version/wheel-path argument (flags parsed via loop over remaining
       args after the positional is consumed).
    2. Validate --ip is a syntactically plausible address/hostname; no
       further validation performed.
    3. Build ExecStart command string from supplied flags, quoting values.
    4. Write unit file via heredoc to /etc/systemd/system/solax-monitor.service
       (requires sudo, consistent with existing sudo usage in the script).
    5. Run systemctl daemon-reload; systemctl enable --now solax-monitor.
    6. Print service status/next-steps instead of the manual-instruction
       block, only when --ip was supplied.
    7. Update usage banner in the script header to document new flags.
  code_changes:
    - component: "install.sh"
      file: "bin/install.sh"
      change_summary: >
        New flag parser; systemd unit generation and enable/start block,
        conditional on --ip; usage banner update.
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "bin/install.sh command-line arguments"
      change_type: "signature"
      details: "Adds optional --ip/--port/--unit-id/--interval/--serve/--http-port/--allow flags after the existing positional argument."
      backward_compatible: "yes"

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Manual execution of install.sh on a Linux host (or Pi)."
  test_cases:
    - scenario: "Run install.sh --ip 192.168.1.100 with a valid wheel"
      expected_result: "Unit file created, enabled, active; ExecStart contains the given IP and defaults for unspecified flags"
    - scenario: "Run install.sh --ip 192.168.1.100 --port 1502 --http-port 9000 --serve"
      expected_result: "ExecStart reflects all supplied flags"
    - scenario: "Re-run install.sh --ip ... a second time"
      expected_result: "Unit file regenerated identically; service restarted; no errors"
    - scenario: "Run install.sh with no flags (legacy invocation)"
      expected_result: "Behavior unchanged from prior release: symlink only, manual-instruction message printed, no systemd operations"
  regression_scope:
    - "Existing wheel resolution, venv creation, and symlink logic unchanged"
  validation_criteria:
    - "systemctl is-active solax-monitor reports active after --ip install"
    - "systemctl show solax-monitor shows After=network-online.target"
    - "install.sh exits 0 in all four test cases"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Implement flag parsing and systemd generation in bin/install.sh"
      owner: "Tactical Domain (Claude Code)"
    - step: "Code review"
      owner: "Strategic Domain"
  rollback_procedure: "Restore install.sh from git history; systemctl disable --now solax-monitor && rm /etc/systemd/system/solax-monitor.service"
  deployment_notes: "No impact on existing installations that do not use --ip."

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-b4e7f1a9"
      relationship: "related, raised during same review; unrelated concern"
  related_issues:
    - issue_ref: "issue-f2a8c471"
      relationship: "source"

notes: "Raised during review of change-b4e7f1a9 (macOS support, rejected)."

version_history:
  - version: "1.0"
    date: "2026-07-02"
    author: "William Watson"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
