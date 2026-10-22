# ForgeLab — reviewer gate confound and contract fix — 2026-10-22

Class: A (unblocks the reviewer gate before Dental). Author: Claude, at the PO's request after PR #77.
Base: main `b9739bb` (PR #77 merged). Production routes, models, timeouts, budgets and gates unchanged.

## Result

PR #76 and PR #77 measured the reviewer with a prompt that already told it the answer. The objective used
for both is the **semantic-repair** objective (SHA-256 `9203af70…670a`), not a product objective. After the
product paragraph it embeds the PM contract, then a stale **"Blocking semantic review"** of the original
one-item code, then "Repair every blocking requirement". The reviewer prompt places all of it under
`Objective:` (`orchestrator.py`, `review_prompt`), so every reviewed candidate arrived with a prior verdict:

| Stale review in the prompt | What the reviewers then reported |
|---|---|
| AC1 missing: render_estimate/CLI reject three items | Local, GOOD final: "AC1 MISSING … raises a ValueError if the item count is not three" — the requirement itself, read as a defect |
| AC2, AC6 missing | Local, GOOD final: denies aggregate calculation, JSON final_total and tests (PR #77 adjudication) |
| AC3 satisfied: "helper validates discount" | Gemma, BAD discount (2/2): aggregate discount marked SATISFIED, "validates the discount range" — the defect missed |
| AC4 satisfied: calculate_item remains valid | Gemma, BAD helper (2/2): mentions missing final_total yet marks helper preservation SATISFIED |

The objective text is verified (read from the run evidence; hash matches). The alignment of the false
judgments with the stale review is verified from the raw responses. That the stale review **caused** them is a
strong hypothesis, not yet proven: it needs the clean replay below. Real Dental runs use the PO's own objective
and would not carry this text.

Attribution: the instruction for Task B (PR #76) named this objective hash for a full-run test; Task C reused
it. The error is in the test design, not in the Codex execution.

## Two production defects fixed here

1. **Reviewer JSON contract existed only as an Ollama `format` schema.** The prompt ends with "Return ONLY the
   required JSON object" and never names the fields. Local Ollama enforces `format` by constrained decoding, so
   local answers conformed. On the cloud path Gemma received the same `format` (verified in the saved request)
   and returned its own keys (`id`, `description`, `blocking`; no `schema_version`, `summary`, `findings`).
   Fix: `_ai_review_output_contract()` puts the field list and the exact JSON Schema in the review prompt.
   Validation stays strict; nothing is coerced.
2. **Silent truncation by a fixed `num_ctx=4096`.** PR #77 traced the 2,050-token result to Ollama's context
   shift. Fix in `OllamaProvider`: `num_ctx` is sized per call from the prompt (+ schema) at a conservative
   3.5 chars/token plus `num_predict` 2048, rounded to 1,024, floor 4,096, ceiling 16,384. Above the ceiling the
   call is refused before any request. After the call, a prompt that Ollama evaluated at more than 8 chars per
   token (PR #76: 21,618 chars → 2,050 tokens = 10.5) is rejected as truncated. Prompts that already fit keep
   `num_ctx=4096`; only previously truncated prompts change.

With the contract added (1,407 chars), the four PR #77 review prompts (17,370–21,618 chars) get `num_ctx`
8,192–9,216, close to the 8,192 PR #77 measured (minimum free RAM 1.395 GiB). The ceiling of 16,384 has **not** been measured on the PO machine; larger prompts
fail closed instead of running blind, but a run near the ceiling may still be slow or memory-tight.

## Tests

200 Python tests pass on Python 3.11 (192 existing + 8 new): context sizing, schema counted in the budget,
oversized prompt refused without a request, truncated evaluation rejected (PR #76 numbers), cached tokens
counted, contract content equals the production schema, the real review prompt carries it, and Gemma's PR #77
shape still fails validation.

NOT VERIFIED: any live model behaviour with the new prompt; RAM at contexts above 9,216 on the PO machine;
whether Ollama Cloud honours `num_ctx`.

## Next action

Re-run the PR #77 reviewer replay on this branch's code with a **clean** objective (the product paragraph only,
as in the PR #74 smoke and the dashboard form), same four candidates, two rounds, local first, Gemma only if
local fails. Dental stays blocked until one reviewer passes that gate.
