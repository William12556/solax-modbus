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
    ├── orchestrator.py  # Main loop and CLI entry point (--mode worker|reviewer|loop)
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

Edit `ai/ael/config.yaml` to set inference endpoint and allowed filesystem path:

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
```

[Return to Table of Contents](<#table of contents>)

---

## Usage

```bash
# Full Ralph Loop (worker + reviewer cycle) — standard invocation
python ai/ael/src/orchestrator.py --mode loop \
  --task workspace/prompt/prompt-<uuid>-<n>.md

# Single worker pass
python ai/ael/src/orchestrator.py --mode worker --task workspace/prompt/prompt-abc123.md

# Single reviewer pass
python ai/ael/src/orchestrator.py --mode reviewer --task workspace/prompt/prompt-abc123.md
```

| Flag | Purpose |
|---|---|
| `--mode` | `worker` \| `reviewer` \| `loop` (default: `loop`) |
| `--task` | Task string or path to task file |
| `--model` | Model for all phases (overrides config default) |
| `--worker-model` | Model for work phase only (loop mode) |
| `--reviewer-model` | Model for review phase only (loop mode) |
| `--max-iterations` | Iteration limit override |
| `--config` | Path to config.yaml |

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

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
