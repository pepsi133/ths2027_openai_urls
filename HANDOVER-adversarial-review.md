# Handover: adversarial review of the share-link entropy verdict

This is the brief that was given to the independent reviewer, kept for the record.

Paste the "Reviewer prompt" block into a fresh chat. Point that chat at the files in
"Inputs". The "Original prompt" section shows the question as first posed.

## Inputs

- `share-link-entropy.html`: TL;DR page with the verdict and the chart.
- `report.md`: long-form findings.
- `scripts/uuid8.py`: decodes the five UUIDs and runs the bit tests.
- `scripts/cost.py`: attack-cost arithmetic.
- `research/large-sample.md` and `research/large-sample-stats.txt`: 4,565 public share links tested with `scripts/corpus_stats.py`.
- `research/public-record.md`: deep-research notes on the generator (if present).

## Original prompt (verbatim)

> I have a theory which I might need to report to openai, about limited enthropiy of
> their shared chats ursl, read below, run research and solid math (scipted) on that
> to confirm or reject thsi theory

The pasted material was an OCR transcript of a ChatGPT conversation. Its facts:

- Share-link IDs are UUIDv8. The first 32 bits are a Unix timestamp in seconds.
- The third segment took only the values `83eb` and `83ed`, on several accounts.
- After removing timestamp, version, variant and the third segment, 78 bits remain
  with unknown entropy.
- Five links from one account on 2026-11-05:

```
6aec6686-4d9c-83ed-b905-76a831afef31
6aec66a2-44d4-83ed-b8b6-98eccf6e2d70
6aec66ab-da64-83ed-8b90-b70c1685a603
6aec66be-b140-83eb-be00-98c77bd09c63
6aec67a7-0e30-83ed-827c-a20ea452bc88
```

- Pairwise bit differences between consecutive links in the 78 positions: 33, 43, 38, 43.
- Open questions: what the timestamp marks, what `83eb`/`83ed` mean, whether same-second
  IDs share bits, whether the 78 bits hold counters or correlations, and whether re-share,
  update and delete change or revoke the ID.

## The verdict under review

Layout: 32 bits Unix seconds (link creation), 14 bits sub-second plus two zero bits,
version nibble 8, 12-bit node id (`83eb` = 1003, `83ed` = 1005), 2 variant bits, 62
random bits. All five samples have `00` as the low two bits of segment 2 (chance 1/1024
under randomness). The 62-bit field shows no counter and no correlation across five
samples. A targeted guess with the exact creation second faces a 2^77.6 space, which is
3.6e8 years at 1e7 requests per second. Verdict: not reportable unless a larger sample
shows structure inside the 62 bits. Two public sources documented the layout earlier in
2026: hindsig.ht/blog/decoding-chatgpt-ids and github.com/RyanDFIR/unfurl/pull/292.

## Reviewer prompt

```
You are an adversarial reviewer. Your job is to break the verdict, not to confirm it.
The author concluded that ChatGPT share-link IDs (chatgpt.com/share/<uuidv8>) hold
62 random bits behind a timestamp, are not guessable, and are not worth reporting to
OpenAI. Assume the author is wrong and look for the evidence that would show it.
Read report.md, share-link-entropy.html and the two scripts first. Run the scripts.

Report each item as CONFIRMED, REFUTED or UNTESTED, with the evidence you used.

1. Layout. Re-derive the field boundaries from the five UUIDs yourself before you
   read the author's table. Could segment 2 be something other than "14-bit
   sub-second + two zero bits", for example a counter that is a multiple of 4?
   What observation would separate the two readings, and do five samples suffice?

2. Sources. Open the two write-ups the layout rests on. Do they show raw evidence
   (sample counts, per-bit statistics) or only assert the layout? Has the node field
   ever carried more than three values at one time? If so, cost.py undercounts the
   space by that factor; recompute.

3. Math. Rerun scripts/cost.py. Then rerun it under the assumptions most favorable
   to an attacker: node fixed, sub-second known, rate 1e8 requests per second. State
   the random-bit count at which the verdict flips.

4. Generator. "CSPRNG-looking" on five samples is a weak claim. List the statistical
   tests that would separate a CSPRNG from a seeded non-cryptographic generator, how
   many samples each needs, and whether one account can collect them within OpenAI's
   published rules. If a public corpus of share links exists (web archives, code
   hosts), name it and estimate its size. If research/ holds a large-sample analysis,
   check its method and rerun its script.

5. Reportability. Read OpenAI's Bugcrowd brief (login needed) and RFC 9562 section 8.
   State under what evidence this would become a valid report, and what severity it
   would carry if the 62 bits turned out to be predictable.

6. Verdict. Pick one: UPHELD, UPHELD WITH CORRECTIONS, OVERTURNED, or CANNOT DECIDE.
   Give the single strongest reason. List any number in the HTML page that you could
   not reproduce.

Do not request share links from other people and do not enumerate IDs against the
live service beyond a handful of existence checks on your own links.
```
