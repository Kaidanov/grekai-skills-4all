# Question schema

The generator edits **only** the `EXAM` object in `template.html`. Everything below documents its
shape. The engine is generic — never edit it.

## `EXAM.meta`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `id` | string | — | **Required, unique.** localStorage namespace `examcreator:<id>`. kebab-case, e.g. `chem8-atoms-he`. |
| `title` | string | — | Shown on the summary screen and as the page title. |
| `subtitle` | string | `""` | Small line under the title (subject · grade · topic). |
| `lang` | string | `"he"` | `"he"`, `"en"`, … drives UI strings and the TTS voice prefix. |
| `dir` | string | `"rtl"` | `"rtl"` or `"ltr"`. Use `ltr` for English. |
| `passingScore` | number | `60` | Percent needed to mark the exam "passed". |
| `shuffleQuestions` | bool | `false` | Shuffle order on a fresh start / retry. |
| `shuffleChoices` | bool | `false` | Reserved; keep MC `answer` as the index into `choices`. |
| `tts` | bool | `true` | Master switch for the read-aloud button. |
| `generatedNote` | string | `""` | If set, a ⚠️ banner shows on Q1. Use it to flag AI-generated questions for review. |

## `EXAM.questions[]`

Every question shares these fields, plus type-specific ones:

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Unique within the exam (`q1`, `q2`, …). Used as the answer key in storage. |
| `type` | string | `"mc"` \| `"tf"` \| `"numeric"` \| `"fill"`. |
| `points` | number | XP awarded for a correct first answer. Default 10. |
| `prompt` | string | The question. **May contain inline HTML** for formulas (see below). |
| `explanation` | string | Shown after answering (and in review). Keep it one short line. |
| `tts` | string | *(optional)* Text read aloud — add **nikud** for Hebrew. Falls back to the prompt text. |

### `type: "mc"` — multiple choice
```js
{ id:"q1", type:"mc", points:10,
  prompt:"כמה זה 7 × 8?",
  tts:"כַּמָּה זֶה שֶׁבַע כָּפוּל שְׁמוֹנֶה?",
  choices:["54","56","48","63"],
  answer:1,                       // INDEX into choices (0-based) — must be valid
  explanation:"7 × 8 = 56." }
```

### `type: "tf"` — true / false
```js
{ id:"q2", type:"tf", points:10,
  prompt:"x + 5 = 12 ⟹ x = 7.",
  answer:true,                    // boolean
  explanation:"x = 12 − 5 = 7." }
```

### `type: "numeric"` — number with tolerance
```js
{ id:"q3", type:"numeric", points:10,
  prompt:"שטח מלבן 6×4?",
  answer:24,                      // number
  tolerance:0,                    // accepted if |input − answer| ≤ tolerance (+tiny epsilon)
  unit:'סמ"ר',                    // optional, shown next to the field & in the key
  explanation:"6 × 4 = 24." }
```
Use a non-zero `tolerance` for rounded / decimal answers (e.g. `answer:3.14, tolerance:0.01`).
Input accepts comma or dot decimals.

### `type: "fill"` — short text
```js
{ id:"q5", type:"fill", points:10,
  prompt:"המספר הראשוני הקטן ביותר הוא ___",
  answer:["2","שתיים"],           // string OR array of accepted synonyms
  explanation:"2 הוא הראשוני הקטן ביותר." }
```
Matching is case-insensitive and whitespace-normalized. List every acceptable spelling/synonym.

## Formulas without libraries

Put inline HTML straight in `prompt` (and a plain-text `tts` for readout). Helpers shipped in the
template's CSS — **no MathJax/KaTeX**:

| Want | Markup |
|------|--------|
| Subscript H₂O | `H<sub>2</sub>O` |
| Superscript x² | `x<sup>2</sup>` |
| Fraction ½ | `<span class="frac"><span>1</span><span class="den">2</span></span>` |
| Square root √x | `<span class="sqrt">x</span>` |
| Keep together | `<span class="nowrap">…</span>` |

Examples: `2H<sub>2</sub> + O<sub>2</sub> → 2H<sub>2</sub>O`, `E = mc<sup>2</sup>`,
`v = <span class="frac"><span>d</span><span class="den">t</span></span>`.

## Internal-consistency checklist (run before delivering)

- [ ] Every `meta.id` is unique vs the user's other apps.
- [ ] Each MC `answer` is a valid index into `choices`.
- [ ] Each `explanation` matches the keyed answer (no contradictions).
- [ ] Numeric `tolerance` is sane (0 for exact integers; small for decimals/rounding).
- [ ] `fill` answers list all reasonable spellings.
- [ ] No invented facts/dates/dosages; AI-generated sets carry a `generatedNote`.
