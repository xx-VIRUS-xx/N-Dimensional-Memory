# Claude Code (Sonnet 5) — EXP-V7 answers

agent_id: `claude-sonnet-5`

For each case, four answers are given, one per condition, using only the evidence that condition permits (see `conditions/`).

---

## V7-HIST-01 (historical_recall)
**Query:** What did we try first, why did we abandon it, and what did we switch to?

- **RAW:** We tried approach A first. We abandoned it because latency was too high. We switched to approach B.
- **RAG:** (fallback = full conversation, since no chunk scored > 0 on keyword overlap) We tried approach A first. We abandoned it because latency was too high. We switched to approach B.
- **V6:** Per stored proposition HIST-01-P1: approach A was tried first (o1), abandoned due to high latency (o2, linked to o1), then approach B was adopted (o3, linked to o2). Current state: approach B.
- **V6+RAW:** Same as V6, cross-checked against the linked raw evidence (o1–o3 map directly to the three source sentences) — no discrepancy found.

---

## V7-ACT-01 (action_outcome)
**Query:** What did we attempt and what was the outcome?

- **RAW:** Redis caching was attempted. Outcome: it reduced repeated database reads (positive) but introduced stale-data issues (negative). As a result, the change was put on hold.
- **RAG:** (fallback = full conversation) Same as RAW.
- **V6:** Per proposition ACT-01-P1: Redis caching attempted (o1); mixed outcome — reduced reads (o2, positive) and stale-data issues (o3, negative), both linked to o1; decision to put on hold (o4, linked to o2 and o3).
- **V6+RAW:** Same as V6, verified against linked raw sentence — consistent.

---

## V7-TIME-01 (temporal_state)
**Query:** What is the latest known service state, and how did it evolve?

- **RAW:** Latest state: webhooks are temporarily disabled (as of May) during migration. Evolution: polling (January) → webhooks (March) → webhooks temporarily disabled (May).
- **RAG:** Only chunk c1 ("In January the service used polling.") was retrieved (keyword overlap policy scored only this chunk > 0 against the query). **Based on retrieved evidence alone, only the January/polling state is supported; the March and May updates are not visible under this retrieval.** This is a genuine RAG failure mode for this case — flagged rather than silently supplemented from outside knowledge.
- **V6:** Per proposition TIME-01-P1: polling (Jan, o1) → superseded by webhooks (Mar, o2) → superseded by webhooks disabled temporarily during migration (May, o3). Derived current state: "webhooks disabled temporarily (migration in progress) as of May." Full history preserved and explicitly sequenced.
- **V6+RAW:** Same as V6, cross-checked against full raw conversation — consistent, and confirms the RAG condition's retrieval gap was a retrieval-policy artifact, not a memory-content gap.

---

## V7-AMB-01 (ambiguity)
**Query:** Who did "He" refer to?

- **RAW:** The conversation states Rahul spoke with Arjun about the deployment, and "He" said the rollout should wait. The text does not establish whether "He" refers to Rahul or Arjun — the reference is ambiguous and is not resolved by the conversation.
- **RAG:** Retrieved chunk: "The conversation did not establish whether 'He' meant Rahul or Arjun." This directly states the ambiguity is unresolved.
- **V6:** Per ambiguity record amb1 (linked to proposition AMB-01-P1): candidate referents are Rahul and Arjun; resolution_status is `unresolved`. Per instruction, this is reported as unresolved rather than guessed.
- **V6+RAW:** Same as V6, confirmed against raw evidence — no additional disambiguating information exists in the full conversation either.

---

## V7-CONFLICT-01 (contradiction)
**Query:** What does memory say about the deployment target?

- **RAW:** Agent A recorded the target as Jaipur; Agent B later recorded it as Delhi, with overlapping validity and no temporal explanation given. The two observations conflict and neither is marked as superseding the other.
- **RAG:** Both chunks were retrieved (both scored equally on keyword overlap). Same conflicting pair surfaced: Jaipur (Agent A) vs. Delhi (Agent B), no resolution given.
- **V6:** Per proposition CONFLICT-01-P1: o1 (Agent A: Jaipur) and o2 (Agent B: Delhi) are both recorded as overlapping-validity observations. Conflict record c1 marks resolution_status as `disputed`. Both observations are preserved; neither overwrites the other. Answer: memory shows a disputed deployment target — Jaipur per Agent A, Delhi per Agent B — with the disagreement explicitly preserved rather than resolved.
- **V6+RAW:** Same as V6; raw evidence confirms no temporal ordering that would justify resolving the conflict.

---

## V7-NEG-01 (negative_knowledge)
**Query:** Have we discussed MongoDB in this conversation?

- **RAW:** No. The supplied conversation discusses PostgreSQL, Redis, and S3, and explicitly states there is no discussion of MongoDB anywhere in this benchmark case. Since this is stated to be the complete conversation, "never discussed" is supported here.
- **RAG:** Retrieved chunks include the explicit negative statement ("There is no discussion of MongoDB anywhere in this benchmark case.") plus the topic-list chunk. Same answer: MongoDB was not discussed.
- **V6:** Per proposition NEG-01-P1, negative_knowledge record: topic MongoDB, status `not_discussed`, basis "complete conversation supplied to this case does not mention MongoDB," completeness_of_evidence marked "complete for this benchmark case." Answer: MongoDB was not discussed.
- **V6+RAW:** Same as V6, cross-checked against raw text — consistent.

---

## V7-PROV-01 (provenance)
**Query:** Who originally observed the failure, and who later confirmed it?

- **RAW:** Codex originally observed that the migration failed. Claude later confirmed the failure after reviewing the test output.
- **RAG:** Both chunks retrieved (both scored > 0). Same answer: Codex observed first, Claude confirmed later based on test output.
- **V6:** Per proposition PROV-01-P1: o1 (source: Codex, type: original_observation, "the migration failed"), o2 (source: Claude, type: confirmation, linked to o1, basis: "reviewed test output"). Answer distinguishes original observation (Codex) from later confirmation (Claude), preserving provenance and basis.
- **V6+RAW:** Same as V6; raw evidence confirms both attributions and the confirmation basis.
