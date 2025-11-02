# Movies LLM API

A FastAPI-based proof of concept that combines movie data with LLM-generated summaries.

---

## Setup

### 1. Create environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 2. Create a .env file
OPENAI_API_KEY=your_api_key_here
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
DB_URL=sqlite:///./movies.db

### 3. Load Data
python ingest_data.py

### 4. Run the API
uvicorn app.main:app --reload

Then open:

Swagger UI - http://127.0.0.1:8000/docs

Example: POST /query
{ "q": "Recommend action movies from 2010" }



