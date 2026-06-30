Created: 2026 June 30

# Implementation Profile: Apple Silicon + MLX (Devstral Small 2 2512, 8bit)

---

## Table of Contents

- [1.0 Overview](<#1.0 overview>)
- [2.0 Placeholder Mappings](<#2.0 placeholder mappings>)
- [3.0 Strategic Domain](<#3.0 strategic domain>)
- [4.0 Tactical Domain](<#4.0 tactical domain>)
- [5.0 Tool-Calling Behaviour](<#5.0 tool-calling behaviour>)
- [6.0 Autonomous Execution Loop](<#6.0 autonomous execution loop>)
- [7.0 Model Selection](<#7.0 model selection>)
- [8.0 Project Setup](<#8.0 project setup>)
- [9.0 Verification Status](<#9.0 verification status>)
- [Version History](<#version history>)

---

## 1.0 Overview

This profile maps governance abstract placeholders to Apple Silicon MLX-based local model tooling using Devstral Small 2 (December 2025 release) at 8bit quantisation. It requires Apple M-series hardware.

| Concern | Implementation |
|---|---|
| Strategic Domain | Claude Desktop (preferred) |
| Tactical Domain | Devstral Small 2 2512 8bit via oMLX + AEL |
| AEL mechanism | AEL orchestrator / Ralph Loop |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Placeholder Mappings

| Placeholder | Resolved Value |
|---|---|
| `<tactical_context>` | `ai/context.md` |

`<tactical_config>/` and `<skills_dir>/` do not apply to this profile. AEL configuration is in `ai/ael/config.yaml`; recipes are in `ai/ael/recipes/`.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Strategic Domain

**Preferred implementation:** Claude Desktop

Any frontier model with sufficient reasoning capability may substitute. The Strategic Domain role requires: planning, governance interpretation, design creation, prompt authoring, and validation.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Tactical Domain

**Implementation:** Devstral Small 2 2512 8bit via oMLX + AEL orchestrator

**Architecture:** Mistral3 (`mistral3`); same model family as the 6bit profile, higher-precision quantisation. Base model: `mistralai/Mistral-Small-3.1-24B-Base-2503`.

**Licence:** Apache 2.0 (Mistral AI). Official model card: `mistralai/Devstral-Small-2-24B-Instruct-2512`.

**Hardware requirement:** Apple M-series chip; ~24 GB unified memory minimum (8bit quantisation; verified resident size 23.48 GB).

**Inference server:**

```bash
omlx serve --model-dir /path/to/ai-models
```

The server exposes an OpenAI-compatible endpoint at `http://localhost:8000/v1`.

**Model location:**

Resident at `ai-models/mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit`. To re-acquire:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="mlx-community/mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit",
    local_dir="/path/to/ai-models/mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit"
)
```

Use Python 3.11+. The `huggingface-cli` may be unreliable on some macOS configurations.

**AEL config** (`ai/ael/config.yaml`):

```yaml
omlx:
  base_url: http://127.0.0.1:8000/v1
  api_key: local
  default_model: mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit
```

The model ID must match the id reported by oMLX `/v1/models` exactly, including the `mistralai_` prefix and `-MLX-8Bit` suffix.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Tool-Calling Behaviour

Devstral Small 2 2512 (all quantisations) emits tool calls in the Mistral `[TOOL_CALLS]` plain-text format. This is the format `ai/ael/src/parser.py` was built and validated against (see module docstring: "Plain-text variant (observed with Devstral via oMLX)").

**Prompt guidance — imperative phrasing** (as for all tactical profiles):

| Avoid | Prefer |
|---|---|
| `You can use the grep tool to search` | `Use the mcp-grep__grep tool to search` |
| `Search for X in the directory` | `Call mcp-grep__grep with pattern X and path Y` |

Name tools explicitly in recipe prompts.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Autonomous Execution Loop

**Implementation:** AEL orchestrator / Ralph Loop

State directory: `ai/state/ralph/` (ephemeral, per-task)

**Prerequisites:**
- oMLX running on `localhost:8000`
- AEL dependencies installed: `pip install -r ai/ael/requirements.txt`
- `ai/ael/config.yaml` configured with `default_model: mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit`

**Invocation:**

```bash
python ai/ael/src/orchestrator.py --mode loop --task ai/workspace/prompt/prompt-<uuid>-<n>.md
```

Worker and reviewer roles are differentiated by prompt engineering within the same model, not by separate model binaries.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Model Selection

| Role | Model | Quantisation | Approx. Memory |
|---|---|---|---|
| Worker | Devstral Small 2 2512 | 8bit | ~23.5 GB resident |
| Reviewer | Devstral Small 2 2512 | 8bit | ~23.5 GB resident |

Context window: 393,216 tokens per oMLX admin endpoint `max_context_window` (matches the 6bit profile's underlying `max_model_len`), **but** the official model card states a 256k (262,144 token) context window, and Mistral's own recommended vLLM serving command sets `--max-model-len 262144` explicitly. The 393,216 figure is the local MLX build's on-disk `config.json` RoPE-scaling ceiling, not a Mistral-validated operating range. Treat 393,216 as an upper bound only; 262,144 is the vendor-recommended and benchmark-validated context length. See [9.0 Verification Status](<#9.0 verification status>).

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Project Setup

**.gitignore additions:**

```
# MLX profile - Tactical Domain
ai/state/ralph/
```

**Setup guide:** [Apple Silicon + MLX Setup Guide](../../../docs/setup-apple-silicon-mlx.md).

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Verification Status

| Item | Status |
|---|---|
| oMLX served id matches `default_model` | Verified (`mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit`) |
| Resident memory footprint | Verified (23.48 GB actual, 24.49 GB estimated — oMLX admin endpoint) |
| Load state at profile creation | Verified — `loaded: true`, `is_default: true` |
| Context window | **Discrepancy** — oMLX reports 393,216 tokens (`max_context_window`); official model card and Mistral's recommended vLLM serving command both specify 256k (262,144). The larger figure is a local build RoPE-scaling ceiling, not a vendor-validated range. See §7.0. |
| Vision capability vs. local model_type | **Discrepancy** — official model card describes Devstral Small 2 as a vision-language model (new vs. predecessor; `transformers` usage shows `Mistral3ForConditionalGeneration`, a VLM class, and supports `image_url` message content). oMLX admin endpoint classifies the local 6bit and 8bit Devstral entries as `model_type: "llm"`, `engine_type: "batched"` — not `vlm`, unlike the Magistral and North-Mini entries which oMLX does mark `vlm`. Vision input support is therefore unverified, and likely unavailable, in this local deployment. Not relevant to the text-only AEL audit task, but a factual gap against the upstream model's stated capability. |
| Model self-identification via `omlx_chat` | **Explained, not a model defect** — a direct `omlx_chat` query (no system prompt) produced "GPT-4.1... trillions of parameters," which is incorrect. The official model card's own test suite shows the *correct* expected behaviour: when invoked with Mistral's `CHAT_SYSTEM_PROMPT.txt` (loaded via `hf_hub_download` and filled with `{name}`/`{today}` placeholders), the model correctly answers "I am Devstral-Small-2-24B-Instruct-2512... created by Mistral AI." AEL's recipes use task-specific system prompts, not Mistral's identity-grounding one, so the hallucination reflects an unprimed query, not an inherent model flaw. Objective figures in this profile are sourced from the oMLX admin endpoint regardless. |
| Tool-call parser compatibility | Verified by construction — `[TOOL_CALLS]` is the format `parser.py` was authored against; confirmed by the official card's `--tool-call-parser mistral` vLLM/SGLang serving flag |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-30 | Initial document |
| 1.1 | 2026-06-30 | Verified against official mistralai/Devstral-Small-2-24B-Instruct-2512 model card: added licence and base model lineage (§4.0); flagged context window discrepancy (393,216 oMLX vs. 262,144 official, §7.0/§9.0); flagged vision-capability vs. local model_type discrepancy (§9.0); corrected self-identification verification note from "hallucinated" to "unprimed query, explained by official CHAT_SYSTEM_PROMPT.txt usage" (§9.0) |

---

Copyright (c) 2026 William Watson. MIT License.
