# AI Data Analyst Agent

An AI-powered data analytics application that converts natural-language business questions into SQL queries and presents the results through an interactive Streamlit dashboard.

## Features

- **Natural-language queries:** Ask questions about products, orders, and revenue.
- **AI-generated SQL:** Uses the Google Gemini API to generate SQL queries.
- **SQLite database:** Stores sample product and order data.
- **SQL validation:** Includes basic checks to reject unsafe SQL statements.
- **Interactive dashboard:** Displays query results in tables and bar charts.
- **Summary metrics:** Shows total orders, total products, and cancelled orders.
- **Retry handling:** Retries certain temporary Gemini API availability errors.

## Technology Stack

- Python
- Google Gemini API
- SQLite
- Pandas
- Streamlit
- Plotly
- python-dotenv

## Project Structure

```text
ai-data-analyst-agent/
├── app/
│   ├── agent.py
│   ├── dashboard.py
│   └── sql_validator.py
├── data/
│   ├── analytics.db
│   ├── orders.csv
│   └── products.csv
├── scripts/
│   ├── create_database.py
│   ├── create_sample_data.py
│   ├── query_engine.py
│   ├── test_database.py
│   ├── test_gemini.py
│   ├── test_gemini_connection.py
│   └── test_sql_validator.py
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd ai-data-analyst-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Get an API key from [Google AI Studio](https://aistudio.google.com/).

Never commit your `.env` file or expose your API key.

### 5. Create the sample database

If the database does not already exist, run:

```bash
python scripts/create_sample_data.py
python scripts/create_database.py
```

### 6. Launch the dashboard

```bash
python -m streamlit run app/dashboard.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## Example Questions

- What are the five most expensive products?
- How many orders were cancelled?
- Which product category has the highest delivered revenue?
- What is the average product price in each category?

## Sample Data

The project uses synthetic sample data containing eight products and 100 orders. Results demonstrate the analytics workflow and should not be interpreted as real business findings.

## Current Limitations

- SQL validation is basic and requires further hardening before use with untrusted queries.
- Unrelated questions are not reliably rejected.
- Gemini availability and API usage limits can affect requests.
- Evaluation across a larger question set is still required.

## Future Improvements

- Stronger SQL parsing and execution limits.
- Better handling of irrelevant or ambiguous questions.
- Automated evaluation using a 40-question test set.
- Improved chart selection and natural-language explanations.
- More comprehensive automated tests.

## Disclaimer

This is a learning and portfolio project. It is not yet a production-ready analytics system.
