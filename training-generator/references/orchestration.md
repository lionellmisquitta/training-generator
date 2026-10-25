# Shared Chat and Codex execution contract (v0.6)

Both hosts use the same `training-generator/SKILL.md`, course schema, validator and persisted `CONTINUE_HERE.json`.

Functional user requests:
- "Create a course": establish full syllabus with planned lessons; create the checkpoint index; author only the next coherent module.
- "Continue course": retrieve stored checkpoint, verify approved artifact hashes and work only on the next unapproved module.
- "Review module": call a real independent reviewer if configured or export a handoff. Never synthesize review results.
- "Show progress": read the checkpoint file, not conversation history.

Local runner:
```bash
python training-generator/scripts/checkpoint.py init --course courses/example --index syllabus.json
python training-generator/scripts/checkpoint.py status --course courses/example
python training-generator/scripts/checkpoint.py submit --course courses/example --module module-1.json --author Codex
python training-generator/scripts/checkpoint.py review --course courses/example --report independent-review.json
python training-generator/scripts/checkpoint.py approve --course courses/example --approver "Human reviewer"
```

Each checkpoint stores content SHA256, validation and review status. Review PASS must match the exact bytes. Human approval follows independent review. No review, no approval. Publication is separately controlled. Chat does not secretly start Codex or Claude Code; it executes the same portable workflow using accessible tools, or supplies a package when persistence is unavailable. A GitHub commit is required for persistent sharing; filesystem atomic writes do not imply atomic GitHub operations.

Reviewer identity is an **honour-system metadata assertion**, not cryptographically proven independence. The checkpoint tool rejects the same author/reviewer string when author is supplied, but cannot establish model identity or prevent fabricated reviews. The reviewer must be a different model or independently isolated session from the author, whichever host is running. No real reviewer has been connected automatically.

Review JSON example:
```json
{"module_sha256":"<sha256-of-module-json-file>","verdict":"pass","reviewer":"Claude Code","findings":[]}
```
The SHA must match the submitted module artifact exactly. A failing verdict sets `needs_repair`; passing only sets `review_passed` pending human approval. Submit must preserve the exact planned lesson titles (case/whitespace normalized); curriculum changes need an explicit separately reviewed replan before resubmission.

Independent Claude Code / other provider review is conditional on an authenticated installed runner and isolated permissions. Child-facing content additionally needs educator and learner validation. The rejected 2026 mass-generated courses must never be marked approved. 