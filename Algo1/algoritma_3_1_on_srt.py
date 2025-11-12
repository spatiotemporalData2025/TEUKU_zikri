#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
algoritma_3_1_full.py
Cari kata/fragmen Jepang yang sering muncul dari file SRT menggunakan Misra-Gries.

Usage:
    python algoritma_3_1_full.py input.srt --k 10 --filters filters.txt --out results.csv --top 30 --strict

Dependencies (recommended):
    pip install "fugashi[unidic-lite]" srt

If fugashi or srt not installed, the script will fallback to simpler tokenization/parsing.
"""
from collections import Counter
import argparse
import csv
import re
import sys
import os

# Try optional deps
try:
    import fugashi
    from fugashi import Tagger
    FUGASHI_AVAILABLE = True
except Exception:
    Tagger = None
    FUGASHI_AVAILABLE = False

try:
    import srt as srt_module
    SRT_AVAILABLE = True
except Exception:
    SRT_AVAILABLE = False

# Regex to match Japanese characters (hiragana, katakana, kanji) and long vowel mark
JP_CHAR_RE = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u30FC]')
# Regex to capture runs of Japanese characters (fallback tokenization)
JP_RUN_RE = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u30FC]+')
# Timestamp line pattern
TIMESTAMP_RE = re.compile(r'^\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}$')

def read_srt_text(path):
    """Return raw subtitle text content (all subtitle texts concatenated)."""
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    # If srt module available, parse cleanly
    if SRT_AVAILABLE:
        try:
            subs = list(srt_module.parse(txt))
            texts = [s.content for s in subs]
            return "\n".join(texts)
        except Exception:
            # fallback to naive
            pass
    # naive fallback: remove index & timestamps, keep other lines
    lines = []
    for line in txt.splitlines():
        s = line.strip()
        if not s:
            continue
        # skip numeric index lines
        if s.isdigit():
            continue
        # skip timestamp lines
        if TIMESTAMP_RE.match(s):
            continue
        lines.append(s)
    return "\n".join(lines)

# Tokenization
def tokenize_with_fugashi(text):
    tagger = Tagger()
    tokens = []
    pos_list = []
    for tok in tagger(text):
        # try to get a lemma/base form safely; many dicts expose 'lemma' or 原形
        base = None
        try:
            feat = tok.feature
            if isinstance(feat, dict):
                base = feat.get("lemma") or feat.get("原形") or feat.get("基本形")
            elif isinstance(feat, (list, tuple)) and len(feat) > 7:
                # some dictionaries put base form at index 7
                base = feat[7] or None
        except Exception:
            base = None
        token_text = base or getattr(tok, "normalized", None) or tok.surface
        # determine coarse POS string if available
        pos = None
        try:
            if hasattr(tok, "pos"):
                pos = tok.pos
            else:
                feat = tok.feature
                if isinstance(feat, dict):
                    pos = feat.get("pos") or feat.get("品詞")
                elif isinstance(feat, (list, tuple)) and len(feat) > 0:
                    pos = feat[0]
        except Exception:
            pos = None
        tokens.append(token_text)
        pos_list.append(pos or "")
    return tokens, pos_list

def regex_tokenize(text):
    """Fallback tokenization: extract runs of JP characters."""
    return JP_RUN_RE.findall(text), ["" for _ in JP_RUN_RE.findall(text)]

# Filters file: ini-like simple sections
def load_filters_txt(path):
    # returns dict with sets: 'fillers', 'stopwords', 'pos_blacklist'
    sections = {"fillers": set(), "stopwords": set(), "pos_blacklist": set()}
    if not path:
        return sections
    if not os.path.exists(path):
        print(f"[warning] filters file not found: {path}", file=sys.stderr)
        return sections
    cur = None
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                key = line[1:-1].strip().lower()
                if key in sections:
                    cur = key
                else:
                    cur = None
                continue
            if cur:
                sections[cur].add(line)
    return sections

def contains_japanese(text: str) -> bool:
    return bool(JP_CHAR_RE.search(text))

LATIN_DIGIT_RE = re.compile(r'[A-Za-z0-9]')

def filter_tokens(tokens, pos_list=None, filters=None, strict=False):
    """
    Keep only tokens that contain Japanese chars and that are not in stopwords/fillers.
    If strict=True: exclude tokens that contain ascii letters or digits.
    If pos_list provided, apply pos_blacklist (skip tokens whose pos startswith any blacklisted).
    """
    if filters is None:
        filters = {"fillers": set(), "stopwords": set(), "pos_blacklist": set()}
    out = []
    for i, tok in enumerate(tokens):
        if not contains_japanese(tok):
            continue
        if strict and LATIN_DIGIT_RE.search(tok):
            continue
        if tok in filters.get("fillers", set()):
            continue
        if tok in filters.get("stopwords", set()):
            continue
        if pos_list and filters.get("pos_blacklist"):
            pos = pos_list[i] if i < len(pos_list) else ""
            # check if pos startswith any blacklisted entry
            skip = False
            for pblk in filters.get("pos_blacklist", set()):
                if not pblk:
                    continue
                if pos and pos.startswith(pblk):
                    skip = True
                    break
            if skip:
                continue
        out.append(tok)
    return out

# Misra-Gries (algoritma_3_1)
def misra_gries(stream, k):
    if k <= 1:
        raise ValueError("k must be > 1")
    counters = {}
    for x in stream:
        if x in counters:
            counters[x] += 1
        elif len(counters) < k - 1:
            counters[x] = 1
        else:
            # decrement all
            remove_keys = []
            for y in list(counters.keys()):
                counters[y] -= 1
                if counters[y] == 0:
                    remove_keys.append(y)
            for y in remove_keys:
                del counters[y]
    return counters

def second_pass_counts(stream, candidate_keys):
    counts = {k: 0 for k in candidate_keys}
    for x in stream:
        if x in counts:
            counts[x] += 1
    return counts

def write_csv(out_path, rows):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["token", "est_count", "true_count", "percent"])
        for tok, est, true, pct in rows:
            w.writerow([tok, est, true, f"{pct:.6f}"])

def main():
    p = argparse.ArgumentParser(description="Algoritma_3_1 (Misra-Gries) untuk teks Jepang dari SRT")
    p.add_argument("input_srt", help="Path ke file SRT input")
    p.add_argument("--k", type=int, default=10, help="Parameter k (default 10) => menyimpan hingga k-1 kandidat")
    p.add_argument("--filters", default=None, help="(opsional) path ke filters.txt")
    p.add_argument("--out", default="algoritma3_1_results.csv", help="CSV output path")
    p.add_argument("--top", type=int, default=30, help="Tampilkan top-N hasil (default 30)")
    p.add_argument("--strict", action="store_true", help="Strict: buang token yang juga mengandung ASCII/angka")
    args = p.parse_args()

    if not os.path.exists(args.input_srt):
        print("File input SRT tidak ditemukan:", args.input_srt, file=sys.stderr)
        sys.exit(1)

    print("Membaca SRT...")
    text = read_srt_text(args.input_srt)
    if not text.strip():
        print("Tidak menemukan teks di SRT (kosong setelah parsing).", file=sys.stderr)
        sys.exit(1)

    # tokenize
    if FUGASHI_AVAILABLE:
        print("Tokenisasi: menggunakan fugashi (unidic) — lebih baik untuk kata/lemma.")
        tokens, pos_list = tokenize_with_fugashi(text)
    else:
        print("Fugashi tidak tersedia — fallback ke regex runs (lebih kasar).")
        tokens, pos_list = regex_tokenize(text)

    print("Total token sebelum filter:", len(tokens))

    filters = load_filters_txt(args.filters) if args.filters else {"fillers": set(), "stopwords": set(), "pos_blacklist": set()}
    if args.filters:
        print(f"Loaded filters: fillers={len(filters['fillers'])}, stopwords={len(filters['stopwords'])}, pos_blacklist={len(filters['pos_blacklist'])}")

    filtered_tokens = filter_tokens(tokens, pos_list=pos_list, filters=filters, strict=args.strict)
    n = len(filtered_tokens)
    print("Total token setelah filter:", n)
    if n == 0:
        print("Tidak ada token hasil filter. Cek filters/strict/encoding.", file=sys.stderr)
        sys.exit(1)

    # run Misra-Gries
    print(f"Menjalankan algoritma_3_1 dengan k={args.k} ...")
    est = misra_gries(filtered_tokens, args.k)
    print("Kandidat (estimasi) ditemukan:", len(est))

    # second pass true counts
    true_counts = second_pass_counts(filtered_tokens, est.keys())

    # prepare rows sorted by true_count descending
    rows = []
    for tok in true_counts:
        cnt = true_counts[tok]
        est_cnt = est.get(tok, 0)
        pct = cnt / n * 100.0
        rows.append((tok, est_cnt, cnt, pct))
    rows_sorted = sorted(rows, key=lambda x: -x[2])

    # write CSV
    write_csv(args.out, rows_sorted)
    print("Hasil ditulis ke:", args.out)

    # print top results
    topn = min(args.top, len(rows_sorted))
    print(f"\nTop {topn} tokens by TRUE frequency:")
    for tok, est_cnt, cnt, pct in rows_sorted[:topn]:
        print(f"{tok!r}: true={cnt}, est={est_cnt}, {pct:.2f}%")

    # cross-check full counter
    c = Counter(filtered_tokens)
    print("\nCross-check top-20 by raw counter:")
    for tok, cnt in c.most_common(20):
        print(f"{tok!r}: {cnt}")

if __name__ == "__main__":
    main()
