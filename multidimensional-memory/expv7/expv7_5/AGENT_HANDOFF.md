# V7.5 Agent Handoff

## Parallel phase
Claude and Copilot run independently. Neither waits for the other.

Each freezes:
- `results/<agent>.memory.json`
- `results/<agent>.memory_eval.json`
- `results/<agent>.report.md`
- condition result files

## Post-run phase
Only after BOTH memory files exist does the orchestrator run:
- Claude memory → Copilot reader
- Copilot memory → Claude reader

If a memory is unavailable at the post-run barrier, the handoff is `not_executed`; agents must never impersonate the other model.

## Freeze rule
After SHA-256 freeze, writer memory cannot be edited to improve query performance.
