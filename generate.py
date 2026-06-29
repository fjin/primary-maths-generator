#!/usr/bin/env python3
"""CLI entry point for generating printable maths worksheets."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from workbook_generator.engine import GeneratorRegistry, WorksheetBuilder
from workbook_generator.recipe import Recipe, load_recipe
from workbook_generator.renderers.latex import LatexRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate mathematics worksheets as LaTeX and optional PDF files."
    )
    parser.add_argument(
        "recipe",
        nargs="?",
        help="Optional YAML recipe file. When supplied it overrides CLI worksheet settings.",
    )
    parser.add_argument("--topic", default="mixed", help="Topic to generate, or 'mixed'.")
    parser.add_argument("--questions", type=int, default=50, help="Number of questions.")
    parser.add_argument("--difficulty", default="year5", help="Difficulty level.")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed.")
    parser.add_argument("--title", default=None, help="Worksheet title.")
    parser.add_argument("--columns", type=int, default=2, choices=[1, 2, 3])
    parser.add_argument("--output-dir", default="output")
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Only write .tex, even when pdflatex is available.",
    )
    return parser.parse_args()


def compile_pdf(tex_path: Path) -> Path | None:
    if shutil.which("pdflatex") is None:
        return None

    subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ],
        cwd=tex_path.parent,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return tex_path.with_suffix(".pdf")


def recipe_from_args(args: argparse.Namespace) -> Recipe:
    if args.recipe:
        return load_recipe(Path(args.recipe))

    return Recipe(
        title=args.title or f"{format_difficulty(args.difficulty)} {args.topic.title()}",
        questions=args.questions,
        difficulty=args.difficulty,
        seed=args.seed,
        columns=args.columns,
        topics=[args.topic],
        output_dir=Path(args.output_dir),
    )


def format_difficulty(value: str) -> str:
    if value.lower().startswith("year") and value[4:].isdigit():
        return f"Year {value[4:]}"
    return value.upper() if value.lower() in {"naplan", "oc", "icas"} else value.title()


def main() -> int:
    args = parse_args()
    recipe = recipe_from_args(args)

    registry = GeneratorRegistry.default()
    worksheet = WorksheetBuilder(registry).build(recipe)
    tex = LatexRenderer(columns=recipe.columns).render(worksheet)

    recipe.output_dir.mkdir(parents=True, exist_ok=True)
    tex_path = recipe.output_dir / f"{worksheet.slug}.tex"
    tex_path.write_text(tex, encoding="utf-8")

    pdf_path = None if args.no_pdf else compile_pdf(tex_path)

    print(f"Wrote {tex_path}")
    if pdf_path:
        print(f"Wrote {pdf_path}")
    else:
        print("Skipped PDF compilation; install pdflatex or omit --no-pdf to enable it.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
