import json
from pathlib import Path

import pandas as pd

from src.verification.basic_checks import compare_numeric


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample" / "retail_sales.csv"
REFERENCE_PATH = ROOT / "data" / "fixtures" / "retail_expected.json"


def load_benchmark():
    data = pd.read_csv(CSV_PATH)
    reference = json.loads(
        REFERENCE_PATH.read_text(encoding="utf-8-sig")
    )
    data["order_date"] = pd.to_datetime(data["order_date"])
    data["sales"] = data["quantity"] * data["unit_price"]
    data["cost"] = data["quantity"] * data["unit_cost"]
    data["profit"] = data["sales"] - data["cost"]
    return data, reference["expected"]


def test_dataset_has_expected_row_count():
    data, expected = load_benchmark()
    assert len(data) == expected["transaction_count"]


def test_dataset_has_expected_total_quantity():
    data, expected = load_benchmark()
    assert int(data["quantity"].sum()) == expected["total_quantity"]


def test_dataset_has_expected_sales_cost_and_profit():
    data, expected = load_benchmark()

    assert data["sales"].sum() == expected["total_sales"]
    assert data["cost"].sum() == expected["total_cost"]
    assert data["profit"].sum() == expected["total_profit"]


def test_monthly_sales_match_reference():
    data, expected = load_benchmark()
    monthly = (
        data.groupby(data["order_date"].dt.strftime("%Y-%m"))["sales"]
        .sum()
        .to_dict()
    )
    assert monthly == expected["monthly_sales"]


def test_product_sales_match_reference():
    data, expected = load_benchmark()
    products = data.groupby("product")["sales"].sum().to_dict()
    assert products == expected["product_sales"]


def test_correct_metric_is_verified():
    result = compare_numeric(expected=159.0, observed=159.0)
    assert result["status"] == "VERIFIED"


def test_incorrect_metric_is_rejected():
    result = compare_numeric(expected=159.0, observed=169.0)
    assert result["status"] == "FAILED"


def test_non_numeric_metric_is_inconclusive():
    result = compare_numeric(expected=159.0, observed="unknown")
    assert result["status"] == "INCONCLUSIVE"
