from __future__ import annotations

import random
from abc import ABC, abstractmethod

from workbook_generator.models import Question


class BaseGenerator(ABC):
    topic: str

    @abstractmethod
    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        """Generate one question."""

