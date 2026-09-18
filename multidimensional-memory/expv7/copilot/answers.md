# Copilot EXP-V7 Answers

## V7-HIST-01

- RAW: We tried approach A first last week. We abandoned it because latency was too high, then switched to approach B.
- RAG: We tried approach A first last week. It failed because latency was too high, so we switched to approach B.
- V6: `obs-hist-1` records approach A as first; `obs-hist-2` records excessive latency as the failure reason; `obs-hist-3` records the switch to approach B.
- V6+RAW: Same answer as RAW, with `obs-hist-1` through `obs-hist-3` as supporting provenance.

## V7-ACT-01

- RAW: We attempted Redis caching. It reduced repeated database reads, but caused stale-data issues, so the change was put on hold.
- RAG: Same answer, supported by the retrieved case chunk.
- V6: `obs-act-1` through `obs-act-4` record the attempt, reduced reads, stale-data issues, and hold decision.
- V6+RAW: Same answer, verified against the linked raw case.

## V7-TIME-01

- RAW: Polling was used in January; in March it was changed to webhooks; in May webhooks were temporarily disabled during migration. The latest known state is temporarily disabled webhooks.
- RAG: Same temporal sequence and latest state, supported by the retrieved case chunk.
- V6: `obs-time-1` through `obs-time-3` preserve the January, March, and May sequence. Latest state is temporarily disabled webhooks.
- V6+RAW: Same answer, verified against linked raw evidence.

## V7-AMB-01

- All conditions: The reference remains ambiguous. The supplied evidence does not establish whether `He` referred to Rahul or Arjun. No interpretation is selected.

## V7-CONFLICT-01

- All conditions: Memory records Jaipur from Agent A and Delhi from Agent B. The observations overlap without a temporal explanation, so the deployment target is disputed. Provenance is preserved; neither observation is silently selected.

## V7-NEG-01

- All conditions: Yes, the complete conversation establishes that MongoDB was not discussed. This negative claim is supported because the case explicitly identifies the conversation as complete.

## V7-PROV-01

- All conditions: Codex originally observed that the migration failed, and Claude later confirmed the failure after reviewing test output.
