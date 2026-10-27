# Course JSON contract (v0.4)

Read `example-lesson.json` as a valid executable example.

Root: `title` (string), `audience` (string), `description` (string), `status` (`draft` or `complete`), optional `learner_age_band` (`6-8` or `adult`, default `adult`), `modules` (array). Each module has `title` and `lessons`.

A planned lesson is `{ "title": "Upcoming topic", "status": "planned" }`. Planned lessons appear disabled in the full index. A `complete` course cannot contain planned lessons. At least one generated lesson is needed to build a playable course.

A generated lesson has `title`, `status:"generated"`, `objectives` (2+ strings), `hook` (30+ words), `explanation` (3+ paragraphs, 300+ words for adults; 150+ for early learners), `examples` (2+ `{title,walkthrough}` objects), `scenes` (3+ `{title,narration,visual}` objects), `lab` (`{title,instructions,success}`), `pitfalls` (array), `questions` (3+ `{prompt,choices:[4 distinct strings],answer:0..3,reason}`), `resources` (array of `{title,url}`), `challenge` (30+ words), optional `evidence_note`.

`explanation` elements can be text strings or objects; `walkthrough` can additionally be an array of text/code steps (>=80 prose words per example). Supported elements are `{type:"text"|"code",text:"..."}`. Code renders in `<pre>`; code is excluded from prose-depth counts.

`visual`: `{type:"tokens"|"flow",items:[strings]}`, `{type:"bars",items:[{label,value}]}`, or `{type:"equation",text:"..."}`. These are scene-level visual examples, NOT sophisticated animation.

The current player uses browser/system speech synthesis, with scene advancement on speech completion, not neural audio files, word-level alignment, timestamp cues, or downloadable TTS weights. A voice may be robotic. URL validation checks HTTPS syntax, NOT live availability or content accuracy. External resources are not bundled for offline use.

Use `python scripts/merge_course.py index.json module1.json module2.json > course.json` to safely replace planned slots with generated lessons by whitespace-normalized case-insensitive title. The validator catches basic structural/depth defects; it cannot verify factual accuracy, real citations, question difficulty or educational effectiveness.

## Corporate applications (optional first-class lesson field)

`corporate_application: {"scenario_title":"...", "scenario":"..."}`. The scenario must contain at least 150 substantive words and demonstrate an actual quantified business decision: explicit payoff or probability assumptions, a computed outcome, a decision implication, and at least one changed assumption that flips or challenges the result. Use distinct industries/functions across lessons. The validator enforces presence/length and overlap guard, not mathematical correctness; manual/adversarial review must recalculate the result. This section renders **before** the questions in the standard player. Do not fork the player to support it.

Optional subject-agnostic applied lesson: `practical_application:{"title":"Listening and Improvisation","scenario_title":"A ii–V–I in three keys","scenario":"..."}` (150+ prose words, genuine worked subject example). Legacy `corporate_application:{"scenario_title":"...","scenario":"..."}` remains readable for backwards compatibility. Neither application nor worked examples count toward explanation depth.
