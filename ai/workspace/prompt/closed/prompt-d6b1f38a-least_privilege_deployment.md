```yaml
# T04 Prompt Document
# Least-Privilege Deployment and Install Reliability

prompt_info:
  id: "prompt-d6b1f38a"
  task_type: "code_generation"
  source_ref: "change-d6b1f38a"
  target_profile: "claude_code"
  date: "2026-07-05"
  iteration: 1
  coupled_docs:
    change_ref: "change-d6b1f38a"
    change_iteration: 1

context:
  purpose: >
    Move the monitor to a least-privilege deployment: run the installer as
    root and the service as a dedicated unprivileged account, log to journald,
    and make installation reliable and completely self-cleaning.
  integration: >
    Modifies bin/install.sh and src/solax_modbus/main.py only. No changes to
    src/tools/emulator/solax_emulator.py or the presentation server. The --ip
    flag parsing and ExecStart construction added in change-f2a8c471 are
    retained; only User and hardening directives change.
  knowledge_references: []
  constraints:
    - "Linux only. No macOS or other-OS branching."
    - "Installer must run as root; if not root, exit 1 with guidance to use sudo. Do not silently self-elevate per command."
    - "Teardown is package-level: stop the service and pip uninstall. Do not rm -rf the venv on install."
    - "Do not delete the 'monitor' account on --uninstall."
    - "Bash, consistent with existing script style (set -e, echo '==> ...'). No inline comments on any paste-ready command lines printed to the user."
    - "Do not diagnose or attempt to work around Fault B beyond moving the download off /tmp."

specification:
  description: >
    Edit main.py to log to journald only. Edit install.sh to require root,
    ensure a 'monitor' system account, download wheels to a mktemp directory,
    tear down the previous package before install, harden the systemd unit
    with User=monitor, and add an --uninstall mode.
  requirements:
    functional:
      - "main.py: remove the FileHandler entry from logging.basicConfig handlers; retain StreamHandler. No other logging change."
      - "install.sh: if effective UID is not 0, print an actionable message ('Run as root: sudo ./install.sh') and exit 1."
      - "install.sh: ensure account exists — id monitor >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin monitor."
      - "install.sh (GitHub wheel path only): download the wheel with curl -o into a directory from mktemp -d; register a trap to rm -rf that directory on EXIT. The local-wheel positional path must not use mktemp."
      - "install.sh: teardown before install — if systemctl is-active --quiet solax-monitor, systemctl stop solax-monitor; then run the venv pip: '$VENV_DIR/bin/pip' uninstall -y solax-modbus (tolerate a missing package)."
      - "install.sh: install the wheel with the venv pip (running as root); then chmod -R a+rX /opt/solax-monitor so the monitor account can read and execute the venv."
      - "install.sh: retain the existing version verification and /usr/local/bin symlink refresh."
      - "install.sh: when --ip is supplied, generate /etc/systemd/system/solax-monitor.service with User=monitor and the hardening directives listed in the design, then daemon-reload and enable --now."
      - "install.sh: when --ip is absent, if the unit exists and is enabled, restart the service; do not remove or rewrite the unit file (Option A: preserve)."
      - "install.sh: add --uninstall — systemctl stop and disable solax-monitor (tolerate absence), rm -f the unit file, daemon-reload, rm -f the /usr/local/bin/solax-monitor symlink, rm -rf /opt/solax-monitor; do NOT remove the monitor account; then exit 0."
      - "install.sh: update the usage banner to state the root requirement and document --uninstall."
    technical:
      language: "Bash / Python"
      version: "bash 4+ / Python 3.13"
      standards:
        - "Preserve set -e; fail loudly on systemctl and pip errors"
        - "Quote all variable expansions, especially in the generated ExecStart line"
        - "Keep the mktemp trap scoped so it does not remove a user-supplied local wheel"

design:
  architecture: >
    Single-file bash installer, additive and modifying; one-line handler-list
    edit in main.py. Root check runs first. Service teardown precedes install;
    unit generation and the --uninstall branch are guarded blocks.
  components:
    - name: "logging.basicConfig (main.py)"
      type: "module"
      purpose: "Emit logs to stdout/stderr for journald capture; no file handler."
      interface:
        inputs: []
        outputs:
          type: "side effect"
          description: "handlers=[logging.StreamHandler()]"
        raises: []
      logic:
        - "Delete the logging.FileHandler('/opt/solax-monitor/solax_poll.log') list element"
        - "Leave level, format, and StreamHandler unchanged"
    - name: "require_root (install.sh)"
      type: "function"
      purpose: "Abort unless run as root."
      interface:
        inputs: []
        outputs:
          type: "side effect"
          description: "Exit 1 with guidance if EUID != 0"
        raises: []
      logic:
        - "[ \"$(id -u)\" -eq 0 ] || { echo 'ERROR: run as root: sudo ./install.sh'; exit 1; }"
    - name: "ensure_monitor_user (install.sh)"
      type: "function"
      purpose: "Create the unprivileged runtime account if absent."
      interface:
        inputs: []
        outputs:
          type: "side effect"
          description: "Creates system user 'monitor' (nologin, no home)"
        raises: []
      logic:
        - "id monitor >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin monitor"
    - name: "teardown_previous (install.sh)"
      type: "function"
      purpose: "Package-level removal of the prior installation."
      interface:
        inputs: []
        outputs:
          type: "side effect"
          description: "Stops the service if active; pip-uninstalls solax-modbus"
        raises: []
      logic:
        - "systemctl is-active --quiet solax-monitor && systemctl stop solax-monitor || true"
        - "\"$VENV_DIR/bin/pip\" uninstall -y solax-modbus 2>/dev/null || true"
    - name: "generate_systemd_unit (install.sh)"
      type: "function"
      purpose: "Write and enable the hardened unit when --ip is supplied."
      interface:
        inputs:
          - name: "IP and existing optional pass-through flags"
            type: "string / array"
            description: "ExecStart construction as in change-f2a8c471"
        outputs:
          type: "side effect"
          description: "Writes the unit; daemon-reload; enable --now"
        raises:
          - "Propagates systemctl failure via set -e"
      logic:
        - "[Unit] Description; After=network-online.target; Wants=network-online.target"
        - "[Service] ExecStart=<venv>/bin/solax-monitor \"$IP\" [flags]; User=monitor; Group=monitor; Restart=on-failure"
        - "[Service] NoNewPrivileges=true; ProtectSystem=strict; ProtectHome=true; PrivateTmp=true"
        - "[Service] CapabilityBoundingSet=; RestrictAddressFamilies=AF_INET AF_INET6; ProtectKernelTunables=true; RestrictNamespaces=true; LockPersonality=true"
        - "[Install] WantedBy=multi-user.target"
        - "systemctl daemon-reload; systemctl enable --now solax-monitor"
    - name: "uninstall_mode (install.sh)"
      type: "function"
      purpose: "Full purge of the installation, preserving the account."
      interface:
        inputs: []
        outputs:
          type: "side effect"
          description: "Removes unit, symlink, and /opt/solax-monitor"
        raises: []
      logic:
        - "systemctl stop solax-monitor 2>/dev/null || true; systemctl disable solax-monitor 2>/dev/null || true"
        - "rm -f /etc/systemd/system/solax-monitor.service; systemctl daemon-reload"
        - "rm -f /usr/local/bin/solax-monitor; rm -rf /opt/solax-monitor"
        - "echo '==> Uninstalled. Account monitor retained.'; exit 0"
  dependencies:
    internal: []
    external:
      - "systemd (systemctl), useradd — present on the Debian 13 target"

data_schema:
  entities: []

error_handling:
  strategy: >
    Rely on the existing set -e. Root check and unknown-flag handling exit 1
    with actionable messages. Teardown tolerates an absent service/package.
  exceptions:
    - exception: "Not root"
      condition: "id -u != 0"
      handling: "Print guidance; exit 1"
    - exception: "Unknown flag"
      condition: "Unrecognized argument"
      handling: "Print 'ERROR: Unknown option: <flag>'; exit 1"
  logging:
    level: "N/A (shell); echo '==> ...' convention"
    format: "echo \"==> ...\""

testing:
  unit_tests: []
  edge_cases:
    - "sudo ./install.sh on the current broken Pi state — completes; orphaned root-owned entry point overwritten"
    - "./install.sh without sudo — exits 1 with guidance; no changes made"
    - "sudo ./install.sh <local-wheel> — mktemp trap must not delete the user's wheel"
    - "sudo ./install.sh --uninstall then sudo ./install.sh --ip <ip> — clean reinstall; monitor account reused"
  validation:
    - "systemctl cat solax-monitor shows User=monitor and all nine hardening directives"
    - "journalctl -u solax-monitor shows output; no /opt/solax-monitor/solax_poll.log exists"
    - "id monitor resolves with a nologin shell"

deliverable:
  format_requirements:
    - "Modify both files in place; do not rewrite unrelated sections"
  files:
    - path: "src/solax_modbus/main.py"
      content: "Remove the FileHandler list element from logging.basicConfig; retain StreamHandler"
    - path: "bin/install.sh"
      content: "Root requirement, monitor account, mktemp download, teardown, a+rX, hardened User=monitor unit, --uninstall, usage banner — per design above"

success_criteria:
  - "main.py creates no log file; logs reach journald under systemd"
  - "sudo ./install.sh removes the previous package and installs cleanly (Fault A resolved)"
  - "GitHub wheel download uses mktemp and succeeds as root (Fault B sidestepped)"
  - "Generated unit runs as User=monitor with the nine hardening directives"
  - "--ip regenerates the unit; no --ip preserves the unit and restarts an enabled service"
  - "--uninstall removes unit, symlink, and /opt/solax-monitor; monitor account retained"
  - "Non-root invocation exits 1 without side effects"

element_registry:
  source: ""
  entries:
    modules: []
    classes: []
    functions: []
    constants: []

notes: >
  Human decisions (2026-07-05): account 'monitor'; journald-only; sudo
  ./install.sh; mktemp download off /tmp; Option A unit preservation;
  --uninstall included; full nine-directive hardening set. Teardown is
  package-level (pip uninstall), NOT rm -rf of the venv. Do not delete the
  monitor account on uninstall. Retain change-f2a8c471 flag parsing and
  ExecStart logic; change only User and hardening. Do not add interactive
  prompting or config-file loading.
```
