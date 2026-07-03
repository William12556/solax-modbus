```yaml
# T04 Prompt Document
# Relocate SolaxEmulator source out of the solax_modbus package tree

prompt_info:
  id: "prompt-d7f4a9c2"
  task_type: "refactor"
  source_ref: "design-c2b3c4d5"
  target_profile: "claude_code"
  date: "2026-07-03"
  iteration: 1

context:
  purpose: >
    Move the emulator from src/solax_modbus/emulator/ to src/tools/emulator/,
    outside the solax_modbus package. The emulator has no import dependency
    on solax_modbus and no test depends on it being package-importable;
    package membership was structural coincidence. This corrects a
    documentation contradiction: docs/guide.md instructed
    `python -m solax_modbus.emulator.solax_emulator`, which requires a
    package install the guide never specified, causing ModuleNotFoundError
    for users running the emulator from a bare venv.
  integration: >
    docs/guide.md §6.2 and all active governance documents (design-c2b3c4d5,
    design-8f3a1b2c, design-solax-modbus-master.md, name registry,
    requirements, traceability matrix, test-46d32423) have already been
    updated to reference src/tools/emulator/solax_emulator.py. This prompt
    performs the corresponding source-side move only.
  knowledge_references:
    - "ai/workspace/design/design-c2b3c4d5-component_protocol_emulator.md (v1.5)"
  constraints:
    - "solax_emulator.py content is unchanged — relocate the file, do not regenerate it"
    - "No pyproject.toml change: src/solax_modbus/emulator/ has no __init__.py, so [tool.setuptools.packages.find] never discovered it as a package; nothing in pyproject.toml references the emulator path. Verify this remains true after the move — if any reference exists, flag it rather than editing package configuration unilaterally"
    - "Do not modify solax_emulator.py's contents"

specification:
  description: >
    File relocation and one new stub file. No functional code changes.
  requirements:
    functional:
      - "Create directory src/tools/emulator/"
      - "Move src/solax_modbus/emulator/solax_emulator.py to src/tools/emulator/solax_emulator.py, content unchanged"
      - "Create src/tools/emulator/README.md with the stub content specified in deliverable.files"
      - "Remove src/solax_modbus/emulator/ (including old README.md and __pycache__)"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "No code changes to solax_emulator.py"

design:
  architecture: "File relocation, no structural code change"
  components:
    - name: "emulator relocation"
      type: "module"
      purpose: "Decouple emulator from solax_modbus package"
      logic:
        - "mkdir -p src/tools/emulator/"
        - "git mv src/solax_modbus/emulator/solax_emulator.py src/tools/emulator/solax_emulator.py (preserve history if using git mv; otherwise move + git add)"
        - "Write src/tools/emulator/README.md per deliverable.files"
        - "Remove src/solax_modbus/emulator/ directory entirely (old README.md, __pycache__)"
        - "Confirm src/solax_modbus/emulator/ no longer exists"
        - "Confirm src/tools/emulator/solax_emulator.py is byte-identical to the pre-move version"
  dependencies:
    internal: []
    external: []

testing:
  validation:
    - "python3 src/tools/emulator/solax_emulator.py --port 5020 starts without ModuleNotFoundError"
    - "No references to src/solax_modbus/emulator/ remain in src/ or pyproject.toml"

deliverable:
  format_requirements:
    - "Perform the move; do not regenerate solax_emulator.py from this prompt"
  files:
    - path: "src/tools/emulator/solax_emulator.py"
      content: "(unchanged — relocated from src/solax_modbus/emulator/solax_emulator.py)"
    - path: "src/tools/emulator/README.md"
      content: |
        # Solax Inverter Modbus TCP Emulator

        Standalone Modbus TCP server emulating a Solax X3 Hybrid 6.0-D
        inverter for offline development and testing. Requires only
        `pymodbus` — no project package install.

        Full usage, register map, and behavior: see
        [docs/guide.md §6.2](<../../../docs/guide.md#62-emulator>).

        ```bash
        pip install pymodbus
        python3 solax_emulator.py --port 5020
        ```

        ---

        Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

success_criteria:
  - "src/solax_modbus/emulator/ no longer exists"
  - "src/tools/emulator/solax_emulator.py exists, content unchanged"
  - "src/tools/emulator/README.md exists with stub content"
  - "Emulator runs via python3 src/tools/emulator/solax_emulator.py --port 5020"

notes: >
  Documentation (docs/guide.md, all ai/workspace/ design and governance
  documents) already reflects the new path — this prompt is source-only.
  Do not edit any ai/workspace/ or docs/ files.
```
