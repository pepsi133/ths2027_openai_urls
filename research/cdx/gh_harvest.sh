#!/bin/bash
# Harvest share-link UUIDs from GitHub code search text fragments. 10 req/min limit.
out=gh_fragments.jsonl; : > $out
for pfx in 66 67 68 69 6a; do
  for page in $(seq 1 10); do
    gh api -X GET search/code -H "Accept: application/vnd.github.text-match+json" \
      -f q="\"chatgpt.com/share/$pfx\"" -f per_page=100 -f page=$page \
      --jq '.items[].text_matches[].fragment' >> $out 2>>gh_err.log || echo "fail $pfx $page" >> gh_err.log
    sleep 7
  done
  echo "prefix $pfx done, fragments: $(wc -l < $out)"
done
grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-8[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}' $out | sort -u > gh_uuids.txt
grep -oE 'chatgpt\.com/share/[0-9a-f]{8}-[0-9a-f]{4}-8[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}' $out | sed 's#.*/share/##' | sort -u > gh_share_strict.txt
echo "GH_DONE strict share uuids: $(wc -l < gh_share_strict.txt)"
echo "GH_DONE unique v8 uuids: $(wc -l < gh_uuids.txt)"
