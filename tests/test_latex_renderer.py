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

    def test_latex_renderer_formats_multiple_choice_questions(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt="Which number is closest to 6,500? A. 6,049 B. 6,481 C. 6,725 D. 6,951",
                    answer="B. 6,481",
                    topic="number_system",
                    subtopic="place_value",
                    difficulty=3,
                    meta={"source": "question_bank"},
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer().render(worksheet)

        self.assertIn("Which number is closest to 6,500?", latex)
        self.assertIn(r"\begin{enumerate}[label=\Alph*.", latex)
        self.assertIn(r"\item 6,049", latex)
        self.assertIn(r"\item 6,481", latex)
        self.assertIn(r"\item 6,725", latex)
        self.assertIn(r"\item 6,951", latex)
        self.assertNotIn("A. 6,049 B. 6,481", latex)

    def test_latex_renderer_does_not_format_plain_question_mentions_of_options(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt="Bus A has 18 students and Bus B has 23 students. Which bus has more students?",
                    answer="Bus B",
                    topic="word_problems",
                    subtopic="comparison",
                    difficulty=3,
                    meta={"source": "question_bank"},
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer().render(worksheet)

        self.assertIn("Bus A has 18 students", latex)
        self.assertNotIn(r"\begin{enumerate}[label=\Alph*.", latex)

    def test_latex_renderer_formats_plain_text_fractions(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt=(
                        "Chef Alfredo's Restaurant had a supply of 12 litres of mustard sauce. "
                        "They wanted to use all the mustard sauce for five days, using the same amount each day. "
                        "How much should they use each day? A 2 1/5 litres D 2 4/5 litres "
                        "B 2 2/5 litres E 3 litres C 2 3/5 litres"
                    ),
                    answer="B. 2 2/5 litres",
                    topic="fractions",
                    subtopic="word_problems",
                    difficulty=3,
                    meta={"source": "question_bank"},
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer().render(worksheet)

        self.assertIn(r"\item \(2\frac{1}{5}\) litres", latex)
        self.assertIn(r"\item \(2\frac{2}{5}\) litres", latex)
        self.assertIn(r"\item \(2\frac{3}{5}\) litres", latex)
        self.assertIn(r"\item \(2\frac{4}{5}\) litres", latex)
        self.assertIn(r"\item B. \(2\frac{2}{5}\) litres", latex)
        self.assertNotIn("2 1/5 litres", latex)

    def test_latex_renderer_can_hide_multiple_choice_options(self) -> None:
        worksheet = Worksheet(
            title="Sample",
            slug="sample",
            questions=[
                Question(
                    prompt="Which number is closest to 6,500? A. 6,049 B. 6,481 C. 6,725 D. 6,951",
                    answer="B. 6,481",
                    topic="number_system",
                    subtopic="place_value",
                    difficulty=3,
                    meta={"source": "question_bank"},
                )
            ],
            seed=42,
            difficulty="year5",
        )

        latex = LatexRenderer(show_multiple_choice=False).render(worksheet)

        self.assertIn(r"\item Which number is closest to 6,500?", latex)
        self.assertIn(r"\item 6,481", latex)
        self.assertNotIn(r"\begin{enumerate}[label=\Alph*.", latex)
        self.assertNotIn("A. 6,049", latex)


if __name__ == "__main__":
    unittest.main()
