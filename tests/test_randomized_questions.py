import random
import re
import unittest

from workbook_generator.engine import GeneratorRegistry, WorksheetBuilder
from workbook_generator.question_bank import QuestionBank
from workbook_generator.recipe import Recipe


class RandomizedQuestionTests(unittest.TestCase):
    def test_templates_only_excludes_fixed_questions(self):
        bank = QuestionBank(templates_only=True)
        for seed in range(40):
            question = bank.generate_one("word_problems", 1, random.Random(seed))
            self.assertEqual(question.meta["source"], "template")

    def test_speed_worksheet_is_unique_and_reproducible(self):
        recipe = Recipe(
            title="Randomised Speed", questions=100, difficulty="year3",
            seed=777, columns=2, topics=["word_problems"],
            subtopics=["speed_distance_time"],
        )
        builder = WorksheetBuilder(GeneratorRegistry.default(randomized=True))
        first = builder.build(recipe)
        second = builder.build(recipe)
        self.assertEqual(first.questions, second.questions)
        self.assertEqual(len({q.prompt for q in first.questions}), 100)
        self.assertNotEqual(first.questions[0].prompt, first.questions[1].prompt)

    def test_percentage_transfer_answers_match_both_final_balances(self):
        bank = QuestionBank(templates_only=True)
        template = next(
            t for t in bank._templates
            if t["subtopic"] == "percentages" and t["difficulty"] == 4
            and "transfer" in t.get("derived", {})
        )
        # Use the main wording so the quantities can be checked independently.
        template = {k: v for k, v in template.items() if k != "question_forms"}
        for seed in range(100):
            question = bank._instantiate_template(template, random.Random(seed))
            base, percent, transfer = map(int, re.findall(r"\d+", question.prompt))
            first_after = base + transfer
            second_after = base * (100 + percent) // 100 - transfer
            self.assertGreaterEqual(second_after, 0)
            self.assertGreater(first_after, second_after)
            self.assertEqual(int(question.answer.split()[0]), first_after - second_after)

    def test_wording_forms_change_without_changing_quantities(self):
        bank = QuestionBank(templates_only=True)
        template = next(t for t in bank._templates if t.get("question_forms")
                        and t["subtopic"] == "speed_distance_time")
        template = {
            **template,
            "variables": {"name": {"choices": ["Mia"]},
                          "speed": {"choices": [30]}, "minutes": {"choices": [7]}},
        }
        questions = [bank._instantiate_template(template, random.Random(seed))
                     for seed in range(20)]
        self.assertEqual(len({q.prompt for q in questions}), 2)
        self.assertEqual({q.answer for q in questions}, {"210 metres"})


if __name__ == "__main__":
    unittest.main()
