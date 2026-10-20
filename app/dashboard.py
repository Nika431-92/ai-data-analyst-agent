
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agent import generate_sql
from app.sql_validator import validate_sql
from scripts.query_engine import run_query


st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Analyst Agent")
st.caption("Ask questions about products, orders, and revenue.")

# Dashboard summary cards
try:
    summary = run_query("""
        SELECT
            (SELECT COUNT(*) FROM orders) AS total_orders,
            (SELECT COUNT(*) FROM products) AS total_products,
            (SELECT COUNT(*) FROM orders
             WHERE status = 'cancelled') AS cancelled_orders
    """)

    total_orders, total_products, cancelled_orders = summary["rows"][0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Orders", total_orders)
    col2.metric("Total Products", total_products)
    col3.metric("Cancelled Orders", cancelled_orders)

except Exception as error:
    st.warning(f"Could not load summary metrics: {error}")


question = st.text_input(
    "Ask a business question",
    placeholder="Which category has the highest delivered revenue?",
)


if st.button("Analyze", type="primary", disabled=not question.strip()):
    try:
        # Block data modification requests.
        if any(word in question.lower() for word in [
            "delete", "drop table", "erase", "truncate"
        ]):
            st.error(
                "I can't modify or delete data. "
                "I can only perform read-only analysis."
            )
            st.stop()

        with st.spinner("Gemini is analyzing your question..."):
            sql = generate_sql(question)
            safe_sql = validate_sql(sql)
            result = run_query(safe_sql)

        st.subheader("Analysis Results")

        if result["rows"]:
            dataframe = pd.DataFrame(
                result["rows"],
                columns=result["columns"],
            )
            st.dataframe(
    dataframe,
    use_container_width=True,
    column_config={
        "total_revenue": st.column_config.NumberColumn(
            "Total Revenue (₹)",
            format="₹%.2f",
        ),
        "avg_price": st.column_config.NumberColumn(
            "Average Price (₹)",
            format="₹%.2f",
        ),
        "price": st.column_config.NumberColumn(
            "Price (₹)",
            format="₹%.2f",
        ),
    },
)

            numeric_columns = dataframe.select_dtypes(
                include="number"
            ).columns.tolist()

            if len(numeric_columns) >= 1 and len(dataframe) > 1:
                st.subheader("Quick Visualization")

                label_columns = [
                    column
                    for column in dataframe.columns
                    if column not in numeric_columns
                ]

                if label_columns:
                    chart_data = dataframe.set_index(label_columns[0])
                    st.bar_chart(chart_data[numeric_columns[0]])
                    st.bar_chart(
    chart_data[numeric_columns[0]],
    height=350,
)
                else:
                    st.info(
                        "No category column is available for a bar chart."
                    )
        else:
            st.info("The query returned no results.")

        with st.expander("View generated SQL"):
            st.code(safe_sql, language="sql")

    except Exception as error:
        st.error(f"Could not analyze this question: {error}")


st.divider()
st.caption("Powered by Gemini, SQLite, Python, and Streamlit.")
