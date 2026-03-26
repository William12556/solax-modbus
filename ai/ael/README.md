# AEL — Autonomous Execution Loop

---

## Table of Contents

- [Overview](<#overview>)
- [Structure](<#structure>)
- [Requirements](<#requirements>)
- [Installation](<#installation>)
- [Configuration](<#configuration>)
- [Usage](<#usage>)
- [Recipes](<#recipes>)
- [Testing](<#testing>)
- [Version History](<#version history>)

---

## Overview

The AEL orchestrator is a standalone Python tool loop implementing the Ralph Loop pattern. It connects directly to MCP servers, sends tool definitions to an oMLX inference endpoint, parses model tool calls in both OpenAI and Mistral plain-text formats, dispatches tools, injects results into message history, and iterates until the model produces a response containing no tool calls.

[Return to Table of Contents](<#table of contents>)

---

## Structure

```
ael/
├── config.yaml          # Inference endpoint, MCP server definitions, loop control
├── requirements.txt     # Python dependencies
├── recipes/
│   ├── ralph-work.yaml  # Worker role system prompt
│   └── ralph-review.yaml # Reviewer role system prompt
└── src/
    ├── orchestrator.py  # Main loop and CLI entry point (--mode worker|reviewer|loop|reset)
    ├── budget.py        # Context budget calculator (run before authoring T04 prompts)
    ├── mcp_client.py    # MCP stdio connection and tool dispatch
    └── parser.py        # Mistral [TOOL_CALLS] plain-text parser
```

[Return to Table of Contents](<#table of contents>)

---

## Requirements

- Python 3.11+
- oMLX running on `http://127.0.0.1:8000`
- MCP servers configured in `config.yaml`

[Return to Table of Contents](<#table of contents>)

---

## Installation

Install dependencies into the project virtual environment:

```bash
pip install -r ai/ael/requirements.txt
```

[Return to Table of Contents](<#table of contents>)

---

## Configuration

Edit `ai/ael/config.yaml`:

```yaml
omlx:
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "local"
  default_model: "<model-name>"

mcp_servers:
  filesystem:
    command: "/usr/local/bin/npx"
    args:
      - "-y"
      - "@j0hanz/filesystem-mcp@latest"
      - "/Users/williamwatson/Documents/GitHub/solax-modbus"
    env:
      PATH: "/opt/homebrew/opt/node@24/bin:/usr/local/bin:/usr/bin:/bin"

loop:
  max_iterations: 10
  state_dir: ".ael/ralph"

context:
  models_dir: "~/ai-models"   # set to your local model storage path
  context_window: null        # null = read from model config.json on disk
  budget_warn_pct: 0.80
  budget_abort_pct: 0.95
```

**`context.models_dir`** must be updated to point to your local model storage directory after deploying from skel. `budget.py` searches this directory for the model's `config.json` to determine the context window size. If your model is remote or the path cannot be resolved, set `context.context_window` to an explicit integer value instead.

[Return to Table of Contents](<#table of contents>)

---

## Usage

```bash
# Generate context budget report (run once at setup and after model changes)
python ai/ael/src/budget.py

# Full Ralph Loop (worker + reviewer cycle) — standard invocation
python ai/ael/src/orchestrator.py --mode loop \
  --task workspace/prompt/prompt-<uuid>-<n>.md

# Single worker pass
python ai/ael/src/orchestrator.py --mode worker --task workspace/prompt/prompt-abc123.md

# Single reviewer pass
python ai/ael/src/orchestrator.py --mode reviewer --task workspace/prompt/prompt-abc123.md

# Reset AEL state after human acceptance
python ai/ael/src/orchestrator.py --mode reset
```

| Flag | Purpose |
|---|---|
| `--mode` | `worker` \| `reviewer` \| `loop` \| `reset` (default: `loop`) |
| `--task` | Task string or path to task file |
| `--model` | Model for all phases (overrides config default) |
| `--worker-model` | Model for work phase only (loop mode) |
| `--reviewer-model` | Model for review phase only (loop mode) |
| `--max-iterations` | Iteration limit override |
| `--config` | Path to config.yaml |

**`budget.py`** reads `config.yaml` and the model's `config.json` from disk to compute context window size, warn/abort thresholds, and recommended `tactical_brief` sizing. It writes `.ael/ralph/context-budget.md`. The Strategic Domain reads this file before authoring any T04 prompt. If the file is absent, the Strategic Domain will instruct the human to run `budget.py` before proceeding.

[Return to Table of Contents](<#table of contents>)

---

## Recipes

Recipes are YAML files providing role-specific system prompts.

| Recipe | Role | Purpose |
|---|---|---|
| `ralph-work.yaml` | Worker | Makes incremental progress on the task |
| `ralph-review.yaml` | Reviewer | Evaluates work and outputs `SHIP` or `REVISE` |

State files are written to `.ael/ralph/` during execution. This directory is ephemeral and excluded from git.

**Loop exit states:**
- `SHIP` — Strategic Domain reviews generated code, proceeds to audit
- `BLOCKED` — Strategic Domain seeds T03 Issue from `RALPH-BLOCKED.md`

[Return to Table of Contents](<#table of contents>)

---

## Testing

Unit tests for the parser are in the framework repository. Integration tests require oMLX running on `127.0.0.1:8000`.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-13 | Copied from LLM-Governance-and-Orchestration framework v7.7; config.yaml scoped to solax-modbus project path |
| 1.1 | 2026-03-20 | Added budget.py; added --mode reset; updated Configuration and Usage sections; context.models_dir note |
| 1.2 | 2026-03-25 | Added `format_tool_signatures()` to orchestrator.py: injects tool parameter signatures into `{{TOOLS}}` system prompt placeholder to prevent model tool-call hallucination |
| 1.3 | 2026-03-25 | Added `mcp-grep` server to `config.yaml` MCP server definitions |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
