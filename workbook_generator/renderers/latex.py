from __future__ import annotations

import re
from textwrap import dedent

from workbook_generator.models import Question, Worksheet


class LatexRenderer:
    def __init__(
        self,
        columns: int = 2,
        answer_columns: int = 3,
        show_multiple_choice: bool = True,
    ) -> None:
        self.columns = columns
        self.answer_columns = answer_columns
        self.show_multiple_choice = show_multiple_choice

    def render(self, worksheet: Worksheet) -> str:
        question_rows = "\n".join(
            rf"            \item {self._format_question_text(question.prompt, question.meta)}"
            for question in worksheet.questions
        )
        answer_rows = "\n".join(
            rf"            \item {self._format_answer_text(question)}"
            for question in worksheet.questions
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

            \begin{{multicols}}{{{self.answer_columns}}}
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

    def _format_question_text(self, value: str, meta: dict) -> str:
        parsed = self._parse_multiple_choice(value)
        if parsed:
            stem, options = parsed
            if meta.get("source"):
                stem = self._format_plain_text_with_fractions(stem)
                options = [
                    (label, self._format_plain_text_with_fractions(option_text))
                    for label, option_text in options
                ]
            if not self.show_multiple_choice:
                return rf"{stem}"
            option_rows = "\n".join(
                rf"                \item {option_text}"
                for _, option_text in options
            )
            return (
                rf"{stem}"
                "\n"
                r"            \begin{enumerate}[label=\Alph*., itemsep=0.15em, topsep=0.3em, leftmargin=1.7em]"
                "\n"
                f"{option_rows}"
                "\n"
                r"            \end{enumerate}"
            )

        if meta.get("source"):
            return self._format_plain_text_with_fractions(value)
        return value

    def _format_answer_text(self, question: Question) -> str:
        answer = question.answer
        if not self.show_multiple_choice:
            parsed = self._parse_multiple_choice(question.prompt)
            match = re.match(r"^([A-E])\.?\s*(.*)$", answer)
            if parsed and match:
                _, options = parsed
                answer_label, answer_text = match.groups()
                matching_option = next(
                    (option_text for label, option_text in options if label == answer_label),
                    None,
                )
                answer = answer_text or matching_option or answer

        if question.meta.get("source"):
            return self._format_plain_text_with_fractions(answer)
        return answer

    @classmethod
    def _format_plain_text_with_fractions(cls, value: str) -> str:
        result: list[str] = []
        cursor = 0
        pattern = re.compile(r"(?<![\w/])(?:(\d+)\s+)?(\d+)/(\d+)(?![\w/])")

        for match in pattern.finditer(value):
            result.append(cls._escape_plain_text(value[cursor : match.start()]))
            whole, numerator, denominator = match.groups()
            if whole:
                result.append(rf"\({whole}\frac{{{numerator}}}{{{denominator}}}\)")
            else:
                result.append(rf"\(\frac{{{numerator}}}{{{denominator}}}\)")
            cursor = match.end()

        result.append(cls._escape_plain_text(value[cursor:]))
        return "".join(result)

    @classmethod
    def _parse_multiple_choice(cls, value: str) -> tuple[str, list[tuple[str, str]]] | None:
        stem_end = value.rfind("?")
        if stem_end == -1:
            return None

        stem = value[: stem_end + 1].strip()
        choices_text = value[stem_end + 1 :].strip()
        if not stem or not choices_text:
            return None

        matches = []
        index = 0
        while index < len(choices_text):
            if (
                (index == 0 or choices_text[index - 1].isspace())
                and choices_text[index : index + 1] in "ABCDE"
            ):
                label = choices_text[index]
                cursor = index + 1
                if cursor < len(choices_text) and choices_text[cursor] == ".":
                    cursor += 1
                if cursor < len(choices_text) and choices_text[cursor].isspace():
                    while cursor < len(choices_text) and choices_text[cursor].isspace():
                        cursor += 1
                    matches.append((label, index, cursor))
                    index = cursor
                    continue
            index += 1

        if len(matches) < 2 or matches[0][0] != "A":
            return None

        options = []
        for option_index, (label, _, value_start) in enumerate(matches):
            value_end = matches[option_index + 1][1] if option_index + 1 < len(matches) else len(choices_text)
            option_text = choices_text[value_start:value_end].strip()
            options.append((label, option_text))

        labels = {label for label, _ in options}
        if not {"B", "C"}.issubset(labels) or any(not option_text for _, option_text in options):
            return None

        return stem, sorted(options, key=lambda option: option[0])

    @staticmethod
    def _escape_plain_text(value: str) -> str:
        result: list[str] = []
        special_chars = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
        }
        index = 0
        while index < len(value):
            char = value[index]
            if char == "\\" and index + 1 < len(value) and value[index + 1] in special_chars:
                result.append(char)
                result.append(value[index + 1])
                index += 2
                continue
            result.append(special_chars.get(char, char))
            index += 1
        return "".join(result)
