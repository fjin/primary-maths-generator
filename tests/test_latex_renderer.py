from workbook_generator.models import Question, Worksheet
from workbook_generator.renderers.latex import LatexRenderer
import unittest


class LatexRendererTests(unittest.TestCase):
    def test_latex_renderer_includes_questions_and_answers(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt=r"$1+1=$",
                    answer=r"$2$",
                    topic="number",
                    subtopic="addition",
                    difficulty=1,
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer().render(worksheet)

        self.assertIn(r"\documentclass", latex)
        self.assertIn(r"\item $1+1=$", latex)
        self.assertIn(r"\item $2$", latex)

    def test_answer_key_defaults_to_three_columns(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt=r"$1+1=$",
                    answer=r"$2$",
                    topic="number",
                    subtopic="addition",
                    difficulty=1,
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer(columns=2).render(worksheet)

        self.assertIn(r"\begin{multicols}{2}", latex)
        self.assertIn(r"\begin{multicols}{3}", latex)

    def test_latex_renderer_escapes_plain_text_bank_questions(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt="Complete the pattern: 1, 2, 3, _____, _____. Save 25% of $40.",
                    answer="$10_00",
                    topic="number_system",
                    subtopic="patterns",
                    difficulty=1,
                    meta={"source": "question_bank"},
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer().render(worksheet)

        self.assertIn(r"\_\_\_\_\_", latex)
        self.assertIn(r"25\%", latex)
        self.assertIn(r"\$40", latex)
        self.assertIn(r"\$10\_00", latex)


if __name__ == "__main__":
    unittest.main()
