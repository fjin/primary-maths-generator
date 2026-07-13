# Year 5 Workbook Generator

A small, extensible Python project for generating printable mathematics worksheets with answer keys. It writes LaTeX and can compile a PDF when `pdflatex` is installed.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generate.py --topic fractions --questions 40 --seed 123
```

Or generate from YAML:

```bash
python generate.py examples/year5-mixed.yaml
```

Outputs are written to `output/`.

## CLI Examples

```bash
python generate.py --topic fractions --questions 200
python generate.py --topic mixed --questions 250 --difficulty year5 --seed 2026
python generate.py --topic money --questions 50 --no-pdf
```

Supported topics:

- `fractions`
- `decimals`
- `percentages`
- `geometry`
- `measurement`
- `money`
- `time`
- `word_problems`
- `naplan`
- `mixed`

## YAML Recipe

```yaml
title: Year 5 Fractions
questions: 200
difficulty: year5
seed: 123
layout:
  columns: 2
topics:
  - fractions
```

Weighted mixes are also supported:

```yaml
title: Year 5 Review
questions: 100
mix:
  fractions: 40
  decimals: 20
  percentages: 20
  word_problems: 20
```

## Architecture

- `generate.py` handles the command line interface.
- `workbook_generator/models.py` defines `Question` and `Worksheet`.
- `workbook_generator/generators/` contains one generator class per topic.
- `data/question_bank.json` stores curated questions that can be sampled directly.
- `data/question_templates.json` stores questions with random variables and answer formulas.
- `workbook_generator/engine.py` selects generators and builds worksheets.
- `workbook_generator/renderers/latex.py` renders printable LaTeX with an answer key.

To add a topic, create a new `BaseGenerator` subclass and register it in `GeneratorRegistry.default()`.

## Adding Real Questions

Add curated questions to `data/question_bank.json`:

```json
{
  "topic": "word_problems",
  "subtopic": "money",
  "difficulty": 3,
  "question": "Mia buys 3 notebooks for \\$4.50 each. How much does she spend?",
  "answer": "\\$13.50",
  "tags": ["year5", "money", "multiplication"],
  "source": "curated"
}
```

The word-problem generator prefers questions that exactly match the selected difficulty. For example, `--difficulty year6` prefers questions with difficulty `4`. If there are no matching questions, it falls back to easier questions.

## Adding Randomised Questions

Add templates to `data/question_templates.json` when you want the numbers and answer to change together:

```json
{
  "topic": "word_problems",
  "subtopic": "addition_subtraction",
  "difficulty": 3,
  "question": "A library starts the day with {start} books. {borrowed} books are borrowed and {returned} books are returned. How many books are left?",
  "answer_formula": "start - borrowed + returned",
  "answer_format": "{answer}",
  "variables": {
    "start": { "min": 250, "max": 800, "step": 10 },
    "borrowed": { "min": 50, "max": 300, "step": 5 },
    "returned": { "min": 20, "max": 150, "step": 5 }
  },
  "constraints": ["borrowed < start"],
  "tags": ["year5", "template"],
  "source": "template"
}
```

Templates can also calculate several derived values, which is useful for ratios:

```json
{
  "question": "{person_a} and {person_b} share {total} candies in the ratio {ratio_a}:{ratio_b}. How many candies does each person get?",
  "answer_format": "{person_a}: {share_a}, {person_b}: {share_b}",
  "variables": {
    "ratio_a": { "choices": [2, 3, 4, 5, 6] },
    "ratio_b": { "choices": [1, 2, 3, 4, 5] },
    "unit": { "min": 2, "max": 12 }
  },
  "derived": {
    "total": "unit * (ratio_a + ratio_b)",
    "share_a": "unit * ratio_a",
    "share_b": "unit * ratio_b"
  }
}
```

## Tests

```bash
python -m unittest discover
```
