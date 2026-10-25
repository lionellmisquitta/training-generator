# Training Generator

Reusable course-authoring Skill and knowledge baseline. **Status: v0.5 Skill implemented; v0.6 module checkpoint orchestration and independent Claude Code review are proposed, not yet implemented.**

## Current capability
- `training-generator/SKILL.md` is the current Skill.
- Its validator rejects substantial duplicate prose, repeated labs, duplicate code, and templated questions. The earlier Grade 2 Maths, Game Theory and full AI Engineering generated courses **failed** the v0.5 originality gate and are **not approved for publication**.
- The offline player builds HTML5 from course JSON, but no SCORM implementation, neural voice or independently validated course-content pipeline is claimed.

## Proposed workflow
1. Define the full curriculum and record evidence-backed concepts and prerequisites in `knowledge-graph/`.
2. Author **one module per checkpoint**, without mass-generating templated lessons.
3. Run deterministic tests and cross-module duplication checks.
4. Run an independently configured Claude Code reviewer in an isolated read-only workspace; require reproducible defects and evidence.
5. Repair, retest, and request human publication approval. Only then mark module `approved`.
6. Save `CONTINUE_HERE.json` and content hashes; resume from the last approved module.

Codex-to-Claude orchestration, provider adapters, persistent checkpoint runner, SCORM export, and full Graph Generator KGP visualizations are future implementation work.

## Knowledge baseline
`knowledge-graph/nodes.jsonl`, `relationships.jsonl`, `evidence.jsonl`, `decisions.md`, `unknowns.md`. These are **initial source-grounded graph records**, not a validated full KGP package. See `knowledge-graph/README.md`.

## Safety
Do not publish earlier course exports. A passing structural validator is not proof of teaching effectiveness. Child-facing material requires educator review and learner testing.
