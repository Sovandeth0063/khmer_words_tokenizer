# End-to-End Tokenization Flow

Khmer sentences normally have no spaces between words. Here is how the tokenizer turns a raw sentence like `"ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"` into separate words, step by step.

---

## Pipeline Overview

```text
"ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"                        ← 1. Raw Khmer sentence
        │
        ▼  normalize()          (tokenizer/normalizer.py)
"ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"                        ← 2. Cleaned & standardized text
        │
        ▼  lex()                (tokenizer/segmenter.py)
[ khmer: "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា" ]              ← 3. Separated by text type
        │
        ▼  segment_kcc()        (tokenizer/segmenter.py)
["ខ្ញុំ", "ស្រ", "ឡា", "ញ់", "ប្រ", "ទេ", "ស", "ក", "ម្ពុ", "ជា"]  ← 4. 10 KCC clusters
        │
        ▼  predict_tags()       (tokenizer/crf.py + khmer_dictionary.txt)
[  S,     B,     I,    E,    B,    I,    E,   B,    I,     E  ]    ← 5. BIES word tags
        │
        ▼  assemble_tokens()    (tokenizer/assembler.py)
["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]          ← 6. Final word tokens
```

---

## Step-by-Step Explanation

### Step 1 — Raw Input

- **Why:** The tokenizer starts with whatever text the user types or pastes — no spaces between Khmer words, and sometimes mixed with English, numbers, symbols, or messy typing.
- **What happens:** The raw string enters `tokenize(text)` (in `tokenizer/__init__.py`) and is passed into the pipeline without changing anything yet.
- **Example input:**

```text
"ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"
```

---

### Step 2 — Normalize Khmer Unicode (`tokenizer/normalizer.py` → `normalize`)

- **Why:** The same Khmer word can look identical on screen even when typed in different ways behind the scenes. If the text isn't standardized first, dictionary lookup and word splitting can miss valid words.
- **What happens:**
  - **Applies NFC & cleans old characters:** Converts text to standard Unicode form and removes/replaces deprecated characters.
  - **Merges split vowels:** For example, two separate vowel pieces `េ` + `ា` become the single vowel `ោ`.
  - **Reorders marks into canonical order:** Fixes mistyped mark sequences (for example, `ាក្រ` → `ក្រា`) so the consonant stays attached to its subscript and vowel properly.
  - **Removes invisible Zero-Width Spaces (ZWSP):** Strips hidden `\u200b` characters (`"ក\u200bខ"` → `"កខ"`) so they don't break matching, while saving their positions as boundary metadata.
- **Result on our example:** `"ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"` (already clean, no hidden ZWSP found).

---

### Step 3 — Detect Text Spans (`tokenizer/segmenter.py` → `lex`)

- **Why:** Real sentences often mix Khmer with English, numbers, URLs, spaces, or punctuation. Those non-Khmer parts shouldn't be chopped up by the Khmer word splitter.
- **What happens:**
  - Scans the cleaned text and labels each chunk:
    - `khmer` → Khmer letters (sent to Steps 4–6 to split into words)
    - `passthrough` → English words, numbers, Khmer digits, URLs, emails (kept whole, not split by Khmer rules)
    - `whitespace` / `punctuation` → spaces and symbols
  - **What happens to English words & symbols afterward:**
    - `khmer_only=False` (default in Python): English words, numbers, and punctuation stay as-is in the output (e.g. `"ខ្ញុំ loves កម្ពុជា!"` → `["ខ្ញុំ", "loves", "កម្ពុជា", "!"]`).
    - `khmer_only=True` (checked by default in the Web UI): English, numbers, punctuation, and spaces are dropped, leaving only Khmer words (`["ខ្ញុំ", "កម្ពុជា"]`).
- **Result on our example:** One chunk labeled `khmer`: `"ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"`.

---

### Step 4 — Split into Khmer Character Clusters (`tokenizer/segmenter.py` → `segment_kcc`)

- **Why:** You cannot split Khmer character-by-character, because a consonant's subscript (`ជើង`), vowels, and diacritics belong together as one unbreakable visual unit called a **KCC** (Khmer Character Cluster).
- **What happens:**
  - Walks through each `khmer` chunk and keeps every base consonant glued together with any subscripts (`្` + consonant), dependent vowels, and signs.
  - For example, `"ខ្ញុំ"` is **5** separate Unicode characters (`ខ + ្ + ញ + ុ + ំ`), and `segment_kcc()` keeps all 5 together as **1 KCC**, while `"ស្រឡាញ់"` splits into 3 KCCs (`"ស្រ"`, `"ឡា"`, `"ញ់"`).
- **Result on our example (10 KCCs):**

```text
["ខ្ញុំ", "ស្រ", "ឡា", "ញ់", "ប្រ", "ទេ", "ស", "ក", "ម្ពុ", "ជា"]
```

---

### Step 5 — Predict Word Boundaries (`tokenizer/crf.py` / `tokenizer/bimm.py` + `khmer_dictionary.txt`)

- **Why:** Now that we have safe KCC building blocks, we need to look up which KCCs group together into real Khmer words.
- **What happens:**
  - **Custom words first (`add_word`):** Any custom words you added are locked in as single tokens before dictionary splitting (for example, adding `"ប្រទេសកម្ពុជា"` keeps it together as one token).
  - **CRF + Trie (default, `CRFEngine`):** Checks `tokenizer/resources/khmer_dictionary.txt` (loaded into a fast `Trie`) at every KCC position to find matching dictionary words (`"ខ្ញុំ"`, `"ស្រឡាញ់"`, `"ប្រទេស"`, `"កម្ពុជា"`).
    - It scores candidate splits — for example, even though `"ប្រទេសកម្ពុជា"` is also in the dictionary (score `1.7`), splitting it into `"ប្រទេស"` (`2.0`) + `"កម្ពុជា"` (`2.0`) gives a higher total score (`4.0`), so CRF picks `["ប្រទេស", "កម្ពុជា"]`.
    - Then it assigns a **BIES** tag to each KCC:
      - **S** (Single) — 1-KCC word
      - **B** (Begin) — start of a multi-KCC word
      - **I** (Inside) — middle of a word
      - **E** (End) — end of a word
  - **BiMM (optional, `BiMMTokenizer`):** Scans forward and backward against `khmer_dictionary.txt` and picks fewer/longer tokens (giving `["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេសកម្ពុជា"]`).
- **Result on our example (CRF tags):**

```text
KCC:  ខ្ញុំ   ស្រ   ឡា   ញ់   ប្រ   ទេ   ស   ក   ម្ពុ   ជា
Tag:   S     B     I    E    B    I    E   B    I     E
```

---

### Step 6 — Assemble Tokens (`tokenizer/assembler.py` → `assemble_tokens`)

- **Why:** Turn the KCCs + BIES tags back into complete words, and combine them with any kept non-Khmer spans from Step 3.
- **What happens:**
  - Reads the tags left to right:
    - `S`     → `"ខ្ញុំ"`
    - `B I E` → `"ស្រ" + "ឡា" + "ញ់"` = `"ស្រឡាញ់"`
    - `B I E` → `"ប្រ" + "ទេ" + "ស"` = `"ប្រទេស"`
    - `B I E` → `"ក" + "ម្ពុ" + "ជា"` = `"កម្ពុជា"`
  - Applies `keep_whitespace` and `khmer_only` filtering before returning the list.
- **Final Output:**

```python
["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
```

---

## How to Use It

```python
from tokenizer import tokenize, KhmerTokenizer

# Default (CRF engine)
tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា")
# ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]

# Keep English & punctuation (default behavior)
tokenize("ខ្ញុំ loves កម្ពុជា!")
# ["ខ្ញុំ", "loves", "កម្ពុជា", "!"]

# Keep only Khmer words
tokenize("ខ្ញុំ loves កម្ពុជា 100%!", khmer_only=True)
# ["ខ្ញុំ", "កម្ពុជា"]

# Use BiMM dictionary engine instead of CRF
KhmerTokenizer(engine="bimm").tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា")
# ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេសកម្ពុជា"]
```

**CLI & Web UI:**

```powershell
py -m tokenizer.cli "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"
py scripts/web_app.py
```
