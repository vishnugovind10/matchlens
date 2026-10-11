# Architecture

The source of truth is the JSONL synthetic event stream. The backend parses immutable event objects, computes rolling metrics, detects a high-press pattern, and builds an immutable `EvidenceObject`. The observed REST and SSE routes expose different views; neither frontend view creates match intelligence.

```text
EVENT STREAM → NORMALISATION → MATCH STATE ENGINE
                                  ├─ Pressing
                                  ├─ Recoveries / turnovers
                                  ├─ Territory
                                  └─ Attacking threat
                                         ↓
                                  CHANGE DETECTOR
                                         ↓
                              EvidenceObject (observed)
                               ├─ Insight / narrative
                               └─ What-If Engine + parameters
                                          ↓
                                  WhatIfResult (scenario)
```

The observed React panel accepts `EvidenceObject`; the scenario panel accepts `WhatIfResult`. The scenario result materializes `observed_at_t0` so the scenario UI never reads evidence metrics. Narrative generation is a bounded deterministic fallback in this prototype. A future Azure AI provider must receive only a selected evidence-derived subset and cannot author evidence or compute metrics.

## Frozen ownership map

| Data | Authority | Consumer |
|---|---|---|
| Raw events | `synthetic_events.jsonl` / replay | `/sse/events` |
| Live charts | backend state engine | `/sse/observed` `metrics_tick` |
| Qualified shift | detector | `shift_qualified` signal |
| Observed evidence | Evidence builder | `/observed/*` |
| Narrative | evidence-derived text | explanation panel |
| Scenario parameters | UI request | `/what-if` |
| Scenario result and t0 | What-If engine | scenario panel |
