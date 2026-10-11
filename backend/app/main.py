from __future__ import annotations

import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from .core import _metrics, build_evidence, clock_seconds, load_events, narrative, run_what_if

app = FastAPI(title="MatchLens", description="Explainable match intelligence over synthetic football events", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
EVENTS = load_events()
EVIDENCE = build_evidence(EVENTS)


@app.get("/health")
def health():
    return {"status": "ok", "match_id": "synthetic_demo_001", "data_source": "synthetic_event_stream_v1"}


@app.get("/observed/latest")
def latest(match_id: str = "synthetic_demo_001"):
    return EVIDENCE if match_id == "synthetic_demo_001" and EVIDENCE.detection["qualified"] else None


@app.get("/observed/{evidence_id}")
def observed(evidence_id: str):
    if evidence_id != EVIDENCE.id:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return EVIDENCE


@app.get("/sse/events")
async def event_stream(match_id: str = "synthetic_demo_001", speed: float = 4.0, start: str = "00:00"):
    if match_id != "synthetic_demo_001" or speed <= 0 or speed > 32:
        raise HTTPException(status_code=400, detail="Unsupported match or replay speed")
    selected = [e for e in EVENTS if clock_seconds(e.timestamp) >= clock_seconds(start)]
    async def stream():
        for seq, event in enumerate(selected, 1):
            yield "data: " + json.dumps({"type": "event", "replay_id": "replay_demo", "sequence_number": seq, "match_id": match_id, "event": event.model_dump(), "replay": {"speed": speed}}) + "\n\n"
            await asyncio.sleep(0.03 / speed)
        yield "data: " + json.dumps({"type": "shift_qualified", "replay_id": "replay_demo", "sequence_number": len(selected) + 1, "match_id": match_id, "evidence_id": EVIDENCE.id, "trigger_timestamp": EVIDENCE.match_context["trigger_timestamp"], "replay": {"speed": speed}}) + "\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/sse/observed")
async def metrics_stream(match_id: str = "synthetic_demo_001", replay_id: str = "replay_demo"):
    if match_id != "synthetic_demo_001":
        raise HTTPException(status_code=404, detail="Match not found")
    async def stream():
        for seq, event in enumerate(EVENTS, 1):
            metrics = _metrics(EVENTS[:seq], clock_seconds(event.timestamp))
            yield "data: " + json.dumps({"type": "metrics_tick", "replay_id": replay_id, "sequence_number": seq, "match_id": match_id, "at_timestamp": event.timestamp, "windows": {"rolling_sec": 300}, "metrics": {k: {"value": v, "unit": "share" if k == "territory_share" else "index" if k in {"pressing_intensity", "attacking_threat"} else "count_per_10min"} for k, v in metrics.items() if k != "final_third_entries_rate_10min"}, "replay": {"speed": 4.0}}) + "\n\n"
            await asyncio.sleep(.03)
    return StreamingResponse(stream(), media_type="text/event-stream")


class ScenarioRequest(BaseModel):
    evidence_id: str
    mode: str = "hold_current_pressing"
    horizon_sec: int = Field(default=600, ge=60, le=1800)


@app.post("/what-if")
def what_if(request: ScenarioRequest):
    if request.evidence_id != EVIDENCE.id or request.mode != "hold_current_pressing":
        raise HTTPException(status_code=400, detail="Unknown evidence or scenario")
    return run_what_if(EVIDENCE, request.horizon_sec)


@app.post("/narrative")
def explain(evidence_id: str):
    if evidence_id != EVIDENCE.id:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"provider": "deterministic-local-fallback", "text": narrative(EVIDENCE)}
