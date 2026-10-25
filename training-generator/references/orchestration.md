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
python training-generator/scripts/checkpoint.py submit --course courses/example --module module-1.json
python training-generator/scripts/checkpoint.py review --course courses/example --report independent-review.json
python training-generator/scripts/checkpoint.py approve --course courses/example --approver "Human reviewer"
```

Each checkpoint stores content SHA256, validation and review status. Review PASS must match the exact bytes. Human approval follows independent review. No review, no approval. Publication is separately controlled. Chat does not secretly start Codex or Claude Code; it executes the same portable workflow using accessible tools, or supplies a package when persistence is unavailable. A GitHub commit is required for persistent sharing; filesystem atomic writes do not imply atomic GitHub operations.

Independent Claude Code / other provider review is conditional on an authenticated installed runner and isolated permissions. Child-facing content additionally needs educator and learner validation. The rejected 2026 mass-generated courses must never be marked approved. 