from __future__ import annotations

import random
from fractions import Fraction

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question, latex_fraction
from workbook_generator.question_bank import QuestionBank


class FractionGenerator(BaseGenerator):
    topic = "fractions"

    def __init__(self, question_bank: QuestionBank | None = None) -> None:
        self.question_bank = question_bank or QuestionBank()

    def generate_one(
        self,
        rng: random.Random,
        difficulty: int,
        subtopics: list[str] | None = None,
    ) -> Question:
        bank_question = self.question_bank.generate_one(
            self.topic,
            difficulty,
            rng,
            subtopics=subtopics,
        )
        if bank_question:
            return bank_question

        denominators = [2, 3, 4, 5, 6, 8, 10, 12]
        denominator_a = rng.choice(denominators[: 4 + difficulty])
        denominator_b = rng.choice(denominators[: 4 + difficulty])

        operations = ["+", "-"]
        if difficulty >= 3:
            operations.append(r"\times")
        if difficulty >= 5:
            operations.append(r"\div")
        operation = rng.choice(operations)

        # Keep multiplication/division operands as proper fractions so the
        # arithmetic stays approachable; mixed numbers are only used for +/-.
        allow_mixed = difficulty >= 3 and operation in ("+", "-")
        a = self._random_operand(rng, denominator_a, allow_mixed)
        b = self._random_operand(rng, denominator_b, allow_mixed)

        if operation == "+":
            answer = a + b
        elif operation == "-":
            if b > a:
                a, b = b, a
            answer = a - b
        elif operation == r"\times":
            answer = a * b
        else:
            answer = a / b

        tags = ["fraction", "arithmetic"]
        tags.append("mixed_numbers" if a >= 1 or b >= 1 else "proper_fractions")

        prompt = rf"${latex_fraction(a)} {operation} {latex_fraction(b)} =$"
        return Question(
            prompt=prompt,
            answer=rf"${latex_fraction(answer)}$",
            topic=self.topic,
            subtopic="operations",
            difficulty=difficulty,
            tags=tuple(tags),
        )

    @staticmethod
    def _random_operand(rng: random.Random, denominator: int, allow_mixed: bool) -> Fraction:
        proper = Fraction(rng.randint(1, denominator - 1), denominator)
        if allow_mixed and rng.random() < 0.5:
            whole = rng.randint(1, 4)
            return whole + proper
        return proper
