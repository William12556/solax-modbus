# Traceability Matrix

**Document:** trace-traceability-matrix-master.md  
**Project:** solax-modbus  
**Status:** Active

---

## Table of Contents

- [Functional Requirements](<#functional requirements>)
- [Non-Functional Requirements](<#non-functional requirements>)
- [Component Mapping](<#component mapping>)
- [Design Document Cross-Reference](<#design document cross-reference>)
- [Test Coverage](<#test coverage>)
- [Bidirectional Navigation](<#bidirectional navigation>)
- [Version History](<#version history>)

---

## Functional Requirements

| ID | Requirement | Design | Code | Test | Status |
|----|-------------|--------|------|------|--------|
| a1b2c3d4 | Data acquisition via Modbus TCP | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| b2c3d4e5 | Grid telemetry (3-phase) | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| c3d4e5f6 | PV generation telemetry | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| d4e5f6a7 | Battery system telemetry | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| e5f6a7b8 | System status telemetry | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| f6a7b8c9 | Data type conversion | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| a7b8c9d0 | Console display | design-d3c4d5e6-component_presentation_console.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| b8c9d0e1 | Connection management | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | test-a1b2c3d5 | Implemented |
| c9d0e1f2 | Data validation | design-a6b7c8d9-component_data_validator.md | TBD | TBD | Retired |
| d0e1f2a3 | Time-series storage | design-b7c8d9e0-component_data_storage.md | src/solax_modbus/data/storage.py | TBD | Implemented |
| e1f2a3b4 | Data buffering | design-c8d9e0f1-component_data_buffer.md | TBD | TBD | Retired |
| f2a3b4c5 | Retention policies | design-b7c8d9e0-component_data_storage.md | src/solax_modbus/data/storage.py | TBD | Implemented |
| a3b4c5d6 | Threshold alerting | design-e0f1a2b3-component_application_alerting.md | TBD | TBD | Planned |
| b4c5d6e7 | Alert notifications | design-e0f1a2b3-component_application_alerting.md | TBD | TBD | Planned |
| c5d6e7f8 | Configuration write | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD | Planned |
| d6e7f8a9 | Configuration audit | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD | Planned |
| e7f8a9b0 | Multi-inverter coordination | design-f1a2b3c4-component_application_pool.md | TBD | TBD | Planned |
| f8a9b0c1 | Development emulator | design-c2b3c4d5-component_protocol_emulator.md | src/tools/emulator/solax_emulator.py | TBD | Implemented |
| 1a2b3c4d | HTTP telemetry server | design-9b7e2c4a-component_presentation_server.md | src/solax_modbus/presentation/server.py, src/solax_modbus/main.py | tests/test_solax_poll.py | Implemented |
| c2d3e4f5 | Extended (12-month) historical telemetry endpoint | design-b7c8d9e0-component_data_storage.md, design-9b7e2c4a-component_presentation_server.md | src/solax_modbus/data/storage.py, src/solax_modbus/presentation/server.py | TBD | Implemented |

[Return to Table of Contents](<#table of contents>)

---

## Non-Functional Requirements

| ID | Requirement | Target | Design | Code | Test | Status |
|----|-------------|--------|--------|------|------|--------|
| a9b0c1d2 | Polling performance | P99 <1s | design-solax-modbus-master.md | src/solax_modbus/main.py | TBD | Partial |
| b0c1d2e3 | Memory efficiency | RSS ≤512MB | design-solax-modbus-master.md | src/solax_modbus/main.py | TBD | Partial |
| c1d2e3f4 | System reliability | 99.5% uptime | design-solax-modbus-master.md | src/solax_modbus/main.py | TBD | Partial |
| d2e3f4a5 | Error recovery | MTTR <5min | design-solax-modbus-master.md | src/solax_modbus/main.py | TBD | Partial |
| e3f4a5b6 | Code maintainability | Coverage >80% | design-solax-modbus-master.md | src/solax_modbus/main.py | tests/ | Partial |
| f4a5b6c7 | Network security | Zero unauthorized access | design-solax-modbus-master.md | TBD | TBD | Planned |
| a5b6c7d8 | Data protection | Zero plaintext credentials | design-solax-modbus-master.md | TBD | TBD | Planned |
| b6c7d8e9 | Scalability | O(n) to 100 inverters | design-f1a2b3c4-component_application_pool.md | TBD | TBD | Planned |
| c7d8e9f0 | Installation simplicity | <30min deployment | design-solax-modbus-master.md | pyproject.toml | TBD | Partial |
| d8e9f0a1 | Diagnostic capability | MTTD <15min | design-solax-modbus-master.md | src/solax_modbus/main.py | TBD | Partial |

[Return to Table of Contents](<#table of contents>)

---

## Component Mapping

| Component | Requirements | Design | Source | Test |
|-----------|--------------|--------|--------|------|
| SolaxInverterClient | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, b8c9d0e1 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| InverterDisplay | a7b8c9d0 | design-d3c4d5e6-component_presentation_console.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| main | a1b2c3d4 | design-e4d5e6f7-component_application_main.md | src/solax_modbus/main.py | TBD |
| SolaxEmulator | f8a9b0c1 | design-c2b3c4d5-component_protocol_emulator.md | src/tools/emulator/solax_emulator.py | TBD |
| TelemetryServer | 1a2b3c4d, c2d3e4f5 | design-9b7e2c4a-component_presentation_server.md | src/solax_modbus/presentation/server.py | tests/test_solax_poll.py |
| DataValidator | c9d0e1f2 | design-a6b7c8d9-component_data_validator.md | TBD | TBD |
| TimeSeriesStore | d0e1f2a3, f2a3b4c5, c2d3e4f5 | design-b7c8d9e0-component_data_storage.md | src/solax_modbus/data/storage.py | TBD |
| DataBuffer | e1f2a3b4 | design-c8d9e0f1-component_data_buffer.md | TBD | TBD |
| AlertManager | a3b4c5d6, b4c5d6e7 | design-e0f1a2b3-component_application_alerting.md | TBD | TBD |
| InverterController | c5d6e7f8, d6e7f8a9 | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD |
| InverterPool | e7f8a9b0 | design-f1a2b3c4-component_application_pool.md | TBD | TBD |

[Return to Table of Contents](<#table of contents>)

---

## Design Document Cross-Reference

| Design Doc | Requirements | Code | Tests |
|------------|--------------|------|-------|
| design-solax-modbus-master.md | All FR/NFR/AR | src/* | tests/* |
| design-8f3a1b2c-domain_protocol.md | a1b2c3d4, b8c9d0e1, c5d6e7f8 | src/solax_modbus/main.py | TBD |
| design-9e4b2c3d-domain_data.md | c9d0e1f2, d0e1f2a3, e1f2a3b4, f2a3b4c5 | src/solax_modbus/data/storage.py | TBD |
| design-af5c3d4e-domain_presentation.md | a7b8c9d0 | src/solax_modbus/main.py | TBD |
| design-bf6d4e5f-domain_application.md | a3b4c5d6, b4c5d6e7, e7f8a9b0 | TBD | TBD |
| design-c1a2b3d4-component_protocol_client.md | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, b8c9d0e1 | src/solax_modbus/main.py | tests/test_solax_poll.py |
| design-c2b3c4d5-component_protocol_emulator.md | f8a9b0c1 | src/tools/emulator/solax_emulator.py | TBD |
| design-af5c3d4e-domain_presentation.md | 1a2b3c4d | src/solax_modbus/presentation/server.py, src/solax_modbus/main.py | tests/test_solax_poll.py |
| design-9b7e2c4a-component_presentation_server.md | 1a2b3c4d, c2d3e4f5 | src/solax_modbus/presentation/server.py | tests/test_solax_poll.py |
| design-f5e6f7a8-component_protocol_controller.md | c5d6e7f8, d6e7f8a9 | TBD | TBD |
| design-a6b7c8d9-component_data_validator.md | c9d0e1f2 | TBD | TBD |
| design-b7c8d9e0-component_data_storage.md | d0e1f2a3, f2a3b4c5, c2d3e4f5 | src/solax_modbus/data/storage.py | TBD |
| design-c8d9e0f1-component_data_buffer.md | e1f2a3b4 | TBD | TBD |
| design-d3c4d5e6-component_presentation_console.md | a7b8c9d0 | src/solax_modbus/main.py | tests/test_solax_poll.py |
| design-d9e0f1a2-component_presentation_html.md | (future) | TBD | TBD |
| design-e0f1a2b3-component_application_alerting.md | a3b4c5d6, b4c5d6e7 | TBD | TBD |
| design-e4d5e6f7-component_application_main.md | a1b2c3d4 | src/solax_modbus/main.py | TBD |
| design-f1a2b3c4-component_application_pool.md | e7f8a9b0 | TBD | TBD |

[Return to Table of Contents](<#table of contents>)

---

## Test Coverage

| Test File | Requirements Verified | Code Coverage |
|-----------|----------------------|---------------|
| tests/test_solax_poll.py | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, a7b8c9d0, b8c9d0e1, 1a2b3c4d | 100% (24/24 tests passed) |

[Return to Table of Contents](<#table of contents>)

---

## Bidirectional Navigation

### Forward Traceability (Req → Design → Code → Test)

| Requirement | Design | Code | Test |
|-------------|--------|------|------|
| a1b2c3d4 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| b2c3d4e5 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| c3d4e5f6 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| d4e5f6a7 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| e5f6a7b8 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| f6a7b8c9 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| a7b8c9d0 | design-d3c4d5e6-component_presentation_console.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| b8c9d0e1 | design-c1a2b3d4-component_protocol_client.md | src/solax_modbus/main.py | tests/test_solax_poll.py |
| c9d0e1f2 | design-a6b7c8d9-component_data_validator.md | TBD | TBD |
| d0e1f2a3 | design-b7c8d9e0-component_data_storage.md | src/solax_modbus/data/storage.py | TBD |
| e1f2a3b4 | design-c8d9e0f1-component_data_buffer.md | TBD | TBD |
| f2a3b4c5 | design-b7c8d9e0-component_data_storage.md | src/solax_modbus/data/storage.py | TBD |
| a3b4c5d6 | design-e0f1a2b3-component_application_alerting.md | TBD | TBD |
| b4c5d6e7 | design-e0f1a2b3-component_application_alerting.md | TBD | TBD |
| c5d6e7f8 | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD |
| d6e7f8a9 | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD |
| e7f8a9b0 | design-f1a2b3c4-component_application_pool.md | TBD | TBD |
| f8a9b0c1 | design-c2b3c4d5-component_protocol_emulator.md | src/tools/emulator/solax_emulator.py | TBD |
| 1a2b3c4d | design-9b7e2c4a-component_presentation_server.md | src/solax_modbus/presentation/server.py, src/solax_modbus/main.py | tests/test_solax_poll.py |
| c2d3e4f5 | design-b7c8d9e0-component_data_storage.md, design-9b7e2c4a-component_presentation_server.md | src/solax_modbus/data/storage.py, src/solax_modbus/presentation/server.py | TBD |

### Backward Traceability (Test → Code → Design → Req)

| Test | Code | Design | Requirement |
|------|------|--------|-------------|
| tests/test_solax_poll.py | src/solax_modbus/main.py | design-c1a2b3d4-component_protocol_client.md | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, b8c9d0e1 |
| tests/test_solax_poll.py | src/solax_modbus/main.py | design-d3c4d5e6-component_presentation_console.md | a7b8c9d0 |
| TBD | src/tools/emulator/solax_emulator.py | design-c2b3c4d5-component_protocol_emulator.md | f8a9b0c1 |
| tests/test_solax_poll.py | src/solax_modbus/presentation/server.py, src/solax_modbus/main.py | design-9b7e2c4a-component_presentation_server.md | 1a2b3c4d |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-12-28 | Initial skeleton per P01.2.5 |
| 2.0 | 2026-01-08 | Populated with requirements-to-design traceability mappings |
| 3.0 | 2026-01-08 | Updated with test documentation references (test-a1b2c3d5, result-b2c3d4e5), corrected test paths to tests/ directory, marked 8 requirements as fully validated |
| 4.0 | 2026-01-09 | Updated file paths for Python package structure: src/solax_poll.py → src/solax_modbus/main.py, src/emulator/solax_emulator.py → src/solax_modbus/emulator/solax_emulator.py |
| 5.0 | 2026-07-03 | Updated SolaxEmulator code path: src/solax_modbus/emulator/solax_emulator.py → src/tools/emulator/solax_emulator.py (relocated outside package tree, see design-c2b3c4d5 1.5). |
| 6.0 | 2026-07-07 | Added FR-018 (HTTP Telemetry Server, 1a2b3c4d) baseline across all five tables: Functional Requirements, Component Mapping, Design Document Cross-Reference (design-af5c3d4e, design-9b7e2c4a), Test Coverage, Bidirectional Navigation. Updated Test Coverage 23/23 -> 24/24 (pytest, see change-a7c3e9d2). |
| 6.1 | 2026-07-17 | Added FR-020 (Extended 12-Month Historical Telemetry Endpoint, c2d3e4f5, change-b1c2d3e4) to Functional Requirements, Component Mapping (TimeSeriesStore, TelemetryServer), Design Document Cross-Reference, and Bidirectional Navigation. Note: FR-019 (2e5f8a1b, /api/history) remains absent from this matrix, a pre-existing gap deferred from a prior session (not addressed by this entry). |
| 6.2 | 2026-07-17 | P08 review (prompt-b1c2d3e4): corrected stale status Planned -> Implemented for d0e1f2a3, f2a3b4c5, c2d3e4f5 and filled Code columns (src/solax_modbus/data/storage.py, src/solax_modbus/presentation/server.py) across Functional Requirements, Component Mapping, and Design Document Cross-Reference tables — source has existed since change-a2d5f7c9 and was never reflected here. Also corrected c9d0e1f2 and e1f2a3b4 status Planned -> Retired (both retired by change-a2d5f7c9; status was not updated at that time). Test columns remain TBD (no automated tests exist yet for this tier). FR-019 gap (2e5f8a1b) remains open, unaddressed by this entry. |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
