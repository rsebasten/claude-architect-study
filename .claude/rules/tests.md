---
paths: ["**/*.test.*", "**/test_*.py"]
---

# Test files

- Use the standard-library `unittest`; run with `python3 -m unittest <file>`.
- Tests never call the Claude API or any network service. Exercise tool handlers and
  hooks directly with fixed inputs.
- One behavior per test, named `test_<behavior>`; cover each `errorCategory` path.
- Reset shared fixture data in `setUp` (see `reset_data()` in `escalation_agent.py`).
