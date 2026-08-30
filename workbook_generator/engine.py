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
from workbook_generator.generators.number_patterns import NumberPatternGenerator
from workbook_generator.generators.number_system import NumberSystemGenerator
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
                NumberPatternGenerator(),
                NumberSystemGenerator(),
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
    max_duplicate_retries = 1000

    def __init__(self, registry: GeneratorRegistry) -> None:
        self.registry = registry

    def build(self, recipe: Recipe) -> Worksheet:
        rng = random.Random(recipe.seed)
        difficulty = DIFFICULTY_LEVELS.get(recipe.difficulty.lower(), 3)
        topics = self._expand_topics(recipe)
        subtopic_filter_topics = {
            "fractions",
            "money",
            "number_patterns",
            "number_system",
            "time",
            "word_problems",
        }
        if recipe.subtopics and any(
            self.registry.resolve(topic).topic not in subtopic_filter_topics for topic in topics
        ):
            raise ValueError(
                "Subtopic filtering is currently supported only for number_system and word_problems."
            )
        questions: list[Question] = []
        used_prompts: set[str] = set()

        for index in range(recipe.questions):
            generator = self.registry.resolve(topics[index % len(topics)])
            question = self._generate_unique_question(
                generator,
                rng,
                difficulty,
                used_prompts,
                recipe.subtopics,
            )
            questions.append(question)
            used_prompts.add(self._question_key(question.prompt))

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

    @classmethod
    def _generate_unique_question(
        cls,
        generator: BaseGenerator,
        rng: random.Random,
        difficulty: int,
        used_prompts: set[str],
        subtopics: list[str] | None = None,
    ) -> Question:
        for _ in range(cls.max_duplicate_retries):
            question = generator.generate_one(rng, difficulty, subtopics=subtopics)
            if cls._question_key(question.prompt) not in used_prompts:
                return question
        raise ValueError(
            "Could not generate enough unique questions. "
            "Try fewer questions, a different seed, or add more templates/question-bank entries."
        )

    @staticmethod
    def _question_key(prompt: str) -> str:
        return re.sub(r"\s+", " ", prompt).strip().lower()
