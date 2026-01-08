# Traceability Matrix

**Document:** trace-0000-master_traceability-matrix.md  
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
| a1b2c3d4 | Data acquisition via Modbus TCP | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| b2c3d4e5 | Grid telemetry (3-phase) | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| c3d4e5f6 | PV generation telemetry | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| d4e5f6a7 | Battery system telemetry | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| e5f6a7b8 | System status telemetry | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| f6a7b8c9 | Data type conversion | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| a7b8c9d0 | Console display | design-d3c4d5e6-component_presentation_console.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| b8c9d0e1 | Connection management | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | test-a1b2c3d5 | Implemented |
| c9d0e1f2 | Data validation | design-a6b7c8d9-component_data_validator.md | TBD | TBD | Planned |
| d0e1f2a3 | Time-series storage | design-b7c8d9e0-component_data_storage.md | TBD | TBD | Planned |
| e1f2a3b4 | Data buffering | design-c8d9e0f1-component_data_buffer.md | TBD | TBD | Planned |
| f2a3b4c5 | Retention policies | design-b7c8d9e0-component_data_storage.md | TBD | TBD | Planned |
| a3b4c5d6 | Threshold alerting | design-e0f1a2b3-component_application_alerting.md | TBD | TBD | Planned |
| b4c5d6e7 | Alert notifications | design-e0f1a2b3-component_application_alerting.md | TBD | TBD | Planned |
| c5d6e7f8 | Configuration write | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD | Planned |
| d6e7f8a9 | Configuration audit | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD | Planned |
| e7f8a9b0 | Multi-inverter coordination | design-f1a2b3c4-component_application_pool.md | TBD | TBD | Planned |
| f8a9b0c1 | Development emulator | design-c2b3c4d5-component_protocol_emulator.md | src/emulator/solax_emulator.py | TBD | Implemented |

[Return to Table of Contents](<#table of contents>)

---

## Non-Functional Requirements

| ID | Requirement | Target | Design | Code | Test | Status |
|----|-------------|--------|--------|------|------|--------|
| a9b0c1d2 | Polling performance | P99 <1s | design-0000-master_solax-modbus.md | src/solax_poll.py | TBD | Partial |
| b0c1d2e3 | Memory efficiency | RSS ≤512MB | design-0000-master_solax-modbus.md | src/solax_poll.py | TBD | Partial |
| c1d2e3f4 | System reliability | 99.5% uptime | design-0000-master_solax-modbus.md | src/solax_poll.py | TBD | Partial |
| d2e3f4a5 | Error recovery | MTTR <5min | design-0000-master_solax-modbus.md | src/solax_poll.py | TBD | Partial |
| e3f4a5b6 | Code maintainability | Coverage >80% | design-0000-master_solax-modbus.md | src/solax_poll.py | src/tests/ | Partial |
| f4a5b6c7 | Network security | Zero unauthorized access | design-0000-master_solax-modbus.md | TBD | TBD | Planned |
| a5b6c7d8 | Data protection | Zero plaintext credentials | design-0000-master_solax-modbus.md | TBD | TBD | Planned |
| b6c7d8e9 | Scalability | O(n) to 100 inverters | design-f1a2b3c4-component_application_pool.md | TBD | TBD | Planned |
| c7d8e9f0 | Installation simplicity | <30min deployment | design-0000-master_solax-modbus.md | pyproject.toml | TBD | Partial |
| d8e9f0a1 | Diagnostic capability | MTTD <15min | design-0000-master_solax-modbus.md | src/solax_poll.py | TBD | Partial |

[Return to Table of Contents](<#table of contents>)

---

## Component Mapping

| Component | Requirements | Design | Source | Test |
|-----------|--------------|--------|--------|------|
| SolaxInverterClient | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, b8c9d0e1 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| InverterDisplay | a7b8c9d0 | design-d3c4d5e6-component_presentation_console.md | src/solax_poll.py | tests/test_solax_poll.py |
| main | a1b2c3d4 | design-e4d5e6f7-component_application_main.md | src/solax_poll.py | TBD |
| SolaxEmulator | f8a9b0c1 | design-c2b3c4d5-component_protocol_emulator.md | src/emulator/solax_emulator.py | TBD |
| DataValidator | c9d0e1f2 | design-a6b7c8d9-component_data_validator.md | TBD | TBD |
| TimeSeriesStore | d0e1f2a3, f2a3b4c5 | design-b7c8d9e0-component_data_storage.md | TBD | TBD |
| DataBuffer | e1f2a3b4 | design-c8d9e0f1-component_data_buffer.md | TBD | TBD |
| AlertManager | a3b4c5d6, b4c5d6e7 | design-e0f1a2b3-component_application_alerting.md | TBD | TBD |
| InverterController | c5d6e7f8, d6e7f8a9 | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD |
| InverterPool | e7f8a9b0 | design-f1a2b3c4-component_application_pool.md | TBD | TBD |

[Return to Table of Contents](<#table of contents>)

---

## Design Document Cross-Reference

| Design Doc | Requirements | Code | Tests |
|------------|--------------|------|-------|
| design-0000-master_solax-modbus.md | All FR/NFR/AR | src/* | tests/* |
| design-8f3a1b2c-domain_protocol.md | a1b2c3d4, b8c9d0e1, c5d6e7f8 | src/solax_poll.py | TBD |
| design-9e4b2c3d-domain_data.md | c9d0e1f2, d0e1f2a3, e1f2a3b4, f2a3b4c5 | TBD | TBD |
| design-af5c3d4e-domain_presentation.md | a7b8c9d0 | src/solax_poll.py | TBD |
| design-bf6d4e5f-domain_application.md | a3b4c5d6, b4c5d6e7, e7f8a9b0 | TBD | TBD |
| design-c1a2b3d4-component_protocol_client.md | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, b8c9d0e1 | src/solax_poll.py | tests/test_solax_poll.py |
| design-c2b3c4d5-component_protocol_emulator.md | f8a9b0c1 | src/emulator/solax_emulator.py | TBD |
| design-f5e6f7a8-component_protocol_controller.md | c5d6e7f8, d6e7f8a9 | TBD | TBD |
| design-a6b7c8d9-component_data_validator.md | c9d0e1f2 | TBD | TBD |
| design-b7c8d9e0-component_data_storage.md | d0e1f2a3, f2a3b4c5 | TBD | TBD |
| design-c8d9e0f1-component_data_buffer.md | e1f2a3b4 | TBD | TBD |
| design-d3c4d5e6-component_presentation_console.md | a7b8c9d0 | src/solax_poll.py | tests/test_solax_poll.py |
| design-d9e0f1a2-component_presentation_html.md | (future) | TBD | TBD |
| design-e0f1a2b3-component_application_alerting.md | a3b4c5d6, b4c5d6e7 | TBD | TBD |
| design-e4d5e6f7-component_application_main.md | a1b2c3d4 | src/solax_poll.py | TBD |
| design-f1a2b3c4-component_application_pool.md | e7f8a9b0 | TBD | TBD |

[Return to Table of Contents](<#table of contents>)

---

## Test Coverage

| Test File | Requirements Verified | Code Coverage |
|-----------|----------------------|---------------|
| tests/test_solax_poll.py | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, a7b8c9d0, b8c9d0e1 | 100% (23/23 tests passed) |

[Return to Table of Contents](<#table of contents>)

---

## Bidirectional Navigation

### Forward Traceability (Req → Design → Code → Test)

| Requirement | Design | Code | Test |
|-------------|--------|------|------|
| a1b2c3d4 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| b2c3d4e5 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| c3d4e5f6 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| d4e5f6a7 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| e5f6a7b8 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| f6a7b8c9 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| a7b8c9d0 | design-d3c4d5e6-component_presentation_console.md | src/solax_poll.py | tests/test_solax_poll.py |
| b8c9d0e1 | design-c1a2b3d4-component_protocol_client.md | src/solax_poll.py | tests/test_solax_poll.py |
| c9d0e1f2 | design-a6b7c8d9-component_data_validator.md | TBD | TBD |
| d0e1f2a3 | design-b7c8d9e0-component_data_storage.md | TBD | TBD |
| e1f2a3b4 | design-c8d9e0f1-component_data_buffer.md | TBD | TBD |
| f2a3b4c5 | design-b7c8d9e0-component_data_storage.md | TBD | TBD |
| a3b4c5d6 | design-e0f1a2b3-component_application_alerting.md | TBD | TBD |
| b4c5d6e7 | design-e0f1a2b3-component_application_alerting.md | TBD | TBD |
| c5d6e7f8 | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD |
| d6e7f8a9 | design-f5e6f7a8-component_protocol_controller.md | TBD | TBD |
| e7f8a9b0 | design-f1a2b3c4-component_application_pool.md | TBD | TBD |
| f8a9b0c1 | design-c2b3c4d5-component_protocol_emulator.md | src/emulator/solax_emulator.py | TBD |

### Backward Traceability (Test → Code → Design → Req)

| Test | Code | Design | Requirement |
|------|------|--------|-------------|
| tests/test_solax_poll.py | src/solax_poll.py | design-c1a2b3d4-component_protocol_client.md | a1b2c3d4, b2c3d4e5, c3d4e5f6, d4e5f6a7, e5f6a7b8, f6a7b8c9, b8c9d0e1 |
| tests/test_solax_poll.py | src/solax_poll.py | design-d3c4d5e6-component_presentation_console.md | a7b8c9d0 |
| TBD | src/emulator/solax_emulator.py | design-c2b3c4d5-component_protocol_emulator.md | f8a9b0c1 |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-12-28 | Initial skeleton per P01.2.5 |
| 2.0 | 2026-01-08 | Populated with requirements-to-design traceability mappings |
| 3.0 | 2026-01-08 | Updated with test documentation references (test-a1b2c3d5, result-b2c3d4e5), corrected test paths to tests/ directory, marked 8 requirements as fully validated |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
