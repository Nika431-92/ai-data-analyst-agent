# AI Data Analyst Agent

An AI-powered business analytics assistant that answers natural-language questions using SQL queries against a SQLite database and Retrieval-Augmented Generation (RAG) over business knowledge documents.

## Features

- **Natural-language data analysis:** Uses Gemini to generate SQL queries from business questions.
- **SQL validation:** Checks generated queries before execution.
- **Read-only database access:** Executes analytics against a SQLite database without allowing database modifications through the query engine.
- **RAG knowledge retrieval:** Uses Gemini embeddings and cosine similarity to retrieve relevant passages from Markdown documents.
- **Embedding cache:** Saves document embeddings locally and reuses them until the knowledge documents change.
- **Automatic question routing:** Routes questions to SQL, RAG, or both using keyword-based rules.
- **Streamlit dashboard:** Displays results, summary metrics, charts, generated SQL, knowledge answers, and retrieved sources.

## How It Works

1. A user asks a question in the Streamlit dashboard.
2. The router selects SQL, RAG, or BOTH.
3. SQL questions are converted into SQL, validated, and executed against SQLite.
4. RAG questions retrieve relevant passages from the business knowledge base.
5. Combined questions use both database results and retrieved knowledge to generate an answer.
6. Results and supporting sources are displayed in the dashboard.

## Project Structure

```text
ai-data-analyst-agent/
├── app/
│   ├── agent.py
│   ├── dashboard.py
│   ├── rag.py
│   ├── router.py
│   └── sql_validator.py
├── data/
│   ├── analytics.db
│   ├── products.csv
│   ├── orders.csv
│   └── knowledge/
│       └── business_glossary.md
├── scripts/
│   ├── create_sample_data.py
│   ├── create_database.py
│   ├── query_engine.py
│   ├── test_database.py
│   ├── test_gemini.py
│   ├── test_gemini_connection.py
│   ├── test_rag.py
│   └── test_sql_validator.py
├── .env
├── .gitignore
├── readme.md
└── requirements.txt
```

## Requirements

- Python
- A Gemini API key
- The packages listed in `requirements.txt`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Nika431-92/ai-data-analyst-agent.git
cd ai-data-analyst-agent
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own key. Never commit the `.env` file or share the API key publicly.

### 5. Start the dashboard

```powershell
streamlit run app/dashboard.py
```

Open the local URL displayed in the terminal.

## Example Questions

### SQL Data Analysis

- How many orders were cancelled?
- Which product category has the highest delivered revenue?
- What are the five most expensive products?

### Business Knowledge (RAG)

- What counts as delivered revenue?
- What does a returned order mean?

### Combined Analysis

- Explain the delivered revenue rules and calculate total delivered revenue.

The automatic router currently uses keyword-based rules. Routing may need improvement for questions with ambiguous or unusual wording.

## Tests

Run SQL validation tests:

```powershell
python -m scripts.test_sql_validator
```

Run RAG retrieval tests:

```powershell
python -m scripts.test_rag
```

The SQL validator test suite currently has 18 test cases. RAG tests require a configured Gemini API key and may make API requests when embeddings need to be generated.

## Current Limitations

- Automatic routing uses simple keyword rules rather than a dedicated intent classifier.
- RAG answers depend on the available knowledge documents and retrieved passages.
- The current knowledge base contains a business glossary rather than a general document-upload system.
- SQL validation provides safeguards but should not be treated as a complete production security boundary.
- The sample business data is synthetic and should not be interpreted as real business performance.
- The application requires a configured Gemini API key for AI functionality.

## Technology Stack

Python · Streamlit · SQLite · Pandas · Gemini API · Embeddings · Retrieval-Augmented Generation (RAG)

## Future Improvements

- More robust intent classification and routing.
- Support for uploading and indexing additional business documents.
- Better conversational follow-up handling.
- Expanded automated tests and answer-quality evaluation.
- Deployment and production security hardening.

## License

Add a license before distributing the project if you intend to permit reuse by others.
