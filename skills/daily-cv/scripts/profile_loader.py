"""
profile_loader.py — shared profile + run-target loading for the daily-cv generators.

Single source of truth: profile/PROFILE.json (gitignored, your real data).
The generators (generate_cv.py, generate_cover_letter.py, generate_pdf.py) call
load_profile() instead of hardcoding any person's facts.

Resolution order for the profile path:
  1. --profile <path> CLI flag, or the DAILY_CV_PROFILE env var.
  2. profile/PROFILE.json        (your real, gitignored profile)
  3. profile/PROFILE.example.json (fictional Jane Doe fallback — prints a loud warning)

Run target (company / role / dates / output) is per-application and comes from, in order:
  CLI flags  ->  profile["target_defaults"]  ->  built-in defaults.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# profile/ lives next to scripts/ inside the skill.
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROFILE_DIR = os.path.normpath(os.path.join(_SCRIPTS_DIR, "..", "profile"))
_REAL = os.path.join(_PROFILE_DIR, "PROFILE.json")
_EXAMPLE = os.path.join(_PROFILE_DIR, "PROFILE.example.json")


def resolve_profile_path(explicit: str | None = None) -> str:
    """Return the profile JSON path to load, honoring CLI/env override and fallback."""
    candidate = explicit or os.environ.get("DAILY_CV_PROFILE")
    if candidate:
        if not os.path.isfile(candidate):
            sys.exit(f"ERROR: profile not found at --profile/DAILY_CV_PROFILE path: {candidate}")
        return candidate
    if os.path.isfile(_REAL):
        return _REAL
    if os.path.isfile(_EXAMPLE):
        sys.stderr.write(
            "\n"
            "============================================================\n"
            "WARNING: profile/PROFILE.json not found.\n"
            "Falling back to the FICTIONAL example (PROFILE.example.json).\n"
            "Output will be for 'Jane Doe', NOT a real person.\n"
            "Copy PROFILE.template.json to PROFILE.json and fill it in.\n"
            "See INIT.md to populate it from LinkedIn / Gmail / AI chats.\n"
            "============================================================\n\n"
        )
        return _EXAMPLE
    sys.exit(
        "ERROR: no profile found. Expected profile/PROFILE.json or profile/PROFILE.example.json."
    )


def load_profile(explicit: str | None = None) -> dict:
    """Load and minimally validate the profile JSON."""
    path = resolve_profile_path(explicit)
    with open(path, "r", encoding="utf-8") as fh:
        profile = json.load(fh)
    identity = profile.get("identity", {})
    if not identity.get("display_name"):
        sys.exit(f"ERROR: profile {path} is missing identity.display_name")
    profile["_source_path"] = path
    return profile


def contact_line(profile: dict, include_clearance: bool = True) -> str:
    """Build the single contact line shown under the name."""
    c = profile.get("contact", {})
    ident = profile.get("identity", {})
    parts = [
        c.get("phone"),
        c.get("email"),
        c.get("linkedin"),
        c.get("website"),
        ident.get("location"),
    ]
    line = "  |  ".join(p for p in parts if p)
    clearance = (ident.get("clearances") or "").strip()
    if include_clearance and clearance:
        line += "  |  " + clearance
    return line


def competencies_text(profile: dict) -> str:
    """Pipe-join the competencies list into one line."""
    return "  |  ".join(profile.get("competencies", []))


def add_target_args(parser: argparse.ArgumentParser) -> None:
    """Register the per-run TARGET flags shared by all generators."""
    parser.add_argument("--profile", help="Path to a profile JSON (overrides PROFILE.json).")
    parser.add_argument("--company", help="Target company name.")
    parser.add_argument("--role", help="Target role title.")
    parser.add_argument("--run-date", dest="run_date", help="YYYYMMDD for the filename.")
    parser.add_argument("--letter-date", dest="letter_date", help="Human-readable date in a cover letter.")
    parser.add_argument("--salutation", help="Cover-letter salutation override.")
    parser.add_argument("--output-dir", dest="output_dir", help="Folder to write outputs into.")


def resolve_target(profile: dict, args: argparse.Namespace) -> dict:
    """Merge per-run target from CLI flags over profile target_defaults over built-ins."""
    defaults = {
        "company": "Acme Corp",
        "role": "VP Engineering",
        "run_date": "20260101",
        "letter_date": "January 1, 2026",
        "salutation": None,
        "output_dir": "./out",
    }
    defaults.update({k: v for k, v in profile.get("target_defaults", {}).items() if v})
    for key in ("company", "role", "run_date", "letter_date", "salutation", "output_dir"):
        val = getattr(args, key, None)
        if val:
            defaults[key] = val
    if not defaults.get("salutation"):
        defaults["salutation"] = f"Dear Hiring Team, {defaults['company']},"
    os.makedirs(defaults["output_dir"], exist_ok=True)
    return defaults
