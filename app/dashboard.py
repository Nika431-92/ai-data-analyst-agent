
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from app.agent import generate_sql
from app.rag import retrieve_documents
from app.router import route_question
from app.sql_validator import validate_sql
from scripts.query_engine import run_query


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

ANSWER_MODEL = "gemini-3.5-flash-lite"


# --------------------------------------------------
# RAG answer generation
# --------------------------------------------------

def answer_from_knowledge(question, documents):
    """Answer using retrieved business knowledge."""

    if not documents:
        return (
            "I couldn't find relevant information in the "
            "available business knowledge documents."
        )

    context = "\n\n".join(
        f"Source: {doc['source']}\n{doc['text']}"
        for doc in documents
    )

    prompt = f"""
You are a business knowledge assistant.

Answer the user's question using only the supplied context.
Do not invent facts or use outside knowledge.
If the context does not contain enough information, say so.
Be clear and concise.

Context:
{context}

User question:
{question}
"""

    response = client.models.generate_content(
        model=ANSWER_MODEL,
        contents=prompt,
    )

    return response.text or "No answer was generated."


def answer_with_both(question, sql_result, documents):
    """Combine database results with retrieved business knowledge."""

    if sql_result["rows"]:
        dataframe = pd.DataFrame(
            sql_result["rows"],
            columns=sql_result["columns"],
        )
        data_context = dataframe.to_string(index=False)
    else:
        data_context = "The SQL query returned no rows."

    knowledge_context = "\n\n".join(
        f"Source: {doc['source']}\n{doc['text']}"
        for doc in documents
    ) or "No relevant business knowledge passages were retrieved."

    prompt = f"""
You are an AI data analyst.

Answer the user's question using the database results and business
knowledge provided below.

Rules:
- Treat the SQL results as the source of numerical data.
- Use the knowledge passages for business definitions and rules.
- Do not invent numbers or business rules.
- If either source is insufficient, clearly say so.
- Keep the answer concise and distinguish results from definitions.

Database results:
{data_context}

Retrieved business knowledge:
{knowledge_context}

User question:
{question}
"""

    response = client.models.generate_content(
        model=ANSWER_MODEL,
        contents=prompt,
    )

    return response.text or "No answer was generated."


# --------------------------------------------------
# SQL execution
# --------------------------------------------------

def execute_sql_question(question):
    """Generate, validate, and execute a read-only SQL query."""

    sql = generate_sql(question)
    safe_sql = validate_sql(sql)
    result = run_query(safe_sql)

    return safe_sql, result


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Analyst Agent")
st.caption(
    "Ask questions about products, orders, revenue, and business knowledge."
)


# --------------------------------------------------
# Summary cards
# --------------------------------------------------

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


# --------------------------------------------------
# Question input
# --------------------------------------------------

question = st.text_input(
    "Ask a business question",
    placeholder=(
        "Which category has the highest delivered revenue?"
    ),
)


# --------------------------------------------------
# Analyze
# --------------------------------------------------

if st.button("Analyze", type="primary", disabled=not question.strip()):
    try:
        normalized_question = question.lower()

        # Basic protection against obvious destructive requests.
        destructive_phrases = (
            "delete",
            "drop table",
            "erase",
            "truncate",
            "remove all data",
            "modify the database",
        )

        if any(
            phrase in normalized_question
            for phrase in destructive_phrases
        ):
            st.error(
                "I can't modify or delete data. "
                "I can only perform read-only analysis."
            )
            st.stop()

        # Automatically choose SQL, RAG, or BOTH.
        mode = route_question(question)
        st.caption(f"Automatically selected route: {mode}")

        sql_query = None
        sql_result = None
        documents = []

        # Run SQL when numerical analysis is required.
        if mode in ("SQL", "BOTH"):
            with st.spinner("Analyzing business data..."):
                sql_query, sql_result = execute_sql_question(question)

        # Retrieve knowledge when business context is required.
        if mode in ("RAG", "BOTH"):
            with st.spinner("Searching business knowledge..."):
                documents = retrieve_documents(question, top_k=3)

        # --------------------------------------------------
        # Display results
        # --------------------------------------------------

        if mode == "SQL":
            st.subheader("Analysis Results")

            if sql_result["rows"]:
                dataframe = pd.DataFrame(
                    sql_result["rows"],
                    columns=sql_result["columns"],
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

                label_columns = [
                    column for column in dataframe.columns
                    if column not in numeric_columns
                ]

                if numeric_columns and len(dataframe) > 1:
                    if label_columns:
                        st.subheader("Quick Visualization")
                        chart_data = dataframe.set_index(label_columns[0])
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
                st.code(sql_query, language="sql")

        elif mode == "RAG":
            st.subheader("Knowledge Answer")

            if client is None:
                st.error("GEMINI_API_KEY is missing from your .env file.")
                st.stop()

            with st.spinner("Generating a grounded answer..."):
                answer = answer_from_knowledge(question, documents)

            st.write(answer)

        else:
            st.subheader("Combined Analysis")

            st.markdown("**Database results**")

            if sql_result["rows"]:
                dataframe = pd.DataFrame(
                    sql_result["rows"],
                    columns=sql_result["columns"],
                )
                st.dataframe(dataframe, use_container_width=True)
            else:
                st.info("The SQL query returned no results.")

            if client is None:
                st.error("GEMINI_API_KEY is missing from your .env file.")
                st.stop()

            with st.spinner("Combining data and business knowledge..."):
                answer = answer_with_both(
                    question,
                    sql_result,
                    documents,
                )

            st.markdown("**Combined explanation**")
            st.write(answer)

            with st.expander("View generated SQL"):
                st.code(sql_query, language="sql")

        # Show retrieved passages for RAG and BOTH.
        if mode in ("RAG", "BOTH"):
            with st.expander("View retrieved sources"):
                if documents:
                    for index, document in enumerate(documents, start=1):
                        st.markdown(
                            f"**{index}. {document['source']}**"
                        )
                        st.caption(
                            f"Relevance score: {document['score']:.3f}"
                        )
                        st.write(document["text"])
                else:
                    st.info("No relevant knowledge passages were retrieved.")

    except Exception as error:
        st.error(f"Could not analyze this question: {error}")


st.divider()
st.caption("Powered by Gemini, SQLite, Python, and Streamlit.")
