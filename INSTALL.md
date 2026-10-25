# Installation and first run

## 1. Download the Skill

From the [repository](https://github.com/lionellmisquitta/training-generator), choose **Code → Download ZIP**, extract it, and locate the **inner** `training-generator/` directory (the folder containing `SKILL.md`). Do not confuse it with the outer repository folder of the same name.

The installable directory must contain `SKILL.md`, `scripts/`, and `references/`.

## 2. Choose your host

### ChatGPT custom Skills

Where custom Skill import is supported, ZIP **only the inner `training-generator/` folder**, preserving that top-level directory, and upload the ZIP through ChatGPT's Skills interface. The exact menu and availability vary by account/client. A GitHub URL by itself does not install the Skill.

### Claude web custom Skills

Where custom Skill upload is supported, import the same ZIP through Claude's Skills settings. Keep the folder intact. `agents/openai.yaml` is ChatGPT-specific metadata and is not required for Claude's execution.

### Claude Code on Windows (project-specific)

Install Git and Python 3 first. Open PowerShell:

```powershell
git clone https://github.com/lionellmisquitta/training-generator.git
cd training-generator
New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse -Force training-generator .claude/skills/
```

The resulting Skill should be at `.claude/skills/training-generator/SKILL.md`. Start Claude Code in this project and ask it to use Training Generator. For a global installation, use `$HOME/.claude/skills/training-generator/`.

## 3. Try it

Request: **"Use Training Generator to create a beginner-to-advanced course on game theory for adults. Create the index and author only the first module. Validate it and save a checkpoint."**

Or resume an existing course: **"Continue from `CONTINUE_HERE.json` and generate only the next module; do not overwrite verified lessons."**

## 4. Validate your course

From the repository's root folder:

```bash
python training-generator/scripts/validate_course.py path/to/course.json
python training-generator/scripts/build_course.py path/to/course.json path/to/course.html
```

The rendered HTML is offline-capable. Speech uses available browser voices; resource links may require internet. The browser must still be tested separately.

## 5. Understand checkpoints

A passing self-review allows **draft continuation**, not publication. An independently executed reviewer and human approval are separate. The canonical state is `CONTINUE_HERE.json`, which must be updated only through `training-generator/scripts/checkpoint.py`. Read [the orchestration contract](training-generator/references/orchestration.md) for exact commands and report JSON.

## Troubleshooting

- **Skill not discovered:** confirm the top-level installed folder has `SKILL.md` and no extra nested directory.
- **Cannot import ZIP:** confirm there is only one Skill folder, that the platform supports custom Skill upload, and that the archive includes the supporting scripts and references.
- **Checkpoint won't advance:** run `checkpoint.py status`; inspect the failed validation or self-review hash. Do not edit the state by hand.
- **Validation passes but lesson looks thin:** structural validation is only a baseline; require adversarial review and real teaching depth.
