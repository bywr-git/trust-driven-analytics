from datetime import datetime, timezone
from math import isfinite

import pandas as pd


REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "product",
    "quantity",
    "unit_price",
    "unit_cost",
}

NUMERIC_COLUMNS = ("quantity", "unit_price", "unit_cost")


def _issue(
    check_id: str,
    status: str,
    reason: str,
    row_numbers: list[int] | None = None,
    column: str | None = None,
) -> dict:
    return {
        "check_id": check_id,
        "rule_version": "1.0",
        "status": status,
        "reason": reason,
        "row_numbers": row_numbers or [],
        "column": column,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def run_data_quality_checks(data: pd.DataFrame) -> list[dict]:
    """Inspect source data and return evidence records; never mutate input."""
    if data.empty:
        return [
            _issue(
                "dataset_not_empty",
                "INCONCLUSIVE",
                "Dataset contains no rows; data-quality checks cannot "
                "establish data validity.",
            )
        ]

    results = []

    missing_columns = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing_columns:
        results.append(_issue(
            "required_columns",
            "FAILED",
            f"Required columns are missing: {missing_columns}",
        ))
        return results

    results.append(_issue(
        "required_columns",
        "VERIFIED",
        "All required columns are present.",
    ))

    missing_rows = {}
    for column in sorted(REQUIRED_COLUMNS):
        positions = [
            int(position + 2)
            for position, missing in enumerate(data[column].isna())
            if missing
        ]
        # Spreadsheet-style row numbers: header is row 1, first data row is 2.
        if positions:
            missing_rows[column] = positions

    if missing_rows:
        for column, rows in missing_rows.items():
            results.append(_issue(
                f"missing_values:{column}",
                "FAILED",
                f"Missing values found in column '{column}'.",
                rows,
                column,
            ))
    else:
        results.append(_issue(
            "missing_values",
            "VERIFIED",
            "No missing values found in required columns.",
        ))

    ids = data["order_id"].astype("string").str.strip()
    duplicate_mask = ids.notna() & ids.ne("") & ids.duplicated(keep=False)
    duplicate_rows = [
        int(position + 2)
        for position, duplicate in enumerate(duplicate_mask)
        if duplicate
    ]

    if duplicate_rows:
        results.append(_issue(
            "duplicate_order_ids",
            "HUMAN_REVIEW_NEEDED",
            "Order IDs repeat. Confirm whether these rows are duplicate "
            "transactions or legitimate line items.",
            duplicate_rows,
            "order_id",
        ))
    else:
        results.append(_issue(
            "duplicate_order_ids",
            "VERIFIED",
            "No repeated non-empty order IDs found.",
            column="order_id",
        ))

    parsed_dates = pd.to_datetime(data["order_date"], errors="coerce")
    invalid_date_mask = data["order_date"].notna() & parsed_dates.isna()
    invalid_date_rows = [
        int(position + 2)
        for position, invalid in enumerate(invalid_date_mask)
        if invalid
    ]

    if invalid_date_rows:
        results.append(_issue(
            "valid_dates",
            "FAILED",
            "Some non-empty dates could not be parsed.",
            invalid_date_rows,
            "order_date",
        ))
    else:
        results.append(_issue(
            "valid_dates",
            "VERIFIED",
            "All non-empty dates can be parsed.",
            column="order_date",
        ))

    for column in NUMERIC_COLUMNS:
        numeric = pd.to_numeric(data[column], errors="coerce")
        non_numeric_mask = data[column].notna() & numeric.isna()
        non_numeric_rows = [
            int(position + 2)
            for position, invalid in enumerate(non_numeric_mask)
            if invalid
        ]

        if non_numeric_rows:
            results.append(_issue(
                f"numeric_values:{column}",
                "FAILED",
                f"Non-numeric values found in '{column}'.",
                non_numeric_rows,
                column,
            ))
        else:
            results.append(_issue(
                f"numeric_values:{column}",
                "VERIFIED",
                f"All non-empty values in '{column}' are numeric.",
                column=column,
            ))

        finite_mask = numeric.notna() & ~numeric.map(
            lambda value: isfinite(float(value)) if pd.notna(value) else True
        )
        non_finite_rows = [
            int(position + 2)
            for position, invalid in enumerate(finite_mask)
            if invalid
        ]

        if non_finite_rows:
            results.append(_issue(
                f"finite_values:{column}",
                "FAILED",
                f"Non-finite values found in '{column}'.",
                non_finite_rows,
                column,
            ))
        else:
            results.append(_issue(
                f"finite_values:{column}",
                "VERIFIED",
                f"All numeric values in '{column}' are finite.",
                column=column,
            ))

        negative_mask = numeric.notna() & numeric.lt(0)
        negative_rows = [
            int(position + 2)
            for position, negative in enumerate(negative_mask)
            if negative
        ]

        if negative_rows:
            results.append(_issue(
                f"negative_values:{column}",
                "HUMAN_REVIEW_NEEDED",
                f"Negative values found in '{column}'. Confirm whether "
                "they represent refunds, corrections, or invalid data.",
                negative_rows,
                column,
            ))
        else:
            results.append(_issue(
                f"negative_values:{column}",
                "VERIFIED",
                f"No negative values found in '{column}'.",
                column=column,
            ))

    return results
