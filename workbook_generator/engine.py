from __future__ import annotations

import random
import re
from collections.abc import Iterable

from config import DIFFICULTY_LEVELS, TOPIC_ALIASES
from workbook_generator.generators.base import BaseGenerator
from workbook_generator.generators.decimals import DecimalGenerator
from workbook_generator.generators.fractions import FractionGenerator
from workbook_generator.generators.geometry import GeometryGenerator
from workbook_generator.generators.measurement import MeasurementGenerator
from workbook_generator.generators.money import MoneyGenerator
from workbook_generator.generators.naplan import NaplanGenerator
from workbook_generator.generators.percentages import PercentageGenerator
from workbook_generator.generators.time import TimeGenerator
from workbook_generator.generators.word_problems import WordProblemGenerator
from workbook_generator.models import Question, Worksheet
from workbook_generator.recipe import Recipe


class GeneratorRegistry:
    def __init__(self, generators: Iterable[BaseGenerator]) -> None:
        self._generators = {generator.topic: generator for generator in generators}

    @classmethod
    def default(cls) -> "GeneratorRegistry":
        return cls(
            [
                FractionGenerator(),
                DecimalGenerator(),
                PercentageGenerator(),
                GeometryGenerator(),
                MeasurementGenerator(),
                MoneyGenerator(),
                TimeGenerator(),
                WordProblemGenerator(),
                NaplanGenerator(),
            ]
        )

    @property
    def topics(self) -> list[str]:
        return sorted(self._generators)

    def resolve(self, topic: str) -> BaseGenerator:
        normalized = TOPIC_ALIASES.get(topic.lower(), topic.lower())
        if normalized not in self._generators:
            available = ", ".join(self.topics + ["mixed"])
            raise ValueError(f"Unknown topic '{topic}'. Available topics: {available}")
        return self._generators[normalized]


class WorksheetBuilder:
    def __init__(self, registry: GeneratorRegistry) -> None:
        self.registry = registry

    def build(self, recipe: Recipe) -> Worksheet:
        rng = random.Random(recipe.seed)
        difficulty = DIFFICULTY_LEVELS.get(recipe.difficulty.lower(), 3)
        topics = self._expand_topics(recipe)
        questions: list[Question] = []
        used_prompts: set[str] = set()

        for index in range(recipe.questions):
            generator = self.registry.resolve(topics[index % len(topics)])
            question = self._generate_unique_question(generator, rng, difficulty, used_prompts)
            questions.append(question)
            used_prompts.add(question.prompt)

        rng.shuffle(questions)
        return Worksheet(
            title=recipe.title,
            slug=self._slugify(f"{recipe.title}-{recipe.questions}"),
            questions=questions,
            seed=recipe.seed,
            difficulty=recipe.difficulty,
        )

    def _expand_topics(self, recipe: Recipe) -> list[str]:
        if recipe.mix:
            topics: list[str] = []
            for topic, count in recipe.mix.items():
                topics.extend([topic] * int(count))
            return topics or ["fractions"]

        requested = [topic.lower() for topic in recipe.topics]
        if requested == ["mixed"] or "mixed" in requested:
            return [
                "fractions",
                "decimals",
                "percentages",
                "geometry",
                "measurement",
                "money",
                "time",
                "word_problems",
            ]
        return requested

    @staticmethod
    def _slugify(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

    @staticmethod
    def _generate_unique_question(
        generator: BaseGenerator,
        rng: random.Random,
        difficulty: int,
        used_prompts: set[str],
    ) -> Question:
        question = generator.generate_one(rng, difficulty)
        for _ in range(50):
            if question.prompt not in used_prompts:
                return question
            question = generator.generate_one(rng, difficulty)
        return question
