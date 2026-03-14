"""
main.py — Entry-point orchestrator for the Autonomous AI Job Agent.

Chains the full pipeline:
  1. Parse resume
  2. Load preferences
  3. Discover jobs
  4. Score / match jobs
  5. Auto-apply to qualifying jobs
  6. Report results
"""

import os
import sys
import json
import logging
import argparse

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from modules.resume_parser import parse_resume
from modules.preference_manager import load_preferences, save_preferences
from modules.job_discovery import discover_jobs
from modules.matching_engine import score_jobs
from modules.application_engine import auto_apply
from modules.status_tracker import init_db, get_all_applications, get_statistics

# ─── Logging setup ───────────────────────────────────────────────────────────
os.makedirs(config.LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.FileHandler(config.AGENT_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("job-agent")


def run_pipeline(
    resume_path: str,
    preferences: dict | None = None,
    generate_covers: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Execute the full job agent pipeline.

    Args:
        resume_path: Path to the resume file (PDF or DOCX).
        preferences: Optional preferences dict. If None, loads from disk.
        generate_covers: Whether to generate AI cover letters.
        dry_run: If True, simulate everything without writing to DB.

    Returns:
        Summary dict with keys: resume_data, preferences, jobs_found,
        scored_jobs, application_results, statistics.
    """
    logger.info("=" * 60)
    logger.info("JOB AGENT PIPELINE — START")
    logger.info("=" * 60)

    # 1. Initialize database
    init_db()
    logger.info("✓ Database initialized")

    # 2. Parse resume
    logger.info("Step 1/5: Parsing resume — %s", resume_path)
    resume_data = parse_resume(resume_path)
    logger.info(
        "✓ Resume parsed — %d skills, %d education keywords, %s years exp",
        len(resume_data.get("skills", [])),
        len(resume_data.get("education", [])),
        resume_data.get("experience_years", "N/A"),
    )

    # 3. Load / set preferences
    logger.info("Step 2/5: Loading preferences")
    if preferences:
        prefs = save_preferences(preferences)
    else:
        prefs = load_preferences()
    logger.info("✓ Preferences loaded — %s, %s", prefs.get("job_title"), prefs.get("location"))

    # 4. Discover jobs
    logger.info("Step 3/5: Discovering jobs")
    jobs = discover_jobs(prefs)
    logger.info("✓ Found %d job listings", len(jobs))

    # 5. Score jobs
    logger.info("Step 4/5: Scoring jobs against resume")
    scored = score_jobs(resume_data, jobs)
    above_threshold = [j for j in scored if j.get("match_score", 0) >= config.MATCH_THRESHOLD]
    logger.info(
        "✓ Scored %d jobs — %d above %.0f%% threshold",
        len(scored), len(above_threshold), config.MATCH_THRESHOLD,
    )

    # 6. Auto-apply
    logger.info("Step 5/5: Auto-applying to qualifying jobs")
    results = auto_apply(
        scored,
        resume_data,
        resume_file_path=resume_path,
        generate_cover_letters=generate_covers,
        dry_run=dry_run,
    )

    # 7. Summary
    stats = get_statistics()
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("  Total jobs found:     %d", len(jobs))
    logger.info("  Above threshold:      %d", len(above_threshold))
    logger.info("  Applications sent:    %d", stats.get("applied", 0))
    logger.info("  Failed:               %d", stats.get("failed", 0))
    logger.info("  Avg match score:      %.1f%%", stats.get("avg_match_score", 0))
    logger.info("=" * 60)

    return {
        "resume_data": resume_data,
        "preferences": prefs,
        "jobs_found": len(jobs),
        "scored_jobs": scored,
        "application_results": results,
        "statistics": stats,
    }


def print_results(scored_jobs: list[dict]) -> None:
    """Print scored job results to console in a readable format."""
    print("\n" + "=" * 80)
    print(f"{'MATCH':>6}  {'JOB TITLE':<35} {'COMPANY':<25} {'LOCATION'}")
    print("-" * 80)
    for job in scored_jobs:
        score = job.get("match_score", 0)
        marker = "★" if score >= config.MATCH_THRESHOLD else " "
        print(
            f"{score:5.1f}% {marker} {job.get('title', '?'):<35} "
            f"{job.get('company', '?'):<25} {job.get('location', '?')}"
        )
    print("=" * 80)
    above = sum(1 for j in scored_jobs if j.get("match_score", 0) >= config.MATCH_THRESHOLD)
    print(f"★ = Above {config.MATCH_THRESHOLD}% threshold ({above} jobs)\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous AI Job Agent — Intelligent Job Discovery & Application",
    )
    parser.add_argument(
        "--resume", "-r",
        help="Path to resume file (PDF or DOCX)",
        default=None,
    )
    parser.add_argument(
        "--cover-letters", "-c",
        action="store_true",
        help="Generate AI cover letters (requires OpenAI API key)",
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Simulate pipeline without actually applying",
    )
    parser.add_argument(
        "--title", "-t",
        help="Job title to search for",
        default=None,
    )
    parser.add_argument(
        "--field", "-f",
        help="Job field / industry",
        default=None,
    )
    parser.add_argument(
        "--location", "-l",
        help="Job location",
        default=None,
    )

    args = parser.parse_args()

    # Find resume file
    resume_path = args.resume
    if not resume_path:
        for ext in (".pdf", ".docx"):
            candidate = os.path.join(config.DATA_DIR, f"resume{ext}")
            if os.path.exists(candidate):
                resume_path = candidate
                break

    if not resume_path or not os.path.exists(resume_path):
        print("ERROR: No resume file found.")
        print("  Use --resume <path> or place resume.pdf / resume.docx in data/")
        sys.exit(1)

    # Build preferences from CLI args (if provided)
    cli_prefs = None
    if args.title or args.field or args.location:
        cli_prefs = {
            "job_title": args.title or "Software Engineer",
            "job_field": args.field or "Software Engineering",
            "location": args.location or "",
        }

    # Run
    summary = run_pipeline(
        resume_path=resume_path,
        preferences=cli_prefs,
        generate_covers=args.cover_letters,
        dry_run=args.dry_run,
    )

    print_results(summary["scored_jobs"])

    if args.dry_run:
        print("(Dry-run mode — no applications were submitted)\n")


if __name__ == "__main__":
    main()
