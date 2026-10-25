# Shared chat / Codex orchestration (checkpoint engine v0.7)

The checkpoint engine is the sole writer of CONTINUE_HERE.json. The authoring host (chat, Codex, Claude Code) does not hand-edit state.

## Draft-production lane

`planned -> review_pending -> self_verified` using the following commands:

```bash
python scripts/checkpoint.py init --course courses/my-course --index syllabus.json
python scripts/checkpoint.py submit --course courses/my-course --module module-1.json --author ChatGPT
python scripts/checkpoint.py selfreview --course courses/my-course --report self-review.json
python scripts/checkpoint.py status --course courses/my-course
```

After self-verified, the next module may be submitted. All earlier submitted module bytes and SHA-256 hashes are checked on every operation. Self-review report requires `module_sha256`, `review_type:"self_adversarial"`, `overall:"pass"`, `checks` with result (`pass` or `not_executed`) and supporting `evidence`, and `findings`. At least one check must pass; any failed check or unresolved blocking finding prevents completion. `not_executed` must never be described as passed. Self-review is not independent review and grants no publication permission.

## Separate independent review / publication lane

```bash
python scripts/checkpoint.py review --course courses/my-course --module-id m01 --report claude-review.json
python scripts/checkpoint.py approve --course courses/my-course --module-id m01 --approver 'Actual human approver'
```

External review JSON: `{"module_sha256":"exact-content-sha256", "verdict":"pass", "reviewer":"Claude Code", "findings":[]}`. Reviewer identity is user-provided metadata, not cryptographic proof of independence. The engine rejects matching author/reviewer names and incorrect hashes. Approval requires an independent PASS and named human approver. Chat may continue drafting modules while external review trails, without auto-approving any module. A failed independent review marks that module `needs_repair` and blocks new work until reconciliation.

## Recovery

Restore the course directory and call `status` before doing anything else. For historical manually edited state files, create a NEW checkpoint state by `init` using the original syllabus and sequentially `submit` and `selfreview` each module using its existing, byte-for-byte preserved source file and authentic self-review report. Never synthesize a historical self-review PASS or silently promote missing reviews. Keep the original files unchanged in the migration archive. Never regenerate authored lessons merely to repair their state.

No automatic background process, external model access, GitHub sync or browser QA is implied by this engine. Publish authorization is separate.
