---
name: training-generator
description: Create, deepen, revise, validate and package interactive educational courses and lessons as offline HTML5 players. Use for syllabus-based courses, rigorous adult technical education, age-appropriate lessons, narrated visual scene demonstrations, assessment banks and ChatGPT/Codex Skill-driven course generation, resumable one-module checkpoints, and external review handoffs.
---

# Training Generator

Build genuinely teachable courses, not outlines or decorative pages. Work module by module rather than compressing a long course into one shallow generation pass.

## Workflow
1. Identify learner, scope, target depth, syllabus basis, outcomes and offline needs; infer defaults when safe.
2. Design the full module/lesson index. Represent ungenerated lessons as `status:"planned"`; set root `status:"draft"` until all lessons are complete.
3. Read `references/teaching-quality.md`, `references/university-sources.md` and `references/course-schema.md`. Model the JSON on `references/example-lesson.json`.
4. Never use a slot-filled lesson factory: author **one complete coherent module per checkpoint** (split its lessons into separate passes when needed); keep the remainder planned. Research primary university materials and papers first; log source-specific links and evidence limits. Generate original graduate-depth lessons in one module JSON at a time, with mathematical derivations, real code, nontrivial worked steps and labs when appropriate. Preserve source provenance and distinguish verified links from suggested resources. Never invent source checks.
5. Reject cross-lesson duplication of prose, lab, pitfalls, visual sequences, code and question prompts. Run `python scripts/validate_course.py path/to/course.json`, repair every failure and investigate every quality warning rather than targeting the minimum, and check objective answer keys and technical accuracy separately.
6. Validate merged courses (module parts are inputs to merge, not standalone root courses). For large courses use `python scripts/merge_course.py index.json module1.json module2.json > course.json`, then run `python scripts/build_course.py course.json output.html`. The offline player shows the full index including disabled planned lessons, visual scene cues, browser speech, a resources pane and shuffled Practice Time questions.
7. Test the HTML in a browser if a browser harness is available. Otherwise report **static validation only — not browser-tested**. Deliver HTML, editable JSON, and a concise disclosure of unimplemented media and missing lessons.

## Shared chat / Codex orchestration
Read `references/orchestration.md` before creating, continuing, reviewing or approving a course. Use `scripts/checkpoint.py` for the same durable state transitions in both hosts when local execution is available. Advance the draft-generation lane after `selfreview` PASS using the checkpoint script; never promote a module to independently reviewed or approved without separate independent review and human approval. Chat can author and validate directly; Codex is optional, not a requirement for functional users. External provider review is only available if actually configured; otherwise export the review package and keep `review_pending`.

## Scale without losing quality
For large courses, keep a master index with planned lessons; write and validate one module at a time. Merge module JSONs with `scripts/merge_course.py` into a single validated course JSON; do not concatenate manually. The renderer accepts a single merged JSON file. Never label an outline a completed course. For full-course asks, preserve the complete planned index and deliver only the individually-authored lessons achieved in this pass; do not synthesize dozens of repetitive bodies.

## Honesty and boundaries
- Browser system speech may sound robotic and may be unavailable; this Player does **not** integrate Chatterbox, Qwen3-TTS, neural audio packaging, timestamp synchronization or word-level highlighting.
- Visual scenes advance on completed browser speech segments. They are simple interactive visual illustrations, not fully choreographed educational animation.
- HTTPS URL checks validate shape only; online availability and license rights require independent checks.
- The Skill contains no local model weights or execution environment; installed Skills depend on available host tools. Keep human voice quality and multimedia upgrades as future requirements, not delivered features.
- Treat AI-authored educational content as unverified until reviewed. Never claim compliance with a named school's official syllabus without its actual source.
- Correctness, browser support, question quality, reference validity and teaching effectiveness require checks beyond this simple structural validator.
