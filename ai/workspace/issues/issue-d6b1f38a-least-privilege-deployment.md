```yaml
# T03 Issue Document
# Least-Privilege Deployment and Install Reliability

issue_info:
  id: "issue-d6b1f38a"
  title: "Least-Privilege Deployment and Install Reliability"
  date: "2026-07-05"
  reporter: "William Watson"
  status: "open"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-d6b1f38a"
    change_iteration: 1

source:
  origin: "user_report"
  test_ref: ""
  description: >
    Deployment of the current release to the Raspberry Pi fails. install.sh
    cannot complete as the admin user, and the operator's root workarounds
    fail at the download step. Root cause is a privilege model that runs the
    installer partly unprivileged and the runtime service as root.

affected_scope:
  components:
    - name: "install.sh"
      file_path: "bin/install.sh"
    - name: "main.py"
      file_path: "src/solax_modbus/main.py"
  designs: []
  version: "0.1.12"

reproduction:
  prerequisites: "Existing install at /opt/solax-monitor with a root-owned venv; run on the Pi (Debian 13 trixie)."
  steps:
    - "As admin: bash install.sh"
    - "As admin: sudo bash install.sh (root workaround)"
  frequency: "always"
  reproducibility_conditions: "Root-owned venv from a prior install; download target on tmpfs /tmp."
  preconditions: ""
  test_data: ""
  error_output: >
    Fault A (admin): pip install -> OSError [Errno 13] Permission denied:
    '/opt/solax-monitor/venv/bin/solax-monitor'. Fault B (root): curl (23)
    client returned ERROR on write of N bytes when writing the wheel to /tmp.

behavior:
  expected: >
    A single documented command installs or updates the monitor cleanly,
    removes the previous installation, registers the service, and runs it
    with the least privilege required.
  actual: >
    admin-invoked install fails because pip cannot overwrite the root-owned
    venv (Fault A). root-invoked install fails because root cannot write the
    wheel to tmpfs /tmp (Fault B). The service, once installed, runs as root.
  impact: "Deployment blocked. Runtime service over-privileged. Interactive admin use of the CLI is coupled to a root-owned log path."
  workaround: "Provide a local wheel and run the whole installer as root; not reliable while the download targets /tmp."

environment:
  python_version: "3.13"
  os: "Debian 13 (trixie), Raspberry Pi Zero 2W"
  dependencies:
    - library: "pymodbus"
      version: "3.11.4"
  domain: "domain_1"

analysis:
  root_cause: >
    Privilege misallocation. The venv is created with sudo (root-owned) but
    pip runs unprivileged, so an admin-invoked install cannot modify the venv
    (Fault A). The systemd service runs User=root though the application needs
    no runtime privilege: Modbus 502 is an outbound client connection and the
    HTTP server binds the unprivileged port 8080. Running as root is the
    source of the root-owned log-file coupling. Separately, root cannot write
    the wheel to tmpfs /tmp while admin can (Fault B); cause unidentified.
  technical_notes: >
    Verified by source inspection: main.py uses ModbusTcpClient(ip, port)
    (outbound) and http-port defaults to 8080; logging.basicConfig opens a
    FileHandler on /opt/solax-monitor/solax_poll.log at import, coupling every
    invocation to that root-owned path. Fault B hypotheses tmpfs-exhaustion,
    file-attribute, and root .curlrc were each falsified by runtime diagnostics
    (df 1% used, lsattr clear, no /root/.curlrc).
  related_issues:
    - issue_ref: "issue-f2a8c471"
      relationship: "related"

resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    See change-d6b1f38a. Dedicated unprivileged system account 'monitor';
    journald-only logging (remove FileHandler); installer runs entirely as
    root (sudo ./install.sh) with the wheel downloaded to a mktemp directory
    off /tmp (sidesteps Fault B); package-level teardown before install;
    explicit --uninstall mode; hardened systemd unit with User=monitor.
  change_ref: "change-d6b1f38a"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: "Separate install-time privilege (root, bounded) from runtime privilege (least). Runtime user owns nothing and writes nothing."
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - "sudo ./install.sh on the Pi completes and removes the prior package cleanly (Fault A resolved)"
    - "Wheel download succeeds when the installer runs as root (Fault B sidestepped via mktemp)"
    - "systemctl show solax-monitor reports User=monitor and the hardening directives"
    - "journalctl -u solax-monitor receives log output; no solax_poll.log is created"
    - "sudo ./install.sh --uninstall stops, disables, and removes the installation"
  verification_results: ""

traceability:
  design_refs: []
  change_refs:
    - "change-d6b1f38a"
  test_refs: []

notes: >
  Fault B (root cannot write tmpfs /tmp) is sidestepped by moving the download
  off /tmp, not diagnosed. Its root cause remains unidentified after three
  falsified hypotheses; deferred by human decision (2026-07-05).

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-05"
    author: "William Watson"
    changes:
      - "Initial issue document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
