# Software Design Specification Correction Plan

Created: 2025 10 29

## Table of Contents

- [Overview](<#overview>)
- [Phase 1: Register Map Corrections](<#phase 1 register map corrections>)
- [Phase 2: Data Structure Updates](<#phase 2 data structure updates>)
- [Phase 3: Code Example Updates](<#phase 3 code example updates>)
- [Phase 4: Documentation Enhancements](<#phase 4 documentation enhancements>)
- [Phase 5: Verification and Validation](<#phase 5 verification and validation>)
- [Implementation Order](<#implementation order>)
- [Risk Assessment](<#risk assessment>)

[Return to Table of Contents](<#table of contents>)

---

## Overview

**Document:** solax-modbus-software-design-specification.md  
**Current Version:** 1.0  
**Target Version:** 1.1  
**Estimated Changes:** ~150 lines modified, ~200 lines added

**Scope:**
- Correct all register addresses in Section 6.1
- Add missing registers and parameters
- Update data structures in Section 5.2
- Revise code examples throughout document
- Add multi-register value handling
- Complete enumeration definitions

**Out of Scope:**
- Architecture changes (remains valid)
- Non-functional requirements (remain valid)
- Testing strategy (remains valid)
- Deployment procedures (remain valid)

[Return to Table of Contents](<#table of contents>)

---

## Phase 1: Register Map Corrections

### Task 1.1: Update Section 6.1 Input Registers Table

**Location:** Section 6.1, Input Registers table

**Changes Required:**

Replace existing table with corrected addresses:

```markdown
**Input Registers (Function Code 0x04):**

#### PV String Parameters

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x0003 | PV1 Voltage | uint16 | 0.1 | V | R |
| 0x0004 | PV2 Voltage | uint16 | 0.1 | V | R |
| 0x0005 | PV1 Current | uint16 | 0.1 | A | R |
| 0x0006 | PV2 Current | uint16 | 0.1 | A | R |
| 0x0007 | Grid Frequency (legacy) | uint16 | 0.01 | Hz | R |
| 0x0008 | Inverter Temperature | int16 | 1 | °C | R |
| 0x0009 | Run Mode | uint16 | 1 | enum | R |
| 0x000A | PV1 Power | uint16 | 1 | W | R |
| 0x000B | PV2 Power | uint16 | 1 | W | R |

#### Battery Parameters

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x0014 | Battery Voltage | int16 | 0.1 | V | R |
| 0x0015 | Battery Current | int16 | 0.1 | A | R |
| 0x0016 | Battery Power | int16 | 1 | W | R |
| 0x0017 | BMS Connection State | uint16 | 1 | bool | R |
| 0x0018 | Battery Temperature | int16 | 1 | °C | R |
| 0x0019 | Battery Status | uint16 | 1 | enum | R |
| 0x001A | Reserved | - | - | - | - |
| 0x001B | Reserved | - | - | - | - |
| 0x001C | Battery SOC | uint16 | 1 | % | R |

#### Energy Statistics

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x0020 | Battery Charge Today | uint16 | 0.1 | kWh | R |
| 0x0046 | Feedin Power (Low) | uint16 | - | - | R |
| 0x0047 | Feedin Power (High) | uint16 | - | - | R |
| 0x0050 | Energy Today | uint16 | 0.1 | kWh | R |
| 0x0052 | Energy Total (Low) | uint16 | - | - | R |
| 0x0053 | Energy Total (High) | uint16 | - | - | R |

**Note:** Feedin Power and Energy Total are 32-bit values (little-endian).  
Feedin Power: Positive = export to grid, Negative = import from grid

#### Grid Three-Phase Parameters

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x006A | Grid Voltage Phase R | uint16 | 0.1 | V | R |
| 0x006B | Grid Current Phase R | int16 | 0.1 | A | R |
| 0x006C | Grid Power Phase R | int16 | 1 | W | R |
| 0x006D | Grid Frequency Phase R | uint16 | 0.01 | Hz | R |
| 0x006E | Grid Voltage Phase S | uint16 | 0.1 | V | R |
| 0x006F | Grid Current Phase S | int16 | 0.1 | A | R |
| 0x0070 | Grid Power Phase S | int16 | 1 | W | R |
| 0x0071 | Grid Frequency Phase S | uint16 | 0.01 | Hz | R |
| 0x0072 | Grid Voltage Phase T | uint16 | 0.1 | V | R |
| 0x0073 | Grid Current Phase T | int16 | 0.1 | A | R |
| 0x0074 | Grid Power Phase T | int16 | 1 | W | R |
| 0x0075 | Grid Frequency Phase T | uint16 | 0.01 | Hz | R |

#### Grid Import/Export Energy

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x0098 | Feedin Energy Today (Low) | uint16 | - | - | R |
| 0x0099 | Feedin Energy Today (High) | uint16 | - | - | R |
| 0x009A | Consumption Energy Today (Low) | uint16 | - | - | R |
| 0x009B | Consumption Energy Today (High) | uint16 | - | - | R |

**Note:** Both values are 32-bit unsigned integers (little-endian), scale 0.01 kWh
```

**Impact:** Complete rewrite of input register table (~50 lines)

### Task 1.2: Add Multi-Register Value Handling Section

**Location:** After Section 6.1 register tables, before Section 6.2

**New Content:**

```markdown
### 6.1.1 Multi-Register Values

Several parameters use 32-bit values spanning two consecutive 16-bit registers:

**32-bit Signed Integer (Little-Endian):**
- Feedin Power (0x0046-0x0047)
  - Low word at 0x0046, high word at 0x0047
  - Range: -2,147,483,648 to +2,147,483,647 W
  - Positive = export, Negative = import

**32-bit Unsigned Integer (Little-Endian):**
- Energy Total (0x0052-0x0053)
- Feedin Energy Today (0x0098-0x0099)
- Consumption Energy Today (0x009A-0x009B)

**Conversion Examples:**

```python
def read_32bit_signed(low: int, high: int) -> int:
    """Convert two 16-bit registers to signed 32-bit (little-endian)."""
    value = (high << 16) | low
    return value if value < 2147483648 else value - 4294967296

def read_32bit_unsigned(low: int, high: int) -> int:
    """Convert two 16-bit registers to unsigned 32-bit (little-endian)."""
    return (high << 16) | low
```
```

**Impact:** New subsection (~30 lines)

### Task 1.3: Update Enumeration Values

**Location:** Section 6.1, Enumeration Values subsection

**Changes Required:**

Add Battery Status enumeration after Run Mode:

```markdown
*Battery Status (0x0019):*
- 0: Idle/Stop
- 1: Charging
- 2: Discharging
```

**Impact:** Add 4 lines to existing section

### Task 1.4: Update Holding Registers Commentary

**Location:** Section 6.1, Holding Registers table header

**Add Note:**

```markdown
**Note:** Holding register addresses shown are preliminary. Verify against 
protocol specification Section 5 (User Settings) before implementing write 
operations. Read-only mode recommended for initial deployment per REQ-CC-001.
```

**Impact:** Add 3 lines

[Return to Table of Contents](<#table of contents>)

---

## Phase 2: Data Structure Updates

### Task 2.1: Update GridMetrics Dataclass

**Location:** Section 5.2, Data Structures

**Changes Required:**

```python
@dataclass
class GridMetrics:
    """Three-phase grid electrical parameters."""
    voltage_r: float  # Volts
    voltage_s: float  # Volts
    voltage_t: float  # Volts
    current_r: float  # Amperes
    current_s: float  # Amperes
    current_t: float  # Amperes
    power_r: float    # Watts
    power_s: float    # Watts
    power_t: float    # Watts
    frequency_r: float  # Hertz - ADD
    frequency_s: float  # Hertz - ADD
    frequency_t: float  # Hertz - ADD
    timestamp: datetime
```

**Impact:** Add 3 fields

### Task 2.2: Update BatteryMetrics Dataclass

**Location:** Section 5.2, Data Structures

**Changes Required:**

```python
@dataclass
class BatteryMetrics:
    """Battery system parameters."""
    voltage: float        # Volts
    current: float        # Amperes (positive = charge)
    power: int           # Watts (positive = charge)
    soc: int            # State of charge (%)
    temperature: int     # Celsius
    bms_connected: bool  # BMS communication active - ADD
    status: int         # Battery status (0=idle, 1=charge, 2=discharge) - ADD
    capacity: int       # Watt-hours
    timestamp: datetime
```

**Impact:** Add 2 fields

### Task 2.3: Add EnergyStats Dataclass

**Location:** Section 5.2, after BatteryMetrics

**New Content:**

```python
@dataclass
class EnergyStats:
    """Energy accounting and totals."""
    generation_today: float      # kWh - Daily solar generation
    generation_total: float      # kWh - Lifetime solar generation
    battery_charge_today: float  # kWh - Daily battery charge
    feedin_today: float         # kWh - Daily grid export
    consumption_today: float     # kWh - Daily grid import
    feedin_power: int          # W - Instantaneous grid power (signed)
    timestamp: datetime
```

**Impact:** Add new dataclass (~15 lines)

### Task 2.4: Update SolaxInverter Class

**Location:** Section 5.2, Key Classes

**Changes Required:**

Update method signature:

```python
def get_energy_statistics() -> EnergyStats  # Update return type
```

**Impact:** Update 1 line

[Return to Table of Contents](<#table of contents>)

---

## Phase 3: Code Example Updates

### Task 3.1: Update RegisterMap Example

**Location:** Section 5.1, Key Classes

**No changes required** - RegisterMap is abstract and addresses stored internally

**Impact:** None

### Task 3.2: Update Performance Optimization Example

**Location:** Section 13.1, Optimization Strategies, Task 1

**Changes Required:**

Update batch read example:

```python
# Inefficient: Multiple reads
pv1_voltage = read_register(0x0003)  # UPDATE from 0x0009
pv2_voltage = read_register(0x0004)  # UPDATE from 0x000A
pv1_current = read_register(0x0005)  # UPDATE from 0x000B

# Optimized: Batch read
# Read PV parameters (9 registers)
registers = read_registers(0x0003, 9)  # UPDATE from different base
pv1_voltage = registers[0] * 0.1
pv2_voltage = registers[1] * 0.1
pv1_current = registers[2] * 0.1
# ... etc
```

**Impact:** Update 6 lines

### Task 3.3: Update Test Examples

**Location:** Section 10.1, Example Test Cases

**Changes Required:**

Update addresses in test examples:

```python
def test_register_scaling():
    """Verify correct scaling of register values."""
    raw_value = 2305  # 230.5V from register 0x006A
    scaled = scale_voltage(raw_value)
    assert scaled == 230.5
```

**Impact:** Update comments in 3 test examples

[Return to Table of Contents](<#table of contents>)

---

## Phase 4: Documentation Enhancements

### Task 4.1: Add Register Access Patterns Section

**Location:** New Section 6.1.2 after Multi-Register Values

**New Content:**

```markdown
### 6.1.2 Recommended Register Access Patterns

**Efficient Batch Reads:**

Group contiguous registers to minimize Modbus transactions:

```python
# Group 1: PV and System Status (9 registers)
pv_data = read_input_registers(0x0003, 9)
# Returns: PV1V, PV2V, PV1I, PV2I, freq, temp, mode, PV1P, PV2P

# Group 2: Battery Parameters (9 registers)
battery_data = read_input_registers(0x0014, 9)
# Returns: voltage, current, power, BMS, temp, status, rsv, rsv, SOC

# Group 3: Grid Three-Phase (12 registers)
grid_data = read_input_registers(0x006A, 12)
# Returns: R(V,I,P,F), S(V,I,P,F), T(V,I,P,F)

# Group 4: Energy Statistics (dispersed, read individually)
energy_today = read_input_registers(0x0050, 1)[0]
energy_total = read_input_registers(0x0052, 2)
feedin_power = read_input_registers(0x0046, 2)
```

**Polling Strategy:**

- High-frequency (1s): PV, Battery, Grid power
- Medium-frequency (10s): Energy statistics
- Low-frequency (60s): Temperatures, status
```

**Impact:** New subsection (~35 lines)

### Task 4.2: Update Appendix A Reference

**Location:** Section 18, Appendix A

**Changes Required:**

Update placeholder text:

```markdown
## Appendix A: Register Reference Tables

### A.1 Complete Input Register Map

See Section 6.1 for verified input register addresses.

**Register Groups:**
- PV Parameters: 0x0003-0x000B
- Battery Parameters: 0x0014-0x001C
- Energy Statistics: 0x0020, 0x0046-0x0047, 0x0050, 0x0052-0x0053
- Grid Parameters: 0x006A-0x0075
- Grid Energy: 0x0098-0x009B

**Unverified Ranges:**
The following register ranges require investigation:
- 0x0000-0x0002
- 0x000C-0x0013
- 0x001D-0x001F
- 0x0021-0x0045
- 0x0048-0x004F, 0x0051, 0x0054-0x0069
- 0x0076-0x0097
- 0x009C onwards

Consult Solax protocol specification for complete register documentation.
```

**Impact:** Replace placeholder (~25 lines)

### Task 4.3: Update Section 2.3 Design Principles

**Location:** Section 2.3

**Add Principle:**

```markdown
6. **Protocol Fidelity**: Maintain strict adherence to vendor protocol specifications
```

**Impact:** Add 1 line

### Task 4.4: Update Document Control

**Location:** End of document

**Changes Required:**

Update version table:

```markdown
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-25 | System Architect | Initial release |
| 1.1 | 2025-10-29 | System Architect | Register map corrections per POC validation |
```

**Impact:** Add 1 row

[Return to Table of Contents](<#table of contents>)

---

## Phase 5: Verification and Validation

### Task 5.1: Create Register Mapping Verification Document

**Location:** Create new file: `/docs/verification/register-address-mapping.md`

**Content:**

Cross-reference table showing:
- Design spec address
- POC validated address
- Solax protocol PDF page reference
- Verification status

**Impact:** New file (~100 lines)

### Task 5.2: Update References Section

**Location:** Section 18.1

**Add Reference:**

```markdown
4. Register Map Verification Report - `docs/verification/register-map-verification-report.md`
5. Design Specification Verification Checklist - `docs/verification/design-specification-verification-checklist.md`
```

**Impact:** Add 2 lines

[Return to Table of Contents](<#table of contents>)

---

## Implementation Order

### Step 1: Core Corrections (Critical)
- Task 1.1: Update Section 6.1 Input Registers Table
- Task 1.2: Add Multi-Register Value Handling Section
- Task 1.3: Update Enumeration Values

**Priority:** P1  
**Estimated Time:** 45 minutes  
**Risk:** Low

### Step 2: Data Structure Updates (High)
- Task 2.1: Update GridMetrics Dataclass
- Task 2.2: Update BatteryMetrics Dataclass
- Task 2.3: Add EnergyStats Dataclass
- Task 2.4: Update SolaxInverter Class

**Priority:** P1  
**Estimated Time:** 30 minutes  
**Risk:** Low

### Step 3: Code Examples (Medium)
- Task 3.1: Update RegisterMap Example
- Task 3.2: Update Performance Optimization Example
- Task 3.3: Update Test Examples

**Priority:** P2  
**Estimated Time:** 20 minutes  
**Risk:** Low

### Step 4: Documentation Enhancements (Medium)
- Task 4.1: Add Register Access Patterns Section
- Task 4.2: Update Appendix A Reference
- Task 4.3: Update Section 2.3 Design Principles
- Task 4.4: Update Document Control

**Priority:** P2  
**Estimated Time:** 40 minutes  
**Risk:** Low

### Step 5: Verification (Low)
- Task 5.1: Create Register Mapping Verification Document
- Task 5.2: Update References Section

**Priority:** P3  
**Estimated Time:** 25 minutes  
**Risk:** Low

**Total Estimated Time:** 2.5 hours

[Return to Table of Contents](<#table of contents>)

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Additional register errors discovered | Medium | Step-by-step verification, cross-reference POC |
| Protocol version differences | Low | Document applies to V3.21 specifically |
| Breaking existing code references | Low | Version increment signals breaking changes |

### Process Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incomplete updates | Medium | Checklist-based verification |
| Inconsistent terminology | Low | Follow established conventions |
| Missing cross-references | Low | Global search for affected sections |

### Validation Approach

**Pre-Implementation:**
1. Review change plan
2. Verify POC addresses against protocol PDF (manual)
3. Identify any additional affected sections

**During Implementation:**
1. Make changes in order specified
2. Mark each task complete
3. Cross-reference related sections

**Post-Implementation:**
1. Search document for old addresses (0x0000, 0x0001, etc.)
2. Verify all dataclass fields match register definitions
3. Check code examples use correct addresses
4. Validate all internal cross-references

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-29 | System Architect | Initial change plan |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
