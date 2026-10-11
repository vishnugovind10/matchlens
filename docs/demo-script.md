# Demo script

## 0:00 — Follow the synthetic match

Show the event ticker and five observed metric readouts. The values update from the synthetic event and `metrics_tick` streams.

Narration:

> This is MatchLens. It follows a synthetic football event stream and tracks the match state as events arrive. We are looking for a meaningful tactical change, not just another isolated statistic.

## 0:20 — Spot the shift

Let the Arsenal high-press sequence reach the ticker. The shift signal triggers retrieval of the observed evidence.

Narration:

> Arsenal begin pressing higher. Liverpool turnovers and Arsenal high recoveries follow, alongside more attacking territory. MatchLens qualifies that pattern as a high-pressing shift.

## 0:40 — Inspect the evidence

Show the observed panel's baseline, detection values, deltas, and supporting event sequence.

Narration:

> The insight is tied to a specific window of synthetic events. The before-and-after rates use comparable five-minute windows, and the event IDs let us trace the evidence. This is an observed relationship, not proof that pressing caused the later actions.

## 1:00 — Read the explanation

Show the grounded explanation under the `OBSERVED — COMPUTED FROM EVENTS` label.

Narration:

> The explanation is generated from the computed evidence. This prototype uses a deterministic local narrative, so the demo works without cloud credentials or an unconstrained chatbot.

## 1:15 — Explore What-If

Choose **Run What-If**. Show the separate scenario section, its t0 timestamp and values, then assumptions and limitations.

Narration:

> Now we can explore a conditional ten-minute scenario if Arsenal maintain the current pressing intensity. The What-If result carries its own observed-at-t0 values, assumptions, and limitations. It is a scenario projection, not a prediction; it does not predict goals or a final score.

## Close

Show the final hero message:

```text
DETECT → PROVE → EXPLAIN → EXPLORE
```

> That’s MatchLens: it detects a tactical shift from live events, proves it with evidence, explains why it matters, and lets you explore what happens if it continues.
