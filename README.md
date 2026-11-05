# ChatGPT share-link entropy check

Read the rendered report: https://pepsi133.github.io/ths2027_openai_urls/share-link-entropy.html

This repository answers one question: can a `chatgpt.com/share/<uuidv8>` link be guessed? The check ran on 2026-11-05. The verdict is no. Each identifier carries 62 random bits behind a timestamp, so it is not guessable. An adversarial review upheld the verdict with corrections.

## Files

- `share-link-entropy.html`: summary page with chart.
- `report.md`: long-form findings.
- `scripts/uuid8.py`: decodes the owner's five share IDs field by field.
- `scripts/cost.py`: estimates the cost of a guessing attack.
- `scripts/corpus_stats.py`: runs bit-level tests on a list of share IDs.
- `review/REVIEW.md`: the adversarial review and its corrections.
- `review/recompute.py`: the reviewer's independent recomputation.
- `review/corpus_stats.py`: the reviewer's independent corpus tests.
- `research/large-sample.md`: the large-sample test on GitHub share IDs.
- `research/large-sample-stats.txt`: full output of that test.
- `research/public-record.md`: prior art and public statements.
- `research/cdx/gh_harvest.sh`: the GitHub code search harvest that produced the corpus.
- `research/cdx/gh_share_strict.txt`: 4,565 public share IDs.
- `research/github_share_ids_2026-11-05.txt`: 793 share URLs from GitHub, 692 of them version 8.
- `research/wayback_chat_openai_com_share_2026-11-05.txt`: Wayback CDX rows for `chat.openai.com/share/*`, truncated to bare share UUIDs.
- `HANDOVER-adversarial-review.md`: the handover prompt for the adversarial review.
- `index.html`: redirect to the report page for GitHub Pages.
- `VISIBILITY.md`: states that the repository is public and what identifiers it holds.

## How to reproduce

```
python3 -I scripts/uuid8.py
python3 -I scripts/cost.py
python3 -I scripts/corpus_stats.py research/cdx/gh_share_strict.txt
```

## Sources

- https://hindsig.ht/blog/decoding-chatgpt-ids/
- https://github.com/RyanDFIR/unfurl/pull/292
- RFC 9562, Universally Unique IDentifiers (UUIDs).

## Scope note

All live requests went to the owner's own share links. No other account or link was touched, and no ID was enumerated.
