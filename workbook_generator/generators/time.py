from __future__ import annotations

import random

from workbook_generator.generators.base import BaseGenerator
from workbook_generator.models import Question


class TimeGenerator(BaseGenerator):
    topic = "time"

    def generate_one(self, rng: random.Random, difficulty: int) -> Question:
        start_hour = rng.randint(7, 18)
        start_minute = rng.choice([0, 5, 10, 15, 20, 30, 45])
        duration = rng.choice([25, 35, 45, 50, 65, 75, 90, 105])
        total = start_hour * 60 + start_minute + duration
        end_hour = (total // 60) % 24
        end_minute = total % 60
        prompt = f"A lesson starts at {start_hour:02d}:{start_minute:02d} and lasts {duration} minutes. What time does it finish?"
        return Question(
            prompt=prompt,
            answer=f"{end_hour:02d}:{end_minute:02d}",
            topic=self.topic,
            subtopic="elapsed_time",
            difficulty=difficulty,
            tags=("time",),
        )

