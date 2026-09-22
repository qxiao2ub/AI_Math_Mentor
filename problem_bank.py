from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DATA_PATH = Path(__file__).resolve().parent / "data" / "problem_bank.json"


def load_problem_bank() -> List[Dict[str, Any]]:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def stage_key(stage_label: str) -> str:
    lower = stage_label.lower()
    if "litsey" in lower or "лицей" in lower or "lyceum" in lower:
        return "lyceum"
    if "univers" in lower or "универс" in lower:
        return "university"
    return "school"


def filter_problems(
    problems: List[Dict[str, Any]],
    stage: str,
    grade: int,
    topic: str | None = None,
) -> List[Dict[str, Any]]:
    selected = [
        p for p in problems
        if p["stage"] == stage
        and int(p["grade_min"]) <= int(grade) <= int(p["grade_max"])
    ]
    if topic and topic != "All":
        selected = [p for p in selected if p["topic"] == topic]
    return selected
