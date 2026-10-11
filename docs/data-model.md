# Data model and metric definitions

`synthetic_demo_001` is a fictional deterministic event stream labelled `synthetic_event_stream_v1`. Event records contain match ID, event ID, match-clock timestamp, team, type, optional zone, and metadata. Replay time never overwrites match time.

The MVP calculates a trailing 300-second view at the match time represented by each event. Counts below use that window, multiplied by two to express a per-10-minute rate. They are simplified synthetic formulas, not official performance statistics.

| Canonical field | Demo calculation |
|---|---|
| `pressing_intensity` | Arsenal pressure events / 10, capped at 1.0 |
| `high_recoveries_rate_10min` | Arsenal high-zone recoveries × 2 |
| `forced_turnovers_rate_10min` | Liverpool turnovers × 2 |
| `territory_share` | Arsenal attacking/high-zone actions divided by both teams' such actions; 0.5 if none |
| `attacking_threat` | Weighted Arsenal shots (0.65) and shots on target (1.0), divided by 2 and capped at 1.0 |

The detector qualifies the authored demo when pressing intensity is at least 0.5 and high recoveries are at least 4 per 10 minutes. This threshold is explicit and deterministic; it does not establish causation. Values missing from a time window must not be interpreted as observed evidence of zero.

`EvidenceObject` carries the baseline and detection summaries, deltas, supporting event IDs, rule configuration, provenance, and engine versions. `WhatIfResult` carries an opaque evidence reference and its own `observed_at_t0`, assumptions, limitations, scenario outputs, and model version. These objects are semantically and structurally separate.
