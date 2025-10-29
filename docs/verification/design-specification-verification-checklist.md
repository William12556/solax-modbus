# Design Specification Verification Checklist

Created: 2025 10 29

## Table of Contents

- [Verification Status](<#verification status>)
- [Input Registers Verification](<#input registers verification>)
- [Holding Registers Verification](<#holding registers verification>)
- [Data Type Verification](<#data type verification>)
- [Enumeration Verification](<#enumeration verification>)
- [Register Map Gaps](<#register map gaps>)
- [Architecture Verification](<#architecture verification>)
- [Next Actions](<#next actions>)

[Return to Table of Contents](<#table of contents>)

---

## Verification Status

**Document:** solax-modbus-software-design-specification.md v1.0  
**Protocol Reference:** Hybrid-X1X3-G4-ModbusTCPRTU-V3.21-English_0622-public-version.pdf  
**Verification Date:** 2025-10-29  
**Status:** Pending Manual Verification

### Critical Items Requiring Verification

| Item | Section | Status | Priority |
|------|---------|--------|----------|
| Input register addresses | 6.1 | UNVERIFIED | P1 |
| Holding register addresses | 6.1 | UNVERIFIED | P1 |
| Data type definitions | 6.1 | UNVERIFIED | P1 |
| Scaling factors | 6.1 | UNVERIFIED | P1 |
| Enumeration values | 6.1 | UNVERIFIED | P1 |
| Register gaps | 6.1 | UNVERIFIED | P2 |
| Function codes | 6.1 | UNVERIFIED | P2 |

[Return to Table of Contents](<#table of contents>)

---

## Input Registers Verification

### Grid Parameters (Phase R/S/T)

**Design Specification Claims:**

| Address | Field | Type | Scale | Unit |
|---------|-------|------|-------|------|
| 0x0000 | Grid Voltage Phase R | uint16 | 0.1 | V |
| 0x0001 | Grid Voltage Phase S | uint16 | 0.1 | V |
| 0x0002 | Grid Voltage Phase T | uint16 | 0.1 | V |
| 0x0003 | Grid Current Phase R | uint16 | 0.1 | A |
| 0x0004 | Grid Current Phase S | uint16 | 0.1 | A |
| 0x0005 | Grid Current Phase T | uint16 | 0.1 | A |
| 0x0006 | Grid Power Phase R | int16 | 1 | W |
| 0x0007 | Grid Power Phase S | int16 | 1 | W |
| 0x0008 | Grid Power Phase T | int16 | 1 | W |

**Verification Required:**
- [ ] Confirm addresses 0x0000-0x0008 are correct for X3 Hybrid
- [ ] Verify scaling factor is 0.1 for voltage
- [ ] Verify scaling factor is 0.1 for current
- [ ] Verify power uses int16 (signed) vs uint16
- [ ] Confirm register order (R, S, T phases)

### PV Parameters

**Design Specification Claims:**

| Address | Field | Type | Scale | Unit |
|---------|-------|------|-------|------|
| 0x0009 | PV1 Voltage | uint16 | 0.1 | V |
| 0x000A | PV2 Voltage | uint16 | 0.1 | V |
| 0x000B | PV1 Current | uint16 | 0.1 | A |
| 0x000C | PV2 Current | uint16 | 0.1 | A |

**Verification Required:**
- [ ] Confirm addresses 0x0009-0x000C are correct
- [ ] Verify there are only 2 PV inputs (not 3)
- [ ] Verify scaling factor is 0.1
- [ ] Check if PV power is calculated or read from registers

**Missing from Design:**
- PV1 Power register (if exists)
- PV2 Power register (if exists)
- Total PV power register (if exists)

### Battery Parameters

**Design Specification Claims:**

| Address | Field | Type | Scale | Unit |
|---------|-------|------|-------|------|
| 0x0014 | Battery Voltage | uint16 | 0.1 | V |
| 0x0015 | Battery Current | int16 | 0.1 | A |
| 0x0016 | Battery Power | int16 | 1 | W |
| 0x001C | Battery Temperature | int16 | 1 | °C |
| 0x001D | Battery SOC | uint16 | 1 | % |

**Verification Required:**
- [ ] Confirm address 0x0014 for battery voltage
- [ ] Confirm address 0x0015 for battery current (signed)
- [ ] **CRITICAL:** Verify address 0x0016 for battery power
- [ ] Check gap between 0x0016 and 0x001C (registers 0x0017-0x001B)
- [ ] **CRITICAL:** Verify address 0x001C for battery temperature
- [ ] Confirm address 0x001D for battery SOC

**Potential Issues:**
- Large gap between battery power and temperature registers suggests missing data
- Need to verify what registers 0x0017-0x001B contain

### System Status

**Design Specification Claims:**

| Address | Field | Type | Scale | Unit |
|---------|-------|------|-------|------|
| 0x0020 | Feedin Power | int16 | 1 | W |
| 0x0047 | Run Mode | uint16 | 1 | enum |

**Verification Required:**
- [ ] **CRITICAL:** Verify address 0x0020 for feedin power
- [ ] Verify address 0x0047 for run mode
- [ ] Identify registers between 0x0020 and 0x0047 (gap of 39 registers!)

**Missing from Design:**
- Grid frequency register
- Inverter temperature register
- Total output power register
- Energy today/total registers
- Fault/error code registers
- Firmware version register

[Return to Table of Contents](<#table of contents>)

---

## Holding Registers Verification

**Design Specification Claims:**

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x001F | Operating Mode | uint16 | 1 | enum | RW |
| 0x0020 | Charge Start Hour | uint16 | 1 | hour | RW |
| 0x0021 | Charge Start Minute | uint16 | 1 | minute | RW |
| 0x0022 | Charge End Hour | uint16 | 1 | hour | RW |
| 0x0023 | Charge End Minute | uint16 | 1 | minute | RW |
| 0x0024 | Discharge Start Hour | uint16 | 1 | hour | RW |
| 0x0025 | Discharge Start Minute | uint16 | 1 | minute | RW |
| 0x0026 | Discharge End Hour | uint16 | 1 | hour | RW |
| 0x0027 | Discharge End Minute | uint16 | 1 | minute | RW |
| 0x0028 | Charge Power Limit | uint16 | 1 | W | RW |
| 0x0029 | Discharge Power Limit | uint16 | 1 | W | RW |

**Verification Required:**
- [ ] **CRITICAL:** Confirm holding register base address
- [ ] Verify operating mode is at 0x001F
- [ ] Verify time window register addresses
- [ ] Verify power limit register addresses
- [ ] Check if multiple time windows are supported
- [ ] Identify valid ranges for all writable registers

**Potential Issues:**
- Holding register 0x001F conflicts with input register addressing scheme
- Typical Modbus devices separate input (3xxxx) and holding (4xxxx) register spaces
- Need to verify function codes: 0x03 for holding, 0x04 for input

**Missing from Design:**
- Grid export limit register (if supported)
- Battery SOC limits (min/max charge levels)
- Remote control enable/disable register
- Password/lock registers

[Return to Table of Contents](<#table of contents>)

---

## Data Type Verification

### Signed vs Unsigned Integers

**Design Claims Signed (int16):**
- Grid Power (R/S/T phases) - VERIFY: Could be negative (grid feed-in)
- Battery Current - VERIFY: Positive = charge, negative = discharge
- Battery Power - VERIFY: Positive = charge, negative = discharge
- Battery Temperature - VERIFY: Should support negative temperatures
- Feedin Power - VERIFY: Sign convention unclear

**Design Claims Unsigned (uint16):**
- Grid Voltage - Reasonable (always positive)
- Grid Current - VERIFY: Should always be positive
- PV Voltage - Reasonable (always positive)
- PV Current - Reasonable (always positive)
- Battery Voltage - Reasonable (always positive)
- Battery SOC - Reasonable (0-100%)
- Run Mode - Reasonable (enumeration)

**Verification Required:**
- [ ] Confirm sign convention for power values
- [ ] Verify battery current sign (charge vs discharge)
- [ ] Clarify feedin power sign convention
- [ ] Check if grid current is ever negative

### Multi-Register Values

**Missing from Design:**
- Are there any 32-bit (2-register) values?
- Daily energy counters (typically uint32)
- Total energy counters (typically uint32)
- Operating hours (typically uint32)

**Verification Required:**
- [ ] Check for multi-register values in protocol
- [ ] Verify byte order (big-endian vs little-endian)
- [ ] Confirm register pairing (high/low word order)

[Return to Table of Contents](<#table of contents>)

---

## Enumeration Verification

### Operating Mode (0x001F)

**Design Specification Claims:**
- 0: Self-use mode
- 1: Feed-in priority
- 2: Backup mode
- 3: Manual mode

**Verification Required:**
- [ ] Confirm enumeration values 0-3
- [ ] Verify mode names match protocol
- [ ] Check for additional modes (e.g., off-grid, force charge)
- [ ] Identify default/safe mode

### Run Mode (0x0047)

**Design Specification Claims:**
- 0: Waiting
- 1: Checking
- 2: Normal
- 3: Fault
- 4: Permanent fault
- 5: Update mode
- 6: Off-grid waiting
- 7: Off-grid
- 8: Self-testing
- 9: Idle
- 10: Standby

**Verification Required:**
- [ ] Confirm all 11 run mode values
- [ ] Verify mode names match protocol
- [ ] Check for additional modes beyond 10
- [ ] Identify which modes require alerts

[Return to Table of Contents](<#table of contents>)

---

## Register Map Gaps

### Identified Gaps Requiring Investigation

**Gap 1: 0x000D - 0x0013 (7 registers)**
Between PV Current and Battery Voltage

**Potential contents:**
- Additional PV parameters
- Inverter output parameters
- AC output voltage/current/power

**Gap 2: 0x0017 - 0x001B (5 registers)**
Between Battery Power and Battery Temperature

**Potential contents:**
- Additional battery parameters
- BMS communication status
- Battery capacity information

**Gap 3: 0x001E - 0x001F (2 registers)**
Between Battery SOC and Feedin Power

**Potential contents:**
- Battery charging state
- Inverter load power

**Gap 4: 0x0021 - 0x0046 (38 registers!)**
Between Feedin Power and Run Mode

**Potential contents:**
- Energy statistics (today, total)
- Operating hours
- Fault codes
- Grid frequency
- Inverter temperature
- EPS output parameters (if applicable)
- Additional system parameters

**Verification Required:**
- [ ] Map all registers in gaps
- [ ] Identify which are relevant to monitoring
- [ ] Determine which should be in design specification

[Return to Table of Contents](<#table of contents>)

---

## Architecture Verification

### Function Code Usage

**Design Assumes:**
- 0x03: Read Holding Registers
- 0x04: Read Input Registers
- 0x06: Write Single Register (implied)
- 0x10: Write Multiple Registers (implied)

**Verification Required:**
- [ ] Confirm function codes supported by inverter
- [ ] Verify read vs write register separation
- [ ] Check if broadcast (unit ID 0) is supported
- [ ] Verify maximum registers per read operation

### Protocol Parameters

**Design Assumes:**
- Port: 502 (Modbus TCP standard)
- Unit ID: 1 (default slave address)
- Timeout: 1 second
- Byte order: Big-endian (Modbus standard)

**Verification Required:**
- [ ] Confirm default port 502
- [ ] Verify unit ID can be configured
- [ ] Check recommended timeout value
- [ ] Verify byte order (should be big-endian per Modbus spec)

### Data Acquisition Strategy

**Design Proposes:**
- Batch reading of contiguous registers
- Minimum 1-second polling interval
- Separate reads for different register groups

**Verification Required:**
- [ ] Confirm maximum registers per read
- [ ] Verify minimum polling interval restriction
- [ ] Check if inverter supports multiple simultaneous connections
- [ ] Identify optimal register groupings for batch reads

[Return to Table of Contents](<#table of contents>)

---

## Next Actions

### Priority 1: Manual Protocol Review

Required actions:
1. Open Hybrid-X1X3-G4-ModbusTCPRTU-V3.21-English_0622-public-version.pdf
2. Create complete register map with all addresses
3. Verify each address, data type, and scaling factor
4. Document all enumerations and their meanings
5. Identify all missing registers in current design

### Priority 2: Update Design Specification

Based on verification findings:
1. Correct all register addresses
2. Add missing registers to Section 6.1
3. Complete enumeration definitions
4. Add register valid ranges
5. Document multi-register values
6. Add register map diagrams

### Priority 3: Create Register Map Document

Separate detailed register map document:
1. Complete input register table (0x0000 onwards)
2. Complete holding register table
3. Register groupings for efficient batch reads
4. Register access patterns
5. Error codes and fault registers

### Priority 4: Validate Against POC

Cross-reference with solax-modbus-poc.md:
1. Verify POC testing used correct addresses
2. Confirm observed data matches expected types
3. Validate scaling factors against real data
4. Document any discrepancies found

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-29 | Verification Team | Initial verification checklist |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
