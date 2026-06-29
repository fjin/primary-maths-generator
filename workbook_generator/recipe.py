from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on minimal installs
    yaml = None


@dataclass(frozen=True)
class Recipe:
    title: str
    questions: int
    difficulty: str
    seed: int
    columns: int
    topics: list[str]
    output_dir: Path = Path("output")
    mix: dict[str, int] | None = None


def load_recipe(path: Path) -> Recipe:
    if yaml is None:
        raise RuntimeError(
            "YAML recipes require PyYAML. Install dependencies with: pip install -r requirements.txt"
        )

    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    layout = data.get("layout", {})
    topics = data.get("topics", ["mixed"])
    mix = data.get("mix")

    if isinstance(topics, str):
        topics = [topics]

    return Recipe(
        title=data.get("title", path.stem.replace("-", " ").title()),
        questions=int(data.get("questions", 50)),
        difficulty=data.get("difficulty", "year5"),
        seed=int(data.get("seed", 42)),
        columns=int(layout.get("columns", data.get("columns", 2))),
        topics=list(topics),
        output_dir=Path(data.get("output_dir", "output")),
        mix=mix,
    )
