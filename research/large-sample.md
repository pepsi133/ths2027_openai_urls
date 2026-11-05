# Large-sample entropy test of ChatGPT share-link IDs (2026-11-05)

## Corpus
- Source: GitHub code search, query `"chatgpt.com/share/<prefix>"` for prefixes 66..6a, text-match
  fragments, 10 pages of 100 per prefix (3 pages lost to the rate limit).
- Raw fragments (30,567 lines, untrusted data): not included in the repository because they
  contain third-party text and leaked credentials; `research/cdx/gh_harvest.sh` regenerates them.
- Strict set: UUIDs that directly follow `chatgpt.com/share/`: `research/cdx/gh_share_strict.txt`,
  4,565 unique, 2024-09-12 to 2026-11-04.
- Common Crawl indexes 2025-47 to 2026-43: 7 hits, 0 v8 ids. Wayback CDX: offline during the run.
- Script: `scripts/corpus_stats.py`, self-tested on 3,000 synthetic CSPRNG ids (all tests quiet)
  and 3,000 counter ids (per-bit |z| 55, chi-square 540,939, serial correlation 0.999).
- Full output: `research/large-sample-stats.txt`.

## Results, strict set (n = 4,565)
| Test | Result | Random expectation |
|---|---|---|
| Low 2 bits of segment 2 | `00` in 4,565 of 4,565 | layout: always 0 |
| 14-bit sub-second before 2024-10-28 (n=1,175) | max 15,235 | ns>>16 model: <= 15,258 |
| 14-bit sub-second after 2024-10-28 (n=3,390) | max 16,382, mean 8,191 | uniform: ~8,191 |
| Per-bit ones count, 62 bits | worst z = 2.71, 0 bits with z > 3 | ~0.17 bits with z > 3 |
| Nibble chi-square, 225 df | 219.4 | 225 +/- 21 |
| Bits 60-61 | 1154 / 1117 / 1159 / 1135 | ~1141 each |
| Lag-1 serial correlation, time order | -0.0039 | 0 +/- 0.015 |
| Same-node consecutive pairs increasing | 0.506 (871 pairs) | 0.5 random, ~1.0 counter |
| Hamming distance, time-adjacent | mean 31.01, min 16, max 44 | 31.0 +/- 3.9 |
| Collisions on top 32 random bits | 0 | 0.002 |

## Node field
81 distinct values over the period. About 20 active per month in 2024-09 to 2026-02 (nodes 0-19),
a peak of 45 in 2026-04 during a migration, and 7 per month since 2026-07. The earlier page
assumed 3 current nodes; the real count is larger, which widens the search space by up to 7/3.
`scripts/cost.py` keeps 3 as the attacker-favorable floor.

## Verdict
The 62-bit field is indistinguishable from a cryptographic random source on 4,565 real ids.
No counter, no bias, no serial structure, no collisions. Combined with the layout, the
"limited entropy" theory is rejected with a real sample, not only with arithmetic.

## Limits
- GitHub-published links are a biased sample (people who paste links into code and docs),
  but the generator does not know where a link will be pasted.
- Tests detect counters, biased bits, and linear structure. They cannot detect a well-seeded
  non-cryptographic generator whose outputs are spread across many processes. That would
  need hundreds of consecutive outputs from one process, which no public corpus provides.
