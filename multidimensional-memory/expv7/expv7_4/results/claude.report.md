# EXP-V7.4 — Claude Code report

## 1. Selection quality

- agent identity: `claude`
- Writer: delegated to a fresh clean-room subagent (this session had prior exposure to gold data and prior experiment reports across V7.1-V7.3, so per RUN_PROMPT.md's instruction, direct execution would have invalidated the anti-cheating rule). The subagent was restricted to exactly 2 readable files: `EXP-V7.4.md` and `data/conversation_v7_4_unlabeled.jsonl`. It confirmed in its own report reading only those 2 files.
- **Selection recall = 1.0, precision = 1.0, F1 = 1.0**: all 20 gold `signal_event_ids` retained (verified against `data/benchmark_v7_4.json` after freezing), zero false positives, zero false negatives, retention ratio 1.67% (20/1,200).
- **This result is qualitatively stronger evidence than V7.3's identical score**, because V7.4's corpus was specifically engineered to remove the lexical shortcut V7.3 exploited. I independently verified this by: (a) confirming `tests/test_v74.py::test_no_simple_boilerplate_tell` passes (no single substring separates signal from distractor), and (b) directly reading distractor text like "Database options were discussed without a decision." and "A billing database migration was discussed as a possibility." (events E10000, E10028) alongside the real decision "We chose PostgreSQL for billing because auditability mattered more than migration effort." (E0014) — genuinely close in vocabulary and topic, differing only in whether an actual decision was made. The writer subagent's own report describes explicitly checking for and ruling out a hidden shortcut (frequency-counting the ~1,180 non-signal events into ~40 distinct near-identical templates, confirming none was an outlier) before committing to per-event content judgment.
- **Caveat, stated plainly**: this is still one benchmark corpus with exactly 20 curated signal events designed by the same generator that designed the adversarial distractors. A perfect score here demonstrates robustness against this specific adversarial design, not that autonomous selection is solved in general.

## 2. Memory construction quality

Full detail in `results/claude.memory_eval.json`. 11 records (types: decision, action_outcome ×2, belief_evolution, state_transition ×3, ambiguity, negative_knowledge ×2, provenance), citing all 20 correct source events, zero invented event IDs.

**Adversarial trap handling (6/6 checked, all correct):**
1. Discussion-vs-decision: only the actual PostgreSQL decision (E0014) was promoted to a `decision` record; topically similar "discussed without a decision" / "discussed as a possibility" distractors were correctly excluded.
2. Action-vs-intention: E1201 ("We will document the webhook state history...") was kept but explicitly tagged as an intention, not folded into the completed-action state history.
3. Inference-vs-confirmation: E0449 (Claude's inference) and E0450 (Rahul's confirmation) kept as two distinct `belief_evolution` steps rather than collapsed into one fact.
4. Obsolete-vs-current state: E1200 ("decision remains PostgreSQL, no later reversal") kept as a separate currency-confirming record, explicitly distinguished from the unrelated failed DynamoDB prototype (correctly not treated as a reversal).
5. Scoped negative knowledge with a similar later mention: E0549 (not discussed in billing review) and E1103 (MongoDB proposal in a different project) kept as two linked-but-distinct records rather than merged or treated as contradictory.
6. Full state history vs. latest-state collapse: both the Redis and webhook threads preserve every transition, not just the final state.

**One genuine tooling/gold defect discovered during evaluation**: `data/v6_memory.json` in this workspace is a stale leftover from the V7.1 series — its `case_id`s are `V71-*` and 19 of its 20 referenced event IDs do not exist anywhere in the V7.4 corpus at all (verified by direct set intersection; only 1 coincidental overlap, `E0449`, almost certainly an unrelated ID collision between independently generated corpora). This file could not be used as record-level ground truth. Evaluation instead used `data/benchmark_v7_4.json`'s `signal_event_ids` and per-case `required_event_ids`, which are genuinely V7.4-specific.

## 3. Consumption quality

| Condition | Cases | Applicable checks | Correct | Incorrect | Unsupported |
| --------- | ----: | -----------------: | ------: | --------: | -----------: |
| RAW              | 8 | 15 | 15 | 0 | 0 |
| RAG              | 8 | 15 | **5** | **10** | 0 |
| V6-GENERATED     | 8 | 18 | 18 | 0 | 0 |
| V6-GENERATED+RAW | 8 | 18 | 18 | 0 | 0 |

**RAG performance collapsed dramatically relative to V7.1-V7.3** (which each had exactly one failing case out of eight; this run has six of eight cases affected, and one case — V74-TIME-01 — retrieved zero required events out of three). This is a real, verified effect of the adversarial corpus design diluting the top-6 lexical retrieval budget across far more semantically similar noise, not a bug in my retrieval implementation (spot-checked: e.g. the query "Reconstruct webhook state through the latest known state" shares almost no vocabulary with "Webhooks were re-enabled after idempotency handling was deployed" beyond the word "webhooks" itself, so it loses the ranking to unrelated chunks across 1,200 noisy events).

Every RAG answer under-evidenced by a retrieval gap explicitly reported the gap rather than guessing or falling back to the full corpus (which the protocol forbids).

## 4. Cross-agent quality

- **Copilot → Claude**: executed by this session. Read only `results/copilot.memory.json` (SHA-256 verified exact match: `a7a44a01...8ac702`), no raw conversation, no gold. Copilot's memory (6 highly-consolidated records vs. my own 11) was fully sufficient to answer all 8 delayed queries correctly. One granularity note flagged in the handoff record: Copilot's record R1 lists event E0803 (Copilot's own later memory-preservation step) in `source_event_ids` but does not narrate it as a distinct provenance role in the record's text fields, unlike my own artifact's explicit `provenance` record (R011) — a real structural difference between the two writers' choices, not an error.
- **Claude → Copilot**: **not executed by this session.** I cannot genuinely act as "the Copilot agent." `results/claude_to_copilot.json` retains Copilot's own honest `not_executed` placeholder from when it ran (correctly written, since my memory artifact didn't exist yet). My `results/claude.memory.json` is now frozen and available for a genuine Copilot session to consume.

## 5. Retrieval failures

Detailed per-case in `results/claude.RAG.json`. Summary of required-event coverage by the deterministic top-6 lexical retriever (built fresh for this workspace as `src/build_rag_v74.py`, since the provided `src/build_rag.py` is hardcoded to nonexistent V7.1 files — see below):

| Case | Required | Retrieved | Missing |
|---|---|---|---|
| V74-HIST-01 | 3 | 2 | E0142 |
| V74-DEC-01 | 3 | 2 | E0732 |
| V74-ACT-01 | 3 | 2 | E0357 |
| V74-TIME-01 | 3 | 0 | E0402, E0888, E1191 (all 3) |
| V74-AMB-01 | 1 | 1 | none |
| V74-BELIEF-01 | 2 | 1 | E0449 |
| V74-NEG-01 | 2 | 2 | none |
| V74-PROV-01 | 5 | 2 | E0068, E0142, E0450 |

Only 2 of 8 cases had fully sufficient retrieval. This is the clearest and most severe RAG degradation across the V7.1-V7.4 series, and directly supports EXP-V7.4's stated hypothesis that semantic/lexical adversarial density stresses similarity-only retrieval harder than curated corpora do.

## 6. Tooling/specification defects (documented, not silently patched)

1. **`src/build_rag.py` is broken for this workspace**: hardcoded to read `data/conversation_v7_1.jsonl` and `data/benchmark_v7_1.json`, neither of which exists in `expv7_4/data/`. Running it as-is throws `FileNotFoundError`. I created `src/build_rag_v74.py` (same fixed deterministic lexical-retrieval algorithm, corrected to point at `conversation_v7_4.jsonl`/`benchmark_v7_4.json`, writing to `data/rag_index_v74.json`/`data/rag_retrievals_v74.json`) rather than overwrite the original script.
2. **`src/validate_v71.py` is broken for this workspace**: hardcoded to `benchmark_v7_1.json`'s case-ID set (`V71-*`), which rejects every V7.4 record (`V74-*` case IDs). I created `src/validate_v74.py`, a new V7.4-specific validator, rather than patch the old one.
3. **No consumption-result JSON schema was provided for V7.4** (only `schemas/memory_v74.schema.json` for the memory artifact itself exists). `src/validate_v74.py` validates consumption records structurally (case_id membership, condition enum, correctness dict shape, evidence_used array) without a formal JSON Schema file, since none was supplied to extend.
4. **`data/v6_memory.json` is stale/foreign to this corpus** (detailed in section 2 above) — a real gold-data defect, not just a tooling one.
5. **Cross-agent condition-label inconsistency reproduces from V7.3**: Copilot's `results/copilot.V6-GENERATED.json` and `results/copilot.V6-GENERATED+RAW.json` both use the literal string `"V6"` in their `condition` field despite correct filenames — the exact same pattern documented in the V7.3 report. This is now a *consistent* cross-run behavior in Copilot's output pipeline, not a one-off slip, worth fixing at the source rather than re-discovering each round. Surfaced as a non-fatal warning by `validate_v74.py` (16 warnings) rather than causing a hard failure.

## 7. Limitations

- No token or latency instrumentation available in this manual, interactive-session run; all `input_tokens`/`latency_ms` fields are `null` throughout.
- The clean-room writer subagent's report is trusted but not independently re-verified beyond checking its output artifact against gold post-hoc.
- The Claude→Copilot cross-agent handoff direction remains unexecuted pending a genuine Copilot session; only Copilot→Claude was genuinely completed here.
- RAG's severe degradation in this run is specific to the fixed top-6 lexical-overlap retrieval policy used throughout this experiment series; it should not be read as a claim about retrieval-augmented generation in general, only about this specific deterministic baseline under this specific adversarial corpus, per EXP-V7.4.md's own "Important distinction" section.
