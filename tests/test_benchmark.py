import json
from pathlib import Path

import pandas as pd
import pytest

from src.verification.basic_checks import compare_numeric
from src.verification.metric_verifier import (
    calculate_reference_metrics,
    verify_reported_metrics,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample" / "retail_sales.csv"
REFERENCE_PATH = ROOT / "data" / "fixtures" / "retail_expected.json"


def load_benchmark():
    data = pd.read_csv(CSV_PATH)
    reference = json.loads(
        REFERENCE_PATH.read_text(encoding="utf-8-sig")
    )
    return data, reference["expected"]


def test_dataset_has_expected_row_count():
    data, expected = load_benchmark()
    assert len(data) == expected["transaction_count"]


def test_dataset_has_expected_total_quantity():
    data, expected = load_benchmark()
    assert int(data["quantity"].sum()) == expected["total_quantity"]


def test_dataset_has_expected_sales_cost_and_profit():
    data, expected = load_benchmark()
    metrics = calculate_reference_metrics(data)

    assert metrics["total_sales"] == expected["total_sales"]
    assert metrics["total_cost"] == expected["total_cost"]
    assert metrics["total_profit"] == expected["total_profit"]


def test_monthly_sales_match_reference():
    data, expected = load_benchmark()
    metrics = calculate_reference_metrics(data)
    assert metrics["monthly_sales"] == expected["monthly_sales"]


def test_product_sales_match_reference():
    data, expected = load_benchmark()
    metrics = calculate_reference_metrics(data)
    assert metrics["product_sales"] == expected["product_sales"]


def test_correct_metric_is_verified():
    result = compare_numeric(expected=159.0, observed=159.0)
    assert result["status"] == "VERIFIED"


def test_incorrect_metric_is_rejected():
    result = compare_numeric(expected=159.0, observed=169.0)
    assert result["status"] == "FAILED"


def test_non_numeric_metric_is_inconclusive():
    result = compare_numeric(expected=159.0, observed="unknown")
    assert result["status"] == "INCONCLUSIVE"


def test_verifier_accepts_reference_metrics():
    data, expected = load_benchmark()
    results = verify_reported_metrics(
        data, expected, dataset_version="retail_sales_v1"
    )

    assert len(results) == 7
    assert all(item["status"] == "VERIFIED" for item in results)


def test_verifier_detects_incorrect_total_sales():
    data, expected = load_benchmark()
    reported = dict(expected)
    reported["total_sales"] = 999.0

    results = verify_reported_metrics(
        data, reported, dataset_version="retail_sales_v1"
    )
    sales_check = next(
        item for item in results if item["metric_id"] == "total_sales"
    )

    assert sales_check["status"] == "FAILED"
    assert sales_check["expected"] == 159.0
    assert sales_check["observed"] == 999.0


def test_missing_metric_is_inconclusive():
    data, expected = load_benchmark()
    reported = dict(expected)
    del reported["product_sales"]

    results = verify_reported_metrics(
        data, reported, dataset_version="retail_sales_v1"
    )
    product_check = next(
        item for item in results if item["metric_id"] == "product_sales"
    )

    assert product_check["status"] == "INCONCLUSIVE"
    assert product_check["observed"] is None


def test_verifier_detects_wrong_monthly_sales():
    data, expected = load_benchmark()
    reported = dict(expected)
    reported["monthly_sales"] = dict(expected["monthly_sales"])
    reported["monthly_sales"]["2026-01"] = 999.0

    results = verify_reported_metrics(
        data, reported, dataset_version="retail_sales_v1"
    )
    monthly_check = next(
        item for item in results if item["metric_id"] == "monthly_sales"
    )

    assert monthly_check["status"] == "FAILED"
    assert monthly_check["details"]


def test_unsupported_metric_is_not_verified():
    data, expected = load_benchmark()
    reported = dict(expected)
    reported["customer_lifetime_value"] = 500.0

    results = verify_reported_metrics(
        data, reported, dataset_version="retail_sales_v1"
    )
    extra_check = next(
        item for item in results
        if item["metric_id"] == "customer_lifetime_value"
    )

    assert extra_check["status"] == "INCONCLUSIVE"


def test_missing_required_column_is_rejected():
    data, expected = load_benchmark()
    data = data.drop(columns=["unit_cost"])

    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_reference_metrics(data)
