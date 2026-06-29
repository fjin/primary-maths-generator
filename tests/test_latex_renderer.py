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


if __name__ == "__main__":
    unittest.main()
