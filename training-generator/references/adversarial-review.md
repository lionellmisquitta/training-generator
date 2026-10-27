# Adversarial quality review

Before a lesson is called self-verified, challenge content coverage, prerequisite alignment, numeric derivations, assessment answer keys, executable code and edge cases, cross-lesson originality, pedagogical fit, visuals, accessibility, and offline player runtime. Run relevant scripts, correct defects and rerun affected checks up to three times. Record passed, failed and not-executed checks with evidence. Never label self-review as independent model review.

Store an adjacent self-review JSON containing module_sha256, review_type="self_adversarial", overall="pass", a nonempty checks array (name, result, evidence), and findings. A pending or unavailable tool must be recorded as not_executed rather than pass. A publication decision requires a separate independent review and human authorization.

## Mandatory adversarial self-review structure
The `selfreview` JSON must contain six named PASS checks with concrete evidence (minimum descriptive detail): `mathematics`, `examples`, `assessment`, `application`, `sources`, `duplication`. Cite executed assertions and independent recalculations, explain why example situations are materially distinct, disclose unverified links, and list unresolved risks. A hand-authored PASS without test artifacts is not proof of testing. Record `not_executed` explicitly; it cannot satisfy the hard gate. Run `release_gate.py --phase draft` before handing off. A publish label requires separate hash-bound independent review, actual browser QA record, and human approval.


## Required independent teaching review evidence
For each lesson, separately record: each objective mapped to demonstrated teaching; calculated claims and counterexamples; lab values compared with quiz and code tests; application game structure versus main examples (not merely words); exact source link accessibility versus title; potential answer-length and position cues. A self-review cannot self-certify an independent pass.
