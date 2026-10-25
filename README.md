# Training Generator

Create substantial educational courses **one module at a time**, with offline HTML5 lessons, worked examples, practice questions, executable checks, and resumable checkpoints.

> **Status:** The Skill and its local tools are available in this repository. The generated AI Engineering course is **not fully uploaded here**. Course content is not publication-approved merely because its structural checks pass. External Claude/Codex execution and unattended hosted orchestration are not bundled.

## Quick installation

The installable Skill folder is **[`training-generator/`](training-generator/)**. Keep its `SKILL.md`, `scripts/`, `references/`, and `agents/` together. See **[INSTALL.md](INSTALL.md)** for step-by-step installation in ChatGPT, Claude, and Claude Code.

**Claude Code (Windows PowerShell; install for one project):**

```powershell
git clone https://github.com/lionellmisquitta/training-generator.git
cd training-generator
New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse -Force training-generator .claude/skills/
```

Open this repository in Claude Code; the Skill will be at `.claude/skills/training-generator/SKILL.md`. For a global Claude Code install, copy the `training-generator` folder to `~/.claude/skills/` instead.

**ChatGPT / Claude web:** create a ZIP containing exactly one top-level `training-generator/` folder, then use the product's custom Skill upload/import interface if it is available to your account. Do not upload only `SKILL.md`: the scripts and references are required. Installation steps and availability may differ by client and plan.

## How to use

Tell the assistant: **"Use Training Generator to create a course on [topic] for [audience]."** It should build a syllabus and author the next complete module rather than mass-generate shallow lessons.

To resume: **"Use Training Generator to continue from `CONTINUE_HERE.json`; preserve earlier modules and run the adversarial review."**

To validate or build a course locally (Python 3 required):

```bash
python training-generator/scripts/validate_course.py path/to/course.json
python training-generator/scripts/build_course.py path/to/course.json path/to/course.html
```

Open the resulting `course.html` in a browser. The player uses browser/system speech; external resources and neural voices are not packaged offline.

## Checkpoint flow

The draft-production lane is **`planned → review_pending → self_verified → next module`**. Self-verification consists of executable checks and an adversarial review report tied to the submitted module's SHA-256.

Independent review (such as actual Claude Code output) and human approval are **separate gates**. Never hand-edit `CONTINUE_HERE.json`, invent review evidence, or represent self-verified material as independently approved.

The command contract and report formats are in [orchestration.md](training-generator/references/orchestration.md). Teaching requirements are in [teaching-quality.md](training-generator/references/teaching-quality.md), and the course JSON structure is described in [course-schema.md](training-generator/references/course-schema.md).

## Project layout

```text
training-generator/                 # install this folder as one Skill
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
knowledge-graph/                    # early project knowledge baseline
courses/ai-engineering/             # status and import instructions; not full course data
```

## Current limitations

The validator checks structure and some originality heuristics; it does **not** establish factual accuracy, adequate pedagogy, browser correctness, independent review, or suitability for children. A separate reviewer must actually execute before its verdict is recorded. Automated cloud continuation, neural narration, SCORM export, and full browser QA are not included.

This repository is a reusable **course-authoring tool**, not a certified collection of completed courses.
