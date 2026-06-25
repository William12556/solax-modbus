# Prompt: Fix Pymodbus API Compatibility - Replace 'slave' with 'unit' Parameter

Created: 2025-01-21

---

## Table of Contents

- [Prompt Information](<#prompt information>)
- [Context](<#context>)
- [Specification](<#specification>)
- [Design](<#design>)
- [Data Schema](<#data schema>)
- [Error Handling](<#error handling>)
- [Testing](<#testing>)
- [Deliverable](<#deliverable>)
- [Success Criteria](<#success criteria>)
- [Version History](<#version history>)

---

## Prompt Information

```yaml
prompt_info:
  id: "prompt-46d32423"
  task_type: "debug"
  source_ref: "change-2b7a0458"
  date: "2025-01-21"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-2b7a0458"
    change_iteration: 1
```

[Return to Table of Contents](<#table of contents>)

---

## Context

```yaml
context:
  purpose: "Fix TypeError caused by pymodbus API version incompatibility in SolaxInverterClient"
  integration: "Modbus client component for reading Solax X3 Hybrid 6.0-D inverter registers"
  knowledge_references: []
  constraints:
    - "Must maintain backward compatibility with existing functionality"
    - "No changes to register addresses or protocol logic"
    - "Preserve all error handling and retry mechanisms"
    - "Read-only operations only"
```

[Return to Table of Contents](<#table of contents>)

---

## Specification

```yaml
specification:
  description: |
    Update all Modbus register read operations in SolaxInverterClient to use pymodbus 3.x 
    compatible 'unit' parameter instead of deprecated 'slave' parameter. The change affects 
    line 162 in read_registers() method where read_input_registers is called with slave=self.unit_id.
  
  requirements:
    functional:
      - "Replace all occurrences of slave=self.unit_id with unit=self.unit_id"
      - "Verify all read_input_registers calls updated"
      - "Verify all read_holding_registers calls updated (if any exist)"
      - "Maintain identical register reading behavior"
      - "Preserve connection logic, retry mechanisms, and error handling"
    
    technical:
      language: "Python"
      version: "3.13"
      standards:
        - "Maintain existing thread-safety"
        - "Preserve all error handling patterns"
        - "Keep comprehensive debug logging with traceback"
        - "Maintain professional docstrings"
        - "PEP 8 compliant code style"
  
  performance:
    - target: "No performance impact"
      metric: "Same execution time as before"
```

[Return to Table of Contents](<#table of contents>)

---

## Design

```yaml
design:
  architecture: "Minimal surgical change to existing SolaxInverterClient class"
  
  components:
    - name: "read_registers"
      type: "method"
      purpose: "Read Modbus input registers with updated API parameter"
      interface:
        inputs:
          - name: "address"
            type: "int"
            description: "Starting register address"
          - name: "count"
            type: "int"
            description: "Number of registers to read"
          - name: "description"
            type: "str"
            description: "Description for logging"
        outputs:
          type: "Optional[list]"
          description: "List of register values or None on error"
        raises:
          - "ModbusException"
          - "Exception"
      logic:
        - "Call self.client.read_input_registers with address, count, unit parameters"
        - "Check result for errors using result.isError()"
        - "Log successful reads at DEBUG level"
        - "Log errors at ERROR level with exception info"
        - "Return register list on success, None on failure"
  
  dependencies:
    internal:
      - "No internal dependencies changed"
    external:
      - "pymodbus >= 3.0.0 (API requirement)"
```

[Return to Table of Contents](<#table of contents>)

---

## Data Schema

```yaml
data_schema:
  entities: []  # No data schema changes
```

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

```yaml
error_handling:
  strategy: "Preserve existing error handling - no changes"
  exceptions:
    - exception: "ModbusException"
      condition: "Modbus protocol errors"
      handling: "Log with traceback, return None"
    - exception: "Exception"
      condition: "Unexpected errors"
      handling: "Log with traceback, return None"
  logging:
    level: "ERROR for exceptions, DEBUG for successful reads"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

[Return to Table of Contents](<#table of contents>)

---

## Testing

```yaml
testing:
  unit_tests:
    - scenario: "Read input registers with valid parameters"
      expected: "No TypeError, successful register read"
    - scenario: "Read with connection failure"
      expected: "Proper error handling, no API-related exceptions"
  
  edge_cases:
    - "First register read after connection"
    - "Multiple sequential reads"
    - "Read during network timeout"
  
  validation:
    - "Application starts without TypeError"
    - "All register reads complete successfully"
    - "Error logs show proper exception types (not TypeError)"
```

[Return to Table of Contents](<#table of contents>)

---

## Deliverable

```yaml
deliverable:
  format_requirements:
    - "Save updated code directly to src/solax_modbus/main.py"
    - "Maintain exact file structure and formatting"
    - "Preserve all comments and docstrings"
  
  files:
    - path: "src/solax_modbus/main.py"
      content: |
        Update line 162 in read_registers method:
        
        BEFORE:
        result = self.client.read_input_registers(
            address=address,
            count=count,
            slave=self.unit_id
        )
        
        AFTER:
        result = self.client.read_input_registers(
            address=address,
            count=count,
            unit=self.unit_id
        )
        
        Search for any other occurrences of read_input_registers or read_holding_registers
        with slave= parameter and update those as well.
```

[Return to Table of Contents](<#table of contents>)

---

## Success Criteria

```yaml
success_criteria:
  - "No TypeError exceptions when reading registers"
  - "All register read operations execute successfully"
  - "Application runs without crashes"
  - "Logging shows successful register reads"
  - "No behavioral changes in data collection"
  - "pymodbus 3.x API compatibility confirmed"
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Author          | Changes                    |
| ------- | ---------- | --------------- | -------------------------- |
| 1.0     | 2025-01-21 | William Watson  | Initial prompt creation    |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
