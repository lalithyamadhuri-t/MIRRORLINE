# Hindsight integration

MIRRORLINE uses a memory abstraction with the same three core operations as
Hindsight:

- `retain`: store an experience
- `recall`: retrieve relevant memories
- `reflect`: reason across accumulated memories

The official Python client is supported in `hindsight_adapter.py`.

Environment variables:

```text
HINDSIGHT_URL=http://localhost:8888
HINDSIGHT_API_KEY=
HINDSIGHT_BANK_ID=mirrorline-demo
```

The current official Python client exposes async `aretain`, `arecall`, and
`areflect` methods, which are appropriate for FastAPI async applications.

For the hackathon, connect the application to the current Hindsight Cloud or
self-hosted instance and keep the local deterministic memory mode as a
development fallback.
