from app.domain.engine.constraints import evaluate_powerocean_constraints


def test_powerocean_1p_rejects_over_3_batteries() -> None:
    result = evaluate_powerocean_constraints("1P", None, required_modules=4, battery_unit_kwh=5.0, peak_kw=5.0)
    assert result["feasible"] is False


def test_powerocean_3p_enforces_jb_limit() -> None:
    result = evaluate_powerocean_constraints("3P", "3P", required_modules=10, battery_unit_kwh=5.0, peak_kw=10.0)
    assert result["feasible"] is False
    assert any("9 batteries" in w for w in result["warnings"])


def test_powerocean_3p_plus_parallel_and_limits() -> None:
    result = evaluate_powerocean_constraints("3P", "3P_PLUS", required_modules=25, battery_unit_kwh=5.0, peak_kw=50.0)
    assert result["inverter"]["count"] == 2
    assert result["feasible"] is False
