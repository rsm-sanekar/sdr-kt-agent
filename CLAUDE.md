You are helping me build an AI-powered onboarding agent for Salesforce SDRs.
This is a class project for MGT 449 GenAI for Business at UCSD.

## The Product
One cohesive AI agent that handles the full SDR onboarding lifecycle at Salesforce.
The deliverable is the entire agent — not any single feature.
4 features that all connect to one shared self-improving knowledge base.

## The Core Idea
Every human-approved interaction feeds back into ChromaDB.
The KB gets smarter the more people use it.
Nothing enters the KB without human approval — this is a core design decision.

## The 12-Step Process We Are Improving

Step 1 - Pre-boarding: AI-Automated. Generates personalized Trailhead path from SDR profile.
Step 2 - Company orientation: Human-driven. No AI. Culture works best from people.
Step 3 - Trail Guide matching: AI-Automated. Matches mentors on expertise and satisfaction scores.
Step 4 - Role training: Human + AI Collab. AI tutor answers product Q&A via RAG.
Step 5 - Simulations: Human + AI Collab. AI generates dynamic prospect personas.
Step 6 - Pitch to leaders: Human-driven. Leaders evaluate in person.
Step 7 - Certification: Human Checkpoint. AI scores, trainer makes final call.
Step 8 - Boot Camp: Human + AI Collab. AI plays prospect role with adaptive objections.
Step 9 - AE assignment: Human Checkpoint. AI ranks AEs, manager decides.
Step 10 - Supervised prospecting: Human + AI Collab. Claude generates coaching note per call.
Step 11 - First qualified meeting: Human Checkpoint. AI checks MEDDIC criteria.
Step 12 - Full quota: AI-Automated. SEED delivers personalized nudges via Slack.

## Baseline Metrics We Are Improving Against
- Time to certification: 6 weeks → target 4 weeks
- Feedback latency: 24-72 hours → target under 4 hours
- Manager review time: 3-5 hrs/week → target under 1 hr/week
- Content update lag: 5-10 days → target under 24 hours
- Quota attainment: 42% → target 55%+

## 4 Features (all equal, all part of one agent)

### 1. AI Tutor (addresses Step 4)
- SDR asks a product question in plain English
- System searches ChromaDB for relevant Salesforce docs
- claude-sonnet-4-6 answers with citations from retrieved chunks
- SDR marks answer helpful → Q&A pair stored back in ChromaDB
- Low confidence answers (score below 0.4) flagged → logged to data/gap_tracker.json
- Human checkpoint: SDR marks helpful or not helpful

### 2. Pre-boarding Plan Generator (addresses Step 1)
- Manager inputs new SDR profile: territory, vertical, experience level
- claude-sonnet-4-6 generates personalized Trailhead learning path
- Manager reviews, edits if needed, approves
- Approved plan stored, SDR receives it
- Human checkpoint: manager approves before anything is sent

### 3. Offboarding KT (closes the knowledge loop)
- Departing SDR answers structured AI interview questions
- claude-sonnet-4-6 synthesizes answers into a handoff document
- Departing employee + manager both approve
- Approved handoff doc stored in ChromaDB
- Future SDRs can retrieve it via AI Tutor
- Human checkpoint: dual approval before entering KB

### 4. Coaching Notes (addresses Step 10)
- Manager uploads call recording or transcript
- Whisper API transcribes audio to text
- Claude (claude-sonnet-4-6) generates structured note:
  * What worked
  * What to improve
  * 2 specific language alternatives the SDR can use verbatim
- Manager reviews, adds context if needed, approves
- Zero-edit approvals stored as gold standard examples in ChromaDB
- Future coaching prompts include retrieved gold standard examples
- Human checkpoint: manager approves before SDR sees it

## Self-Improving KB Loop
- AI Tutor: approved Q&A pairs → ChromaDB
- Offboarding: approved handoff docs → ChromaDB
- Coaching Notes: zero-edit approved notes → ChromaDB as gold standard
- Gap tracker: logs unanswered questions → human fills → enters KB

## Human Checkpoints — Never Skip These
Every feature has Approve / Edit / Reject before storing or sending.
Track whether manager edited or approved as-is. Store that metadata.
This is the core academic argument of the project.

Why each checkpoint exists:
- Pre-boarding approval: manager has context AI cannot see — SDR personality, current team dynamics
- Offboarding dual approval: bad info in KB corrupts every future retrieval — stakes are high
- Coaching note approval: manager adds relational context — prospect relationship, SDR circumstances
- AI Tutor helpful/not helpful: gates what Q&A enters the KB as validated knowledge

## Tech Stack
- Frontend: React (Vite) + TailwindCSS
- Backend: FastAPI (Python)
- claude-sonnet-4-6: everything — AI Tutor, Pre-boarding, Offboarding, Coaching Notes, Synthetic data, KB scraper fallback
- OpenAI Whisper API: call transcription ONLY (the only remaining OpenAI dependency)
- ChromaDB DefaultEmbeddingFunction: all embeddings (no API key needed)
- ChromaDB: local vector store at data/chroma_db/
- python-dotenv: load .env
- No LangChain — direct SDK calls only

## API Keys (in .env)
- ANTHROPIC_API_KEY = personal key (claude-sonnet-4-6 for everything)
- OPENAI_API_KEY = for Whisper transcription only

## Project Structure
sdr-kt-agent/
  backend/
    main.py        ← FastAPI, all API endpoints
    rag.py         ← RAG retrieval pipeline
    embeddings.py  ← ChromaDB read/write (ALREADY BUILT)
    prompts.py     ← ALL prompt templates centralized here only
    whisper.py     ← Whisper transcription pipeline
    synthetic.py   ← synthetic data generation
  frontend/
    src/
      pages/
        Tutor.jsx
        Preboarding.jsx
        Offboarding.jsx
        CoachingNotes.jsx
        Dashboard.jsx
      components/
        Sidebar.jsx
        ApprovalCard.jsx   ← reusable, appears on every page
        ChatInterface.jsx
  data/
    raw/           ← scraped Salesforce docs
    synthetic/     ← generated SDR and AE profiles
    chroma_db/     ← vector store (gitignored)
  DESIGN.md        ← Linear dark design system (read before any UI work)
  .env             ← API keys (gitignored)
  requirements.txt

## FastAPI Endpoints to Build
POST /tutor/ask
POST /tutor/approve
POST /preboarding/generate
POST /preboarding/approve
POST /offboarding/generate
POST /offboarding/approve
POST /coaching/generate
POST /coaching/approve
GET  /dashboard/metrics

## Design System (read DESIGN.md before any frontend work)
- Dark theme, Linear/Vercel aesthetic
- Background: #050506 (never pure black)
- Accent: #5E6AD2 (indigo)
- Text primary: #EDEDEF, Text muted: #8A8F98
- Cards: bg-gradient from-white/[0.08] to-white/[0.02], border border-white/[0.06], rounded-2xl
- Buttons primary: bg-[#5E6AD2] with multi-layer accent glow shadow
- Every page: two-column layout, input left, AI output right
- ApprovalCard at bottom of every page:
  * Approve / Edit / Reject buttons
  * Shows generation time, model used, token count
  * Approved state: green glow border
  * Edited state: amber glow border
- Sidebar: fixed left, 220px wide, 5 nav items with active accent indicator

## Data — All Synthetic, No Real Salesforce Data
- Salesforce docs: scraped from help.salesforce.com and Trailhead (public); claude-sonnet-4-6 fallback for JS-rendered pages
- SDR profiles: 30 synthetic profiles generated via claude-sonnet-4-6
- Call transcripts: 50 synthetic transcripts generated via claude-sonnet-4-6
- AE profiles: 20 synthetic profiles generated via claude-sonnet-4-6
- All calibrated against Bridge Group benchmarks and RepVue data

## Build Order (4 weeks)
Week 1: rag.py → prompts.py → synthetic.py → main.py tutor endpoints → AI Tutor frontend
Week 2: preboarding backend + UI → offboarding backend + UI
Week 3: whisper.py → coaching notes backend + UI
Week 4: dashboard + KB metrics + full integration + demo prep

## What Is Already Built
- embeddings.py — complete, all KB read/write functions done:
  * add_documents()
  * query()
  * add_qa_pair()
  * add_coaching_note()
  * add_handoff_doc()

## Rules — Follow These Always
- All prompts in prompts.py only, never scattered in other files
- Backend logic never inside frontend components
- Always use claude-sonnet-4-6 for all AI calls (Anthropic SDK)
- Only use OpenAI SDK for Whisper transcription in whisper.py
- Always load keys from .env via python-dotenv
- Write comments explaining what each function does and why
- Human approval checkpoint on every single feature, no exceptions
- Keep functions modular and small — one responsibility per function

## Current Status — Update This Every Session
All features complete (real mode, MOCK_MODE = False):
- [x] embeddings.py — DefaultEmbeddingFunction (no API key), all KB read/write done
- [x] rag.py — claude-sonnet-4-6, answer_question() + log_gap()
- [x] prompts.py — all 8 prompt pairs: TUTOR, PREBOARDING, OFFBOARDING, COACHING, SYNTHETIC x3
- [x] synthetic.py — claude-sonnet-4-6, generate_sdr_profiles/ae_profiles/call_transcripts/all()
- [x] scraper.py — claude-sonnet-4-6 fallback for JS-rendered Salesforce pages
- [x] whisper.py — OpenAI Whisper only, loads OPENAI_API_KEY from .env
- [x] main.py — all 9 endpoints live, MOCK_MODE = False
- [x] Full frontend — Tutor, Preboarding, Offboarding, CoachingNotes, Dashboard pages
- [ ] Run scraper.py to populate ChromaDB (needs ANTHROPIC_API_KEY in .env)
- [ ] Run synthetic.py to generate demo data (needs ANTHROPIC_API_KEY in .env)
