# Primary Maths Generator

A small, extensible Python project for generating printable primary-school mathematics worksheets with answer keys. It supports fixed question banks, randomised question templates, LaTeX output, and PDF compilation when `pdflatex` is installed.

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

## Static Web App

This repository includes a GitHub Pages-friendly worksheet generator:

- `index.html`
- `styles.css`
- `app.js`
- `data/question_bank.json`

The web app runs entirely in the browser. Users can choose a topic, subtopic,
difficulty, question count, columns, seed, and title. It displays all selected
questions in one section and all answers in a second section, with a print
friendly layout.

To preview locally:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

For exact CLI-style PDFs from GitHub, use the `Generate PDF` workflow in the
Actions tab. Click `Run workflow`, choose the topic, subtopic, difficulty,
question count, seed, columns, and title, then download the `worksheet-pdf`
artifact after the run finishes.

## CLI Examples

```bash
python generate.py --topic fractions --questions 200
python generate.py --topic mixed --questions 250 --difficulty year5 --seed 2026
python generate.py --topic word_problems --questions 40 --difficulty year5 --columns 2 --answer-columns 3
python generate.py --topic word_problems --subtopic ratios --questions 100 --difficulty year5
python generate.py --topic word_problems --subtopic two_unknown_linear_ratio --questions 100 --difficulty year5
python generate.py --topic word_problems --subtopic geometry_angles,geometry_properties,geometry_multistep --questions 100 --difficulty year5
python generate.py --topic number_system --questions 10 --difficulty year5
python generate.py --topic number_patterns --questions 20 --difficulty year3
python generate.py --topic money --questions 50 --no-pdf
```

## CLI Options

```text
python generate.py [recipe] [options]
```

- `recipe`: optional YAML recipe file.
- `--topic`: topic to generate, or `mixed`.
- `--subtopic`: optional word-problem filter, such as `ratios`, `money`, `fractions`, `two_unknowns`, or `fraction_comparison`.
- `--questions`: number of questions.
- `--difficulty`: level to generate, such as `year3`, `year4`, `year5`, `year6`, `naplan`, `selective`, `oc`, or `icas`.
- `--seed`: random seed. Same seed gives the same worksheet again.
- `--title`: custom worksheet title.
- `--columns`: number of columns for the question pages. Allowed values: `1`, `2`, `3`.
- `--answer-columns`: number of columns for the answer key. Allowed values: `1`, `2`, `3`, `4`. Default is `3`.
- `--output-dir`: folder for generated `.tex` and `.pdf` files. Default is `output`.
- `--no-pdf`: write only `.tex` and skip PDF compilation.

Example with compact answer key:

```bash
python generate.py --topic word_problems --questions 80 --difficulty year5 --columns 2 --answer-columns 3
```

Example with ratio questions only:

```bash
python generate.py --topic word_problems --subtopic ratios --questions 100 --difficulty year5
```

Example with two-unknown linear ratio questions only:

```bash
python generate.py --topic word_problems --subtopic two_unknown_linear_ratio --questions 100 --difficulty year5
```

Example with geometry, shape properties, angles, and multi-step geometry questions:

```bash
python generate.py --topic word_problems --subtopic geometry_angles,geometry_properties,geometry_multistep --questions 100 --difficulty year5
```

Example with more compact answers:

```bash
python generate.py --topic word_problems --questions 80 --difficulty year5 --answer-columns 4
```

Supported topics:

- `fractions`
- `decimals`
- `percentages`
- `geometry`
- `measurement`
- `money`
- `number_patterns`
- `number_system`
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

Subtopic filters are supported for word problems:

```yaml
title: Year 5 Ratios
questions: 100
difficulty: year5
seed: 777
layout:
  columns: 2
topics:
  - word_problems
subtopic: ratios
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

Difficulty mapping:

```text
year3      difficulty 1
year4      difficulty 2
year5      difficulty 3
year6      difficulty 4
naplan     difficulty 4
oc         difficulty 4
selective  difficulty 5
icas       difficulty 5
```

`data/question_bank.json` stores fixed questions and fixed answers. `data/question_templates.json` stores reusable question forms with random numbers and calculated answers. The word-problem generator uses both.

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
