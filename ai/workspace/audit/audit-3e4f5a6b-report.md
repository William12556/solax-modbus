# Audit Report — solax-modbus src/

Generated: 2026-06-28

---
## src/solax_modbus/emulator/solax_emulator.py :: SolaxEmulatorState.__init__  [iteration 27]
- **Type:** style
- **Location:** line 103 (range 103–112)
- **Description:** Constructor lacks a docstring to document its purpose and the state variables it initializes.
- **Severity:** low
- **Type:** conformance
- **Location:** line 103 (range 103–112)
- **Description:** Initial state values (25°C for inverter_temp, 20°C for battery_temp) are hardcoded without using named constants from the configuration section, making them harder to modify centrally.
- **Severity:** low
- **Type:** error-handling
- **Location:** line 103 (range 103–112)
- **Description:** The constructor initializes state without validation of the initial values from configuration constants, which could lead to unexpected behavior if constants contain invalid values.
- **Severity:** low
- **Type:** dead-code
- **Location:** line 110-111
- **Description:** The inverter_temp and battery_temp variables are initialized but there's no clear usage of these temperature values elsewhere in the codebase, suggesting they may be dead code.
- **Severity:** low

---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.validate  [iteration 23]
- **Type:** style
- **Location:** line 76
- **Description:** Docstring is minimal and doesn't describe parameters (address, count) or the return value behavior (boolean).
- **Severity:** low
- **Type:** error-handling
- **Location:** line 76
- **Description:** Method doesn't validate the count parameter, which could lead to unexpected behavior if negative or extremely large values are provided.
- **Severity:** medium

## Summary

Findings by severity:

- High: 0
- Medium: 0
- Low: 0

---

## Findings

---
## src/solax_modbus/emulator/solax_emulator.py :: SolaxEmulatorState.get_input_registers  [iteration 10]
- **Type:** style
- **Location:** line 159 (range 159–220)
- **Description:** Docstring is minimal and doesn't describe the method's purpose, return value, or the register mapping it implements.
- **Severity:** low
---
## src/solax_modbus/main.py :: SolaxInverterClient._process_battery_data  [iteration 18]
- **Type:** error-handling
- **Location:** line 280 (range 280–288)
- **Description:** No parameter validation or error handling for the `regs` parameter, which could cause IndexError if the input list is shorter than expected or None.
- **Severity:** medium
---
## src/solax_modbus/main.py :: SolaxInverterClient._process_grid_data  [iteration 17]
- **Type:** error-handling
- **Location:** line 252 (range 252–268)
- **Description:** Method lacks input validation for the 'regs' parameter, assuming exactly 12 registers are provided without checking length or None values, which could cause IndexError if input is malformed.
- **Severity:** medium
---
---
## src/solax_modbus/emulator/solax_emulator.py :: SolaxEmulatorState.get_holding_registers  [iteration 17]
- **Type:** style
- **Location:** line 236-237
- **Description:** The calculation `BATTERY_MAX_CHARGE_CURRENT * int(BATTERY_VOLTAGE)` and `BATTERY_MAX_DISCHARGE_CURRENT * int(BATTERY_VOLTAGE)` could result in values that exceed typical 16-bit register limits (65535), potentially causing overflow or incorrect values in the emulator.
- **Severity:** medium
- **Type:** dead-code
- **Location:** line 223-242
- **Description:** The method initializes a large array of 128 registers but only populates registers at addresses 0x1F through 0x29, leaving most register values as default zeros (0). This suggests potential waste or incomplete register mapping.
- **Severity:** low
---
## src/solax_modbus/main.py :: InverterDisplay.display_statistics  [iteration 14]
- **Type:** error-handling
- **Location:** line 310 (range 310–408)
- **Description:** Method lacks validation of data types and field existence before accessing dictionary values, which could cause KeyError or TypeError if data structure is malformed.
- **Severity:** medium
- **Type:** conformance
- **Location:** line 310
- **Description:** Missing return type hint (-> None) in docstring despite being properly annotated in method signature.
- **Severity:** low
- **Type:** complexity
- **Location:** line 310 (range 310–408)
- **Description:** Method has approximately 100 lines with multiple nested conditionals for displaying different inverter metrics, which could be refactored into smaller display helper methods for better maintainability.
- **Severity:** low
---
## src/solax_modbus/main.py :: main  [iteration 13]
- **Type:** error-handling
- **Location:** line 438
- **Description:** The main monitoring loop catches all exceptions generically without distinguishing between different error types (e.g., connection errors, data parsing errors), which makes debugging difficult.
- **Severity:** medium
- **Type:** error-handling
- **Location:** line 456
- **Description:** There's no specific handling for ModbusException errors within the main loop, which could mask important communication issues with the inverter.
- **Severity:** low
- **Type:** dead-code
- **Location:** line 438 (range 438–456)
- **Description:** The main loop always sleeps for `poll_interval` seconds after an exception, which might be unnecessary for certain error conditions like keyboard interrupts or connection timeouts.
- **Severity:** low

---
## src/solax_modbus/emulator/solax_emulator.py :: state_update_loop  [iteration 9]
- **Type:** error-handling
- **Location:** line 331–350
- **Description:** The function uses a bare `except` clause that catches all exceptions, which could hide bugs and make debugging difficult. Consider catching specific exceptions.
- **Severity:** medium

- **Type:** complexity
- **Location:** line 331
- **Description:** The function imports the `random` module inside the `get_pv_power` method of `SolaxEmulatorState`, which is inefficient. The import should be at the top of the file.
- **Severity:** low

- **Type:** style
- **Location:** line 159 (range 159–220)
- **Description:** Method is overly long (62 lines) and combines multiple responsibilities (PV calculations, battery calculations, grid calculations, and register mapping).
- **Severity:** medium

- **Type:** complexity
- **Location:** line 159 (range 159–220)
- **Description:** Method has high cognitive complexity due to handling multiple calculations in one place without helper methods to break down functionality.
- **Severity:** medium

- **Type:** error-handling
- **Location:** line 164, 165
- **Description:** Potential division by zero risk in PV current calculations despite guards for zero voltage, as the division could still occur in edge cases.
- **Severity:** low

- **Type:** conformance
- **Location:** line 192–218
- **Description:** Register mapping uses magic numbers (0x00, 0x01, etc.) without documentation of what these addresses represent in the Solax protocol.
- **Severity:** medium

- **Type:** dead-code
- **Location:** line 190
- **Description:** Creates a large array of 128 registers but only uses a subset (up to 0x47), leading to potential waste and confusion about which registers are actually used.
- **Severity:** low

- **Type:** dead-code
- **Location:** line 193–195
- **Description:** Redundant calculation of grid voltage for all three phases (R, S, T) when they all use the same value.
- **Severity:** low

---
## src/solax_modbus/emulator/solax_emulator.py :: SolaxEmulatorState.update_state  [iteration 11]
- **Type:** style
- **Location:** line 126 (range 126–160)
- **Description:** Docstring is minimal and doesn't describe the method's purpose, the state variables it updates, or the business logic it implements.
- **Severity:** low

- **Type:** complexity
- **Location:** line 126 (range 126–160)
- **Description:** Method combines multiple responsibilities including PV power calculation, battery state-of-charge management, and temperature simulation without helper methods to break down functionality.
- **Severity:** medium

- **Type:** error-handling
- **Location:** line 129–131
- **Description:** No error handling for potential issues with time calculations (e.g., time going backward, which could result in negative dt values).
- **Severity:** low

- **Type:** conformance
- **Location:** line 126 (range 126–160)
- **Description:** Magic numbers are used extensively throughout the method (1000, 500, 2000, 10, 90, 45, 25, 30, 20) without defined constants for clarity.
- **Severity:** medium

- **Type:** conformance
- **Location:** line 136, 141, 147, 152
- **Description:** The method directly manipulates instance state without providing any validation or bounds checking on the calculations that modify state variables.
- **Severity:** low

- **Type:** dead-code
- **Location:** line 159–160
- **Description:** The inverter_temp and battery_temp variables are updated but there's no clear usage of these temperature values elsewhere in the codebase, suggesting they may be dead code.
- **Severity:** low

---
## src/solax_modbus/main.py :: SolaxInverterClient.poll_inverter  [iteration 7]
- **Type:** style
- **Location:** line 180 (range 180–240)
- **Description:** Method is moderately long (61 lines) and could benefit from breaking down the repeated read_registers and processing logic into smaller helper methods.
- **Severity:** low

- **Type:** complexity
- **Location:** line 180 (range 180–240)
- **Description:** Method has multiple nested conditionals and repeated patterns of reading registers and updating the data dictionary, which could be simplified with helper methods.
- **Severity:** low

- **Type:** error-handling
- **Location:** line 188–192
- **Description:** Missing error handling for the case where only one of the two required PV register sets (pv_vc_regs or pv_power_regs) is read successfully, leading to incomplete PV data processing.
- **Severity:** medium

- **Type:** error-handling
- **Location:** line 233–238
- **Description:** No validation or error handling for the run_mode mapping when the register value is not in the predefined RUN_MODES dictionary.
- **Severity:** low

- **Type:** conformance
- **Location:** line 182–236
- **Description:** Method reads multiple sets of registers independently without a transactional approach, which could lead to inconsistent data if the inverter state changes during polling.
- **Severity:** medium

- **Type:** dead-code
- **Location:** line 180 (range 180–240)
- **Description:** The method initializes an empty data dictionary but doesn't guarantee that all expected data fields will be present, potentially causing issues for downstream consumers expecting complete datasets.
- **Severity:** low

---
## src/solax_modbus/emulator/solax_emulator.py :: run_emulator  [iteration 12]
- **Type:** style
- **Location:** line 268
- **Description:** Docstring is minimal and doesn't describe parameters (host, port, unit_id) or return value behavior.
- **Severity:** low

- **Type:** error-handling
- **Location:** line 268 (range 268–320)
- **Description:** Bare except clause catches all exceptions without specific handling for different error types.
- **Severity:** medium

- **Type:** error-handling
- **Location:** line 268 (range 268–320)
- **Description:** No parameter validation for host, port, or unit_id values before starting the server.
- **Severity:** low

- **Type:** error-handling
- **Location:** line 275
- **Description:** State update thread is marked as daemon but there's no mechanism to cleanly shutdown the thread when the server stops.
- **Severity:** low

- **Type:** conformance
- **Location:** line 327–350
- **Description:** CLI argument parsing doesn't include validation for port range (should be 1-65535) or unit_id range (typically 1-255).
- **Severity:** low
---
## src/solax_modbus/main.py :: SolaxInverterClient.connect  [iteration 8]
- No findings.
---
## src/solax_modbus/emulator/solax_emulator.py :: SolaxEmulatorState._to_signed_16bit  [iteration 34]
- No findings.

---
## src/solax_modbus/main.py :: SolaxInverterClient._to_unsigned_32  [iteration 33]
- **Type:** error-handling
- **Location:** line 309 (range 309–311)
- **Description:** Method lacks parameter validation for input integers, which could cause unexpected behavior with invalid values or non-integer inputs.
- **Severity:** low

- No other findings for this method.
---
## src/solax_modbus/main.py :: SolaxInverterClient._to_signed_32  [iteration 33]
- No findings.
---
## src/solax_modbus/main.py :: SolaxInverterClient._to_signed  [iteration 31]
- No findings.

---
## src/solax_modbus/main.py :: SolaxInverterClient.disconnect  [iteration 30]
- No findings.
---
## src/solax_modbus/main.py :: SolaxInverterClient.read_registers  [iteration 14]
- **Type:** error-handling
- **Location:** line 152
- **Description:** Exception messages include the 'description' parameter directly without validation, which could potentially leak sensitive information if descriptions contain internal details in future usage.
- **Severity:** low

- **Type:** error-handling
- **Location:** line 152 (range 152–181)
- **Description:** Generic Exception catch block is used alongside specific ModbusException handling, which could mask unexpected errors and make debugging more difficult than using more specific exception types.
- **Severity:** medium

- **Type:** conformance
- **Location:** line 155
- **Description:** Method uses result.registers directly without null/None check, potentially causing AttributeError if result is None or has unexpected structure.
- **Severity:** low

- **Type:** style
- **Location:** line 155
- **Description:** Return statement at line 155 lacks a type hint annotation in the docstring, though the method signature correctly specifies Optional[list].
- **Severity:** low
---
## src/solax_modbus/emulator/solax_emulator.py :: SolaxEmulatorState.get_pv_power  [iteration 11]
- **Type:** style
- **Location:** line 121
- **Description:** The `random` module is imported inside the function body, which is inefficient and goes against Python best practices. Import should be at the top of the module.
- **Severity:** low
- **Type:** dead-code
- **Location:** line 121
- **Description:** The import of the `random` module occurs inside a function that may not always be called during execution, leading to potential unnecessary imports during runtime.
- **Severity:** low
---
## src/solax_modbus/main.py :: SolaxInverterClient._process_pv_data  [iteration 19]
- **Type:** error-handling
- **Location:** line 269 (range 269–278)
- **Description:** Method lacks input validation for 'vc_regs' and 'power_regs' parameters, assuming they contain exactly 4 and 2 elements respectively without checking length or None values, which could cause IndexError if input is malformed.
- **Severity:** medium
---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.getValues  [iteration 20]
- **Type:** style
- **Location:** line 80-88
- **Description:** Method lacks proper parameter type hints and return type annotation in the docstring, though the implementation is clear.
- **Severity:** low
---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.getValues  [iteration 20]
- **Type:** complexity
- **Location:** line 80-88
- **Description:** Method doesn't handle edge cases like negative address values, though it gracefully handles out-of-bounds access by returning default values.
- **Severity:** low
---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.getValues  [iteration 20]
- **Type:** error-handling
- **Location:** line 80-88
- **Description:** Method doesn't validate the address parameter before using it, relying on caller to use validate() method first, which could lead to unexpected behavior with negative addresses.
- **Severity:** low
---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.getValues  [iteration 20]
- **Type:** dead-code
- **Location:** line 83-85
- **Description:** Default value assignment in __init__ uses first value in list which may not be semantically appropriate for all use cases.
- **Severity:** low
---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.getValues  [iteration 20]
- **Type:** conformance
- **Location:** line 80-88
- **Description:** Method implements different behavior than pymodbus standard interface by returning default values instead of raising exceptions for out-of-bounds access.
- **Severity:** medium
---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.setValues  [iteration 21]
- **Type:** style
- **Location:** line 89 (range 89–94)
- **Description:** Method lacks proper parameter type hints and return type annotation in the docstring, though the implementation is clear.
- **Severity:** low

- **Type:** error-handling
- **Location:** line 89 (range 89–94)
- **Description:** Method doesn't validate input parameters (address and values), potentially leading to IndexError with negative addresses or None values.
- **Severity:** medium

- **Type:** error-handling
- **Location:** line 93 (range 93–94)
- **Description:** Method silently ignores values that would exceed array bounds instead of raising an exception or validating input first, inconsistent with defensive programming practices.
- **Severity:** medium

- **Type:** conformance
- **Location:** line 89 (range 89–94)
- **Description:** Method implements different error handling behavior than getValues - it doesn't use the validate() method to check bounds before writing, making behavior inconsistent between read and write operations.
- **Severity:** medium

---
## src/solax_modbus/emulator/solax_emulator.py :: DynamicModbusDataBlock.__init__  [iteration 24]
- **Type:** style
- **Location:** line 70 (range 70–74)
- **Description:** Constructor lacks docstring to document parameters (address, values) and the initialization logic.
- **Severity:** low
- **Type:** error-handling
- **Location:** line 73
- **Description:** Method uses `self.values[0]` as default_value without checking if the values list is empty, which could cause IndexError.
- **Severity:** medium
- **Type:** error-handling
- **Location:** line 70 (range 70–74)
- **Description:** Constructor accepts input parameters without type validation or sanity checking, potentially leading to runtime errors with invalid inputs.
- **Severity:** medium

---
## src/solax_modbus/main.py :: SolaxInverterClient.__init__  [iteration 29]
- **Type:** error-handling
- **Location:** line 95 (range 95–104)
- **Description:** Constructor lacks parameter validation for input values (ip, port, unit_id), which could lead to runtime errors with invalid inputs like non-numeric port values or empty IP strings.
- **Severity:** low

- No findings.