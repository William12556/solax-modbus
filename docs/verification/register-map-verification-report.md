# Register Map Verification Report

Created: 2025 10 29

## Table of Contents

- [Executive Summary](<#executive summary>)
- [Critical Discrepancies](<#critical discrepancies>)
- [Verified Registers](<#verified registers>)
- [Missing Registers](<#missing registers>)
- [Recommended Corrections](<#recommended corrections>)

[Return to Table of Contents](<#table of contents>)

---

## Executive Summary

**Purpose:** Verify Software Design Specification register map against POC implementation  
**Status:** CRITICAL DISCREPANCIES IDENTIFIED  
**Priority:** P1 - Immediate correction required

### Key Findings

**CRITICAL ISSUES:**
1. Design specification register addresses do NOT match POC implementation
2. Grid parameters use completely different address range
3. Battery parameters have different addresses
4. Multiple register gaps unaccounted for

**IMPACT:**
- Software Design Specification Section 6.1 contains incorrect register addresses
- Implementation based on these addresses will fail
- POC has validated correct addresses through actual testing

[Return to Table of Contents](<#table of contents>)

---

## Critical Discrepancies

### Grid Parameters (Three-Phase)

**Design Specification Claims (Section 6.1):**

| Address | Field | Actual POC Address | Discrepancy |
|---------|-------|-------------------|-------------|
| 0x0000 | Grid Voltage R | 0x006A | ❌ WRONG |
| 0x0001 | Grid Voltage S | 0x006E | ❌ WRONG |
| 0x0002 | Grid Voltage T | 0x0072 | ❌ WRONG |
| 0x0003 | Grid Current R | 0x006B | ❌ WRONG |
| 0x0004 | Grid Current S | 0x006F | ❌ WRONG |
| 0x0005 | Grid Current T | 0x0073 | ❌ WRONG |
| 0x0006 | Grid Power R | 0x006C | ❌ WRONG |
| 0x0007 | Grid Power S | 0x0070 | ❌ WRONG |
| 0x0008 | Grid Power T | 0x0074 | ❌ WRONG |

**POC Evidence (solax-modbus-poc.md, lines 412-423):**
```python
# Grid Data - Three Phase (Registers 0x006A-0x0075)
data = self.read_input_registers(0x006A, 12)
if data:
    stats['grid_voltage_r'] = data[0] * 0.1  # 0x006A
    stats['grid_current_r'] = self._to_signed(data[1]) * 0.1  # 0x006B
    stats['grid_power_r'] = self._to_signed(data[2])  # 0x006C
    stats['grid_frequency_r'] = data[3] * 0.01  # 0x006D
```

**Conclusion:** Grid parameters are at 0x006A-0x0075, NOT 0x0000-0x0008

### PV Parameters

**Design Specification (Section 6.1):**

| Address | Field | Actual POC Address | Status |
|---------|-------|-------------------|--------|
| 0x0009 | PV1 Voltage | 0x0003 | ❌ WRONG |
| 0x000A | PV2 Voltage | 0x0004 | ❌ WRONG |
| 0x000B | PV1 Current | 0x0005 | ❌ WRONG |
| 0x000C | PV2 Current | 0x0006 | ❌ WRONG |

**POC Evidence (lines 437-446):**
```python
# PV Data (Registers 0x0003-0x000B)
data = self.read_input_registers(0x0003, 9)
if data:
    stats['pv1_voltage'] = data[0] * 0.1  # 0x0003
    stats['pv2_voltage'] = data[1] * 0.1  # 0x0004
    stats['pv1_current'] = data[2] * 0.1  # 0x0005
    stats['pv2_current'] = data[3] * 0.1  # 0x0006
    stats['pv1_power'] = data[7]  # 0x000A
    stats['pv2_power'] = data[8]  # 0x000B
```

**Conclusion:** PV voltages at 0x0003-0x0004, currents at 0x0005-0x0006, powers at 0x000A-0x000B

### Battery Parameters

**Design Specification (Section 6.1):**

| Address | Field | Actual POC Address | Status |
|---------|-------|-------------------|--------|
| 0x0014 | Battery Voltage | 0x0014 | ✅ CORRECT |
| 0x0015 | Battery Current | 0x0015 | ✅ CORRECT |
| 0x0016 | Battery Power | 0x0016 | ✅ CORRECT |
| 0x001C | Battery Temperature | 0x0018 | ❌ WRONG |
| 0x001D | Battery SOC | 0x001C | ❌ WRONG |

**POC Evidence (lines 449-457):**
```python
# Battery Data (Registers 0x0014-0x001C)
data = self.read_input_registers(0x0014, 9)
if data:
    stats['battery_voltage'] = self._to_signed(data[0]) * 0.1  # 0x0014
    stats['battery_current'] = self._to_signed(data[1]) * 0.1  # 0x0015
    stats['battery_power'] = self._to_signed(data[2])  # 0x0016
    # data[3] is BMS connection state (0x0017)
    stats['battery_temperature'] = self._to_signed(data[4])  # 0x0018
    # data[5] is battery status (0x0019)
    # data[6-7] reserved (0x001A-0x001B)
    stats['battery_soc'] = data[8]  # 0x001C
```

**Conclusion:** Battery temperature at 0x0018, SOC at 0x001C, NOT as specified in design

### System Status

**Design Specification (Section 6.1):**

| Address | Field | Actual POC Address | Status |
|---------|-------|-------------------|--------|
| 0x0020 | Feedin Power | 0x0046-0x0047 | ❌ WRONG |
| 0x0047 | Run Mode | 0x0009 | ❌ WRONG |

**POC Evidence:**
```python
# Feed-in Power (Registers 0x0046-0x0047, 32-bit signed)
data = self.read_input_registers(0x0046, 2)

# System Status (Registers 0x0008-0x0009)
data = self.read_input_registers(0x0008, 2)
if data:
    stats['inverter_temperature'] = self._to_signed(data[0])  # 0x0008
    stats['run_mode'] = self._get_run_mode(data[1])  # 0x0009
```

**Conclusion:** Feedin power is 32-bit at 0x0046-0x0047, Run mode at 0x0009

[Return to Table of Contents](<#table of contents>)

---

## Verified Registers

### Input Registers (Function Code 0x04) - Corrected Map

#### PV String Parameters (0x0003-0x000B)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x0003 | PV1 Voltage | uint16 | 0.1 | V | ✅ |
| 0x0004 | PV2 Voltage | uint16 | 0.1 | V | ✅ |
| 0x0005 | PV1 Current | uint16 | 0.1 | A | ✅ |
| 0x0006 | PV2 Current | uint16 | 0.1 | A | ✅ |
| 0x0007 | Grid Frequency (legacy) | uint16 | 0.01 | Hz | ⚠️ POC skips |
| 0x0008 | Inverter Temperature | int16 | 1 | °C | ✅ |
| 0x0009 | Run Mode | uint16 | 1 | enum | ✅ |
| 0x000A | PV1 Power | uint16 | 1 | W | ✅ |
| 0x000B | PV2 Power | uint16 | 1 | W | ✅ |

#### Battery Parameters (0x0014-0x001C)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x0014 | Battery Voltage | int16 | 0.1 | V | ✅ |
| 0x0015 | Battery Current | int16 | 0.1 | A | ✅ |
| 0x0016 | Battery Power | int16 | 1 | W | ✅ |
| 0x0017 | BMS Connection State | uint16 | 1 | bool | ✅ |
| 0x0018 | Battery Temperature | int16 | 1 | °C | ✅ |
| 0x0019 | Battery Status | uint16 | 1 | enum | ✅ |
| 0x001A | Reserved | - | - | - | - |
| 0x001B | Reserved | - | - | - | - |
| 0x001C | Battery SOC | uint16 | 1 | % | ✅ |

#### Battery Charge Energy (0x0020)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x0020 | Battery Charge Today | uint16 | 0.1 | kWh | ✅ |

#### Feed-in Power (0x0046-0x0047)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x0046 | Feedin Power (Low) | uint16 | - | - | ✅ |
| 0x0047 | Feedin Power (High) | uint16 | - | - | ✅ |

**Note:** 32-bit signed little-endian value. Positive = export, Negative = import

#### Energy Generation (0x0050-0x0053)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x0050 | Energy Today | uint16 | 0.1 | kWh | ✅ |
| 0x0051 | Unknown | - | - | - | - |
| 0x0052 | Energy Total (Low) | uint16 | - | - | ✅ |
| 0x0053 | Energy Total (High) | uint16 | - | - | ✅ |

**Note:** Energy Total is 32-bit unsigned little-endian, scale 0.1 kWh

#### Grid Three-Phase Parameters (0x006A-0x0075)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x006A | Grid Voltage R | uint16 | 0.1 | V | ✅ |
| 0x006B | Grid Current R | int16 | 0.1 | A | ✅ |
| 0x006C | Grid Power R | int16 | 1 | W | ✅ |
| 0x006D | Grid Frequency R | uint16 | 0.01 | Hz | ✅ |
| 0x006E | Grid Voltage S | uint16 | 0.1 | V | ✅ |
| 0x006F | Grid Current S | int16 | 0.1 | A | ✅ |
| 0x0070 | Grid Power S | int16 | 1 | W | ✅ |
| 0x0071 | Grid Frequency S | uint16 | 0.01 | Hz | ✅ |
| 0x0072 | Grid Voltage T | uint16 | 0.1 | V | ✅ |
| 0x0073 | Grid Current T | int16 | 0.1 | A | ✅ |
| 0x0074 | Grid Power T | int16 | 1 | W | ✅ |
| 0x0075 | Grid Frequency T | uint16 | 0.01 | Hz | ✅ |

#### Grid Import/Export Energy (0x0098-0x009B)

| Address | Field | Type | Scale | Unit | Verified |
|---------|-------|------|-------|------|----------|
| 0x0098 | Feedin Energy Today (Low) | uint16 | - | - | ✅ |
| 0x0099 | Feedin Energy Today (High) | uint16 | - | - | ✅ |
| 0x009A | Consumption Energy Today (Low) | uint16 | - | - | ✅ |
| 0x009B | Consumption Energy Today (High) | uint16 | - | - | ✅ |

**Note:** Both are 32-bit unsigned little-endian, scale 0.01 kWh

[Return to Table of Contents](<#table of contents>)

---

## Missing Registers

### Registers Not Covered in Design Specification

**Critical gaps identified:**

1. **Grid Frequency** (0x006D, 0x0071, 0x0075) - per phase
2. **BMS Connection State** (0x0017)
3. **Battery Status** (0x0019) - charge/discharge/stop enumeration
4. **Battery Charge Today** (0x0020)
5. **Energy Total** (0x0052-0x0053) - cumulative generation
6. **Feedin Energy Today** (0x0098-0x0099) - grid export
7. **Consumption Energy Today** (0x009A-0x009B) - grid import

### Register Ranges Requiring Investigation

- 0x0000-0x0002: Unknown content
- 0x000C-0x0013: Unknown content (18 registers)
- 0x001D-0x001F: Unknown content
- 0x0021-0x0045: Unknown content (37 registers!)
- 0x0048-0x004F: Unknown content
- 0x0051: Unknown content
- 0x0054-0x0069: Unknown content (22 registers)
- 0x0076-0x0097: Unknown content (34 registers!)

**Total unverified registers:** >100 registers

[Return to Table of Contents](<#table of contents>)

---

## Recommended Corrections

### Priority 1: Immediate Updates Required

#### Update Section 6.1 Input Register Table

Replace entire table with verified register map from POC. Critical corrections:

**Grid Parameters:**
- Change from 0x0000-0x0008 → 0x006A-0x0075
- Add grid frequency per phase (0x006D, 0x0071, 0x0075)

**PV Parameters:**
- Change addresses: 0x0009-0x000C → 0x0003-0x0006
- Add PV power registers: 0x000A-0x000B
- Move inverter temperature to 0x0008
- Move run mode to 0x0009

**Battery Parameters:**
- Keep voltage/current/power at 0x0014-0x0016 (correct)
- Change temperature: 0x001C → 0x0018
- Change SOC: 0x001D → 0x001C
- Add BMS connection state: 0x0017
- Add battery status: 0x0019

**System Status:**
- Change feedin power: 0x0020 → 0x0046-0x0047 (32-bit)
- Change run mode: 0x0047 → 0x0009

**Energy Totals:**
- Add Energy Today: 0x0050
- Add Energy Total: 0x0052-0x0053 (32-bit)
- Add Battery Charge Today: 0x0020
- Add Feedin Energy Today: 0x0098-0x0099 (32-bit)
- Add Consumption Energy Today: 0x009A-0x009B (32-bit)

#### Update Section 5.2 Data Structures

Add missing fields to dataclasses:

```python
@dataclass
class GridMetrics:
    """Three-phase grid electrical parameters."""
    voltage_r: float
    voltage_s: float
    voltage_t: float
    current_r: float
    current_s: float
    current_t: float
    power_r: float
    power_s: float
    power_t: float
    frequency_r: float  # ADD
    frequency_s: float  # ADD
    frequency_t: float  # ADD
    timestamp: datetime

@dataclass
class BatteryMetrics:
    """Battery system parameters."""
    voltage: float
    current: float
    power: int
    soc: int
    temperature: int
    bms_connected: bool  # ADD
    battery_status: int  # ADD (enum: charge/discharge/stop)
    capacity: int
    timestamp: datetime

@dataclass
class EnergyStats:  # ADD NEW
    """Energy accounting."""
    generation_today: float  # kWh
    generation_total: float  # kWh
    battery_charge_today: float  # kWh
    feedin_today: float  # kWh
    consumption_today: float  # kWh
    timestamp: datetime
```

#### Update Section 6.1 Enumeration Values

Add battery status enumeration:

**Battery Status (0x0019):**
- 0: Stop/Idle
- 1: Charging
- 2: Discharging

### Priority 2: Complete Register Map

Create comprehensive register map document:

1. Map all registers from 0x0000 to 0x00FF
2. Identify purpose of unknown register ranges
3. Verify against official Solax protocol PDF
4. Document multi-register (32-bit) values
5. Add register read optimization groups

### Priority 3: Update Code Examples

Revise all code examples in Sections 5.x and 13.x to use correct addresses.

### Priority 4: Add Protocol Notes

Document critical protocol details:

1. 32-bit values use little-endian byte order
2. Signed conversion required for certain registers
3. Optimal register groupings for batch reads
4. Register access patterns for efficiency

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-29 | Verification Team | Initial verification report |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
