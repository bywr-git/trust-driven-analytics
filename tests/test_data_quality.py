from pathlib import Path

import pandas as pd

from src.verification.data_quality import run_data_quality_checks


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample" / "retail_sales.csv"


def load_data():
    return pd.read_csv(CSV_PATH)


def find_check(results, check_id):
    return next(result for result in results if result["check_id"] == check_id)


def test_clean_benchmark_has_no_failed_checks():
    results = run_data_quality_checks(load_data())
    assert not any(result["status"] == "FAILED" for result in results)


def test_missing_required_value_is_detected():
    data = load_data()
    data.loc[0, "product"] = None

    results = run_data_quality_checks(data)
    check = find_check(results, "missing_values:product")

    assert check["status"] == "FAILED"
    assert check["row_numbers"] == [2]


def test_missing_required_column_is_detected():
    data = load_data().drop(columns=["unit_cost"])

    results = run_data_quality_checks(data)
    check = find_check(results, "required_columns")

    assert check["status"] == "FAILED"
    assert "unit_cost" in check["reason"]


def test_duplicate_order_ids_need_review():
    data = load_data()
    data.loc[1, "order_id"] = data.loc[0, "order_id"]

    results = run_data_quality_checks(data)
    check = find_check(results, "duplicate_order_ids")

    assert check["status"] == "HUMAN_REVIEW_NEEDED"
    assert check["row_numbers"] == [2, 3]


def test_invalid_date_is_detected():
    data = load_data()
    data.loc[2, "order_date"] = "not-a-date"

    results = run_data_quality_checks(data)
    check = find_check(results, "valid_dates")

    assert check["status"] == "FAILED"
    assert check["row_numbers"] == [4]


def test_non_numeric_quantity_is_detected():
    data = load_data()
    data["quantity"] = data["quantity"].astype(object)
    data.loc[0, "quantity"] = "unknown"

    results = run_data_quality_checks(data)
    check = find_check(results, "numeric_values:quantity")

    assert check["status"] == "FAILED"
    assert check["row_numbers"] == [2]


def test_negative_price_needs_review():
    data = load_data()
    data.loc[0, "unit_price"] = -10

    results = run_data_quality_checks(data)
    check = find_check(results, "negative_values:unit_price")

    assert check["status"] == "HUMAN_REVIEW_NEEDED"
    assert check["row_numbers"] == [2]


def test_source_data_is_not_modified():
    data = load_data()
    original = data.copy(deep=True)

    run_data_quality_checks(data)

    pd.testing.assert_frame_equal(data, original)
