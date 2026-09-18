# EXP-V7.3 — Claude Code report

## Execution provenance
- agent identity: `claude`
- number of cases: 8
- number of conditions: 4 (RAW, RAG, V6-GENERATED, V6-GENERATED+RAW)
- total consumption records: 32 (8 × 4), plus `results/claude.memory.json` (47-record generated memory) and `results/claude.memory_eval.json` (evaluation against gold), plus a filled `results/copilot_to_claude.json` (cross-agent reader step, replacing a prior honest `not_executed` placeholder).
- validation: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` → 4 passed (unrelated local `--browser` pytest-plugin conflict requires that env flag in this environment, same as V7.1/V7.2). `python src/validate_v73.py` (a **new V7.3-specific validator created for this run**, see "Tooling/specification defects" below) → 64 consumption records validated across both agents' files, 2 memory artifacts found, 2 memory_eval artifacts found, 2 cross-agent handoff artifacts found, with 17 non-fatal warnings surfaced (16 condition-label + 1 memory-key inconsistency, both from Copilot's files — detailed below). All 32 of my own consumption records additionally pass strict `jsonschema.validate` against a new `schemas/agent_result_v73.schema.json`.

## Writer methodology (clean-room delegation, disclosed per protocol)

I could not personally perform Phase 1 as a genuine blind writer: earlier in this same session I had already read the gold `data/v6_memory.json`, the labeled corpus, and the benchmark case definitions during the V7.1/V7.2 tasks. Per RUN_PROMPT.md's explicit instruction ("If your current session has previously seen the gold memory or prior results, delegate Phase 1 to a fresh clean-room subagent and disclose that in the report"), I:

1. Constructed an **unlabeled writer-view corpus** at `data/conversation_v73_unlabeled.jsonl` — the same 1,200 events with the `kind` (signal/distractor) field stripped, everything else (event_id, timestamp, speaker, text, topics) intact. This file is a new artifact created for this run, not a modification of `data/conversation_v7_1.jsonl`.
2. Spawned a fresh subagent with an explicit allow-list of exactly 2 readable files (`EXP-V7.3.md` and the unlabeled corpus) and an explicit deny-list covering the labeled corpus, gold memory, benchmark file, all `results/`, and all prior V7.0/V7.1/V7.2 writeups.
3. The subagent confirmed in its own report reading exactly those 2 files and no others, and produced `results/claude.memory.json` using pure content-based judgment (it detected that 1,180 of 1,200 events shared a literal repeated boilerplate substring — "routine progress and no final decision" — and treated those as non-durable noise, keeping the remaining 20 individually-read events because each contained a decision, outcome, state transition, confirmation/inference, ambiguity, or explicit negative-knowledge statement).

I then performed Phases 2–5 myself, since those explicitly require gold access.

## Selection metrics (full detail in `results/claude.memory_eval.json`)

- **Selection recall = 1.0, precision = 1.0, F1 = 1.0**: all 20 gold signal event IDs retained, zero false positives, zero false negatives, out of 1,200 events (retention ratio 1.67%, compression ratio 98.33%).
- **Important caveat, verified and disclosed rather than left as an uncomplicated win**: I checked whether the corpus's signal/distractor boundary is a genuinely hard semantic discrimination problem or an easy lexical one. It is the latter — the boilerplate substring the writer used as its exclusion filter has **zero mismatches** against the `kind` label across all 1,200 events (verified directly by string-matching against the labeled corpus after the writer artifact was frozen). This means the perfect selection score demonstrates clean execution of an easy version of the selection problem in this particular synthetic benchmark, not strong evidence that blind importance-selection generalizes to corpora without such a clean lexical tell. This is a property of the benchmark corpus generator, not something I was asked to or should fix.

## Memory metrics

- Observation coverage: 20/20 gold event IDs, 0 invented event IDs, recall = precision = 1.0.
- Relationship/state/proposition semantic coverage: high. All gold relationship and state claims have a semantic counterpart in generated memory; two cases (V71-ACT-01's invoice-export thread and the full webhook-migration thread) received fully independent state_history structures the writer built with zero knowledge that these were "benchmark cases" at all.
- Ambiguity: both conclusions match gold (unresolved between Rahul/Arjun), but generated memory kept **two separate ambiguity records** (one per source event, E0312 and E0515) rather than gold's single merged record, specifically because the corpus text never explicitly states the two mentions concern the same referent. This is a documented, defensible representational divergence, not an error.
- Belief history / provenance chain: both fully preserve the observation → confirmation → inference → confirmation → later-memory-read sequence with correct epistemic-status labels and no agent collapsed into an anonymous source; the generated provenance chain is a 6-step superset of gold's 5 steps (adds the original E0005 decision as an earlier step).
- Negative knowledge: exact semantic match to gold, correctly grounded in the explicit positive completeness statement (E0548), not retrieval absence.
- Invented-record rate: 0.

## Consumption metrics

| Condition | Cases | Applicable checks | Correct | Incorrect | Unsupported |
| --------- | ----: | -----------------: | ------: | --------: | -----------: |
| RAW              | 8 | 15 | 15 | 0 | 0 |
| RAG              | 8 | 16 | 14 | 2 | 0 |
| V6-GENERATED     | 8 | 18 | 18 | 0 | 0 |
| V6-GENERATED+RAW | 8 | 18 | 18 | 0 | 0 |

The single RAG failure is the same deterministic gap observed identically in V7.1 and V7.2 (re-verified fresh this run): the top-6 retrieved chunks for V71-TIME-01 contain only 2 of 4 required events (E0233, E0401), missing E0887/E1190 (webhooks-disabled, webhooks-re-enabled). My RAG answer explicitly reported this as an evidence gap rather than guessing, so `factual`/`temporal` were marked `false` (unanswered, not wrong-but-confident).

## Cross-agent result

- **Copilot → Claude** (this session as reader): executed. Read only `results/copilot.memory.json` (SHA-256 verified: `71aa87c5...b95f` matches exactly, confirming genuine consumption of the frozen artifact, not a fabricated summary). All 8 delayed queries answered correctly from Copilot's 19-record memory alone, no raw conversation consulted. Result written to `results/copilot_to_claude.json`, replacing a prior honest `not_executed` placeholder that Copilot's own session had left there (correctly, since Claude's memory artifact didn't exist yet when Copilot ran).
- **Claude → Copilot**: **not executed by this session.** I cannot genuinely act as "the Copilot agent" — doing so would mean fabricating a cross-model result. `results/claude_to_copilot.json` still contains Copilot's own honest `not_executed` placeholder from its run (correctly written at the time, since my `claude.memory.json` didn't exist yet). My `claude.memory.json` is now frozen and available; this handoff direction requires a genuine Copilot session to pick it up and is left as-is rather than faked.

## Failures and retrieval gaps

Only one failure across all 32+8 = 40 answered cases in this run: **V71-TIME-01 under RAG**, described above. No failures in RAW, V6-GENERATED, V6-GENERATED+RAW, or the Copilot→Claude cross-agent handoff.

## Tooling/specification defects (documented, not silently patched)

1. **Condition-enum mismatch** (same class of issue as V7.2): `schemas/agent_result_v71.schema.json`'s `condition` enum only allows the V7.1-era `RAW/RAG/V6/V6+RAW` strings, but EXP-V7.3.md (inheriting from EXP-V7.2.md) requires the distinct `V6-GENERATED`/`V6-GENERATED+RAW` condition names. I created `schemas/agent_result_v73.schema.json` (enum extended only, base file untouched) and a new `src/validate_v73.py` (the repo had no V7.3-specific validator), per RUN_PROMPT.md's explicit instruction.
2. **Cross-agent condition-label inconsistency, found via the new validator**: Copilot's own `results/copilot.V6-GENERATED.json` and `results/copilot.V6-GENERATED+RAW.json` files use the literal string `"V6"` in their `condition` field (8 records each, 16 total) despite the filenames correctly using the V7.3 names. My validator treats this as a non-fatal warning (surfaced explicitly, 16 warnings printed) rather than crashing, since rejecting Copilot's genuinely-executed results over a label string would be worse than flagging the inconsistency for the consolidated report to note. This is exactly the kind of cross-agent labeling drift V7.1's consolidated report also had to call out (there, a contradictory sentence in Copilot's V7.1 report needed correcting) — it reproduces as a live example rather than a one-off.
3. **Memory-artifact key-naming inconsistency**: `results/claude.memory.json` uses a top-level `"memory"` key for its record list; `results/copilot.memory.json` uses `"records"` instead. Both are structurally reasonable; neither is specified as mandatory in EXP-V7.3.md. My validator accepts either with a warning rather than picking one as canonical.
4. **`AGENT_HANDOFF.md` in this directory is stale**: it is a verbatim copy of the V7.2 handoff (references `expv7_2`, V7.2-era phase numbering, and V7.2's writer protocol which still permits `raw_event_ids`/case IDs — directly contradicting V7.3's core "no relevance hints" rule). I did not follow it; I followed `EXP-V7.3.md`, `README.md`, and `RUN_PROMPT.md`, which are internally consistent with each other and specific to V7.3. This mismatch is disclosed here rather than silently worked around, since a future run could otherwise be misled by that file's presence.

## Limitations

- No token or latency instrumentation was available in this manual, interactive-session run; all `input_tokens`/`latency_ms` fields are `null` throughout, as required.
- The clean-room writer subagent's report is trusted but not independently re-verified beyond checking its output artifact against gold post-hoc (e.g., I cannot literally prove it never glanced at a forbidden file beyond its own attestation and the tool-call structure I gave it).
- This run's perfect selection score should not be read as general evidence that blind memory-formation from arbitrary noisy corpora is a solved problem — see the boilerplate-lexical-tell caveat above, which is the single most important limitation of this specific result.
- The Claude→Copilot cross-agent handoff direction remains unexecuted pending a genuine Copilot session.
