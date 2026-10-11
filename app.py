
import json
from io import BytesIO

import pandas as pd
import streamlit as st

from src.verification.data_quality import run_data_quality_checks
from src.verification.metric_verifier import (
    calculate_reference_metrics,
    verify_reported_metrics,
)


st.set_page_config(
    page_title="Trust-Driven Analytics",
    page_icon="🔎",
    layout="wide",
)

st.title("Trust-Driven Analytics")
st.caption(
    "Inspect business data, verify supported calculations, "
    "and review evidence before trusting the results."
)

uploaded_file = st.file_uploader(
    "Upload a business dataset (CSV)",
    type=["csv"],
)

if uploaded_file is None:
    st.info("Upload a CSV file to begin verification.")
    st.stop()

try:
    data = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Could not read this CSV: {exc}")
    st.stop()

st.subheader("1. Dataset overview")

col1, col2, col3 = st.columns(3)
col1.metric("Rows", len(data))
col2.metric("Columns", len(data.columns))
col3.metric("Missing cells", int(data.isna().sum().sum()))

with st.expander("Preview source data", expanded=True):
    st.dataframe(data.head(100), use_container_width=True)

with st.expander("Column types"):
    schema = pd.DataFrame({
        "Column": data.columns,
        "Detected type": [str(dtype) for dtype in data.dtypes],
        "Missing values": [int(data[c].isna().sum()) for c in data.columns],
    })
    st.dataframe(schema, use_container_width=True)

st.divider()
st.subheader("2. Data-quality verification")

if st.button("Run data-quality checks", type="primary"):
    try:
        quality_results = run_data_quality_checks(data)
        st.session_state["quality_results"] = quality_results
    except Exception as exc:
        st.error(f"Data-quality verification could not finish: {exc}")

quality_results = st.session_state.get("quality_results")

if quality_results is not None:
    quality_df = pd.DataFrame(quality_results)
    counts = quality_df["status"].value_counts()

    a, b, c, d = st.columns(4)
    a.metric("Verified", int(counts.get("VERIFIED", 0)))
    b.metric("Failed", int(counts.get("FAILED", 0)))
    c.metric("Inconclusive", int(counts.get("INCONCLUSIVE", 0)))
    d.metric("Human review", int(counts.get("HUMAN_REVIEW_NEEDED", 0)))

    st.dataframe(quality_df, use_container_width=True)

    st.download_button(
        "Download data-quality evidence (JSON)",
        data=json.dumps(quality_results, indent=2, ensure_ascii=False),
        file_name="data_quality_evidence.json",
        mime="application/json",
    )

st.divider()
st.subheader("3. Metric verification")

st.write(
    "This verifier currently supports retail datasets containing "
    "order ID, order date, product, quantity, unit price, and unit cost."
)

required_columns = {
    "order_id", "order_date", "product",
    "quantity", "unit_price", "unit_cost",
}

if required_columns.issubset(data.columns):
    if st.button("Calculate reference metrics"):
        try:
            st.session_state["reference_metrics"] = (
                calculate_reference_metrics(data)
            )
        except Exception as exc:
            st.error(f"Reference calculation failed: {exc}")

    reference_metrics = st.session_state.get("reference_metrics")

    if reference_metrics is not None:
        st.write("Calculated reference metrics")
        st.json(reference_metrics)

        st.caption(
            "To test a dashboard, enter the values it reports below. "
            "Do not enter the reference values unless those are genuinely "
            "the dashboard's reported results."
        )

        with st.form("reported_metrics_form"):
            reported_sales = st.number_input(
                "Dashboard-reported total sales",
                value=0.0,
                format="%.2f",
            )
            submitted = st.form_submit_button("Verify reported sales")

        if submitted:
            results = verify_reported_metrics(
                data,
                {"total_sales": reported_sales},
                dataset_version=uploaded_file.name,
            )
            st.session_state["metric_results"] = results

        metric_results = st.session_state.get("metric_results")

        if metric_results is not None:
            metric_df = pd.DataFrame(metric_results)
            st.dataframe(metric_df, use_container_width=True)

            st.download_button(
                "Download metric evidence (JSON)",
                data=json.dumps(
                    metric_results, indent=2, ensure_ascii=False
                ),
                file_name="metric_verification_evidence.json",
                mime="application/json",
            )
else:
    missing = sorted(required_columns - set(data.columns))
    st.warning(
        "Metric verification is unavailable for this dataset. "
        f"Missing required columns: {missing}"
    )

st.divider()
st.caption(
    "A successful check verifies only the stated rule against the "
    "uploaded data. It does not establish that the source data is factual."
)
