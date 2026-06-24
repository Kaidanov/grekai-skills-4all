# daily-cv Scripts

Reusable document generators and helper scripts for the `daily-cv` skill.

## Document generators (Python)

Each script has a clearly-marked `TARGET (edit per run)` block at the top — set
the company/role/date/output (and tune the summary/competencies/body to the JD),
then run. The candidate profile below the TARGET block is the source-of-truth
(R10) and changes only when the real CV changes.

- `generate_cv.py` — single-page CV as `.docx` (python-docx; R19).
- `generate_cover_letter.py` — single-page cover letter as `.docx`; edit `BODY_PARAGRAPHS` and `SALUTATION` (R18) per run.
- `generate_pdf.py` — CV as a clean-text-layer PDF (reportlab). Prefer reportlab/weasyprint over LibreOffice headless or fpdf2 (R30). Validate exactly 1 page with `pdfinfo` afterwards (R15).

Keep `generate_cv.py` and `generate_pdf.py` summary/competencies text in sync (R22).
Requires `python-docx` and `reportlab` (`pip install python-docx reportlab`).

## Tracker maintenance

- `cleanup_tracker.gs` — Google Apps Script template for Google Sheets tracker cleanup.

Review placeholders before running scripts against private trackers or Drive files.