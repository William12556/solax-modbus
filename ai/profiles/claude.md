Created: 2026 March 13

# Implementation Profile: Claude

---

## Table of Contents

- [Overview](<#overview>)
- [Placeholder Mappings](<#placeholder mappings>)
- [Strategic Domain](<#strategic domain>)
- [Tactical Domain](<#tactical domain>)
- [Autonomous Execution Loop](<#autonomous execution loop>)
- [Project Setup](<#project setup>)
- [Version History](<#version history>)

---

## 1. Overview

This profile maps governance abstract placeholders to Claude-based tooling for the solax-modbus project.

| Concern | Implementation |
|---|---|
| Strategic Domain | Claude Desktop |
| Tactical Domain | Claude Code |
| AEL mechanism | Python AEL orchestrator (`ai/ael/`) |

[Return to Table of Contents](<#table of contents>)

---

## 2. Placeholder Mappings

| Placeholder | Resolved Value |
|---|---|
| `<tactical_config>/` | `.claude/` |
| `<skills_dir>/` | `skills/` (within `.claude/`) |
| `<tactical_context>` | `CLAUDE.md` |
| Local context file | `CLAUDE.local.md` |

[Return to Table of Contents](<#table of contents>)

---

## 3. Strategic Domain

**Implementation:** Claude Desktop

Role: planning, governance interpretation, design creation, prompt authoring, validation.

Context file update mechanism: `# key` notation during Claude Code sessions updates `CLAUDE.md` in place.

[Return to Table of Contents](<#table of contents>)

---

## 4. Tactical Domain

**Implementation:** Claude Code

Configuration directory: `.claude/`

Skills directory: `.claude/skills/`

Context file: `CLAUDE.md` at project root (checked into git).

Local context file: `CLAUDE.local.md` at project root (`.gitignore`'d).

**Prerequisites:**
- Anthropic API key configured
- Claude Code installed: `npm install -g @anthropic-ai/claude-code`

[Return to Table of Contents](<#table of contents>)

---

## 5. Autonomous Execution Loop

**Implementation:** Python AEL orchestrator

AEL source: `ai/ael/`

State directory: `.ael/ralph/` (ephemeral, per-task, excluded from git)

**Prerequisites:**
```bash
pip install -r ai/ael/requirements.txt
```

Configure `ai/ael/config.yaml` with inference endpoint and MCP server definitions.

**Invocation (from project root):**
```bash
python ai/ael/src/orchestrator.py --mode loop \
  --task workspace/prompt/prompt-<uuid>-<n>.md
```

**Exit states:**
- `SHIP` — Strategic Domain reviews generated code, proceeds to audit
- `BLOCKED` — Strategic Domain seeds T03 Issue from `RALPH-BLOCKED.md`

[Return to Table of Contents](<#table of contents>)

---

## 6. Project Setup

**.gitignore additions (included in project .gitignore):**
```
# Tactical Domain
CLAUDE.local.md
.claude/settings.json
.claude/commands/
.ael/ralph/
```

**Directory structure additions (within `solax-modbus/`):**
```
├── ai/
│   ├── ael/                  # Python AEL orchestrator
│   └── profiles/
│       └── claude.md         # This file
├── .claude/
│   ├── skills/
│   │   ├── governance/
│   │   ├── testing/
│   │   ├── validation/
│   │   └── audit/
│   └── commands/
├── bin/                      # Project-scoped integration scripts
└── CLAUDE.md                 # Tactical Domain context file
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-13 | Initial document for solax-modbus; Python AEL orchestrator replacing Goose |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
