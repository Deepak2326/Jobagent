"""
config.py — Central configuration constants and settings for the Job Agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

RESUME_PDF_PATH = os.path.join(DATA_DIR, "resume.pdf")
RESUME_DOCX_PATH = os.path.join(DATA_DIR, "resume.docx")
PARSED_RESUME_PATH = os.path.join(DATA_DIR, "parsed_resume.json")
USER_PREFERENCES_PATH = os.path.join(DATA_DIR, "user_preferences.json")
JOB_LISTINGS_PATH = os.path.join(DATA_DIR, "job_listings.json")
DATABASE_PATH = os.path.join(DATA_DIR, "applications.db")

AGENT_LOG_PATH = os.path.join(LOGS_DIR, "agent.log")
ERROR_LOG_PATH = os.path.join(LOGS_DIR, "errors.log")

# ─── Matching Engine ──────────────────────────────────────────────────────────
MATCH_THRESHOLD = 60.0  # Minimum match percentage to auto-apply

# Weighted scoring breakdown (must sum to 1.0)
WEIGHT_SKILLS = 0.50
WEIGHT_EXPERIENCE = 0.30
WEIGHT_EDUCATION = 0.20

# ─── Application Engine ──────────────────────────────────────────────────────
MIN_DELAY_SECONDS = 2   # Minimum delay between application submissions
MAX_DELAY_SECONDS = 5   # Maximum delay between application submissions

# ─── API Keys ────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")

# ─── Job Discovery ───────────────────────────────────────────────────────────
MAX_JOB_RESULTS = 100  # Maximum number of job listings to fetch per query

# ─── spaCy Model ─────────────────────────────────────────────────────────────
SPACY_MODEL = "en_core_web_sm"

# ─── Ensure directories exist ────────────────────────────────────────────────
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
