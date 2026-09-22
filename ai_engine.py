from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import sympy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline


ERROR_LABELS = [
    "correct",
    "calculation_error",
    "sign_error",
    "algebra_transformation_error",
    "concept_gap",
    "incomplete_step",
    "formatting_error",
]

LABEL_TEXT = {
    "uz": {
        "correct": "to‘g‘ri",
        "calculation_error": "hisoblash xatosi",
        "sign_error": "ishora xatosi",
        "algebra_transformation_error": "algebraik o‘zgartirish xatosi",
        "concept_gap": "tushuncha yetishmasligi",
        "incomplete_step": "to‘liq bo‘lmagan qadam",
        "formatting_error": "yozuv/parsing xatosi",
    },
    "ru": {
        "correct": "верно",
        "calculation_error": "вычислительная ошибка",
        "sign_error": "ошибка знака",
        "algebra_transformation_error": "ошибка алгебраического преобразования",
        "concept_gap": "пробел в понимании",
        "incomplete_step": "неполный шаг",
        "formatting_error": "ошибка записи/разбора",
    },
    "en": {
        "correct": "correct",
        "calculation_error": "calculation error",
        "sign_error": "sign error",
        "algebra_transformation_error": "algebraic transformation error",
        "concept_gap": "concept gap",
        "incomplete_step": "incomplete step",
        "formatting_error": "formatting/parsing error",
    },
}

FEEDBACK = {
    "uz": {
        "correct": "Bu qadam matematik jihatdan to‘g‘ri.",
        "calculation_error": "Amallarni qayta hisoblang; sonli natijada xato bor.",
        "sign_error": "Musbat va manfiy ishoralarni tekshiring, ayniqsa hadni tenglamaning boshqa tomoniga o‘tkazganda.",
        "algebra_transformation_error": "Bu o‘zgartirish oldingi tenglamaga teng kuchli emas. Bir xil amalni tenglamaning ikkala tomoniga qo‘llang.",
        "concept_gap": "Ushbu qadam uchun kerakli qoida yoki formula to‘liq qo‘llanmagan.",
        "incomplete_step": "Qadam yo‘nalishi to‘g‘ri bo‘lishi mumkin, lekin natijani tugating yoki tenglikni aniq yozing.",
        "formatting_error": "Qadamni faqat matematik yozuvda kiriting, masalan `3*x+5=20` yoki `x=5`.",
    },
    "ru": {
        "correct": "Этот шаг математически верен.",
        "calculation_error": "Пересчитайте арифметику: числовой результат неверен.",
        "sign_error": "Проверьте знаки, особенно при переносе слагаемого в другую часть уравнения.",
        "algebra_transformation_error": "Преобразование не равносильно предыдущему. Выполняйте одну и ту же операцию с обеими частями.",
        "concept_gap": "Нужное правило или формула применены не полностью.",
        "incomplete_step": "Направление может быть верным, но завершите вычисление или запишите равенство точнее.",
        "formatting_error": "Введите математическую запись, например `3*x+5=20` или `x=5`.",
    },
    "en": {
        "correct": "This step is mathematically valid.",
        "calculation_error": "Recalculate the arithmetic; the numerical result is incorrect.",
        "sign_error": "Check positive and negative signs, especially when moving a term across an equation.",
        "algebra_transformation_error": "This transformation is not equivalent to the prior equation. Apply the same operation to both sides.",
        "concept_gap": "The required rule or formula has not been fully applied.",
        "incomplete_step": "The direction may be reasonable, but finish the calculation or write the equality more precisely.",
        "formatting_error": "Enter mathematical notation such as `3*x+5=20` or `x=5`.",
    },
}

STYLE_PREFIX = {
    "socratic": {
        "uz": "Savol: oldingi qadamdan bu natijaga kelish uchun qaysi amal tenglamaning ikkala tomoniga qo‘llanishi kerak? ",
        "ru": "Вопрос: какую операцию нужно применить к обеим частям, чтобы получить этот шаг? ",
        "en": "Question: what operation must be applied to both sides to reach this step? ",
    },
    "concise": {"uz": "Qisqa maslahat: ", "ru": "Краткая подсказка: ", "en": "Concise hint: "},
    "worked": {"uz": "Namuna yo‘li: ", "ru": "Пример хода решения: ", "en": "Worked-path cue: "},
}


@dataclass
class StepResult:
    index: int
    student_step: str
    is_correct: bool
    status: str
    diagnosis: str
    expected_step: str
    feedback: str
    confidence: float

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _normalize(text: str) -> str:
    text = str(text).strip()
    replacements = {
        "−": "-", "–": "-", "×": "*", "·": "*", "÷": "/",
        "^": "**", "π": "pi", "√": "sqrt",
        "’": "'", "′": "'", ",": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", "", text)
    return text


@lru_cache(maxsize=4096)
def _local_dict() -> Dict[str, Any]:
    symbols = {name: sp.Symbol(name) for name in [
        "x", "y", "z", "a", "b", "c", "C", "n", "d", "a1", "a10", "an", "t"
    ]}
    return {
        **symbols,
        "pi": sp.pi,
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "log": sp.log,
        "exp": sp.exp,
        "abs": sp.Abs,
    }


def parse_math(text: str) -> Tuple[str, Any]:
    cleaned = _normalize(text)
    if not cleaned:
        raise ValueError("Empty step")
    if cleaned.count("=") > 1:
        raise ValueError("Use one equality per line")
    local = _local_dict()
    if "=" in cleaned:
        left, right = cleaned.split("=", 1)
        if not left or not right:
            raise ValueError("Incomplete equality")
        lhs = sp.sympify(left, locals=local)
        rhs = sp.sympify(right, locals=local)
        return "equation", (lhs, rhs)
    return "expression", sp.sympify(cleaned, locals=local)


def _is_zero(expr: Any) -> bool:
    try:
        simplified = sp.simplify(expr)
        if simplified == 0:
            return True
        equals = simplified.equals(0)
        return bool(equals)
    except Exception:
        return False


def mathematically_equivalent(a: str, b: str) -> bool:
    try:
        kind_a, obj_a = parse_math(a)
        kind_b, obj_b = parse_math(b)
    except Exception:
        return False

    if kind_a == "expression" and kind_b == "expression":
        return _is_zero(obj_a - obj_b)

    if kind_a == "equation" and kind_b == "equation":
        ra = sp.expand(obj_a[0] - obj_a[1])
        rb = sp.expand(obj_b[0] - obj_b[1])
        if _is_zero(ra) and _is_zero(rb):
            return True
        if _is_zero(ra - rb) or _is_zero(ra + rb):
            return True
        try:
            ratio = sp.simplify(ra / rb)
            return bool(ratio != 0 and not ratio.free_symbols)
        except Exception:
            return False

    # Accept an equation like x=5 against the expression 5 only when the
    # equation's right side is the expression and the left side is a symbol.
    if kind_a == "equation" and kind_b == "expression":
        lhs, rhs = obj_a
        return bool(lhs.is_Symbol and _is_zero(rhs - obj_b))
    if kind_b == "equation" and kind_a == "expression":
        lhs, rhs = obj_b
        return bool(lhs.is_Symbol and _is_zero(rhs - obj_a))
    return False


TRAINING_ROWS = [
    ("3+4=8 arithmetic number wrong", "calculation_error"),
    ("12/3=5 numerical operation incorrect", "calculation_error"),
    ("15 percent of 200 equals 20", "calculation_error"),
    ("x-4=10 becomes x=6 wrong sign", "sign_error"),
    ("-3*x=9 becomes x=3 sign", "sign_error"),
    ("negative changes to positive", "sign_error"),
    ("divide only one side of equation", "algebra_transformation_error"),
    ("3*x=12 becomes x=6 invalid algebra", "algebra_transformation_error"),
    ("squared equation transformed incorrectly", "algebra_transformation_error"),
    ("uses perimeter formula for area", "concept_gap"),
    ("probability denominator omits outcomes", "concept_gap"),
    ("derivative rule missing", "concept_gap"),
    ("3*x= incomplete", "incomplete_step"),
    ("answer stops before simplification", "incomplete_step"),
    ("only writes formula without substitution", "incomplete_step"),
    ("three x plus five equals words", "formatting_error"),
    ("unbalanced parenthesis", "formatting_error"),
    ("multiple equals signs malformed", "formatting_error"),
] * 4


@lru_cache(maxsize=1)
def train_error_models() -> Tuple[Pipeline, Tuple[TfidfVectorizer, MLPClassifier]]:
    texts = [r[0] for r in TRAINING_ROWS]
    labels = [r[1] for r in TRAINING_ROWS]
    linear = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), analyzer="word")),
        ("model", LogisticRegression(max_iter=500, random_state=42)),
    ])
    linear.fit(texts, labels)

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=256)
    dense = vectorizer.fit_transform(texts).toarray()
    mlp = MLPClassifier(
        hidden_layer_sizes=(24, 12),
        solver="lbfgs",
        max_iter=500,
        random_state=42,
    )
    mlp.fit(dense, labels)
    return linear, (vectorizer, mlp)


def _numeric_only(text: str) -> bool:
    return not bool(re.search(r"[a-zA-Z]", _normalize(text)))


def _rule_diagnosis(student: str, expected: str) -> Optional[str]:
    s = _normalize(student)
    e = _normalize(expected)
    if s.count("(") != s.count(")") or s.count("=") > 1:
        return "formatting_error"
    if s.endswith("=") or not s:
        return "incomplete_step"
    if _numeric_only(s) and _numeric_only(e):
        return "calculation_error"
    if s.replace("-", "") == e.replace("-", "") and s != e:
        return "sign_error"
    expected_vars = set(re.findall(r"[a-zA-Z]+\d*", e)) - {"sqrt", "sin", "cos", "tan", "pi"}
    student_vars = set(re.findall(r"[a-zA-Z]+\d*", s))
    if expected_vars and not expected_vars.intersection(student_vars):
        return "concept_gap"
    return None


def classify_error(student: str, expected: str) -> Tuple[str, float]:
    override = _rule_diagnosis(student, expected)
    if override:
        return override, 0.93
    linear, (vectorizer, mlp) = train_error_models()
    text = f"student {student} expected {expected} transformation"
    linear_probs = linear.predict_proba([text])[0]
    linear_classes = linear.classes_
    dense = vectorizer.transform([text]).toarray()
    mlp_probs = mlp.predict_proba(dense)[0]
    mlp_classes = mlp.classes_
    scores: Dict[str, float] = {}
    for cls, prob in zip(linear_classes, linear_probs):
        scores[cls] = scores.get(cls, 0.0) + 0.6 * float(prob)
    for cls, prob in zip(mlp_classes, mlp_probs):
        scores[cls] = scores.get(cls, 0.0) + 0.4 * float(prob)
    label = max(scores, key=scores.get)
    # Algebraic errors are the conservative fallback for a parsed but
    # non-equivalent symbolic step.
    if scores[label] < 0.42:
        return "algebra_transformation_error", 0.58
    return label, float(scores[label])


def _styled_feedback(label: str, lang: str, style: str, expected: str, hint: str) -> str:
    base = FEEDBACK.get(lang, FEEDBACK["en"])[label]
    prefix = STYLE_PREFIX.get(style, STYLE_PREFIX["concise"]).get(lang, "")
    if label == "correct":
        return base
    if style == "worked":
        suffix = f" {hint} "
        if expected:
            suffix += f"→ `{expected}`"
        return prefix + suffix.strip()
    if style == "socratic":
        return prefix + base
    return prefix + base


def evaluate_steps(
    student_steps: Iterable[str],
    expected_steps: List[str],
    lang: str = "uz",
    style: str = "concise",
    hint: str = "",
) -> List[StepResult]:
    clean_steps = [str(step).strip() for step in student_steps if str(step).strip()]
    results: List[StepResult] = []
    cursor = 0

    for idx, student in enumerate(clean_steps, start=1):
        expected = expected_steps[min(cursor, len(expected_steps) - 1)] if expected_steps else ""
        try:
            parse_math(student)
        except Exception:
            label = "formatting_error"
            results.append(StepResult(
                idx, student, False, "incorrect", label, expected,
                _styled_feedback(label, lang, style, expected, hint), 0.99
            ))
            continue

        match_index: Optional[int] = None
        for j in range(cursor, len(expected_steps)):
            if mathematically_equivalent(student, expected_steps[j]):
                match_index = j
                break

        # A repeated but valid earlier step is not a new correct advance.
        if match_index is None:
            for j in range(0, cursor):
                if mathematically_equivalent(student, expected_steps[j]):
                    label = "incomplete_step"
                    results.append(StepResult(
                        idx, student, False, "repeated", label, expected,
                        _styled_feedback(label, lang, style, expected, hint), 0.96
                    ))
                    break
            else:
                label, confidence = classify_error(student, expected)
                results.append(StepResult(
                    idx, student, False, "incorrect", label, expected,
                    _styled_feedback(label, lang, style, expected, hint), confidence
                ))
            continue

        skipped = match_index > cursor
        cursor = match_index + 1
        status = "correct_skipped" if skipped else "correct"
        results.append(StepResult(
            idx, student, True, status, "correct", expected_steps[match_index],
            _styled_feedback("correct", lang, style, expected_steps[match_index], hint), 1.0
        ))

    return results


def score_results(results: List[StepResult], expected_count: int) -> float:
    if not results:
        return 0.0
    correct = sum(r.is_correct for r in results)
    completeness = min(1.0, len(results) / max(1, expected_count))
    return round(100.0 * (0.8 * correct / len(results) + 0.2 * completeness), 1)


def choose_feedback_style(state: Dict[str, Any], epsilon: float = 0.12) -> str:
    styles = ["socratic", "concise", "worked"]
    q = state.setdefault("feedback_q", {style: 0.0 for style in styles})
    if random.random() < epsilon:
        return random.choice(styles)
    return max(styles, key=lambda style: q.get(style, 0.0))


def update_feedback_bandit(state: Dict[str, Any], style: str, reward: float) -> None:
    q = state.setdefault("feedback_q", {})
    n = state.setdefault("feedback_n", {})
    count = int(n.get(style, 0)) + 1
    old = float(q.get(style, 0.0))
    q[style] = old + (float(reward) - old) / count
    n[style] = count


def recommend_problem(
    problems: List[Dict[str, Any]],
    current_problem_id: str,
    attempts: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    candidates = [p for p in problems if p["id"] != current_problem_id]
    if not candidates:
        return None
    error_counts: Dict[str, int] = {}
    for attempt in attempts:
        for label in attempt.get("errors", []):
            error_counts[label] = error_counts.get(label, 0) + 1
    # Prefer a problem on the same topic after an error, otherwise a nearby
    # difficulty. This is deterministic enough for a classroom demo.
    current = next((p for p in problems if p["id"] == current_problem_id), None)
    if current:
        same_topic = [p for p in candidates if p["topic"] == current["topic"]]
        if same_topic:
            return sorted(same_topic, key=lambda p: abs(p["difficulty"] - current["difficulty"]))[0]
    return sorted(candidates, key=lambda p: p["difficulty"])[0]


def results_dataframe(results: List[StepResult], lang: str) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append({
            "#": result.index,
            "Step": result.student_step,
            "Status": result.status,
            "Diagnosis": LABEL_TEXT.get(lang, LABEL_TEXT["en"])[result.diagnosis],
            "Expected": result.expected_step,
            "Feedback": result.feedback,
            "Confidence": round(result.confidence, 2),
        })
    return pd.DataFrame(rows)
