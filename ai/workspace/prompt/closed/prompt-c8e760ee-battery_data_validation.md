Created: 2026 September 29

```yaml
prompt_info:
  id: "prompt-c8e760ee"
  task_type: "debug"
  source_ref: "change-c8e760ee"
  target_profile: "engine"
  date: "2026-09-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-c8e760ee"
    change_iteration: 1

context:
  purpose: "Stop a short or missing battery register list from aborting the poll cycle."
  integration: >
    SolaxInverterClient._process_battery_data is called only from
    poll_inverter() after a successful read. The fix is local to that method.
  knowledge_references: []
  constraints:
    - "Modify only src/solax_modbus/main.py (_process_battery_data) and tests/test_solax_poll.py"
    - "Do not change poll_inverter, read_registers, REGISTER_MAPPINGS or any other method"
    - "Do not create any other file"
    - "Valid 9-register input must produce exactly the current result"

specification:
  description: "Guard clause in _process_battery_data plus two unit tests."
  requirements:
    functional:
      - "expected = self.REGISTER_MAPPINGS['battery_data']['count']"
      - "If regs is None or len(regs) < expected: logger.warning(...) naming expected and received counts, return {}"
      - "Otherwise return the existing dict unchanged"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "PEP 8"
        - "Use the module-level logger"
        - "Update the method docstring to state the empty-dict behaviour"

design:
  architecture: "Guard clause at method entry"
  components:
    - name: "_process_battery_data"
      type: "function"
      purpose: "Convert battery registers to metrics"
      interface:
        inputs:
          - name: "regs"
            type: "list | None"
            description: "Battery registers from address 0x0014, count 9"
        outputs:
          type: "Dict[str, Any]"
          description: "Battery metrics, or {} when regs is None or too short"
        raises: []
      logic:
        - "Read expected count from REGISTER_MAPPINGS"
        - "Guard: None or short -> warning, return {}"
        - "Existing conversion unchanged"
  dependencies:
    internal: []
    external: []

error_handling:
  strategy: "Log and degrade: return no battery metrics for this poll"
  exceptions: []
  logging:
    level: "WARNING"
    format: "Battery data incomplete: expected <n> registers, got <m>"

testing:
  unit_tests:
    - scenario: "test_process_battery_data_short: regs with 5 values"
      expected: "result == {}"
    - scenario: "test_process_battery_data_none: regs None"
      expected: "result == {}"
  edge_cases:
    - "Existing test_process_battery_data must still pass unchanged"
  validation:
    - "python -m pytest tests/test_solax_poll.py -q passes"

deliverable:
  format_requirements:
    - "Save changes directly to the specified paths"
    - "Execute pytest for tests/test_solax_poll.py on completion; report pass/fail summary"
  files:
    - path: "src/solax_modbus/main.py"
      content: "Guard clause and docstring update in _process_battery_data only"
    - path: "tests/test_solax_poll.py"
      content: "Two new tests in the existing test class, after test_process_battery_data"

success_criteria:
  - "Short and None input return {} and log a warning"
  - "Valid input unchanged; all tests in tests/test_solax_poll.py pass"
  - "No other file changed"

element_registry:
  source: "ai/workspace/design/design-solax-modbus-name_registry-master.md"
  entries:
    functions:
      - name: "_process_battery_data"
        module: "solax_modbus.main"
        signature: "_process_battery_data(self, regs: list) -> Dict[str, Any]"

notes: "First live engine run in solax-modbus after the AI-G&O layout migration (pilot for AI-G&O change-5bcd46ad)."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.11"
  schema_type: "t03_prompt"
```

```yaml
tactical_brief: >
  Project root: /Users/williamwatson/Documents/GitHub/solax-modbus.
  Edit exactly two files, using absolute paths:
  (1) /Users/williamwatson/Documents/GitHub/solax-modbus/src/solax_modbus/main.py
  — in SolaxInverterClient._process_battery_data only, add a guard at the top:
  expected = self.REGISTER_MAPPINGS['battery_data']['count']; if regs is None
  or len(regs) < expected, call logger.warning("Battery data incomplete:
  expected %d registers, got %s", expected, None if regs is None else len(regs))
  and return {}. Leave the existing return dict unchanged. Update the
  docstring to say an empty dict is returned for missing or short input.
  (2) /Users/williamwatson/Documents/GitHub/solax-modbus/tests/test_solax_poll.py
  — directly after test_process_battery_data, add
  test_process_battery_data_short (regs = [2705, 124, 3354, 0, 24], assert
  result == {}) and test_process_battery_data_none (regs = None, assert
  result == {}), using the existing client fixture.
  Do not modify any other method or file and do not create files. List both
  absolute paths as deliverables in work-summary.txt.
  Success: the two new tests and all existing tests in tests/test_solax_poll.py pass.
```

---

Copyright (c) 2026 William Watson. MIT License.
