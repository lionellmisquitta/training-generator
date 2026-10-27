# Game Theory Explained — 11-module repaired course draft

**Status: educational draft, not approved for public course release.**

The downloadable [course package](./Game_Theory_Explained_M01_M11_Repaired_Draft.zip) contains all 11 modules, 22 lessons, 88 questions, the offline-oriented HTML player, canonical JSON, module sources, checkpoint state, QA evidence and independent review history.

## Verification and approval

- Training Generator v2.3 draft release gate: **PASS**.
- Numerical/structural M10–M11 audit: **110 checks pass**.
- Modules M01–M08 are unchanged and preserve independent reviews bound to their exact content hashes.
- Modules M09–M11 were repaired following Claude's independent review; **their previous reviews do not approve the new hashes**.
- The publication release gate intentionally **FAILS**: fresh M09–M11 independent review, human module/course approval, and current-player browser acceptance remain outstanding.

## Repairs made

- M09: removed conflicting entrant entry-cost value 950; retained 800 consistently.
- M10: added runnable fairness/logit and population-dynamics Python checks; replaced a dominance/penalty example with a genuine compatibility-bridge coordination case (threshold from 4/7 to 0.40).
- M11: added executable mixed-strategy and supplier-contract checks and explicitly identified deliberate reuse of Module 3 inspection-game concepts.

See `README.md`, `CLAUDE_REVIEW_HANDOFF.md`, `qa/REPAIR_QA.json` and `evidence/` inside the ZIP for reconstruction and verification instructions.

The archive is a **sample draft for review**, not a certified or human-approved published educational edition.
