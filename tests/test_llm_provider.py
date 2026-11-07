"""REAL_LLM_MODE adapter tests: provider selection, structured output, error handling. No network calls:
the OpenAI client is replaced by a fake that returns or raises what the Responses API would."""

from types import SimpleNamespace

import httpx2
import openai
import pytest

from ppm_agent.agents.critic import Critic
from ppm_agent.agents.generator import ThoughtGenerator
from ppm_agent.agents.llm import (MOCK_AGENT_MODE, REAL_LLM_MODE, LLMCallError, LLMConfigurationError, OpenAIResponsesClient,
                                  agent_mode, detect_llm_client)
from ppm_agent.agents.scoring import weighted_score
from ppm_agent.agents.tot import ToTController
from ppm_agent.agents.validation import validate_assessment
from ppm_agent.models import (CriticAssessment, CriticOutput, DependencyHypothesis, GeneratedHypothesis, GeneratorOutput)
from test_agentic import ScriptedGenerator, hyp, state_with_evidence

REQUEST = httpx2.Request("POST", "https://api.openai.com/v1/responses")


def response(parsed, status="completed", refusal=None, reason=None):
    content = [SimpleNamespace(type="refusal", refusal=refusal)] if refusal else []
    return SimpleNamespace(output_parsed=parsed, status=status, output=[SimpleNamespace(content=content)],
                           incomplete_details=SimpleNamespace(reason=reason), usage=SimpleNamespace(input_tokens=100, output_tokens=20))


class FakeOpenAI:
    """Stands in for openai.OpenAI: records responses.parse kwargs; returns or raises the scripted outcomes in order."""

    def __init__(self, *outcomes):
        self.outcomes, self.requests = list(outcomes), []
        self.responses = SimpleNamespace(parse=self._parse)

    def _parse(self, **kwargs):
        self.requests.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def real_client(*outcomes):
    fake = FakeOpenAI(*outcomes)
    return OpenAIResponsesClient(model="test-model", client=fake), fake


def gen_out(*items):
    return GeneratorOutput(hypotheses=[GeneratedHypothesis(**{"intermediate_activity": None, "contradicting_evidence_ids": [],
                                                              "assumptions": [], "reasoning_summary": "r", **i}) for i in items])


def critic_out(score=80, claimed=False, reasons=(), doc=None, model=50, strength="supports the claim", label="STRONGLY_SUPPORTED"):
    return CriticOutput(documentary_evidence_score=score if doc is None else doc, engineering_consistency_score=score,
                        model_consistency_score=model, predictive_usefulness_score=score, evidence_support_label=label,
                        evidence_strength_summary=strength,
                        contradictions=[], unsupported_assumptions=[], critic_concerns=[], critic_claimed_hard_failure=claimed,
                        critic_claimed_hard_failure_reasons=list(reasons), critic_summary="model judgement")


# --- provider selection -----------------------------------------------------------------------


def test_no_key_means_mock_mode(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert detect_llm_client() is None and agent_mode(None) == MOCK_AGENT_MODE


def test_key_selects_responses_client_in_real_mode(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-a-real-key")
    monkeypatch.setenv("OPENAI_MODEL", "some-model")
    client = detect_llm_client()  # constructing the SDK client makes no network call
    assert isinstance(client, OpenAIResponsesClient) and client.model == "some-model" and agent_mode(client) == REAL_LLM_MODE


# --- structured output ------------------------------------------------------------------------


def test_output_schemas_are_strict_compatible_subsets_of_the_domain_models():
    for schema, domain in ((GeneratedHypothesis, DependencyHypothesis), (CriticOutput, CriticAssessment)):
        assert set(schema.model_fields) <= set(domain.model_fields)
        assert all(f.is_required() for f in schema.model_fields.values())  # strict structured output: no defaults
    assert "overall_score" not in CriticOutput.model_fields and "hypothesis_id" not in GeneratedHypothesis.model_fields


def test_adapter_uses_responses_parse_with_schema_and_records_usage():
    client, fake = real_client(response(critic_out()))
    out = client.complete("sys", "user", CriticOutput)
    assert isinstance(out, CriticOutput)
    req = fake.requests[0]
    assert (req["model"], req["instructions"], req["input"], req["text_format"]) == ("test-model", "sys", "user", CriticOutput)
    assert req["temperature"] == 0 and req["store"] is False
    assert client.usage_summary()["input_tokens"] == 100 and client.usage_summary()["successful_responses"] == 1


def test_real_generator_output_is_still_validated_in_python():
    rs, chunk_ids = state_with_evidence()
    client, _ = real_client(response(gen_out({"relationship_type": "DIRECT", "supporting_evidence_ids": ["E1"]},
                                             {"relationship_type": "INDIRECT", "supporting_evidence_ids": ["E9"]})))
    rs.depth = 1
    hyps, errors = ThoughtGenerator(client).propose(rs)
    assert [h.hypothesis_id for h in hyps] == ["D1.root.1", "D1.root.2"]  # ids, depth and activities come from Python
    assert all((h.source_activity, h.target_activity, h.depth) == ("A1", "A2", 1) for h in hyps)
    controller = ToTController(ScriptedGenerator([]), Critic(None))
    rs.pending_hypotheses, rs.all_hypotheses = list(hyps), list(hyps)
    controller.validate(rs, chunk_ids)
    assert [h.hypothesis_id for h in rs.pending_hypotheses] == ["D1.root.1"]
    assert any("'E9' does not exist" in e for e in rs.validation_errors["D1.root.2"])
    assert any("intermediate activity" in e for e in rs.validation_errors["D1.root.2"])


def test_real_critic_total_is_computed_in_python_and_hard_constraints_come_from_python():
    # Updated with the validation-ownership refactor: a critic-reported hard failure no longer forces a FAIL.
    rs, _ = state_with_evidence()
    client, _ = real_client(response(critic_out(120)), response(critic_out(90, claimed=True, reasons=["E3 contradicts it"])))
    a = Critic(client).assess(hyp("H"), rs)
    assert a.documentary_evidence_score == 100 and a.overall_score == weighted_score(100, 100, 50, 100)
    assert validate_assessment(a, {"H"}) == []
    b = Critic(client).assess(hyp("H"), rs)
    assert b.hard_constraint_pass and b.hard_constraint_failures == [] and b.deterministic_validation_result == "PASS"
    assert b.critic_claimed_hard_failure and b.critic_claimed_hard_failure_reasons == ["E3 contradicts it"]
    assert b.critic_validation_disagreement


# --- error handling ---------------------------------------------------------------------------


@pytest.mark.parametrize("outcome, match", [
    (response(None, refusal="I can't help with that"), "refusal"),
    (response(None, status="incomplete", reason="max_output_tokens"), "incomplete"),
    (openai.APIConnectionError(request=REQUEST), "APIConnectionError"),
    (openai.RateLimitError("slow down", response=httpx2.Response(429, request=REQUEST), body=None), "RateLimitError"),
])
def test_recoverable_failures_raise_llm_call_error(outcome, match):
    client, _ = real_client(outcome)
    with pytest.raises(LLMCallError, match=match):
        client.complete("s", "u", CriticOutput)


@pytest.mark.parametrize("exc", [
    openai.AuthenticationError("Incorrect API key provided: sk-proj-abc123***wxyz", response=httpx2.Response(401, request=REQUEST), body=None),
    openai.NotFoundError("model not found", response=httpx2.Response(404, request=REQUEST), body=None),
    openai.RateLimitError("quota", response=httpx2.Response(429, request=REQUEST), body={"code": "insufficient_quota"}),
])
def test_configuration_failures_are_fatal_and_redacted(exc):
    client, _ = real_client(exc)
    with pytest.raises(LLMConfigurationError) as info:
        client.complete("s", "u", CriticOutput)
    assert "abc123" not in str(info.value) and "wxyz" not in str(info.value)


def test_failed_calls_are_logged_not_invented():
    rs, chunk_ids = state_with_evidence()
    client, _ = real_client(openai.APITimeoutError(request=REQUEST))
    rs.depth = 1
    hyps, errors = ThoughtGenerator(client).propose(rs)
    assert hyps == [] and "generator call failed" in errors[0]

    rs, chunk_ids = state_with_evidence()
    client, _ = real_client(openai.APITimeoutError(request=REQUEST))
    controller = ToTController(ScriptedGenerator([hyp("a")]), Critic(client))
    decision = controller.run(rs, chunk_ids)
    assert rs.model_calls == 2 and rs.assessments == {}
    assert any(p["reason"].startswith("CRITIC CALL FAILED") for p in rs.pruning_log)
    assert decision.decision == "UNRESOLVED"
