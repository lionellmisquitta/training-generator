
# Training Generator

[![Training Generator — One prompt in. A whole course out.](media/training-generator.gif)](media/training-generator-burst-graph-arrow.mp4)

**One prompt in. A whole course out.**

Turn a single prompt into a structured, interactive educational course — with in-depth lessons, worked examples, practice questions, and an offline HTML5 learning experience.

**▶ Click the animated demo above to watch the full video.**

---

## What is Training Generator?

Training Generator is an AI Skill that helps ChatGPT, Codex, and compatible AI assistants create comprehensive educational courses.

Rather than generating an entire course in one shallow pass, it develops one complete module at a time, validating and reviewing the content before proceeding.

### Key Features

- **AI-powered course creation** — Generate a structured syllabus from a topic, audience, and learning objective.
- **In-depth lessons** — Include explanations, worked examples, mathematical derivations, and executable code where appropriate.
- **Interactive HTML5 player** — Export courses as standalone HTML files that work offline.
- **Practice and assessments** — Generate quizzes and knowledge checks alongside lessons.
- **Narrated learning** — Use available browser speech synthesis to read lesson content aloud.
- **Resumable checkpoints** — Continue from the last verified module without regenerating previous work.
- **Adversarial quality reviews** — Identify duplicated material, incorrect answers, shallow explanations, and technical mistakes.
- **Independent review support** — Export review packages for evaluation by a separately configured reviewer such as Claude Code.
- **Portable workflow** — Use the Skill in compatible ChatGPT and Claude environments.

> **Development status:** The Skill and its local authoring tools are available. Independent review, browser testing, and human publication approval remain separate quality gates. Neural narration, full animation, and automatic cloud orchestration are not implemented.

---

## Sample Courses

### AI Engineering — 22 Lessons Across 11 Modules

Explore an AI Engineering course generated using the Training Generator workflow.

The course covers topics such as retrieval, model training, inference optimization, agents, evaluation, alignment, and enterprise deployment.

**[Explore the AI Engineering sample →](sample-courses/ai-engineering/README.md)**

The full course has been authored as a draft. Its complete player and source files are not yet fully uploaded to this repository.

**Quality status:** Ten modules previously passed independent review against their recorded hashes. Module 5 was subsequently repaired and requires another independent review. Course-wide assessment improvements and browser testing remain outstanding.

---

## Quick Installation

The reusable Skill is located in the [`training-generator/`](training-generator/) folder.

It contains:

- `SKILL.md` — Main Skill instructions
- `scripts/` — Course validation, checkpoint management, merging, and HTML generation
- `references/` — Course schemas, teaching-quality requirements, and review protocols
- `agents/` — ChatGPT Skill metadata

### Option 1 — ChatGPT

1. Download this repository using **Code → Download ZIP**.
2. Extract the repository.
3. Locate the inner `training-generator/` folder containing `SKILL.md`.
4. ZIP that folder, preserving its complete directory structure.
5. Import it through ChatGPT's custom Skills interface, where supported.

Do not upload only `SKILL.md`; the supporting scripts and references are part of the Skill.

### Option 2 — Claude Code

Install Git and Python 3, then open PowerShell:

```powershell
git clone https://github.com/lionellmisquitta/training-generator.git
cd training-generator

New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse -Force training-generator .claude/skills/
```

Start Claude Code in the project.

The installed Skill will be located at:

```text
.claude/skills/training-generator/SKILL.md
```

For global installation, place the Skill folder under `~/.claude/skills/`.

### Option 3 — Claude Web

Where custom Skills are supported, upload the same complete Skill ZIP through Claude's Skills interface.

**[Read the full installation guide →](INSTALL.md)**

---

## How to Use

Once the Skill is installed, ask your AI assistant:

**Example 1 — Create a course**

> Use Training Generator to create a graduate-level course on AI Engineering. Build the full syllabus, then generate and validate the first module.

**Example 2 — Create a school course**

> Use Training Generator to build a Grade 2 Mathematics course aligned with the syllabus I provide. Use age-appropriate explanations, worked examples, and practice questions.

**Example 3 — Continue an existing course**

> Use Training Generator to continue from CONTINUE_HERE.json. Preserve all previously generated modules and complete the next checkpoint.

**Example 4 — Review course quality**

> Run an adversarial review of the latest module. Check mathematical correctness, executable examples, assessment keys, teaching depth, and cross-lesson duplication.

---

## Build an Offline HTML Course

Python 3 is required for local validation and rendering.

Validate an existing course JSON:

```bash
python training-generator/scripts/validate_course.py path/to/course.json
```

Generate its standalone HTML player:

```bash
python training-generator/scripts/build_course.py path/to/course.json path/to/course.html
```

Open `course.html` in a modern browser.

The course player provides lesson navigation, practice questions, and browser-based narration. External learning resources may require an internet connection.

---

## Quality and Checkpoint Workflow

Training Generator maintains a resumable state for each course.

```text
Define Course
     |
     v
Create Full Syllabus
     |
     v
Author One Module
     |
     v
Validate + Test
     |
     v
Adversarial Self-Review
     |
     v
Self-Verified Checkpoint
     |
     v
Continue Next Module
```

Independent review and human approval happen through separate gates.

A self-verified module is **not automatically publication-approved**.

Checkpoint state is recorded in `CONTINUE_HERE.json` and managed through:

```text
training-generator/scripts/checkpoint.py
```

**[Read the checkpoint orchestration guide →](training-generator/references/orchestration.md)**

---

## Repository Structure

```text
training-generator/
|
|-- README.md
|-- INSTALL.md
|
|-- media/
|   |-- training-generator-demo.gif
|   |-- training-generator-burst-graph-arrow.mp4
|
|-- training-generator/
|   |-- SKILL.md
|   |-- agents/
|   |-- scripts/
|   |-- references/
|
|-- sample-courses/
|   |-- ai-engineering/
|
|-- knowledge-graph/
```

The structure above shows the intended demo and sample layout. The GIF and complete AI Engineering course assets must be uploaded before those components are fully available.

---

## Current Limitations

Training Generator is an evolving course-authoring system.

- Structural validation does not guarantee factual or pedagogical accuracy.
- Independent external review must actually be performed; it is not simulated.
- Browser speech uses available system voices, not bundled neural TTS.
- Visual scenes are not equivalent to fully choreographed animations.
- Browser compatibility and learning effectiveness require separate testing.
- SCORM export and unattended cloud orchestration are not currently included.
- Generated courses require appropriate human review before publication, particularly for children.

---

## Project Vision

**Make deep, structured education easier to create, validate, improve, and share.**

From a single prompt to an interactive course — without sacrificing learning quality for generation speed.
