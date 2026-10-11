# API contract

- `GET /health`: status and synthetic match identity.
- `GET /sse/events?match_id=synthetic_demo_001&speed=4&start=00:20`: replay events followed by a shift signal. Event match timestamps are preserved; speed controls emission pacing.
- `GET /sse/observed?match_id=synthetic_demo_001&replay_id=replay_demo`: `metrics_tick` updates.
- `GET /observed/latest?match_id=synthetic_demo_001`: latest qualified immutable evidence, or `null`.
- `GET /observed/{evidence_id}`: canonical `EvidenceObject`, 404 for unknown ID.
- `POST /what-if` JSON `{"evidence_id":"...","mode":"hold_current_pressing","horizon_sec":600}`: immutable `WhatIfResult`.
- `POST /narrative?evidence_id=...`: deterministic local evidence-grounded narrative.

SSE messages use `text/event-stream` with JSON `data` containing `type`, `replay_id`, `sequence_number`, `match_id`, and `replay`. The What-If endpoint accepts 60–1800 seconds and rejects unknown evidence or scenario modes.
