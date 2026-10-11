from pathlib import Path

import pandas as pd

from src.verification.defect_benchmark import run_corrupted_data_benchmark


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample" / "retail_sales.csv"


def load_data():
    return pd.read_csv(CSV_PATH)


def test_benchmark_injects_five_known_defects():
    report = run_corrupted_data_benchmark(load_data())
    assert report["total_defects"] == 5
    assert len(report["cases"]) == 5


def test_all_known_defects_are_detected():
    report = run_corrupted_data_benchmark(load_data())
    assert report["detected_defects"] == 5
    assert report["missed_defects"] == 0
    assert report["detection_rate_pct"] == 100.0


def test_each_case_produces_its_expected_status():
    report = run_corrupted_data_benchmark(load_data())

    for case in report["cases"]:
        assert case["actual_status"] == case["expected_status"], case


def test_report_contains_explanations():
    report = run_corrupted_data_benchmark(load_data())

    assert all(case["reason"].strip() for case in report["cases"])


def test_benchmark_does_not_modify_source_data():
    data = load_data()
    original = data.copy(deep=True)

    run_corrupted_data_benchmark(data)

    pd.testing.assert_frame_equal(data, original)
