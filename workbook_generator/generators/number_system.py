from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question
from workbook_generator.question_bank import QuestionBank


class NumberSystemGenerator(BaseGenerator):
    topic = "number_system"

    def __init__(self, question_bank: QuestionBank | None = None) -> None:
        self.question_bank = question_bank or QuestionBank()

    def generate_one(
        self,
        rng: random.Random,
        difficulty: int,
        subtopics: list[str] | None = None,
    ) -> Question:
        use_bank = rng.random() < 0.2
        bank_question = self.question_bank.generate_one(
            self.topic,
            difficulty,
            rng,
            subtopics=subtopics,
        )
        if bank_question and (use_bank or subtopics):
            return bank_question

        return self._generate_procedural(rng, difficulty, subtopics=subtopics)

    def _generate_procedural(
        self,
        rng: random.Random,
        difficulty: int,
        subtopics: list[str] | None = None,
    ) -> Question:
        generators = {
            "place_value": self._place_value_question,
            "expanded_form": self._expanded_form_question,
            "ordering_numbers": self._ordering_question,
            "rounding": self._rounding_question,
            "number_patterns": self._pattern_question,
            "digit_logic": self._digit_logic_question,
        }
        candidates = list(generators)
        if subtopics:
            normalized = {value.strip().lower().replace("-", "_") for value in subtopics}
            candidates = [name for name in candidates if name in normalized]
            if not candidates:
                requested = ", ".join(subtopics)
                raise ValueError(f"No number-system questions found for subtopic: {requested}")

        subtopic = rng.choice(candidates)
        prompt, answer, tags = generators[subtopic](rng, difficulty)
        return Question(
            prompt=prompt,
            answer=answer,
            topic=self.topic,
            subtopic=subtopic,
            difficulty=difficulty,
            tags=("number_system", *tags),
            meta={"source": "procedural"},
        )

    @staticmethod
    def _place_value_question(rng: random.Random, difficulty: int) -> tuple[str, str, tuple[str, ...]]:
        places = [
            ("ones", 1),
            ("tens", 10),
            ("hundreds", 100),
            ("thousands", 1_000),
            ("ten-thousands", 10_000),
        ]
        if difficulty >= 3:
            places.append(("hundred-thousands", 100_000))
        place_name, place_value = rng.choice(places[1:])
        digit = rng.randint(1, 9)
        number = rng.randint(10_000, 999_999 if difficulty >= 3 else 99_999)
        number = number - ((number // place_value) % 10) * place_value + digit * place_value
        return (
            f"What is the value of the digit {digit} in {number:,}?",
            f"{digit * place_value:,}",
            ("place_value",),
        )

    @staticmethod
    def _expanded_form_question(rng: random.Random, difficulty: int) -> tuple[str, str, tuple[str, ...]]:
        upper = 999_999 if difficulty >= 3 else 99_999
        number = rng.randint(10_000, upper)
        parts = []
        place = 1
        remaining = number
        while remaining:
            digit = remaining % 10
            if digit:
                parts.append(digit * place)
            remaining //= 10
            place *= 10
        expanded = " + ".join(f"{part:,}" for part in reversed(parts))
        return (
            f"Write {expanded} as one number.",
            f"{number:,}",
            ("expanded_form", "place_value"),
        )

    @staticmethod
    def _ordering_question(rng: random.Random, difficulty: int) -> tuple[str, str, tuple[str, ...]]:
        upper = 999_999 if difficulty >= 3 else 99_999
        numbers = rng.sample(range(1_000, upper), 4)
        return (
            "Put these numbers in order from smallest to largest: "
            + ", ".join(f"{number:,}" for number in numbers),
            ", ".join(f"{number:,}" for number in sorted(numbers)),
            ("ordering", "comparison"),
        )

    @staticmethod
    def _rounding_question(rng: random.Random, difficulty: int) -> tuple[str, str, tuple[str, ...]]:
        place = rng.choice([10, 100, 1_000] if difficulty >= 3 else [10, 100])
        upper = 999_999 if difficulty >= 3 else 99_999
        number = rng.randint(1_000, upper)
        rounded = round(number / place) * place
        place_name = {10: "10", 100: "100", 1_000: "1,000"}[place]
        return (
            f"Round {number:,} to the nearest {place_name}.",
            f"{rounded:,.0f}",
            ("rounding",),
        )

    @staticmethod
    def _pattern_question(rng: random.Random, difficulty: int) -> tuple[str, str, tuple[str, ...]]:
        step = rng.choice([25, 50, 100, 250, -25, -50, -100, -250])
        start = rng.randint(1_000, 9_000 if difficulty < 3 else 90_000)
        values = [start + step * index for index in range(5)]
        while min(values) < 0:
            start = rng.randint(1_000, 90_000)
            values = [start + step * index for index in range(5)]
        return (
            "Complete the pattern: "
            + ", ".join(f"{number:,}" for number in values[:3])
            + ", _____, _____",
            f"{values[3]:,}, {values[4]:,}",
            ("patterns",),
        )

    @staticmethod
    def _digit_logic_question(rng: random.Random, difficulty: int) -> tuple[str, str, tuple[str, ...]]:
        thousands = rng.randint(2, 8)
        hundreds = rng.randint(0, 9)
        tens = (thousands + hundreds + rng.randint(1, 4)) % 10
        ones = rng.randint(0, 9)
        number = thousands * 1_000 + hundreds * 100 + tens * 10 + ones
        return (
            "I am a four-digit number. "
            f"My thousands digit is {thousands}. "
            f"My hundreds digit is {hundreds}. "
            f"My tens digit is {tens}. "
            f"My ones digit is {ones}. "
            "What number am I?",
            f"{number:,}",
            ("digits", "logic"),
        )
