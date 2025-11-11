NL2SQL RAG Chatbot – Natural Language to SQL Query Generation
Overview

This project enables users to query relational databases using natural language.
It leverages Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to translate human questions into executable SQL queries for MySQL databases.

The system dynamically retrieves the most relevant schema context, constructs a structured prompt, generates SQL using the LLM, executes it safely, and returns the results.

The implementation follows a LangChain-style RAG architecture, developed from scratch for full transparency and control — without depending on external frameworks like LangChain.

Key Features

RAG-based schema retrieval: Retrieves only the most relevant database tables and relationships based on the user query.

Automatic SQL generation: Converts natural-language questions into accurate, executable SQL queries.

Dynamic prompt assembly: Uses schema context and few-shot examples to guide query generation.

Safe query execution: Supports only SELECT queries to prevent modification of underlying data.

Modular, extensible design: Individual components handle schema fetching, embedding, vector storage, LLM calling, and execution.

Embeddings and similarity search: Stores database schema representations in a vector store (ChromaDB) for efficient retrieval.

Supports any MySQL-compatible database: Can adapt to different database structures without code changes.

Architecture Overview

The system is composed of modular layers, each handling a specific stage of the pipeline:

Layer	Description
Schema Extraction	Extracts schema metadata, foreign keys, and sample rows using schema_fetcher.py.
Vector Store	Embeds schema documents and stores them in ChromaDB (vector_store.py).
Similarity Retrieval	Retrieves top-k relevant schema documents for a given question.
Prompt Generation	Dynamically assembles a structured prompt with retrieved schema and few-shot examples (rag_query.py).
LLM Invocation	Uses the OpenAI API to generate valid MySQL SELECT queries.
SQL Execution	Safely executes the generated SQL using sql_executor.py and returns results.
Use Cases

This project can be adapted for:

Enterprise data querying: Allowing non-technical users to query business databases without writing SQL.

Data analysis assistants: Integrating with dashboards to generate SQL dynamically based on natural questions.

Educational tools: Teaching SQL concepts through interactive natural-language interfaces.

Database exploration: Automatically discovering patterns or relationships within unknown datasets.

How It Works

The user provides a natural language question.

The system retrieves the most relevant tables, columns, and foreign key information from the database.

Retrieved schema documents are stored as embeddings in ChromaDB.

A similarity search retrieves the top-k schema chunks relevant to the user’s question.

A structured prompt with examples and context is sent to the LLM (e.g., GPT-4).

The LLM generates an SQL query.

The query is validated and executed safely.

The system returns the resulting data rows.

Repository Structure
backend/
├── src/
│   ├── config.py
│   ├── embeddings_client.py
│   ├── rag_query.py
│   ├── run_full_pipeline.py
│   ├── schema_fetcher.py
│   ├── schema_inspect.py
│   ├── sql_executor.py
│   ├── vector_store.py
│   └── __init__.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

Setup Instructions
1. Clone the Repository
git clone https://github.com/<your-username>/nl2sql-rag-chatbot.git
cd nl2sql-rag-chatbot/backend

2. Create a Virtual Environment
python -m venv myenv
myenv\Scripts\activate       # For Windows
# or
source myenv/bin/activate    # For macOS/Linux

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the root directory (or copy from .env.example):

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

How to Adapt This for Your Database

You can use this same architecture for any MySQL database by following these steps:

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

This project is open-source and can be freely used for research or development purposes.
Attribution is appreciated.

Author

Hrishikesh Vastrad
AI Engineer Trainee, SandLogic Technologies
India
