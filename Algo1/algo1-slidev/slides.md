---
theme: seriph
title: Algorithm 3.1 - Language Learning
transition: slide-left
mdc: true
---

# Spatiotemporal Data Processing 2025  
## Team B – Language Learning Optimization

<div class="mt-6 text-gray-400 text-sm">
  Implementation of Algorithm 3.1 on Language Learning Process  
  — <i>Tokyo Metropolitan University, Team B</i>
</div>

---

# Problem Statement

- Learning a new language involves memorizing thousands of words.
- Most learners struggle to prioritize *which* words are important.
- Our idea: extract the **most frequent** words from real-world context.

---

# Concept

We apply **Algorithm 3.1 (Misra–Gries)** to detect frequent vocabulary items  
from videos and subtitles, helping learners focus on high-priority words.

---

# Algorithm 3.1 – Misra–Gries

```python
def misra_gries(stream, k):
    counters = {}
    for x in stream:
        if x in counters:
            counters[x] += 1
        elif len(counters) < k - 1:
            counters[x] = 1
        else:
            # decrement all
            for y in list(counters.keys()):
                counters[y] -= 1
                if counters[y] == 0:
                    del counters[y]
    return counters
