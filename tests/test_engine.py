from workbook_generator.engine import GeneratorRegistry, WorksheetBuilder
from workbook_generator.generators.word_problems import WordProblemGenerator
from workbook_generator.question_bank import QuestionBank
from workbook_generator.recipe import Recipe
from pathlib import Path
import json
import unittest


class EngineTests(unittest.TestCase):
    def test_build_is_deterministic(self) -> None:
        recipe = Recipe(
            title="Year 5 Fractions",
            questions=10,
            difficulty="year5",
            seed=7,
            columns=2,
            topics=["fractions"],
        )
        builder = WorksheetBuilder(GeneratorRegistry.default())

        first = builder.build(recipe)
        second = builder.build(recipe)

        self.assertEqual(
            [question.prompt for question in first.questions],
            [question.prompt for question in second.questions],
        )
        self.assertEqual(len(first.questions), 10)

    def test_mixed_topic_expands(self) -> None:
        recipe = Recipe(
            title="Mixed",
            questions=16,
            difficulty="year5",
            seed=1,
            columns=2,
            topics=["mixed"],
        )
        worksheet = WorksheetBuilder(GeneratorRegistry.default()).build(recipe)

        self.assertGreater(len({question.topic for question in worksheet.questions}), 3)

    def test_worksheet_builder_avoids_duplicate_prompts(self) -> None:
        recipe = Recipe(
            title="Year 6 Word Problems",
            questions=20,
            difficulty="year6",
            seed=606,
            columns=2,
            topics=["word_problems"],
        )
        worksheet = WorksheetBuilder(GeneratorRegistry.default()).build(recipe)
        prompts = [question.prompt for question in worksheet.questions]

        self.assertEqual(len(prompts), len(set(prompts)))

    def test_word_problem_generator_uses_question_bank(self) -> None:
        question = WordProblemGenerator().generate_one(__import__("random").Random(1), 3)

        self.assertEqual(question.topic, "word_problems")
        self.assertIn(question.meta.get("source"), {"imported", "template"})

    def test_question_template_updates_answer(self) -> None:
        template_path = Path(__file__).parent / "tmp_question_templates.json"
        template_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "subtopic": "addition_subtraction",
                        "difficulty": 3,
                        "question": "{start} books, {borrowed} borrowed, {returned} returned.",
                        "answer_formula": "start - borrowed + returned",
                        "variables": {
                            "start": {"choices": [350]},
                            "borrowed": {"choices": [200]},
                            "returned": {"choices": [100]},
                        },
                        "source": "template",
                    }
                ]
            )
        )
        try:
            bank = QuestionBank(
                path=Path(__file__).parent / "missing_question_bank.json",
                template_path=template_path,
            )
            question = bank.generate_one("word_problems", 3, __import__("random").Random(1))
        finally:
            template_path.unlink()

        self.assertIsNotNone(question)
        assert question is not None
        self.assertEqual(question.prompt, "350 books, 200 borrowed, 100 returned.")
        self.assertEqual(question.answer, "250")

    def test_question_bank_prefers_exact_difficulty(self) -> None:
        bank_path = Path(__file__).parent / "tmp_question_bank.json"
        bank_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "difficulty": 2,
                        "question": "Easy question",
                        "answer": "easy",
                    },
                    {
                        "topic": "word_problems",
                        "difficulty": 4,
                        "question": "Hard question",
                        "answer": "hard",
                    },
                ]
            )
        )
        try:
            bank = QuestionBank(
                path=bank_path,
                template_path=Path(__file__).parent / "missing_templates.json",
            )
            question = bank.generate_one("word_problems", 4, __import__("random").Random(1))
        finally:
            bank_path.unlink()

        self.assertIsNotNone(question)
        assert question is not None
        self.assertEqual(question.prompt, "Hard question")


if __name__ == "__main__":
    unittest.main()
