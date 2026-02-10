from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _payload(**kwargs):
    payload = {
        "system_family": "powerocean",
        "city": "Ýstanbul",
        "pv_kwp": 8,
        "tariff_tl_per_kwh": 3.5,
        "daily_kwh": 30,
        "avg_kw": None,
        "peak_kw": 8,
        "powerocean_phase": "1P",
        "powerocean_3p_class": None,
        "selected_scenario_id": "S3",
        "expert_mode": False,
        "expert_loads": [],
    }
    payload.update(kwargs)
    return payload


def test_city_normalization_and_selected_scenario_bom_mapping() -> None:
    res = client.post("/analyze", json=_payload(selected_scenario_id="S1"))
    assert res.status_code == 200
    data = res.json()
    assert data["inputs"]["city"] in ["Ýstanbul", "İstanbul", "Istanbul"]

    s1_modules = next(s for s in data["sizing"]["scenarios"] if s["id"] == "S1")["battery_modules"][0]["count"]
    s1_bom_battery = next(i for i in data["bom"]["scenarios"]["S1"]["items"] if "battery" in i["id"])
    assert s1_bom_battery["qty"] == s1_modules
    assert data["bom"]["selected"]["capex_try"] == data["bom"]["scenarios"]["S1"]["capex_try"]


def test_powerocean_inverter_included_in_bom() -> None:
    res = client.post("/analyze", json=_payload(powerocean_phase="3P", powerocean_3p_class="3P"))
    assert res.status_code == 200
    data = res.json()
    item_ids = [i["id"] for i in data["bom"]["selected"]["items"]]
    assert "3p_12kw_inverter" in item_ids


def test_economics_per_scenario_and_selected() -> None:
    res_s1 = client.post("/analyze", json=_payload(selected_scenario_id="S1"))
    res_s3 = client.post("/analyze", json=_payload(selected_scenario_id="S3"))
    assert res_s1.status_code == 200 and res_s3.status_code == 200
    s1 = res_s1.json()
    s3 = res_s3.json()
    assert s1["economics"]["selected"]["capex_try"] == s1["economics"]["scenarios"]["S1"]["capex_try"]
    assert s3["economics"]["selected"]["capex_try"] == s3["economics"]["scenarios"]["S3"]["capex_try"]
    assert s1["economics"]["scenarios"]["S1"]["payback_simple_years"] != s1["economics"]["scenarios"]["S3"]["payback_simple_years"]


def test_expert_hours_multiplier_applies() -> None:
    template = client.get("/metadata").json()["expert_load_templates"][0]
    res = client.post(
        "/analyze",
        json=_payload(
            expert_mode=True,
            expert_hours_mode="high",
            expert_loads=[template],
        ),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["expert_load_contributions"]["hours_mode"] == "high"
    assert data["expert_load_contributions"]["multiplier"] == 1.4
    contrib = data["expert_load_contributions"]["templates"][template]
    assert contrib["kwh_day_scaled"][1] > contrib["kwh_day_original"][1]
