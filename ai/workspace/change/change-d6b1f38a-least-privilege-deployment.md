```yaml
# T02 Change Document
# Least-Privilege Deployment and Install Reliability

change_info:
  id: "change-d6b1f38a"
  title: "Least-Privilege Deployment and Install Reliability"
  date: "2026-07-05"
  author: "William Watson"
  status: "approved"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d6b1f38a"
    issue_iteration: 1

source:
  type: "issue"
  reference: "ai/workspace/issues/issue-d6b1f38a-least-privilege-deployment.md"
  description: >
    Re-architect deployment so the installer runs as root and the runtime
    service runs as a dedicated unprivileged account. Resolves the install
    permission failure (Fault A), removes runtime root, and eliminates the
    root-owned log coupling.

scope:
  summary: >
    Introduce a dedicated system account 'monitor'; run the service as that
    account under a hardened systemd unit; switch logging to journald only;
    run install.sh entirely as root with the wheel download moved off /tmp;
    perform a package-level teardown of the previous installation before each
    install; add an explicit --uninstall mode. Linux only.
  affected_components:
    - name: "install.sh"
      file_path: "bin/install.sh"
      change_type: "modify"
    - name: "main.py"
      file_path: "src/solax_modbus/main.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Diagnosing Fault B (root cannot write tmpfs /tmp) — sidestepped, not fixed"
    - "rm -rf of the venv on install — declined; teardown is package-level (pip uninstall)"
    - "Deleting the 'monitor' account on --uninstall — account is preserved"
    - "macOS or any non-systemd init system"
    - "Config-file parameter loading; changes to solax_emulator.py"

rational:
  problem_statement: >
    The venv is root-owned but pip runs unprivileged, so admin installs fail
    (Fault A). The service runs as root though it needs no runtime privilege
    (Modbus 502 is outbound; HTTP binds unprivileged 8080), which also creates
    a root-owned log file that blocks interactive admin use.
  proposed_solution: >
    Runtime least privilege: create system account 'monitor' (nologin, no
    home); own /opt/solax-monitor as root with read/execute for all; run the
    service as User=monitor under a hardened unit. Logging to journald only
    by removing the FileHandler from main.py. Installer runs as root
    (sudo ./install.sh); the wheel is downloaded to a mktemp directory (off
    /tmp, cleaned on exit), which sidesteps Fault B. Before install, stop any
    running service and pip-uninstall the previous package (package-level
    complete removal). Add --uninstall for full purge.
  alternatives_considered:
    - option: "Add sudo only to the pip calls; keep invoking the script as admin"
      reason_rejected: "Leaves the service running as root, perpetuates the log-permission coupling, and does not address runtime least privilege."
    - option: "Run the whole script as root but keep the /tmp download"
      reason_rejected: "Re-triggers Fault B (root cannot write tmpfs /tmp); the download must move off /tmp."
    - option: "rm -rf the venv on every install for environment-level clean removal"
      reason_rejected: "Declined by human (2026-07-05): venv recreation re-installs pymodbus each run (network and time cost on the Pi). Teardown is package-level."
    - option: "Retain file logging under a monitor-writable path"
      reason_rejected: "Reintroduces a managed writable path and the same ownership-coupling defect class; journald removes the requirement entirely."
  benefits:
    - "Fault A resolved: root installer owns the venv it writes"
    - "Runtime least privilege: monitor owns nothing, writes nothing, binds no privileged port"
    - "Log-permission defect eliminated (journald only)"
    - "Deterministic package removal before install; explicit --uninstall"
    - "Fault B avoided without depending on its unidentified cause"
  risks:
    - risk: "Removing the FileHandler drops the on-disk log"
      mitigation: "journald captures StreamHandler output under systemd (journalctl -u solax-monitor); intended behavior."
    - risk: "monitor runs a network HTTP service (0.0.0.0:8080)"
      mitigation: "Unprivileged account, systemd hardening, and the existing RFC1918 source-IP allowlist contain exposure and blast radius."
    - risk: "ProtectSystem=strict blocks any future runtime write and read-only-venv prevents .pyc caching"
      mitigation: ".pyc compiles in memory (negligible); add a ReadWritePaths entry only if a future write path is introduced."
    - risk: "Fault B is sidestepped, not diagnosed"
      mitigation: "Download moved off /tmp to mktemp; residual system-level cause documented in issue-d6b1f38a and deferred."

technical_details:
  current_behavior: >
    install.sh creates the venv with sudo but runs pip unprivileged; reuses an
    existing venv; cleans via pip uninstall only; generates a User=root unit
    when --ip is supplied. main.py logging.basicConfig attaches a StreamHandler
    and a FileHandler on /opt/solax-monitor/solax_poll.log, opened at import.
  proposed_behavior: >
    install.sh runs entirely as root (sudo ./install.sh). It ensures the
    'monitor' system account exists; downloads the wheel (when fetching from
    GitHub) into a mktemp -d directory removed on exit; stops the service if
    active; pip-uninstalls the previous package; installs the new wheel;
    ensures /opt/solax-monitor is readable and executable by all; refreshes the
    /usr/local/bin symlink; and, when --ip is supplied, writes a hardened
    User=monitor unit and enables/starts it. Without --ip, an existing enabled
    service is restarted; the unit file is preserved (Option A). A new
    --uninstall mode stops, disables, and removes the unit, symlink, and
    /opt/solax-monitor, preserving the 'monitor' account. main.py logs to
    journald only (FileHandler removed; StreamHandler retained).
  implementation_approach: >
    1. main.py: remove the FileHandler entry from logging.basicConfig handlers;
       retain StreamHandler.
    2. install.sh: require root; re-exec or exit with guidance if not root.
    3. Ensure account: id monitor || useradd --system --no-create-home
       --shell /usr/sbin/nologin monitor.
    4. Download: when resolving a GitHub wheel, curl -o into a mktemp -d;
       trap-remove the directory on exit. Local-wheel path unchanged.
    5. Teardown: if systemctl is-active --quiet solax-monitor, stop it; then
       pip uninstall -y solax-modbus (tolerate absence).
    6. Install: pip install the wheel (root); chmod -R a+rX /opt/solax-monitor;
       refresh symlink.
    7. Unit (when --ip): [Service] User=monitor, Group=monitor,
       Restart=on-failure, plus NoNewPrivileges=true, ProtectSystem=strict,
       ProtectHome=true, PrivateTmp=true, CapabilityBoundingSet=,
       RestrictAddressFamilies=AF_INET AF_INET6, ProtectKernelTunables=true,
       RestrictNamespaces=true, LockPersonality=true; After/Wants=
       network-online.target; WantedBy=multi-user.target. daemon-reload;
       enable --now.
    8. Without --ip: if the unit exists and is enabled, restart it.
    9. --uninstall: stop, disable, rm unit, daemon-reload, rm symlink,
       rm -rf /opt/solax-monitor; keep the monitor account.
    10. Update the usage banner (root requirement, --uninstall).
  code_changes:
    - component: "install.sh"
      file: "bin/install.sh"
      change_summary: >
        Require root; ensure monitor account; mktemp download; stop-service +
        pip-uninstall teardown; a+rX on the install tree; hardened User=monitor
        unit; --uninstall mode; usage-banner update.
      functions_affected: []
      classes_affected: []
    - component: "main.py"
      file: "src/solax_modbus/main.py"
      change_summary: "Remove the FileHandler from logging.basicConfig; retain StreamHandler (journald capture)."
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "bin/install.sh invocation"
      change_type: "contract"
      details: "Installer now requires root (sudo ./install.sh). Adds --uninstall. Unit runs as User=monitor, superseding the User=root behavior of change-f2a8c471."
      backward_compatible: "no"
    - interface: "runtime logging output"
      change_type: "contract"
      details: "No on-disk log file; output goes to journald via StreamHandler."
      backward_compatible: "no"

dependencies:
  internal: []
  external:
    - library: "systemd"
      version_change: "none"
      impact: "Hardening directives require a systemd version supporting them (present on Debian 13)."
  required_changes: []

testing_requirements:
  test_approach: "Manual execution on the Pi (Debian 13 trixie)."
  test_cases:
    - scenario: "sudo ./install.sh on a Pi with the current broken/root-owned install"
      expected_result: "Previous package removed; new version installed; no permission error (Fault A resolved)."
    - scenario: "sudo ./install.sh fetching from GitHub"
      expected_result: "Wheel downloads into a mktemp dir and installs; no curl (23); temp dir removed on exit."
    - scenario: "sudo ./install.sh --ip 192.168.1.100"
      expected_result: "Unit written with User=monitor and all hardening directives; service active."
    - scenario: "systemctl show solax-monitor"
      expected_result: "User=monitor; NoNewPrivileges, ProtectSystem=strict, PrivateTmp, etc. present."
    - scenario: "Observe logs"
      expected_result: "journalctl -u solax-monitor shows output; /opt/solax-monitor/solax_poll.log is not created."
    - scenario: "sudo ./install.sh (no --ip) with a service already enabled"
      expected_result: "Service stopped, reinstalled, restarted; unit file preserved."
    - scenario: "sudo ./install.sh --uninstall"
      expected_result: "Service stopped/disabled; unit, symlink, and /opt/solax-monitor removed; monitor account retained."
  regression_scope:
    - "Local-wheel install path (positional wheel argument) unchanged except for the root requirement"
    - "--ip flag parsing and ExecStart construction from change-f2a8c471 unchanged except User and hardening"
  validation_criteria:
    - "install.sh exits 0 for install, --ip, and --uninstall cases"
    - "systemctl is-active solax-monitor reports active after --ip install"
    - "id monitor resolves; monitor has a nologin shell"
    - "The monitor user cannot write within /opt/solax-monitor at runtime (ProtectSystem=strict)"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Remove FileHandler in src/solax_modbus/main.py"
      owner: "Tactical Domain (Claude Code)"
    - step: "Implement root model, monitor account, mktemp download, teardown, hardened unit, and --uninstall in bin/install.sh"
      owner: "Tactical Domain (Claude Code)"
    - step: "Code review (P08)"
      owner: "Strategic Domain"
    - step: "Test (P06)"
      owner: "Strategic Domain"
  rollback_procedure: >
    Restore bin/install.sh and src/solax_modbus/main.py from git history.
    To revert runtime: regenerate the prior User=root unit and userdel monitor
    if desired.
  deployment_notes: >
    First fixed install on the Pi self-heals the current half-uninstalled
    state: the root installer overwrites the orphaned root-owned entry point.
    Documentation (README.md, docs/guide.md) requires a separate,
    non-protocol update: sudo ./install.sh, journalctl, and --uninstall.

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
    - change_ref: "change-f2a8c471"
      relationship: "supersedes the User=root service decision (now User=monitor + hardening)"
  related_issues:
    - issue_ref: "issue-d6b1f38a"
      relationship: "source"

notes: >
  Human decisions (2026-07-05): runtime account 'monitor'; journald-only
  logging; sudo ./install.sh with mktemp download; systemd unit preservation
  (Option A); --uninstall included; full hardening set (baseline four plus
  CapabilityBoundingSet, RestrictAddressFamilies, ProtectKernelTunables,
  RestrictNamespaces, LockPersonality). Teardown is package-level (pip
  uninstall), not rm -rf of the venv. Fault B sidestepped.

version_history:
  - version: "1.0"
    date: "2026-07-05"
    author: "William Watson"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
