from __future__ import annotations

from textwrap import dedent

from workbook_generator.models import Worksheet


class LatexRenderer:
    def __init__(self, columns: int = 2) -> None:
        self.columns = columns

    def render(self, worksheet: Worksheet) -> str:
        question_rows = "\n".join(
            rf"            \item {question.prompt}" for question in worksheet.questions
        )
        answer_rows = "\n".join(
            rf"            \item {question.answer}" for question in worksheet.questions
        )

        return dedent(
            rf"""
            \documentclass[11pt,a4paper]{{article}}
            \usepackage[margin=1.5cm]{{geometry}}
            \usepackage{{amsmath}}
            \usepackage{{multicol}}
            \usepackage{{enumitem}}
            \setlength{{\parindent}}{{0pt}}
            \setlist[enumerate]{{itemsep=0.7em, topsep=0.5em}}

            \begin{{document}}

            \begin{{center}}
            {{\LARGE \textbf{{{self._escape(worksheet.title)}}}}}\\[0.5em]
            Difficulty: {self._escape(worksheet.difficulty)} \quad Seed: {worksheet.seed}
            \end{{center}}

            \begin{{multicols}}{{{self.columns}}}
            \begin{{enumerate}}
{question_rows}
            \end{{enumerate}}
            \end{{multicols}}

            \newpage
            \begin{{center}}
            {{\Large \textbf{{Answer Key}}}}
            \end{{center}}

            \begin{{multicols}}{{{self.columns}}}
            \begin{{enumerate}}
{answer_rows}
            \end{{enumerate}}
            \end{{multicols}}

            \end{{document}}
            """
        ).strip() + "\n"

    @staticmethod
    def _escape(value: str) -> str:
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
        }
        for char, replacement in replacements.items():
            value = value.replace(char, replacement)
        return value
