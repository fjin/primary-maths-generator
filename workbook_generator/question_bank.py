from __future__ import annotations

import ast
import json
import random
from pathlib import Path
from typing import Any

from workbook_generator.models import Question


class QuestionBank:
    def __init__(
        self,
        path: Path | None = None,
        template_path: Path | None = None,
    ) -> None:
        data_dir = Path(__file__).resolve().parent.parent / "data"
        self.path = path or data_dir / "question_bank.json"
        self.template_path = template_path or data_dir / "question_templates.json"
        self._questions = self._load()
        self._templates = self._load_templates()

    def questions_for(self, topic: str, max_difficulty: int) -> list[Question]:
        return [
            question
            for question in self._questions
            if question.topic == topic and question.difficulty <= max_difficulty
        ]

    def generate_one(
        self,
        topic: str,
        max_difficulty: int,
        rng: random.Random,
    ) -> Question | None:
        entries: list[Question | dict[str, Any]] = [
            question
            for question in self._questions
            if question.topic == topic and question.difficulty <= max_difficulty
        ]
        entries.extend(
            template
            for template in self._templates
            if template["topic"] == topic and int(template.get("difficulty", 3)) <= max_difficulty
        )
        if not entries:
            return None

        selected = rng.choice(entries)
        if isinstance(selected, Question):
            return selected
        return self._instantiate_template(selected, rng)

    def _load(self) -> list[Question]:
        if not self.path.exists():
            return []

        raw_questions = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            Question(
                prompt=item["question"],
                answer=str(item["answer"]),
                topic=item["topic"],
                subtopic=item.get("subtopic", "general"),
                difficulty=int(item.get("difficulty", 3)),
                tags=tuple(item.get("tags", [])),
                meta={"source": item.get("source", "question_bank")},
            )
            for item in raw_questions
        ]

    def _load_templates(self) -> list[dict[str, Any]]:
        if not self.template_path.exists():
            return []
        return json.loads(self.template_path.read_text(encoding="utf-8"))

    def _instantiate_template(
        self,
        template: dict[str, Any],
        rng: random.Random,
    ) -> Question:
        values = self._generate_values(template, rng)
        answer = _safe_eval(str(template["answer_formula"]), values)
        values["answer"] = _format_number(answer)

        return Question(
            prompt=template["question"].format(**values),
            answer=str(template.get("answer_format", "{answer}")).format(**values),
            topic=template["topic"],
            subtopic=template.get("subtopic", "general"),
            difficulty=int(template.get("difficulty", 3)),
            tags=tuple(template.get("tags", [])),
            meta={"source": template.get("source", "template")},
        )

    def _generate_values(
        self,
        template: dict[str, Any],
        rng: random.Random,
    ) -> dict[str, int | float | str]:
        variables = template.get("variables", {})
        constraints = template.get("constraints", [])

        for _ in range(100):
            values: dict[str, int | float | str] = {}
            for name, config in variables.items():
                values[name] = _random_value(config, rng)
            if all(bool(_safe_eval(constraint, values)) for constraint in constraints):
                return values

        raise ValueError(f"Could not satisfy template constraints: {template.get('question')}")


def _random_value(config: dict[str, Any], rng: random.Random) -> int | float | str:
    if "choices" in config:
        return rng.choice(config["choices"])

    minimum = int(config["min"])
    maximum = int(config["max"])
    step = int(config.get("step", 1))
    return rng.randrange(minimum, maximum + 1, step)


def _format_number(value: int | float | bool) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _safe_eval(expression: str, variables: dict[str, int | float | str]) -> int | float | bool:
    tree = ast.parse(expression, mode="eval")
    _validate_ast(tree)
    return eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, variables)


def _validate_ast(node: ast.AST) -> None:
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.And,
        ast.Or,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
    )
    for child in ast.walk(node):
        if not isinstance(child, allowed):
            raise ValueError(f"Unsupported formula expression: {ast.dump(child)}")
