# ChatGPT share-link UUIDv8 entropy: theory check (2026-11-05)

## Verdict
Theory "limited entropy" is REJECTED as a reportable vulnerability. The residual random
field is 62 bits, not 78, but 62 CSPRNG-looking bits behind a known timestamp are not
guessable at any realistic request rate. No evidence of counters or correlation in the
random field. Sample size (5) is too small to prove randomness; it is large enough to
reject the specific structures that would make the links guessable.

## Layout (confirmed on the 5 samples; matches Hindsight Foundry and unfurl PR #292)
| bits | field | evidence in samples |
|---|---|---|
| 32 | Unix seconds | all five decode to 2026-11-05 11:20-11:25 UTC, ordered |
| 14 + 2 | sub-second fraction, then two zero bits | low 2 bits of seg2 = 00 in 5/5 (chance 1/1024 if random) |
| 4 | version = 8 | 8 |
| 12 | node id (decimal ranges) | 3ed = node 1005, 3eb = node 1003; published first-seen 2026-06-05 / 2026-04-17 |
| 2 | variant = 10 | 8/9/a/b |
| 62 | random | pairwise Hamming 33-46 on the 78-bit residual, expectation 39 +/- 4.4; no monotonic deltas; 5 constant bit positions vs 4.9 expected |

## Attack cost (scripts: scripts/uuid8.py, scripts/cost.py)
Targeted, attacker knows the exact second of link creation: space 2^77.6
(2^62 x 2^14 sub-second x 3 nodes). At 1e7 req/s: 3.6e8 years expected.
Targeted with a perfect oracle for second, sub-second and node: 2^62 -> 7.3e3 years at 1e7 req/s.
Untargeted, 1000 links created per second platform-wide, 1e7 req/s for a year: 1.4e-6 expected hits.
Break-even for one untargeted hit per year at 1e5 req/s and 100 links/s: about 32 random bits.
The field has 62. The Substack "6% hit rate" claim would require ~7-14 bits total; it counted
HTTP 200 shell pages, not conversations.

## Large sample (added 2026-11-05 19:50 UTC)
4,565 public share-link ids harvested from GitHub code search, 2024-09-12 to 2026-11-04.
All tests on the random expectation: per-bit worst z 2.71, nibble chi-square 219 (225 df),
serial correlation -0.004, same-node increasing fraction 0.506, Hamming 31.0. Sub-second model
confirmed (pre-2024-10-28 max 15,235 <= 15,258; low 2 bits always 00). Node field: 81 values
over the period, ~20 active in 2025, 7 since 2026-07, so NODES=3 in cost.py is a floor.
Details: research/large-sample.md, research/large-sample-stats.txt, scripts/corpus_stats.py.

## Live probe (3 requests)
- GET chatgpt.com/share/<fresh fake v8 id> -> HTTP 404, empty body
- GET chatgpt.com/backend-api/share/<fake> -> HTTP 404 JSON
- GET chatgpt.com/backend-api/share/6aec6686-4d9c-83ed-b905-76a831afef31 -> HTTP 200, 12.6 KB JSON, no login
So the endpoint is a clean existence oracle, and the owner's own share opens unauthenticated (question 8: yes).

## Answers to the open questions from the original transcript (see HANDOVER-adversarial-review.md)
1. Timestamp = link creation. Sample 0..3 are 28, 9, 19 s apart; a conversation-creation stamp would be identical.
2. 83eb/83ed = node/shard ids 1003/1005; shared across accounts and products; not account-bound.
3. Same-second IDs: the 4,565-ID corpus holds three seconds with two IDs each, one pair on the same node. They share only the second and the node; sub-second and random fields differ.
4. No counter, no monotonic pattern, Hamming distances consistent with random. 5 samples cannot exclude a weak PRNG.
5-7. Not tested here; need the owner's account. Re-share / update / delete behavior is a functional test, not an entropy test.
8. Yes, unauthenticated GET works (probe above).

## Adversarial review (a second, independent analysis, 2026-11-05 about 19:50 UTC)
Verdict: UPHELD WITH CORRECTIONS. See review/REVIEW.md. Corrections: 7 current nodes not 3
(space 2^78.8); the 181,000 figure was a timestamp check, not a bit study; backend-api/share
answers plain requests with 200; 14-bit field matches create_time within 5 ms on all five links.
Flip point for targeted guessing at 1e8 req/s: about 44 to 53 random bits.

## Bounty posture
OpenAI Bugcrowd brief (cached text) excludes brute-forcing and most rate-limit issues and wants
a working proof of concept. RFC 9562 section 8 already states UUIDs must not be relied on as
security capabilities; OpenAI's 62 CSPRNG bits + timestamp is the standard mitigation.
A 4,565-link sample shows no structure in the 62 bits. Nothing to report.

## Sources
- https://hindsig.ht/blog/decoding-chatgpt-ids/
- https://github.com/RyanDFIR/unfurl/pull/292
- https://promptjourneys.substack.com/p/easily-guess-chatgpts-share-links (unsupported claim)
- https://bugcrowd.com/engagements/openai (login required for brief)
- RFC 9562 sections 5.8, 6.9, 8
