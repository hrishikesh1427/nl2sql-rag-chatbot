# NL2SQL RAG Chatbot – Natural Language to SQL Query Generation

## Overview
This project enables users to query relational databases using natural language.  
It leverages **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)** to translate human questions into executable **SQL queries** for MySQL databases.

The system dynamically retrieves the most relevant schema context, constructs a structured prompt, generates SQL using the LLM, executes it safely, and returns the results.

The implementation follows a **LangChain-style RAG architecture**, developed from scratch for full transparency and control — without depending on external frameworks like LangChain.

---

## Key Features
- RAG-based schema retrieval: retrieves only the most relevant tables and relationships based on the user query.
- Automatic SQL generation: converts natural-language questions into accurate, executable SQL queries.
- Dynamic prompt assembly: uses schema context and few-shot examples to guide query generation.
- Safe query execution: supports only `SELECT` queries to prevent modification of underlying data.
- Modular, extensible design: individual components handle schema fetching, embedding, vector storage, LLM calling, and execution.
- Embeddings and similarity search: stores database schema representations in a vector store (ChromaDB) for efficient retrieval.
- Supports any MySQL-compatible database: adaptable to different schemas without code changes.

---

## Architecture Overview

The system is composed of modular layers, each handling a specific stage of the pipeline:

| Layer | Description |
|--------|-------------|
| Schema Extraction | Extracts schema metadata, foreign keys, and sample rows using `schema_fetcher.py`. |
| Vector Store | Embeds schema documents and stores them in ChromaDB (`vector_store.py`). |
| Similarity Retrieval | Retrieves top-k relevant schema documents for a given question. |
| Prompt Generation | Dynamically assembles a structured prompt with retrieved schema and few-shot examples (`rag_query.py`). |
| LLM Invocation | Uses the OpenAI API to generate valid MySQL `SELECT` queries. |
| SQL Execution | Safely executes the generated SQL using `sql_executor.py` and returns results. |

---

## Use Cases
- Enterprise data querying: allowing non-technical users to query databases using natural language.
- Data analysis assistants: integrating with dashboards to generate SQL dynamically.
- Educational tools: teaching SQL concepts through interactive natural-language interfaces.
- Database exploration: automatically discovering patterns or relationships within unknown datasets.

---

## How It Works
1. The user provides a natural language question.
2. The system retrieves the most relevant tables, columns, and foreign key information from the database.
3. Retrieved schema documents are stored as embeddings in ChromaDB.
4. A similarity search retrieves the top-k schema chunks relevant to the user’s question.
5. A structured prompt with examples and context is sent to the LLM (e.g., GPT-4).
6. The LLM generates an SQL query.
7. The query is validated and executed safely.
8. The system returns the resulting data rows.



## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/nl2sql-rag-chatbot.git
cd nl2sql-rag-chatbot/backend
2. Create a Virtual Environment
bash
Copy code
python -m venv myenv
myenv\Scripts\activate       # For Windows
# or
source myenv/bin/activate    # For macOS/Linux
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory (or copy from .env.example):

ini
Copy code
OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=demo_user
DB_PASS=demo_pass
DB_NAME=demo_db
5. Initialize the Database
Run your MySQL instance locally or remotely.
Use the provided data seeding script (seed_database.py) to generate sample data if needed.

6. Build the Vector Store
Before running queries, extract and embed the schema:

bash
Copy code
python -m src.schema_fetcher
python -m src.vector_store
7. Run the Query Pipeline
Ask questions in natural language:


python -m src.run_full_pipeline --ask "Show all suppliers who delivered inventory in the last 6 months."
The system will:

Retrieve relevant schema context

Generate SQL through the LLM

Execute the query

Return formatted results in the console
```
How to Adapt This for Your Database
You can use this architecture for any MySQL database by following these steps:

Update the database credentials in the .env file.

Run python -m src.schema_fetcher to generate schema documentation.

Rebuild the vector store using python -m src.vector_store.

Run python -m src.run_full_pipeline with your natural language question.

The system will automatically adapt to the new schema and generate contextually relevant SQL queries.

Model Configuration
By default, the system uses:

Model: gpt-4o-mini (customizable via LLM_MODEL in .env)

Temperature: 0.0 (deterministic outputs)

Max tokens: 256

You can replace this with any compatible OpenAI or open-source model endpoint.

Future Improvements
Integrate OpenAI Embeddings (text-embedding-3-small) for improved schema retrieval accuracy.

Add query explanation alongside SQL generation.

Introduce user feedback loops to fine-tune results.

Build a frontend interface using React or Streamlit for interactive querying.

License
This project is open-source and can be used for research or development purposes.
Attribution is appreciated.

Author
Hrishikesh Vastrad
AI Engineer Trainee, SandLogic Technologies
India

