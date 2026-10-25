
# Training Generator

Build genuinely teachable courses, not outlines or decorative pages. Work module by module rather than compressing a long course into one shallow generation pass.

## Workflow
1. Identify learner, scope, target depth, syllabus basis, outcomes and offline needs; infer defaults when safe.
2. Design the full module/lesson index. Represent ungenerated lessons as `status:"planned"`; set root `status:"draft"` until all lessons are complete.
3. Read `references/teaching-quality.md`, `references/university-sources.md` and `references/course-schema.md`. Model the JSON on `references/example-lesson.json`.
4. Never use a slot-filled lesson factory: author one coherent module per checkpoint, splitting its lessons into multiple passes if necessary; keep the remainder planned. Research primary university materials and papers first; log source-specific links and evidence limits. Generate original graduate-depth lessons in one module JSON at a time, with mathematical derivations, real code, nontrivial worked steps and labs when appropriate. Preserve source provenance and distinguish verified links from suggested resources. Never invent source checks.
5. Reject cross-lesson duplication of prose, lab, pitfalls, visual sequences, code and question prompts. Run `python scripts/validate_course.py path/to/course.json`, repair every failure and investigate every quality warning rather than targeting the minimum, and check objective answer keys and technical accuracy separately.
6. Validate merged courses (module parts are inputs to merge, not standalone root courses). For large courses use `python scripts/merge_course.py index.json module1.json module2.json > course.json`, then run `python scripts/build_course.py course.json output.html`. The offline player shows the full index including disabled planned lessons, visual scene cues, browser speech, a resources pane and shuffled Practice Time questions.
7. Test the HTML in a browser if a browser harness is available. Otherwise report **static validation only — not browser-tested**. Deliver HTML, editable JSON, and a concise disclosure of unimplemented media and missing lessons.

## Mandatory adversarial pre-completion review

Before treating any lesson as complete, perform a deliberate adversarial self-verification pass, including in chat. Follow references/adversarial-review.md: challenge topic coverage, syllabus alignment, prerequisites, solved mathematics, assessment answer keys, executable code, age-appropriate teaching visuals, originality against prior lessons, citations and offline player behavior. Run applicable tests, repair defects, and repeat up to three times. Persist evidence tied to module SHA. Never claim tests not executed.

Chat may produce a SELF-VERIFIED DRAFT after passing these checks but cannot claim independent review. Do not pretend to invoke Claude or bypass the independent-review checkpoint. In Codex/VS Code, when separately installed and authenticated, invoke Claude Code as independent reviewer of the frozen artifact SHA. Otherwise leave review pending. The approved state still requires its separate approval gate.

## Shared Chat, Codex, and Claude Code orchestration

Read `references/orchestration.md` for identical host-neutral commands and state transitions. Functional users can author, resume and review through chat without knowing Codex; a CLI user can run the same skill. Use `scripts/checkpoint.py` whenever a local execution environment is available. Each module needs deterministic validation, an independently supplied review PASS tied to its SHA-256 (reviewer identity is metadata, not cryptographic proof), and separate explicit human approval before advancing. Without reviewer access, export a review handoff and leave the checkpoint `review_pending`. Do not invent cross-session persistence or claim automatic Claude Code calls from chat.

## Scale without losing quality
For large courses, keep a master index with planned lessons; write and validate one module at a time. Merge module JSONs with `scripts/merge_course.py` into a single validated course JSON; do not concatenate manually. The renderer accepts a single merged JSON file. Never label an outline a completed course. For full-course asks, preserve the complete planned index and deliver only the individually-authored lessons achieved in this pass; do not synthesize dozens of repetitive bodies.

## Honesty and boundaries
- Browser system speech may sound robotic and may be unavailable; this Player does **not** integrate Chatterbox, Qwen3-TTS, neural audio packaging, timestamp synchronization or word-level highlighting.
- Visual scenes advance on completed browser speech segments. They are simple interactive visual illustrations, not fully choreographed educational animation.
- HTTPS URL checks validate shape only; online availability and license rights require independent checks.
- The Skill contains no local model weights or execution environment; installed Skills depend on available host tools. Keep human voice quality and multimedia upgrades as future requirements, not delivered features.
- Treat AI-authored educational content as unverified until reviewed. Never claim compliance with a named school's official syllabus without its actual source.
- Correctness, browser support, question quality, reference validity and teaching effectiveness require checks beyond this simple structural validator.
