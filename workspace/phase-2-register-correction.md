Created: 2025 October 29

# Phase 2 Specification: Register Address Correction

## Purpose

Correct Modbus register addresses in `solax_poll.py` to align with verified design specification, enabling functional communication with Solax X3 Hybrid inverters.

## Context

**Current State**: Phase 1 implementation (`solax_poll.py`) contains incorrect register addresses that prevent proper inverter communication.

**Problem**: Register addresses in code do not match design specification Section 6.1, resulting in invalid data reads.

**Impact**: System cannot acquire valid telemetry from inverters.

## Requirements

### Functional

**REQ-F-001**: Correct all input register addresses to match design specification Section 6.1

**REQ-F-002**: Remove direct PV power register reads; calculate from voltage × current

**REQ-F-003**: Preserve existing error handling, logging, and retry mechanisms

**REQ-F-004**: Maintain current display formatting and output structure

### Technical

**REQ-T-001**: Python 3.11+ compatibility maintained

**REQ-T-002**: pymodbus 3.5.0+ API usage unchanged

**REQ-T-003**: No architectural changes to class structure

**REQ-T-004**: Preserve thread-safety characteristics

### Register Address Corrections

| Metric | Current Address | Correct Address | Action |
|--------|----------------|-----------------|--------|
| Grid Voltage R-T | 0x006A | 0x0000 | Correct |
| Grid Current R-T | 0x006B | 0x0003 | Correct |
| Grid Power R-T | 0x006C | 0x0006 | Correct |
| Grid Frequency | 0x006D | 0x0009 (single) | Correct |
| PV1 Voltage | 0x0003 | 0x0009 | Correct |
| PV2 Voltage | 0x0004 | 0x000A | Correct |
| PV1 Current | 0x0005 | 0x000B | Correct |
| PV2 Current | 0x0006 | 0x000C | Correct |
| PV1 Power | 0x000A | Calculate V×I | Remove read |
| PV2 Power | 0x000B | Calculate V×I | Remove read |
| Battery Voltage | 0x0014 | 0x0014 | No change |
| Battery Current | 0x0015 | 0x0015 | No change |
| Battery Power | 0x0016 | 0x0016 | No change |
| Battery Temp | 0x001C | 0x001C | No change |
| Battery SOC | 0x001D | 0x001D | No change |
| Feed-in Power | 0x0046 | 0x0020 | Correct |
| Energy Today | 0x0050 | 0x0050 | No change |
| Energy Total | 0x0052 | 0x0052 | No change |
| Inverter Temp | 0x0008 | 0x0008 | No change |
| Run Mode | 0x0009 | 0x0047 | Correct |

### Data Processing Changes

**PV Power Calculation**:
```python
# Remove direct register reads
# Replace with calculation
pv1_power = pv1_voltage * pv1_current
pv2_power = pv2_voltage * pv2_current
```

**Grid Frequency Handling**:
- Current: Reads per-phase frequency (3 registers)
- Correct: Single frequency register at 0x0009
- Action: Read once, apply to all phases in display

### Quality

**REQ-Q-001**: All register addresses verified against design specification Section 6.1

**REQ-Q-002**: Unit tests updated to reflect corrected addresses

**REQ-Q-003**: Emulator testing validates data acquisition

**REQ-Q-004**: Test coverage maintained at current level (>70%)

**REQ-Q-005**: Code formatting preserved (PEP 8 compliant)

## Success Criteria

1. **Functional Validation**:
   - Emulator returns valid telemetry for all metrics
   - Display output shows logical values
   - No ModbusException errors during normal operation

2. **Technical Validation**:
   - All register addresses match specification
   - PV power calculated correctly (within 1W of V×I product)
   - Existing tests pass with updated addresses

3. **Code Quality**:
   - No regressions in error handling
   - Logging behavior unchanged
   - Class structure preserved

## Out of Scope

- Additional architectural components (database, alerting)
- Multi-inverter support implementation
- Configuration file system
- New functionality beyond corrections
- Performance optimizations
- API development
- Control/write operations

## Testing Requirements

### Unit Tests

Update `tests/test_solax_poll.py`:
- Mock register reads at corrected addresses
- Verify PV power calculation logic
- Test grid frequency single-register handling
- Validate data type conversions

### Integration Tests

Test against emulator:
```bash
# Terminal 1: Start emulator
python emulator/solax_emulator.py

# Terminal 2: Run corrected client
python src/solax_poll.py 127.0.0.1 --interval 5
```

**Expected Results**:
- Grid voltages: 230-240V range
- PV voltages: 300-400V range  
- Battery SOC: 0-100%
- Run mode: "Normal" or valid enumeration
- No address-related errors

### Validation Checklist

- [ ] All register addresses match Section 6.1
- [ ] PV power calculation produces logical results
- [ ] Grid frequency reads single register
- [ ] Feed-in power reads from 0x0020
- [ ] Run mode reads from 0x0047
- [ ] Emulator test successful (5+ poll cycles)
- [ ] Unit tests updated and passing
- [ ] No functional regressions
- [ ] Code formatting preserved

## Implementation Guidance

### File Modifications

**Primary**: `src/solax_poll.py`
- Update `REGISTER_MAPPINGS` dictionary
- Modify `_process_grid_data()` for single frequency
- Modify `_process_pv_data()` to calculate power
- Update register read in `poll_inverter()`

**Secondary**: `tests/test_solax_poll.py`
- Update mock register addresses
- Add PV power calculation tests
- Verify frequency handling

### Preservation Requirements

**Do Not Modify**:
- Connection management logic
- Error handling patterns
- Retry mechanisms with exponential backoff
- Display formatting
- Logging configuration
- Class structure
- Method signatures

### Code Style

- Maintain existing docstring format
- Preserve inline comments
- Follow current indentation pattern
- Keep variable naming conventions

## Deliverables

1. **Corrected Source Code**:
   - `src/solax_poll.py` with address corrections
   - Git commit with clear message

2. **Updated Tests**:
   - `tests/test_solax_poll.py` with corrected mocks
   - All tests passing

3. **Verification Document**:
   - Register address alignment confirmation
   - Emulator test results
   - Evidence of functional operation

4. **Change Summary**:
   - List of modified registers
   - Calculation logic changes
   - Any unexpected impacts

## Risk Assessment

**Low Risk**:
- Register address corrections (isolated change)
- PV power calculation (simple arithmetic)
- Grid frequency consolidation (minor logic change)

**Mitigation**:
- Emulator testing before hardware deployment
- Preserve original file as backup
- Incremental testing approach

## Dependencies

**Required**:
- Python 3.11+
- pymodbus 3.5.0+
- pytest 7.4.0+ (testing)

**Files**:
- `/Users/williamwatson/Documents/GitHub/solax-modbus/src/solax_poll.py`
- `/Users/williamwatson/Documents/GitHub/solax-modbus/tests/test_solax_poll.py`
- `/Users/williamwatson/Documents/GitHub/solax-modbus/emulator/solax_emulator.py`
- `/Users/williamwatson/Documents/GitHub/solax-modbus/docs/design/solax-modbus-software-design-specification.md`

**References**:
- Design Specification Section 6.1 (Register Map)
- Solax Protocol Document (input register definitions)

## Acceptance Criteria

**Pass Conditions**:
1. All register addresses match specification
2. Emulator test completes 5+ cycles without errors
3. Display shows logical telemetry values
4. Unit tests pass with >70% coverage
5. No functional regressions identified

**Failure Conditions**:
- ModbusException during emulator testing
- Illogical values in display output
- Unit test failures
- Loss of existing functionality

## Notes

- This phase focuses solely on correctness, not enhancement
- Hardware testing recommended after emulator validation
- Document any deviations from specification
- Record actual vs. expected values during testing

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-29 | Initial Phase 2 specification |

---

**Copyright:** Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
