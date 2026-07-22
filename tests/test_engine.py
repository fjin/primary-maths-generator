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

    def test_ratio_template_uses_derived_values(self) -> None:
        template_path = Path(__file__).parent / "tmp_ratio_templates.json"
        template_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "subtopic": "ratios",
                        "difficulty": 3,
                        "question": "{person_a} and {person_b} share {total} candies in the ratio {ratio_a}:{ratio_b}.",
                        "answer_format": "{person_a}: {share_a}, {person_b}: {share_b}",
                        "variables": {
                            "person_a": {"choices": ["Tom"]},
                            "person_b": {"choices": ["you"]},
                            "ratio_a": {"choices": [6]},
                            "ratio_b": {"choices": [4]},
                            "unit": {"choices": [1]},
                        },
                        "derived": {
                            "total": "unit * (ratio_a + ratio_b)",
                            "share_a": "unit * ratio_a",
                            "share_b": "unit * ratio_b",
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
        self.assertEqual(
            question.prompt,
            "Tom and you share 10 candies in the ratio 6:4.",
        )
        self.assertEqual(question.answer, "Tom: 6, you: 4")

    def test_ratio_template_can_find_total_from_one_share(self) -> None:
        template_path = Path(__file__).parent / "tmp_ratio_total_templates.json"
        template_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "subtopic": "ratios",
                        "difficulty": 3,
                        "question": "{person_a} and {person_b} have candies in the ratio {ratio_a}:{ratio_b}. {person_a} has {share_a} candies. How many candies do they have altogether?",
                        "answer_format": "{total}",
                        "variables": {
                            "person_a": {"choices": ["Tom"]},
                            "person_b": {"choices": ["you"]},
                            "ratio_a": {"choices": [1]},
                            "ratio_b": {"choices": [3]},
                            "unit": {"choices": [5]},
                        },
                        "derived": {
                            "share_a": "unit * ratio_a",
                            "share_b": "unit * ratio_b",
                            "total": "share_a + share_b",
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
        self.assertEqual(
            question.prompt,
            "Tom and you have candies in the ratio 1:3. Tom has 5 candies. How many candies do they have altogether?",
        )
        self.assertEqual(question.answer, "20")

    def test_template_choice_sets_supply_matched_values(self) -> None:
        template_path = Path(__file__).parent / "tmp_choice_set_templates.json"
        template_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "subtopic": "ratios",
                        "difficulty": 1,
                        "question": "The ratio is {ratio_a}:{ratio_b}.",
                        "answer_format": "{ratio_a} to {ratio_b}",
                        "choice_sets": [
                            {"ratio_a": 3, "ratio_b": 4},
                        ],
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
            question = bank.generate_one("word_problems", 1, __import__("random").Random(1))
        finally:
            template_path.unlink()

        self.assertIsNotNone(question)
        assert question is not None
        self.assertEqual(question.prompt, "The ratio is 3:4.")
        self.assertEqual(question.answer, "3 to 4")

    def test_one_unknown_template_solves_equation(self) -> None:
        template_path = Path(__file__).parent / "tmp_one_unknown_templates.json"
        template_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "subtopic": "one_unknown_equations",
                        "difficulty": 3,
                        "question": "Solve for a: {constant} + {coefficient}a = {total}.",
                        "answer_format": "a = {unknown}",
                        "variables": {
                            "unknown": {"choices": [16]},
                            "coefficient": {"choices": [5]},
                            "constant": {"choices": [20]},
                        },
                        "derived": {"total": "constant + coefficient * unknown"},
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
        self.assertEqual(question.prompt, "Solve for a: 20 + 5a = 100.")
        self.assertEqual(question.answer, "a = 16")

    def test_two_unknown_template_solves_ratio_sum(self) -> None:
        template_path = Path(__file__).parent / "tmp_two_unknown_templates.json"
        template_path.write_text(
            json.dumps(
                [
                    {
                        "topic": "word_problems",
                        "subtopic": "two_unknowns",
                        "difficulty": 3,
                        "question": "The ratio of a to b is {ratio_a}:{ratio_b}. If a + b = {total}, find a and b.",
                        "answer_format": "a = {a_value}, b = {b_value}",
                        "variables": {
                            "ratio_a": {"choices": [2]},
                            "ratio_b": {"choices": [3]},
                            "unit": {"choices": [2]},
                        },
                        "derived": {
                            "a_value": "unit * ratio_a",
                            "b_value": "unit * ratio_b",
                            "total": "a_value + b_value",
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
        self.assertEqual(question.prompt, "The ratio of a to b is 2:3. If a + b = 10, find a and b.")
        self.assertEqual(question.answer, "a = 4, b = 6")

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
