# SDR KT Onboarding Agent

An AI-powered Knowledge Transfer onboarding agent for Sales Development Representatives, built with RAG, voice transcription, and synthetic data generation.

## Stack
- **Backend**: FastAPI, LangChain, ChromaDB, OpenAI, Anthropic Claude, Whisper
- **Frontend**: React (to be scaffolded)

## Setup

```bash
# 1. Clone and enter the repo
cd sdr-kt-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys

# 5. Run the backend
uvicorn backend.main:app --reload
```

## Project Structure

```
backend/       FastAPI app, RAG pipeline, embeddings, prompts, Whisper, synthetic data
frontend/      React frontend (pages + components)
data/raw/      Raw source documents for ingestion
data/synthetic/ Generated synthetic training/demo data
```
