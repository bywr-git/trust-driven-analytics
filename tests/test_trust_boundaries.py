from pathlib import Path

import pandas as pd
import pytest

from src.verification.data_quality import run_data_quality_checks
from src.verification.metric_verifier import verify_reported_metrics


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample" / "retail_sales.csv"


def load_data():
    return pd.read_csv(CSV_PATH)


def find_check(results, check_id):
    return next(item for item in results if item["check_id"] == check_id)


def test_empty_dataset_is_inconclusive():
    data = pd.DataFrame(columns=load_data().columns)

    results = run_data_quality_checks(data)

    assert len(results) == 1
    assert results[0]["status"] == "INCONCLUSIVE"
    assert results[0]["check_id"] == "dataset_not_empty"


def test_negative_price_requires_review_not_automatic_failure():
    data = load_data()
    data.loc[0, "unit_price"] = -10

    results = run_data_quality_checks(data)

    negative_check = find_check(results, "negative_values:unit_price")

    assert negative_check["status"] == "HUMAN_REVIEW_NEEDED"
    assert negative_check["status"] != "FAILED"


def test_missing_dashboard_metric_is_inconclusive():
    data = load_data()
    reported = {
        "transaction_count": len(data),
    }

    results = verify_reported_metrics(
        data, reported, dataset_version="trust_boundary_test"
    )

    sales_check = find_check(results, "metric_match:total_sales")

    assert sales_check["status"] == "INCONCLUSIVE"


def test_unsupported_dashboard_metric_is_inconclusive():
    data = load_data()
    reported = {
        "transaction_count": len(data),
        "unknown_business_metric": 123,
    }

    results = verify_reported_metrics(
        data, reported, dataset_version="trust_boundary_test"
    )

    unsupported_check = find_check(
        results, "unsupported_metric:unknown_business_metric"
    )

    assert unsupported_check["status"] == "INCONCLUSIVE"


def test_empty_dataset_cannot_produce_metric_verification():
    data = pd.DataFrame(columns=load_data().columns)

    with pytest.raises(ValueError, match="empty dataset"):
        verify_reported_metrics(
            data, {}, dataset_version="empty_dataset_test"
        )