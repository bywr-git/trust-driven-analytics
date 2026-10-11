from collections.abc import Mapping
from datetime import datetime, timezone
from math import isclose, isfinite
from numbers import Real

import pandas as pd


REQUIRED_COLUMNS = {
    "order_id", "order_date", "product",
    "quantity", "unit_price", "unit_cost",
}

METRIC_IDS = {
    "transaction_count", "total_quantity", "total_sales",
    "total_cost", "total_profit", "monthly_sales", "product_sales",
}


def calculate_reference_metrics(data: pd.DataFrame) -> dict:
    """Calculate supported metrics from the source dataset."""
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if data.empty:
        raise ValueError("Cannot calculate metrics from an empty dataset.")

    frame = data.copy()
    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="raise")

    for column in ("quantity", "unit_price", "unit_cost"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if frame[column].isna().any():
            raise ValueError(f"Column '{column}' contains missing values.")
        if not frame[column].map(lambda x: isfinite(float(x))).all():
            raise ValueError(f"Column '{column}' contains non-finite values.")

    if frame["order_date"].isna().any():
        raise ValueError("Column 'order_date' contains missing values.")
    if frame["product"].isna().any():
        raise ValueError("Column 'product' contains missing values.")

    frame["sales"] = frame["quantity"] * frame["unit_price"]
    frame["cost"] = frame["quantity"] * frame["unit_cost"]
    frame["profit"] = frame["sales"] - frame["cost"]

    monthly = (
        frame.groupby(frame["order_date"].dt.strftime("%Y-%m"))["sales"]
        .sum().sort_index().to_dict()
    )
    products = frame.groupby("product")["sales"].sum().sort_index().to_dict()

    return {
        "transaction_count": int(len(frame)),
        "total_quantity": float(frame["quantity"].sum()),
        "total_sales": float(frame["sales"].sum()),
        "total_cost": float(frame["cost"].sum()),
        "total_profit": float(frame["profit"].sum()),
        "monthly_sales": {k: float(v) for k, v in monthly.items()},
        "product_sales": {k: float(v) for k, v in products.items()},
    }


def _compare_values(expected, observed, path: str, tolerance: float) -> dict:
    if isinstance(expected, Mapping):
        if not isinstance(observed, Mapping):
            return {
                "status": "FAILED", "expected": dict(expected),
                "observed": observed,
                "reason": f"Expected a grouped result for '{path}'.",
            }

        if set(expected) != set(observed):
            return {
                "status": "FAILED", "expected": dict(expected),
                "observed": dict(observed),
                "reason": f"Group keys differ for '{path}'.",
            }

        mismatches = []
        for key in expected:
            result = _compare_values(
                expected[key], observed[key], f"{path}.{key}", tolerance
            )
            if result["status"] != "VERIFIED":
                mismatches.append({
                    "key": str(key),
                    "status": result["status"],
                    "reason": result["reason"],
                })

        if mismatches:
            return {
                "status": "FAILED", "expected": dict(expected),
                "observed": dict(observed),
                "reason": f"One or more grouped values differ for '{path}'.",
                "mismatches": mismatches,
            }

        return {
            "status": "VERIFIED", "expected": dict(expected),
            "observed": dict(observed),
            "reason": "All grouped values match within tolerance.",
        }

    if (
        isinstance(expected, bool) or isinstance(observed, bool)
        or not isinstance(expected, Real) or not isinstance(observed, Real)
    ):
        return {
            "status": "INCONCLUSIVE", "expected": expected,
            "observed": observed,
            "reason": f"Non-numeric values cannot verify '{path}'.",
        }

    if not isfinite(float(expected)) or not isfinite(float(observed)):
        return {
            "status": "INCONCLUSIVE", "expected": str(expected),
            "observed": str(observed),
            "reason": f"Non-finite values cannot verify '{path}'.",
        }

    passed = isclose(
        float(expected), float(observed),
        rel_tol=tolerance, abs_tol=tolerance,
    )
    return {
        "status": "VERIFIED" if passed else "FAILED",
        "expected": float(expected),
        "observed": float(observed),
        "reason": (
            "Observed value matches the independently calculated result."
            if passed else
            "Observed value differs from the independently calculated result."
        ),
    }


def verify_reported_metrics(
    data: pd.DataFrame,
    reported_metrics: dict,
    dataset_version: str,
    tolerance: float = 1e-9,
) -> list[dict]:
    if not dataset_version.strip():
        raise ValueError("dataset_version must not be empty.")
    if tolerance < 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative.")
    if not isinstance(reported_metrics, dict):
        raise ValueError("reported_metrics must be a dictionary.")

    expected = calculate_reference_metrics(data)
    results = []

    for metric_id in sorted(METRIC_IDS):
        timestamp = datetime.now(timezone.utc).isoformat()

        if metric_id not in reported_metrics:
            comparison = {
                "status": "INCONCLUSIVE",
                "expected": expected[metric_id],
                "observed": None,
                "reason": "The dashboard did not provide this metric.",
            }
        else:
            comparison = _compare_values(
                expected[metric_id], reported_metrics[metric_id],
                metric_id, tolerance,
            )

        results.append({
            "check_id": f"metric_match:{metric_id}",
            "rule_version": "1.0",
            "metric_id": metric_id,
            "dataset_version": dataset_version,
            "status": comparison["status"],
            "expected": comparison["expected"],
            "observed": comparison["observed"],
            "reason": comparison["reason"],
            "details": comparison.get("mismatches", []),
            "checked_at": timestamp,
        })

    for metric_id in sorted(set(reported_metrics) - METRIC_IDS):
        results.append({
            "check_id": f"unsupported_metric:{metric_id}",
            "rule_version": "1.0",
            "metric_id": str(metric_id),
            "dataset_version": dataset_version,
            "status": "INCONCLUSIVE",
            "expected": None,
            "observed": str(reported_metrics[metric_id]),
            "reason": "This metric is not supported by the current verifier.",
            "details": [],
            "checked_at": datetime.now(timezone.utc).isoformat(),
        })

    return results
