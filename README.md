# 🤖 Autonomous AI Job Agent

An intelligent AI agent that automates the end-to-end job search process — from resume analysis, through intelligent job matching, to automated application tracking.

## ✨ Features

- **Resume Parsing** — Upload PDF/DOCX resumes; auto-extract skills, experience, and keywords via NLP
- **Preference Manager** — Define job field, role, location, type, experience level, and salary range
- **Job Discovery** — Scrape job listings from LinkedIn, Indeed, Glassdoor, ZipRecruiter via JobSpy
- **Smart Matching** — TF-IDF + weighted scoring produces a match percentage for each listing
- **Auto-Apply** — Jobs scoring 75%+ are flagged and submitted (simulated in v1)
- **AI Cover Letters** — Optional GPT-powered cover letter generation per job
- **Status Tracking** — SQLite-backed application history with live status updates
- **Streamlit Dashboard** — Modern web UI for the entire workflow

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### Setup
```bash
# Clone and enter project
git clone <repo-url> job-agent && cd job-agent

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure API keys (optional)
# Edit .env with your OpenAI key for cover letter generation
```

### Run the Dashboard
```bash
streamlit run ui/app.py
```

### Run CLI Pipeline
```bash
python main.py
```

## 📁 Project Structure

```
job-agent/
├── main.py                  # CLI orchestrator
├── config.py                # Central settings
├── modules/
│   ├── resume_parser.py     # PDF/DOCX → structured JSON
│   ├── preference_manager.py# Job preference CRUD
│   ├── job_discovery.py     # Job board scraping
│   ├── matching_engine.py   # Resume-to-job scoring
│   ├── application_engine.py# Auto-apply logic
│   ├── status_tracker.py    # SQLite application tracking
│   └── cover_letter_generator.py
├── ui/
│   └── app.py               # Streamlit dashboard
├── data/                    # Runtime data (gitignored)
├── logs/                    # Runtime logs (gitignored)
└── tests/                   # Unit tests
```

## ⚙️ Configuration

All settings live in `config.py`:
- **MATCH_THRESHOLD** — Minimum score to auto-apply (default: 75%)
- **Scoring weights** — Skills 50%, Experience 30%, Education 20%
- **MAX_JOB_RESULTS** — Listings per search (default: 100)

API keys go in `.env` (never committed to Git).

## 🧪 Running Tests
```bash
python -m pytest tests/ -v
```

## 📄 License
MIT
