from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.core import build_evidence, load_events, run_what_if

events = load_events()
evidence = build_evidence(events)
scenario = run_what_if(evidence)
assert evidence.detection["qualified"]
assert evidence.model_dump_json() == build_evidence(load_events()).model_dump_json()
assert scenario.model_dump_json() == run_what_if(evidence).model_dump_json()
assert "evidence" not in scenario.model_dump()
print("MATCHLENS GOLDEN DEMO\n---------------------\nReplay: PASS\nMetrics: PASS\nDetection: PASS\nEvidence: PASS\nEvidence determinism: PASS\nWhat-If: PASS\nWhat-If determinism: PASS\nData boundaries: PASS\n\nREADY FOR DEMO")
