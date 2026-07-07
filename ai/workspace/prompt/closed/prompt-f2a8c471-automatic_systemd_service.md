```yaml
# T04 Prompt Document
# Automatic Systemd Service Registration

prompt_info:
  id: "prompt-f2a8c471"
  task_type: "code_generation"
  source_ref: "change-f2a8c471"
  target_profile: "claude_code"
  date: "2026-07-02"
  iteration: 1
  coupled_docs:
    change_ref: "change-f2a8c471"
    change_iteration: 1

context:
  purpose: >
    Add automatic systemd service registration to bin/install.sh so a Linux
    deployment starts the monitor on boot without a manually authored unit
    file.
  integration: >
    Modifies only bin/install.sh. No changes to src/solax_modbus/main.py or
    src/solax_modbus/emulator/solax_emulator.py. Existing wheel-resolution,
    venv-creation, and symlink logic must remain functionally unchanged for
    invocations that omit the new flags.
  knowledge_references: []
  constraints:
    - "Linux only. Do not add any macOS or other-OS branching (macOS support was reviewed and rejected — see issue-b4e7f1a9)."
    - "Existing positional argument (version string or wheel path) must continue to work exactly as today."
    - "New flags are optional and must not change behavior when omitted."
    - "Bash, POSIX-compatible where practical; consistent with existing script style (set -e, echo '==> ...' status lines)."

specification:
  description: >
    Extend bin/install.sh with a flag parser for --ip, --port, --unit-id,
    --interval, --serve, --http-port, and --allow (repeatable). When --ip is
    supplied, generate and enable a systemd unit for the solax-monitor
    service after the existing install steps complete.
  requirements:
    functional:
      - "Parse --ip IP (string, required to trigger service creation)"
      - "Parse --port PORT (integer, optional, passed through to solax-monitor --port)"
      - "Parse --unit-id ID (integer, optional, passed through as --unit-id)"
      - "Parse --interval SECONDS (integer, optional, passed through as --interval)"
      - "Parse --serve (flag, optional, passed through as --serve)"
      - "Parse --http-port PORT (integer, optional, passed through as --http-port)"
      - "Parse --allow CIDR (string, repeatable, each occurrence passed through as a separate --allow CIDR)"
      - "If --ip is absent: perform no systemd operations; existing manual-instruction output at end of script is unchanged"
      - "If --ip is present: write /etc/systemd/system/solax-monitor.service, run systemctl daemon-reload, run systemctl enable --now solax-monitor"
      - "Unit generation is unconditional and idempotent: always overwrite the unit file and restart the service when --ip is given, even if the unit already exists"
      - "Update the usage comment block at the top of the script to document the new flags"
    technical:
      language: "Bash"
      version: "POSIX / bash 4+"
      standards:
        - "Preserve set -e; fail loudly on systemctl errors"
        - "Quote all variable expansions, especially in the generated ExecStart line"
        - "No inline shell comments on paste-ready command lines printed to the user"

design:
  architecture: >
    Single-file bash script, additive. Argument parsing happens after the
    existing positional-argument resolution block. Systemd generation is a
    new function or inline block placed after the existing symlink section,
    guarded by an `if [ -n "$IP" ]` check.
  components:
    - name: "parse_service_flags"
      type: "function"
      purpose: "Parse --ip/--port/--unit-id/--interval/--serve/--http-port/--allow from remaining CLI args after the positional argument is consumed."
      interface:
        inputs:
          - name: "$@"
            type: "positional parameters"
            description: "Remaining CLI arguments after version/wheel-path is shifted off"
        outputs:
          type: "shell variables"
          description: "IP, MODBUS_PORT_ARG, UNIT_ID_ARG, INTERVAL_ARG, SERVE_FLAG, HTTP_PORT_ARG, ALLOW_ARGS (array)"
        raises:
          - "Exits 1 with an actionable message on an unrecognized flag"
      logic:
        - "Loop over remaining args with a case statement"
        - "For --allow, append to an array (ALLOW_ARGS+=(\"$2\")) to support repetition"
        - "Shift 1 or 2 per flag depending on whether it takes a value"
    - name: "generate_systemd_unit"
      type: "function"
      purpose: "Write and enable the systemd unit when IP is set"
      interface:
        inputs:
          - name: "IP"
            type: "string"
            description: "Inverter IP address, required"
          - name: "MODBUS_PORT_ARG, UNIT_ID_ARG, INTERVAL_ARG, SERVE_FLAG, HTTP_PORT_ARG, ALLOW_ARGS"
            type: "string / array"
            description: "Optional pass-through flags for ExecStart"
        outputs:
          type: "side effect"
          description: "Writes /etc/systemd/system/solax-monitor.service; runs daemon-reload and enable --now"
        raises:
          - "Propagates systemctl failure via set -e"
      logic:
        - "Build ExecStart string: $VENV_DIR/bin/solax-monitor \"$IP\" plus any optional flags present"
        - "Heredoc the unit file via sudo tee to /etc/systemd/system/solax-monitor.service"
        - "Unit contents: [Unit] Description, After=network-online.target, Wants=network-online.target; [Service] ExecStart, User=root, Restart=on-failure; [Install] WantedBy=multi-user.target"
        - "sudo systemctl daemon-reload"
        - "sudo systemctl enable --now solax-monitor"
        - "Echo service status guidance (systemctl status solax-monitor)"
  dependencies:
    internal: []
    external:
      - "systemd (systemctl) — already assumed present on the Linux target per existing script scope"

data_schema:
  entities: []

error_handling:
  strategy: >
    Rely on `set -e` already present in the script; systemctl failures abort
    the script with the default bash error. No new custom error handling
    required beyond the unrecognized-flag case in parse_service_flags.
  exceptions:
    - exception: "Unrecognized flag"
      condition: "An argument after the positional does not match any known flag"
      handling: "Print 'ERROR: Unknown option: <flag>' and exit 1"
  logging:
    level: "N/A (shell script; uses existing echo '==> ...' convention)"
    format: "echo \"==> ...\""

testing:
  unit_tests: []
  edge_cases:
    - "install.sh run with only the positional arg (no flags) — must behave exactly as before this change"
    - "install.sh --ip 192.168.1.100 run twice in succession — unit file and service state must be identical after each run, no errors"
    - "install.sh <version> --ip 192.168.1.100 --allow 10.0.0.0/24 --allow 192.168.1.0/24 — both --allow values appear as separate --allow flags in ExecStart"
  validation:
    - "systemctl cat solax-monitor shows After=network-online.target and Wants=network-online.target"
    - "systemctl is-enabled solax-monitor reports enabled"

deliverable:
  format_requirements:
    - "Modify bin/install.sh in place"
  files:
    - path: "bin/install.sh"
      content: "Modified in place per design above; do not rewrite unrelated sections (wheel resolution, venv creation, version verification)"

success_criteria:
  - "install.sh with no new flags behaves identically to the pre-change script"
  - "install.sh --ip <ip> generates, enables, and starts solax-monitor.service"
  - "Generated unit includes After=network-online.target and Wants=network-online.target"
  - "Re-running install.sh --ip <ip> is idempotent: no errors, unit regenerated, service remains active"
  - "Usage banner at top of script documents the new flags"

element_registry:
  source: ""
  entries:
    modules: []
    classes: []
    functions: []
    constants: []

notes: >
  Human decisions incorporated: service runs as User=root (accepted risk,
  not to be changed without new approval); unit regeneration is
  unconditional/idempotent on every --ip run (accepted risk of overwriting
  manual edits). Do not add interactive prompting or config-file loading —
  both explicitly declined in change-f2a8c471.
```
