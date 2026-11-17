---
paths: ["src/api/**/*"]
---

# API code (src/api/)

- Every handler validates input before doing work and returns a structured error
  `{errorCategory, isRetryable, description}` - never a bare string or stack trace.
- `errorCategory` is one of `validation`, `not_found`, `transient`, `policy`.
  Only `transient` errors set `isRetryable: true`.
- Handlers are thin: business rules live in plain functions that tests can call directly.
- Data is fictional; no real endpoints, hosts, or credentials.
