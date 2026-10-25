# Training Generator v0.7 checkpoint orchestration

Use the script as the sole state writer; never manually edit CONTINUE_HERE.json.

Draft lane: planned -> review_pending -> self_verified.
- python scripts/checkpoint.py init --course courses/demo --index syllabus.json
- python scripts/checkpoint.py submit --course courses/demo --module m01.json --author ChatGPT
- python scripts/checkpoint.py selfreview --course courses/demo --report self-review-m01.json
- python scripts/checkpoint.py status --course courses/demo
After a verified self-review, author the next module without awaiting external review.

Self-review JSON: {"module_sha256":"<exact SHA256>","review_type":"self_adversarial","overall":"pass","checks":[{"name":"validator","result":"pass","evidence":"execution evidence"}],"findings":[]}.
A not_executed check is not a pass. A failing check or unresolved critical/high/blocking finding rejects selfverification.

Independent lane (may lag drafting):
- python scripts/checkpoint.py review --course courses/demo --module-id m01 --report external.json
- python scripts/checkpoint.py approve --course courses/demo --module-id m01 --approver "Human owner"

External JSON: {"module_sha256":"<exact SHA256>","verdict":"pass","reviewer":"Claude Code","findings":[]}. Reviewer name is a metadata assertion, not proof of independent execution. A passing independent review is NOT publication authorization. All module hashes are checked on state transitions. Do not alter existing lesson files during checkpoint repair.

Historical manually edited states should be regenerated through init/submit/selfreview using real original module files and review evidence; never invent a self-review PASS or pretend missing evidence exists.
