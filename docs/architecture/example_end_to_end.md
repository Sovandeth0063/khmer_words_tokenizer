# End-to-End Khmer Tokenizer Example

This example follows the same steps shown in the **End-to-End Data Flow &
Pipeline Architecture** section of
[`system_architecture.md`](./system_architecture.md).

## Input

```text
ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា
```

## 1. Clean and Fix Khmer Text

The tokenizer puts Khmer text into a standard form. It can join split vowels,
fix Khmer marks, remove invalid characters, and put letters in the correct
order.

```text
ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា
```

No visible changes are needed for this example.

## 2. Find Word Boundaries and Remove Hidden Characters

The tokenizer checks for hidden spaces, such as ZWSP, before removing hidden
characters from the text.

```text
Clean text: ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា
Boundary information: none
```

## 3. Separate Non-Khmer Text

The tokenizer checks whether the input contains links, email addresses,
English text, numbers, punctuation, or emojis. These parts are kept together
and are not split as Khmer words.

This example contains only Khmer text, so the complete text continues to the
next step.

## 4. Split Khmer into Letter Groups

The text is divided into small groups. Letters that belong together are kept together.

```text
[ខ្ញុំ, ស្រ, ឡា, ញ់, ប្រ, ទេ, ស, ក, ម្ពុ, ជា]
```

For example, `ប្រ` stays together because its letters form one Khmer character
group.

## 5. Collect Information for Word Splitting

For each group, the tokenizer checks:

- Nearby letter groups
- Vowels and Khmer marks
- Coeng usage
- Matching words in the dictionary
- Known word boundaries

For example, the tokenizer can collect information for `ប្រ`:

```python
{
    "kcc": "ប្រ",
    "has_coeng": "True",
    "has_vowel": "False",
    "base_series": "first",
    "match.forward": "3",
}
```

`match.forward` equal to `3` means that the dictionary finds a word covering
three groups: `ប្រ`, `ទេ`, and `ស`.

The feature extraction code is in
[`features.py`](../../khmer_tokenizer/models/crf/features.py).

## 6. Choose a Word Splitter

The default method is CRF. It uses the collected information and the
dictionary to predict where words should end.

BiMM is the faster alternative. It matches dictionary words from both
directions and can be used as a fallback.

For this example, the CRF method is used.

## 7. Apply a User Dictionary

If the user provides words with `add_word()` or a custom dictionary file, the
tokenizer keeps those matching words together.

No custom words are provided in this example.

## 8. Predict Word Boundaries

The CRF model gives each group a BIES label:

```text
KCCs:  [ខ្ញុំ, ស្រ, ឡា, ញ់, ប្រ, ទេ, ស, ក, ម្ពុ, ជា]
Tags:  [S,    B,   I,  E,  B,   I,  E,  B, I,   E]
```

The labels mean:

- `S` = a single-group word
- `B` = the beginning of a word
- `I` = inside a word
- `E` = the end of a word

## 9. Build the Final Words

The tokenizer joins the groups using the labels:

```python
["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
```

## Complete End-to-End Flow

```text
Raw Khmer input
  ↓
1. Clean and fix Khmer text
  ↓
2. Find boundaries and remove hidden characters
  ↓
3. Separate non-Khmer text
  ↓
4. Split Khmer into letter groups
  ↓
5. Collect information for word splitting
   ↓
6. Choose CRF or BiMM
   ↓
7. Apply the user dictionary
   ↓
8. Predict BIES labels
   ↓
9. Build the final words
  ↓
["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
```
