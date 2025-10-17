---

theme: default
_class: lead
------------

# Algorithm_3_1 (Misra–Gries)

## Finding frequent Japanese words from SRT — tokenization + filtering

---

## Goal

* Extract Japanese subtitles from videos and identify the most frequent words/fragments without storing full frequency tables.
* Fits into a pipeline: audio extraction → ASR (Whisper) → optional translation → frequency analysis.

---

## High-level pipeline

1. **Read SRT** (clean parsing)
2. **Tokenize** (fugashi/unidic recommended; regex fallback otherwise)
3. **Filter**: keep tokens that contain Japanese characters (optional strict rules)
4. **Run Algorithm_3_1 (Misra–Gries)** to get candidate frequent items
5. **Second pass**: compute true counts for candidates
6. **Output**: CSV + summary

---

## Why use Misra–Gries?

* Low memory footprint: stores at most *k−1* candidate items.
* Great for streaming or large corpora from many videos.
* The algorithm guarantees any item with frequency > n/k will be retained as a candidate (then validated in the second pass).

---

## Misra–Gries intuition

* One-pass over the token stream.
* If token is in the candidate map → increment.
* If map has space (< k−1) → add token with count=1.
* If map is full and token is new → decrement every counter by 1; remove zeros.

**Result:** frequently occurring tokens survive; rare tokens get eliminated. A second pass computes exact frequencies of the survivors.

---

## Pseudocode (short)

```text
function misra_gries(stream, k):
    counters = {}
    for x in stream:
        if x in counters:
            counters[x] += 1
        elif len(counters) < k-1:
            counters[x] = 1
        else:
            for y in counters:
                counters[y] -= 1
            remove counters with 0
    return counters
```

Then: `true_counts = second_pass(stream, counters.keys())`

---

## Tokenization: fugashi vs regex

* **Fugashi + unidic-lite** (recommended)

  * Produces lexical tokens, lemmas, and POS tags.
  * Better normalization (e.g., handling different conjugations).

* **Regex fallback**

  * Extracts runs of Japanese characters (hiragana, katakana, kanji).
  * Simpler but coarser (may return long phrases instead of word-level tokens).

---

## Filtering rules

* `contains_japanese(token)` — only keep tokens that include Japanese characters.
* `--strict` option — remove tokens that contain ASCII letters or digits (e.g., `Mサイズ`, `1月`).
* External `filters.txt` (optional): sections `[fillers]`, `[stopwords]`, `[pos_blacklist]`.

  * Use `pos_blacklist` only if POS information is available (i.e., using fugashi).

---

## Example `filters.txt` format

```
[fillers]
はい
えー
うん

[stopwords]
の
に
が
を
は
です
ます

[pos_blacklist]
助詞
記号
感動詞
```

---

## Complexity & properties

* Time: O(n) for first pass + O(n) for second pass (n = number of filtered tokens).
* Memory: O(k) for counters (plus any memory for storing or streaming tokens).
* Guarantee: any item with true frequency > n/k will appear among candidates.

---

## Practical notes

* Run the provided script:
  `python algoritma_3_1_full.py my_video_ja.srt --k 10 --filters filters.txt --out results.csv`
* Output CSV columns: `token, est_count, true_count, percent`
* Quick cross-check: `Counter(filtered_tokens).most_common(20)`

---

## Choosing k

* To catch high-frequency fillers: small k (10–20).
* To detect topical words that appear more rarely (~>1%): k ≈ 100.
* Experiment with multiple k values and compare true counts.

---

## Troubleshooting tips

* `ModuleNotFoundError` for fugashi or srt: install `fugashi[unidic-lite]` and `srt`.
* Encoding issues: ensure SRT is UTF-8 (convert from SHIFT_JIS if needed using iconv).
* Empty results: check `--strict` flag, filters, or whether SRT actually contains Japanese text.

---

## Next steps / enhancements

* Add timestamp mapping (which segments a token appears in).
* Integrate into the Whisper transcription pipeline for automated end-to-end processing.
* Visualize results: word cloud or time-series frequency plots.
* Improve normalization (custom stemming/merging rules for Japanese).

---

## References

* Misra–Gries / Frequent items streaming algorithm
* Fugashi (MeCab wrapper) + Unidic
* Whisper for speech-to-text

---

# Thank you!

Would you like me to export these slides to PDF or add a diagram for the pipeline?
