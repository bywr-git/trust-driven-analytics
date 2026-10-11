import pandas as pd

from src.verification.data_quality import run_data_quality_checks
from src.verification.metric_verifier import (
    calculate_reference_metrics,
    verify_reported_metrics,
)


def _find_check(results: list[dict], check_id: str) -> dict:
    return next(item for item in results if item["check_id"] == check_id)


def run_corrupted_data_benchmark(data: pd.DataFrame) -> dict:
    """Inject known defects into copies and measure detection."""
    cases = []

    # Case 1: missing product
    corrupted = data.copy(deep=True)
    corrupted.loc[corrupted.index[0], "product"] = None
    result = _find_check(
        run_data_quality_checks(corrupted), "missing_values:product"
    )
    cases.append({
        "case_id": "missing_product",
        "expected_status": "FAILED",
        "actual_status": result["status"],
        "detected": result["status"] == "FAILED",
        "reason": result["reason"],
    })

    # Case 2: duplicate order ID
    corrupted = data.copy(deep=True)
    corrupted.loc[corrupted.index[1], "order_id"] = (
        corrupted.loc[corrupted.index[0], "order_id"]
    )
    result = _find_check(
        run_data_quality_checks(corrupted), "duplicate_order_ids"
    )
    cases.append({
        "case_id": "duplicate_order_id",
        "expected_status": "HUMAN_REVIEW_NEEDED",
        "actual_status": result["status"],
        "detected": result["status"] == "HUMAN_REVIEW_NEEDED",
        "reason": result["reason"],
    })

    # Case 3: invalid date
    corrupted = data.copy(deep=True)
    corrupted["order_date"] = corrupted["order_date"].astype(object)
    corrupted.loc[corrupted.index[2], "order_date"] = "not-a-date"
    result = _find_check(
        run_data_quality_checks(corrupted), "valid_dates"
    )
    cases.append({
        "case_id": "invalid_date",
        "expected_status": "FAILED",
        "actual_status": result["status"],
        "detected": result["status"] == "FAILED",
        "reason": result["reason"],
    })

    # Case 4: non-numeric quantity
    corrupted = data.copy(deep=True)
    corrupted["quantity"] = corrupted["quantity"].astype(object)
    corrupted.loc[corrupted.index[3], "quantity"] = "unknown"
    result = _find_check(
        run_data_quality_checks(corrupted), "numeric_values:quantity"
    )
    cases.append({
        "case_id": "non_numeric_quantity",
        "expected_status": "FAILED",
        "actual_status": result["status"],
        "detected": result["status"] == "FAILED",
        "reason": result["reason"],
    })

    # Case 5: incorrect dashboard-reported sales
    expected_metrics = calculate_reference_metrics(data)
    reported_metrics = dict(expected_metrics)
    reported_metrics["total_sales"] += 10.0
    results = verify_reported_metrics(
        data,
        reported_metrics,
        dataset_version="corrupted_benchmark_v1",
    )
    result = _find_check(results, "metric_match:total_sales")
    cases.append({
        "case_id": "incorrect_reported_sales",
        "expected_status": "FAILED",
        "actual_status": result["status"],
        "detected": result["status"] == "FAILED",
        "reason": result["reason"],
    })

    detected_count = sum(case["detected"] for case in cases)
    total = len(cases)

    return {
        "benchmark_version": "1.0",
        "total_defects": total,
        "detected_defects": detected_count,
        "missed_defects": total - detected_count,
        "detection_rate_pct": round(100 * detected_count / total, 2)
        if total else 0.0,
        "cases": cases,
    }
