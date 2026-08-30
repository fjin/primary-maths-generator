#!/usr/bin/env python3
"""Local static server with a CLI-style PDF generation endpoint."""

from __future__ import annotations

import json
import tempfile
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from generate import compile_pdf, format_difficulty
from workbook_generator.engine import GeneratorRegistry, WorksheetBuilder
from workbook_generator.recipe import Recipe
from workbook_generator.renderers.latex import LatexRenderer


ROOT = Path(__file__).resolve().parent
DIFFICULTY_FROM_WEB = {
    "1": "year3",
    "2": "year4",
    "3": "year5",
    "4": "year6",
    "5": "selective",
}


class WorksheetRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self) -> None:
        if unquote(self.path) != "/api/generate":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            pdf_bytes, filename = build_pdf(payload)
        except Exception as error:
            body = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(pdf_bytes)))
        self.end_headers()
        self.wfile.write(pdf_bytes)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))


def build_pdf(payload: dict) -> tuple[bytes, str]:
    topic = str(payload.get("topic") or "mixed")
    subtopic = str(payload.get("subtopic") or "all")
    difficulty = DIFFICULTY_FROM_WEB.get(str(payload.get("difficulty")), str(payload.get("difficulty") or "year5"))
    questions = max(1, min(250, int(payload.get("questions") or 40)))
    columns = max(1, min(3, int(payload.get("columns") or 2)))
    answer_columns = max(1, min(4, int(payload.get("answerColumns") or 3)))
    seed = int(payload.get("seed") or 42)
    title = str(payload.get("title") or f"{format_difficulty(difficulty)} {topic.title()}").strip()
    subtopics = None if subtopic == "all" else [subtopic]

    with tempfile.TemporaryDirectory(prefix="maths_pdf_") as output_dir:
        recipe = Recipe(
            title=title,
            questions=questions,
            difficulty=difficulty,
            seed=seed,
            columns=columns,
            topics=[topic],
            output_dir=Path(output_dir),
            subtopics=subtopics,
        )
        worksheet = WorksheetBuilder(GeneratorRegistry.default()).build(recipe)
        tex = LatexRenderer(columns=recipe.columns, answer_columns=answer_columns).render(worksheet)
        tex_path = recipe.output_dir / f"{worksheet.slug}.tex"
        tex_path.write_text(tex, encoding="utf-8")
        pdf_path = compile_pdf(tex_path)
        if pdf_path is None:
            raise RuntimeError("pdflatex is not installed, so the CLI-style PDF cannot be generated.")
        return pdf_path.read_bytes(), f"{worksheet.slug}.pdf"


def main() -> int:
    server = ThreadingHTTPServer(("localhost", 8000), WorksheetRequestHandler)
    print("Serving http://localhost:8000/")
    print("CLI-style PDF endpoint: http://localhost:8000/api/generate")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
