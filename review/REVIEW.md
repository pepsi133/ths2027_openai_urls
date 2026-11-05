# Adversarial review of the share-link entropy verdict

Reviewer run: 2026-11-05, 19:50 UTC, fresh session, per `HANDOVER-adversarial-review.md`.
Files added by the reviewer: `review/recompute.py` (cost under attacker-favorable
assumptions), `review/corpus_stats.py` (independent bit tests on a URL list),
`research/github_share_ids_2026-11-05.txt` (692 version-8 share IDs from GitHub),
`research/wayback_chat_openai_com_share_2026-11-05.txt` (37,755 Wayback CDX rows, filtered to share-UUID rows).
An empty Internet Archive error page was removed from `research/`.

Verdict under review: ChatGPT `/share/<uuidv8>` IDs hold 62 random bits behind a timestamp,
are not guessable, and are not worth reporting to OpenAI.

## 6. Verdict: UPHELD WITH CORRECTIONS

Strongest reason: the second segment of the ID is the server clock, so the only secret is
the 62-bit field, and that field passes every first-order randomness test on 4,565 real
share IDs. On all five own links, `backend-api/share/<id>` returns a `create_time` whose
fraction of a second matches the 14-bit field to within 4.3 to 5.3 ms. The chance that five
random 14-bit values all land in such a window is about 2.5e-10. With the clock known, the
targeted search space is 2^62 at best for the attacker, which is 730 years at 1e8 requests
per second. The verdict flips only below about 44 to 53 random bits, and the field has 62.

Corrections to the page and report:

1. "Three values are current" for the node field is wrong. Seven nodes (1000 to 1006)
   issue share IDs since 2026-07, and 81 node values appear over the format's lifetime.
   `cost.py` uses 3. With 7, the second-known space is 2^78.8, not 2^77.6. The error runs
   in the author's favor: a larger space is harder to search. The author's own
   `research/large-sample.md`, written during this review, already notes this.
2. "They match the published analysis of about 181,000 archived ids" is mislabeled. The
   181,000 figure is the unfurl PR's timestamp check on conversation IDs. The published bit
   distribution claim is one sentence of Hindsight prose over about 284,000 mixed IDs.
3. At the time of the handover, `research/` held one file, an Internet Archive outage page.
   The large-sample analysis the handover describes did not exist then. It exists now, from
   the author's session (4,565 IDs) and from this review (692 IDs, plus a rerun on the 4,565).
4. `research/public-record.md` section 6 states that `backend-api/share/...` "returns 403
   without a browser session", citing a third-party README. This review measured HTTP 200
   with plain curl and a Mozilla User-Agent string on all five own links, and 404 on an
   altered ID. The endpoint is open and is a clean existence oracle, as `report.md` says.

Numbers on the HTML page that could not be reproduced: none of the computed ones. Every
space, year and break-even figure reproduces from `scripts/cost.py` and
`review/recompute.py`. Two statements of fact fail: "Three values are current" and the
"181,000" attribution.

## 1. Layout: CONFIRMED, counter reading REFUTED

Re-derived from the five IDs before reading the author's table:

- hex 0 to 7 decode to 2026-11-05 11:20:38 to 11:25:27 UTC, in creation order.
- hex 8 to 11: 4d9c, 44d4, da64, b140, 0e30. Low two bits 00 in 5 of 5.
- hex 12 is 8. hex 13 to 15 is 3ed or 3eb. Top two bits of hex 16 are 10, the variant.
- Remaining 62 bits: no shared prefix, no monotonic order, Hamming 33 to 46 per pair.

Separating "sub-second time" from "counter times 4": five samples spaced 9 to 233 s apart
cannot do it, because a per-node counter sampled at random moments also looks uniform. The
API clock does it. `create_time` minus (seconds + field/16384) is +5.0, +5.3, +4.3, +5.2,
+5.2 ms, a 1 ms spread. A counter has no relation to the clock fraction. Second witness:
5,270 of 5,270 IDs across four sources (4,673 distinct, because the 692 and 4,565 sets overlap by 597) (5 own, 8 archived from 2024 to 2025, 692 from
GitHub, 4,565 from the author's GitHub harvest) have the low two bits at 00. The 14-bit
value spans 3 to 16,382 after 2024-10-28 and tops out at 15,235 before that date, which
matches the nanoseconds-shifted-by-16 encoding the unfurl PR documents (maximum 15,258).
Milliseconds (maximum 999) are excluded.

## 2. Sources: CONFIRMED with caveats

- Hindsight (hindsig.ht/blog/decoding-chatgpt-ids): about 284,000 unique IDs from Wayback,
  Common Crawl and the author's corpus. Timestamp validated against first capture.
  Sub-second validated by the pre-2024-10-28 maximum of 15,258. Node table: 1003 first seen
  2026-04-17, 1005 first seen 2026-06-05. The report's dates are correct. Random bits:
  "evenly distributed at every bit position across the sample. I didn't find any more
  structure in there." Prose only. No table, no named test, no dataset.
- unfurl PR 292 (merged 2026-10-29): layout "worked out from ~440k archived IDs"; 181,000
  conversation IDs with no embedded time after first capture; 95,000 other IDs with 2
  outliers. Unit tests are synthetic. Node ranges for conversation and share IDs: 0 to 31
  and 800 to 1023. Separate object nodes 400 to 447 for `/s/` share links, with 401 "by far
  the most common". No raw dumps.
- Node count over time, from the 4,565-ID corpus: 20 nodes per month from 2024-09 to
  2026-02, a peak of 45 in 2026-04, then 7 per month from 2026-07. Recompute with 7 nodes:
  2^78.81 and 8.4e8 years at 1e7 requests per second.

## 3. Math: CONFIRMED

`scripts/cost.py` reruns with the printed figures. Attacker-favorable rerun:

| Assumption | Space | Expected years to one hit |
|---|---|---|
| Node fixed, sub-second known, second known, 1e7 req/s | 2^62 | 7.3e3 |
| Same, 1e8 req/s | 2^62 | 7.3e2 |
| Same, 1e9 req/s | 2^62 | 73 |

Flip points for the random-bit count b, with every other field known to the attacker:

| Target time per link | 1e7 req/s | 1e8 req/s |
|---|---|---|
| 1 year | 49.2 bits | 52.5 bits |
| 1 week | 43.5 bits | 46.8 bits |
| 1 day | 40.7 bits | 44.0 bits |

The author's "about 32 bits" is the untargeted break-even (100 links per second, 1e5
requests per second, 3 nodes, one hit per year) and reproduces at 32.6 bits. It is not
the targeted flip point. The targeted verdict flips near 44 to 53 bits. The field has 62.
A factor of 1,000 in request rate moves the flip point by 10 bits and does not close the gap.

## 4. Generator: CONFIRMED on first-order tests, UNTESTED for state recovery

Tests that separate a CSPRNG from a seeded non-cryptographic generator:

| Test | Catches | Samples needed | Possible from one account under the rules |
|---|---|---|---|
| Per-bit frequency, chi-square | stuck or biased bits | about 1,000 | yes, and the public corpus suffices |
| Adjacent-bit, nibble, byte chi-square | short-range correlation | about 1,000 | yes |
| Lag-1 serial correlation in time order | counter, LCG low bits | about 1,000 | yes |
| Duplicate and birthday test | small state, reseed on fork | millions for 62 bits | no |
| Repeated arithmetic or xor difference between consecutive outputs | LCG, counter, xorshift | tens of consecutive outputs from one generator | no: other users' draws interleave |
| Linear complexity (Berlekamp-Massey) | LFSR-type | twice the state size in consecutive bits | no, same reason |
| MT19937 state recovery | Python `random`, numpy | 624 consecutive 32-bit words, about 312 consecutive IDs from one process | no, same reason |
| Solver on xorshift128+, PCG, LCG | seeded 64-bit generators | 3 to 10 consecutive outputs | only with one worker's whole stream |

The consecutiveness requirement is the real barrier. Share IDs come from many workers, the
same generator feeds conversation and message IDs, and other users' draws interleave with
the researcher's. The brief allows own accounts only and forbids retrieving others'
records, so a researcher cannot collect a consecutive stream. One hundred own links created
by script is ordinary product use and tests first-order structure only.

Public corpus, measured today:

| Source | Share IDs | Of which v8 | Note |
|---|---|---|---|
| Wayback CDX, `chat.openai.com/share/*` | 30,467 | 8 | nearly all v4, pre-2024-08-30 |
| Wayback CDX, `chatgpt.com/share/*` | unknown | unknown | HTTP 503 on every try in both analyses |
| Common Crawl index, 6 newest crawls | 0 | 0 | robots.txt blocks CCBot |
| GitHub code search, reviewer's query | 793 | 692 | 35,264 total hits reported, 10 pages read |
| GitHub code search, author's prefix harvest | 4,565 strict | 4,565 | overlap with the reviewer's set: 597 |
| ShareChat (Hugging Face `tucnguyen/ShareChat`) | 102,740 ChatGPT conversations with a url column | unknown | gated by a license form, not pulled |
| DevGPT (NAIST) | thousands | 0 | 2023, v4 only |

Results, reviewer's independent script on the author's 4,565 IDs, and the author's script
rerun by the reviewer (`research/large-sample-stats.txt` reproduces line for line):

| Test | 4,565 IDs, reviewer's script | 692 IDs, reviewer's script | Random expectation |
|---|---|---|---|
| Per-bit ones, 62 bits | max abs z 2.71, none above 3 | max abs z 2.28 | max about 2.4 to 2.9 |
| Chi-square of bit frequencies, 62 dof | 49.5 | 58.9 | 62 plus or minus 11 |
| Adjacent-bit equality | 0.4991 | 0.4954 | 0.5000 plus or minus 0.0009 and 0.0024 |
| Byte-value chi-square, 255 dof | 229.5 | 257.8 | 255 plus or minus 23 |
| Duplicate 62-bit fields | 0 | 0 | 0 |
| Hamming, same-node IDs within 60 s | 153 pairs, mean 31.76, range 22 to 42 | 21 pairs, mean 29.7 | 31.0 plus or minus 3.9 |
| Repeated arithmetic difference between those pairs | none | none | none |
| Low two bits of segment 2 | 4,565 of 4,565 are 00 | 692 of 692 | layout |

Author's script, additional lines reproduced: lag-1 serial correlation -0.0039 (bound
0.0148); same-node consecutive pairs 871, fraction increasing 0.506 (counter would give
1.0); nibble chi-square 219.4 on 225 dof; no collision on the top 32 bits. The author's
script also carries a positive control: 3,000 synthetic counter IDs fail with per-bit z of
55 and chi-square of 540,939. The reviewer checked the script's field extraction against
the layout and found no error.

Same-second IDs, open question 3 from the original transcript: the 4,565-ID corpus holds three seconds with two IDs each,
one of them on the same node (0x3ec, second 1781371867). The two share nothing beyond the
32-bit second and the node. Sub-second fields differ, 62-bit fields differ.

Nothing in 4,673 distinct real IDs separates the field from a CSPRNG. These tests cannot see a
seeded generator whose outputs are interleaved across many users, and no public method
exists to de-interleave them.

## 5. Reportability: PARTLY UNTESTED

The Bugcrowd page served without login carries the policy sections but not the scope groups
or the out-of-scope list. Those need a researcher login, which this session does not have.
What the public text states:

- "Interact only with your own accounts unless authorized by OpenAI."
- "Do not retrieve additional records to demonstrate impact. Delete any copies you obtained
  and use accounts and data you control to demonstrate the issue."
- Priority follows the Bugcrowd Vulnerability Rating Taxonomy. OpenAI adjusts by likelihood
  or impact. P4 and P5 carry no base bounty.
- Worked example: a critical ChatGPT finding has a $20,000 base. Stacked bonuses reach
  $172,000 for exceptional findings.
- The author's `public-record.md` quotes the brute force exclusion from search snippets:
  "This includes brute forcing our APIs." The reviewer did not see this text first hand.

RFC 9562 section 8, read today: "Implementations SHOULD NOT assume that UUIDs are hard to
guess. For example, they MUST NOT be used as security capabilities (identifiers whose mere
possession grants access). Discovery of predictability in a random number source will
result in a vulnerability." And: "If UUIDs are required for use with any security operation
within an application context in any shape or form, then UUIDv4 (Section 5.4) SHOULD be
utilized." OpenAI puts 62 CSPRNG-looking bits in a v8 instead of 122 in a v4. That is a
design choice the RFC discourages, not a defect, and a share link is by product definition
a capability.

When this becomes a valid report:

- A predictor that names the 62-bit field of the researcher's own next share link before
  it is created, or recovers generator state from the researcher's own links. This is the
  only proof of concept the rules permit and the one that would matter.
- A collision or reuse of the 62-bit field across two links, which shows a small state or a
  reseed fault.
- A derivation of the 62 bits from known inputs, for example a hash of the conversation ID
  and time.
- Pure guessing against the live service never qualifies. The brief excludes it and the
  space makes it pointless.

Severity if the 62 bits were predictable: unauthenticated read of conversations that users
shared to a limited audience. Under the VRT this is Broken Access Control or Sensitive Data
Exposure, P2 for targeted reads and P1 if the predictor scales to mass harvest. The brief's
worked example gives $20,000 base for a critical ChatGPT finding.

## Open questions from the original transcript, status after this review

1. Timestamp marks link creation: CONFIRMED by `create_time` on the share record, with
   `update_time` 0.6 to 1.2 s later, too short for a conversation's lifetime.
2. 83eb and 83ed are nodes 1003 and 1005: CONFIRMED. Nodes 1000 to 1006 are all current.
3. Same-second IDs: CONFIRMED on one same-node pair in the corpus. They share only the
   second and the node.
4. Counters or correlations in the 78 bits: 16 are the clock. 62 pass all tests at n=4,565.
5 to 7. Re-share, update, delete: UNTESTED, functional questions. Note: a nonexistent ID
   returns the same `shared_conversation_deleted` code as a deleted one, so the endpoint
   does not separate "never existed" from "deleted".
8. Own link opens without login: CONFIRMED again today, HTTP 200, 12,594 bytes.

## Live requests made in this review

Seven requests to chatgpt.com, all on the five own IDs or one altered copy of one of them:
five `backend-api/share/<own id>` reads, one `backend-api/share/<altered>` (404 JSON), one
`/share/<altered>` (404, empty body). No other account or link was touched. No ID was
enumerated.
