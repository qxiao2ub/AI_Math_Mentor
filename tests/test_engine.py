from ai_engine import evaluate_steps, mathematically_equivalent, score_results
from problem_bank import filter_problems, load_problem_bank


def test_equivalent_equations():
    assert mathematically_equivalent("3*x+5=20", "3*x=15")
    assert mathematically_equivalent("x=5", "3*x=15")


def test_fraction_equivalence():
    assert mathematically_equivalent("3/4+1/8", "7/8")


def test_correct_solution_scores_high():
    results = evaluate_steps(
        ["3*x+5=20", "3*x=15", "x=5"],
        ["3*x+5=20", "3*x=15", "x=5"],
        lang="en",
    )
    assert all(r.is_correct for r in results)
    assert score_results(results, 3) == 100.0


def test_incorrect_step_is_caught():
    results = evaluate_steps(["3*x+5=20", "3*x=10"], ["3*x+5=20", "3*x=15", "x=5"])
    assert results[0].is_correct
    assert not results[1].is_correct


def test_problem_bank_has_uzbekistan_scope():
    bank = load_problem_bank()
    assert len(bank) >= 20
    assert all(p["id"].startswith("UZ-") for p in bank)
    grade7 = filter_problems(bank, "school", 7)
    assert grade7
