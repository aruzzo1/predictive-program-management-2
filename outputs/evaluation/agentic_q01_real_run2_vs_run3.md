# Agentic Q01: REAL_LLM_MODE Run 2 vs Run 3 (critic calibration + comparative review)

Episode: **A1 Mission-System Software Maturity → A2 Flight-Test Execution**.
Query (Q01): *What evidence indicates that mission-system software maturity affected F-35 flight-test execution?*
Unchanged: retrieval HYBRID_RERANKED_V2_1 top 5 (identical evidence E1–E5), corpus, `gpt-4o-mini`, temperature 0,
ToT config (successors 3, beam 3, depth 3, threshold 70, near tie 5, budget 20), weights 30/30/20/20, model
consistency pinned at 50, the generator prompt, the LangGraph topology, and the validation ownership rule.

What changed between Run 2 and Run 3:
1. **Critic prompt.** Documentary-evidence scoring anchors were added (90–100 / 75–89 / 60–74 / 40–59 / 0–39), plus a
   required `evidence_support_label` (DIRECTLY_STATED / STRONGLY_SUPPORTED / INFERRED / WEAKLY_SUPPORTED / UNSUPPORTED).
   Two further instructions were added: an explicit statement in an authoritative source counts as documentary support
   for the effect it describes, and the critic should score the wording gap between evidence and activities, not the
   absence of experimental proof.
2. **Comparative review.** After the final prune, one advisory call compares the surviving hypotheses. It cannot
   rescore, revive a pruned hypothesis or change validation, and the verdict rule stays deterministic.

| | Run 2 | Run 3 |
|---|---|---|
| Trace | `episode_20261030_134626_A1_A2.{json,md}` | `episode_20261030_140841_A1_A2.{json,md}` |
| Model calls | 4 (1 gen + 3 critic) | **9** (depth 1: 1 gen + 3 critic; depth 2: 2 gen + 2 critic; 1 comparative) |
| Tokens | 8,613 in / 992 out | 21,202 in / 2,364 out |
| Depth / stop | 1 / NO_VIABLE_CANDIDATE | 2 / NO_NEW_CANDIDATES |
| Survivors | none | D1.root.1 DIRECT (70.5), D1.root.2 INDIRECT (70.5) |
| Comparative review | n/a | COMPLETED: prefers D1.root.1 (DIRECT); judges the numerical tie **not genuine** |
| Critic/Python disagreements | 0 | 0 |
| **Decision** | **UNRESOLVED** | **PARTIALLY_SUPPORTED**: DIRECT, 70.5, evidence E2; type in near tie with INDIRECT |

## Hypotheses, evidence, scores and labels

Depth 1. In Run 3 the generator produced the **same three hypotheses as Run 1**, which differ slightly from Run 2's.
The generator did not change, so this is sampling variation.

| ID | Run 2: cites → Doc/Eng/Model/Pred = total | Run 3: cites → Doc/Eng/Model/Pred = total, label | Run 3 outcome |
|---|---|---|---|
| D1.root.1 DIRECT | E2 → 70/60/50/70 = **63.0** | E2 → 75/80/50/70 = **70.5**, STRONGLY_SUPPORTED | survived |
| D1.root.2 INDIRECT via software integration and test | E1 → 40/60/50/30 = 46.0 | E1, E4 → 75/80/50/70 = **70.5**, STRONGLY_SUPPORTED | survived |
| D1.root.3 UNCERTAIN | E5 → 30/40/50/20 = 35.0 | E5 → 40/50/50/40 = 45.0, WEAKLY_SUPPORTED | below threshold |

Depth 2 in Run 3 only. DIRECT and INDIRECT tied at 70.5, which is within the 5-point margin, so the search refined both:

| ID | Cites | Scores = total, label | Outcome |
|---|---|---|---|
| D2.D1.root.1.1 DIRECT | E2 | – | VALIDATION: duplicate of D1.root.1 |
| D2.D1.root.1.2 INDIRECT | E1, E5 | 75/70/50/80 = 69.5, STRONGLY_SUPPORTED | below threshold (by 0.5) |
| D2.D1.root.1.3 UNCERTAIN | E3, E4 | 60/70/50/60 = 61.0, INFERRED | below threshold |
| D2.D1.root.2.1 DIRECT | E2 | – | VALIDATION: duplicate of D1.root.1 |
| D2.D1.root.2.2 INDIRECT | E1, E4 | – | VALIDATION: duplicate of D1.root.2 |
| D2.D1.root.2.3 UNCERTAIN | none | – | VALIDATION: no supporting evidence cited |

There were no new survivors, so the run stopped with NO_NEW_CANDIDATES. Deterministic validation removed 4 of the 6
refinements before any critic call.

## Comparative review (Run 3)

- **Reviewed:** D1.root.1 and D1.root.2 only. D1.root.3 was pruned and was not shown to the reviewer.
- **Preferred:** D1.root.1 (DIRECT). Assumption comparison: DIRECT "requires fewer assumptions … without needing to
  invoke intermediate steps", whereas INDIRECT "relies on the assumption that software integration and test is a
  necessary precursor".
- **Near tie:** numerically yes (70.5 vs 70.5). The reviewer judged it **not genuine** because DIRECT fits better.
- **Effect:** advisory only. The deterministic rule still returns PARTIALLY_SUPPORTED, because the totals are tied
  between two relationship types. The review is recorded in the decision summary and the trace.

## Assessment

**Calibration is more internally consistent:**
- Every label agrees with its anchor band (75 ↔ STRONGLY_SUPPORTED, 60 ↔ INFERRED, 40 ↔ WEAKLY_SUPPORTED).
- Run 2's objection that E2 might be merely "correlational" is gone. The critic now quotes E2 as stating the effect.
- The UNCERTAIN hypothesis now scores below the positive hypotheses. That is consistent with E2 stating a dependency.

**Comparative review adds what the individual critic could not:**
- The individual critic gave DIRECT and INDIRECT *identical* sub-scores, so it never distinguished them. The review did,
  and gave a reason (fewer intermediate assumptions).

**Remaining weaknesses, stated plainly:**
- **The verdict changed by a margin smaller than the noise.** DIRECT cleared the threshold by 0.5 points, and the depth-2
  INDIRECT refinement missed it by 0.5. Run 2 → Run 3 also changed the generator's depth-1 output, so the move from
  UNRESOLVED to PARTIALLY_SUPPORTED cannot be attributed to the calibration alone. **I do not claim Run 3 is better
  because the verdict is now positive.**
- **E2 was labelled STRONGLY_SUPPORTED, not DIRECTLY_STATED.** E2 states that software *delays* affected flight-test
  progress; the hypothesis is about software *maturity*. Treating that as "minor interpretation" is defensible, but the
  critic does not name the delays/maturity gap explicitly.
- **INDIRECT was also scored STRONGLY_SUPPORTED (75),** although the critic's own text says "no passage explicitly
  states this dependency". By the anchors, that is closer to INFERRED (60–74).
- **"Agrees with score ranking" is trivially true here.** With an exact tie, the score leader is chosen by the ID
  tie-break.
- **The review's assumption argument is partly in tension with the individual critic.** The review says DIRECT needs
  fewer assumptions, but the individual critic flagged DIRECT's own assumption ("without other intervening factors") as
  unsupported. The review did not mention this.
- **No contradictions were listed for any hypothesis,** including the UNCERTAIN ones, which E2 arguably contradicts.
- **Cost:** 9 calls and about 2.5× the tokens of Run 2, mostly from the depth-2 refinement that a surviving near tie
  triggers. The comparative review itself is 1 call.

## Limitations

- n = 1 run each. Verdict, survivors and depth all hinge on scores within ±0.5 of the threshold.
- Generator output varies between runs at temperature 0, which confounds any attribution to the critic changes.
- The comparative review is advisory by design. Whether it should be allowed to break a numerical near tie it judges
  "not genuine" is a policy decision that has not been made.
