# Install in Claude

**Download:** [Training Generator skill.zip](skill.zip) (appears here after packaging completes).

**Claude web:** Where custom Skills upload is supported, download the ZIP, upload/import it through your Skills settings, then ask Claude to use Training Generator.

**Claude Code:** Download and extract the ZIP to your project's `.claude/skills/` so the final path is `.claude/skills/training-generator/SKILL.md`. For a global installation, extract to `~/.claude/skills/` instead.

Example prompt: **"Use Training Generator to create a course on [topic] for [audience]. Generate the syllabus and only Module 1 with a review checkpoint."**

This package uses the same portable Skill source as ChatGPT; it does not bundle an autonomous Claude reviewer, a paid API, or an auto-publishing service.

[Detailed guide](../INSTALL.md) · [Home](../README.md)
