"""Deterministic MatchLens domain engine for synthetic football events."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_events.jsonl"
ENGINE_VERSION = "matchlens-engine-v1"


class FrozenDict(dict):
    """JSON-serializable mapping that rejects mutation at every nested level."""
    def _immutable(self, *args, **kwargs):
        raise TypeError("immutable evidence/scenario payload")
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _immutable


def _deep_freeze(value):
    if isinstance(value, dict):
        frozen = dict.__new__(FrozenDict)
        dict.__init__(frozen, {k: _deep_freeze(v) for k, v in value.items()})
        return frozen
    if isinstance(value, list):
        return tuple(_deep_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_deep_freeze(v) for v in value)
    return value


class Event(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    match_id: str
    event_id: str
    timestamp: str
    team: str
    event_type: str
    zone: str | None = None
    metadata: dict[str, str | int | float | bool] = {}


class EvidenceObject(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    kind: Literal["observed"] = "observed"
    type: str = "HIGH_PRESSING_SHIFT"
    team: str
    opponent: str
    match_context: dict
    detection: dict
    evidence: dict
    explanation_contract: dict
    provenance: dict
    engine_versions: dict

    def model_post_init(self, __context):
        for field in ("match_context", "detection", "evidence", "explanation_contract", "provenance", "engine_versions"):
            object.__setattr__(self, field, _deep_freeze(getattr(self, field)))


class WhatIfResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    evidence_id: str
    scenario: dict
    observed_at_t0: dict
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    outputs: dict
    model_versions: dict

    def model_post_init(self, __context):
        for field in ("scenario", "observed_at_t0", "outputs", "model_versions"):
            object.__setattr__(self, field, _deep_freeze(getattr(self, field)))


def load_events(path: Path = DATA_PATH) -> list[Event]:
    events = [Event.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return sorted(events, key=lambda e: (clock_seconds(e.timestamp), e.event_id))


def clock_seconds(clock: str) -> int:
    parts = [int(x) for x in clock.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"Invalid match clock: {clock}")


def _metrics(events: list[Event], end: int) -> dict[str, float]:
    window = [e for e in events if end - 300 < clock_seconds(e.timestamp) <= end]
    arsenal = [e for e in window if e.team == "Arsenal"]
    liverpool = [e for e in window if e.team == "Liverpool"]
    pressures = sum(e.event_type == "PRESSURE" for e in arsenal)
    recoveries = sum(e.event_type == "BALL_RECOVERY" and e.zone == "high" for e in arsenal)
    turnovers = sum(e.event_type == "TURNOVER" for e in liverpool)
    entries = sum(e.event_type in {"FINAL_THIRD_ENTRY", "SHOT", "SHOT_ON_TARGET"} for e in arsenal)
    threat = sum(1.0 if e.event_type == "SHOT_ON_TARGET" else .65 if e.event_type == "SHOT" else .25 for e in arsenal if e.event_type in {"SHOT", "SHOT_ON_TARGET"})
    territory_count = sum(e.zone in {"attacking", "high"} for e in arsenal)
    territory_total = territory_count + sum(e.zone in {"attacking", "high"} for e in liverpool)
    return {
        "pressing_intensity": round(min(1.0, pressures / 10), 3),
        "high_recoveries_rate_10min": round(recoveries * 2, 3),
        "forced_turnovers_rate_10min": round(turnovers * 2, 3),
        "territory_share": round(territory_count / territory_total, 3) if territory_total else .5,
        "attacking_threat": round(min(1.0, threat / 2), 3),
        "final_third_entries_rate_10min": round(entries * 2, 3),
    }


def build_evidence(events: list[Event]) -> EvidenceObject:
    end = max(clock_seconds(e.timestamp) for e in events)
    base = _metrics(events, max(0, end - 600))
    after = _metrics(events, end)
    supporting = [e for e in events if end - 300 < clock_seconds(e.timestamp) <= end]
    raw = {k: after[k] for k in after}
    digest = hashlib.sha256(json.dumps({"baseline": base, "detection": after, "ids": [e.event_id for e in supporting]}, sort_keys=True).encode()).hexdigest()[:16]
    return EvidenceObject(
        id=f"shift_{digest}", team="Arsenal", opponent="Liverpool",
        match_context={"match_id": "synthetic_demo_001", "data_source": "synthetic_event_stream_v1", "trigger_timestamp": events[-1].timestamp},
        detection={"rule": "HIGH_PRESSING_SHIFT", "baseline_window_sec": 600, "detection_window_sec": 300, "qualified": after["pressing_intensity"] >= .5 and after["high_recoveries_rate_10min"] >= 4, "minimum_pressing_intensity": .5},
        evidence={"baseline": base, "detection": after, "deltas": {k: round(after[k] - base[k], 3) for k in after}, "raw_counts": raw, "supporting_events": [{"event_id": e.event_id, "timestamp": e.timestamp, "team": e.team, "event_type": e.event_type, "zone": e.zone} for e in supporting]},
        explanation_contract={"what_changed": "Arsenal increased pressure and recovered the ball higher more often.", "why_it_matters": "The observed sequence coincides with more territory and attacking entries; this is an observed relationship, not causal proof.", "allowed_claims": ["observed relationship", "scenario projection"], "prohibited_claims": ["guaranteed outcome", "predicted goal", "predicted final score"]},
        provenance={"source_event_ids": [e.event_id for e in supporting], "generated_at": "synthetic-deterministic", "metric_config_version": "metrics-v1", "detection_config_version": "high-press-v1"},
        engine_versions={"engine": ENGINE_VERSION},
    )


def run_what_if(evidence: EvidenceObject, horizon_sec: int = 600) -> WhatIfResult:
    obs = evidence.evidence["detection"]
    outputs = {k: round(v * horizon_sec / 600, 3) for k, v in obs.items() if k.endswith("_rate_10min")}
    outputs.update({k: v for k, v in obs.items() if k in {"territory_share", "attacking_threat", "pressing_intensity"}})
    payload = {"evidence_id": evidence.id, "horizon": horizon_sec, "outputs": outputs}
    ident = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
    return WhatIfResult(id=f"whatif_{ident}", evidence_id=evidence.id, scenario={"mode": "hold_current_pressing", "horizon_sec": horizon_sec}, observed_at_t0={"t0_timestamp": evidence.match_context["trigger_timestamp"], "metrics": {k: obs[k] for k in obs}}, assumptions=("Arsenal maintains current pressing intensity.", "Observed relationships remain approximately stable."), limitations=("Scenario projection, not a prediction.", "Does not predict goals or final score.",), outputs=outputs, model_versions={"what_if": "scenario-v1"})


def narrative(evidence: EvidenceObject) -> str:
    d = evidence.evidence["deltas"]
    return (f"Arsenal's pressing intensity rose by {d['pressing_intensity']:+.2f} index points, "
            f"alongside {d['high_recoveries_rate_10min']:+.1f} high recoveries per 10 minutes. "
            "The event sequence also shows greater territory and attacking entries. "
            "These are observed relationships, not proof of cause or a guaranteed outcome.")
