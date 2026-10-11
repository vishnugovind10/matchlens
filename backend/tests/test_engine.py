from app.core import build_evidence, load_events, run_what_if


def test_synthetic_stream_is_ordered_and_qualifies():
    events = load_events()
    assert events == sorted(events, key=lambda e: (e.timestamp, e.event_id))
    assert build_evidence(events).detection["qualified"] is True


def test_evidence_and_what_if_are_immutable_and_deterministic():
    events = load_events()
    first, second = build_evidence(events), build_evidence(events)
    assert first.model_dump_json() == second.model_dump_json()
    try:
        first.team = "Liverpool"
        assert False, "frozen EvidenceObject accepted a mutation"
    except Exception:
        pass
    try:
        first.evidence["detection"]["pressing_intensity"] = 0
        assert False, "nested EvidenceObject accepted a mutation"
    except TypeError:
        pass
    result = run_what_if(first)
    assert result.model_dump_json() == run_what_if(second).model_dump_json()
    assert result.evidence_id == first.id
    assert result.observed_at_t0["t0_timestamp"] == first.match_context["trigger_timestamp"]


def test_what_if_is_separate_and_has_no_evidence_values_attached():
    result = run_what_if(build_evidence(load_events()))
    assert "evidence" not in result.model_dump()
    assert result.limitations and result.assumptions
