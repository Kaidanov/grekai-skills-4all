"""
CV PDF Generator (daily-cv skill).

Generates the CV directly as a single-page PDF via reportlab.

WHY reportlab (R30): LibreOffice headless fails silently / crashes (SIGABRT) in
containerized environments, and fpdf2 positional layout garbles pdfplumber text
extraction. reportlab (and weasyprint HTML-to-PDF) emit a clean, sequentially
encoded text layer that pdfplumber / pdftotext extract correctly for ATS scans.

ALL person-specific content is loaded from the profile (profile/PROFILE.json,
falling back to profile/PROFILE.example.json). Nothing about any person is
hardcoded here. Keep the per-run summary/competencies in sync with generate_cv.py
(R22). After generation, validate exactly 1 page with `pdfinfo` (R15).

USAGE:
  python generate_pdf.py --company Acme --role "VP Engineering" --run-date 20260101
  # optional: --profile <path>  --summary "..."  --competencies "a, b, c"  --output-dir ./out
"""
import argparse
import html as _html
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from profile_loader import (
    load_profile,
    add_target_args,
    resolve_target,
    contact_line,
    competencies_text,
)

DARK_BLUE = HexColor('#1F497D')
DARK_GRAY = HexColor('#444444')
MID_GRAY = HexColor('#666666')
BLACK = HexColor('#000000')


def parse_args():
    p = argparse.ArgumentParser(description="Generate a single-page CV PDF from the profile.")
    add_target_args(p)
    p.add_argument("--summary", help="Override the profile summary for this run (JD-tuned).")
    p.add_argument("--competencies", help="Override competencies (pipe- or comma-separated).")
    return p.parse_args()


def xe(text):
    """XML-escape text for safe insertion into reportlab HTML fragments."""
    return _html.escape(str(text), quote=False)


def make_styles():
    return {
        'name': ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=22, leading=25,
                               alignment=TA_CENTER, textColor=DARK_BLUE, spaceAfter=2),
        'contact': ParagraphStyle('contact', fontName='Helvetica', fontSize=7.5, leading=9,
                                  alignment=TA_CENTER, textColor=DARK_GRAY, spaceAfter=0),
        'section': ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=8, leading=9,
                                  textColor=DARK_BLUE, spaceBefore=5, spaceAfter=2),
        'summary': ParagraphStyle('summary', fontName='Helvetica', fontSize=8.5, leading=10.5,
                                  textColor=BLACK, spaceAfter=0),
        'competencies': ParagraphStyle('competencies', fontName='Helvetica', fontSize=8, leading=10,
                                       textColor=BLACK, spaceAfter=0),
        'role_title': ParagraphStyle('role_title', fontName='Helvetica-Bold', fontSize=8.5, leading=10,
                                     textColor=BLACK, spaceBefore=4, spaceAfter=1),
        'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=8, leading=9.5,
                                 textColor=BLACK, leftIndent=10, spaceAfter=1.5),
        'earlier': ParagraphStyle('earlier', fontName='Helvetica', fontSize=8, leading=9.5,
                                  textColor=BLACK, spaceAfter=1.5),
        'edu': ParagraphStyle('edu', fontName='Helvetica', fontSize=8, leading=9.5,
                             textColor=BLACK, spaceAfter=0),
        'vol': ParagraphStyle('vol', fontName='Helvetica', fontSize=8, leading=9.5,
                             textColor=BLACK, spaceAfter=0),
    }


def section_block(title, S):
    return [
        Paragraph(xe(title).upper(), S['section']),
        HRFlowable(width='100%', thickness=0.5, color=DARK_BLUE, spaceAfter=2, spaceBefore=0),
    ]


def role_header(title, company, dates, city, S):
    html = (f'<b>{xe(title)}</b>  |  <i>{xe(company)}</i>  |  '
            f'<font color="#666666" size="7.5">{xe(dates)}  |  {xe(city)}</font>')
    return Paragraph(html, S['role_title'])


def bul(text, S):
    return Paragraph(f'&#x2022;  {xe(text)}', S['bullet'])


def build_cv(profile, target, summary, competencies):
    S = make_styles()
    ident = profile.get("identity", {})
    out_path = os.path.join(
        target["output_dir"],
        f"{ident.get('filename_slug', 'CV')}_CV_{target['company']}_{target['run_date']}.pdf")

    doc = SimpleDocTemplate(out_path, pagesize=letter,
                            rightMargin=0.5 * inch, leftMargin=0.5 * inch,
                            topMargin=0.3 * inch, bottomMargin=0.3 * inch)
    story = []

    story.append(Paragraph(xe(ident["display_name"]), S['name']))
    story.append(Paragraph(xe(contact_line(profile)), S['contact']))
    story.append(Spacer(1, 4))

    story.extend(section_block('Professional Summary', S))
    story.append(Paragraph(xe(summary), S['summary']))
    story.append(Spacer(1, 1))

    story.extend(section_block('Core Competencies', S))
    story.append(Paragraph(xe(competencies), S['competencies']))
    story.append(Spacer(1, 1))

    story.extend(section_block('Professional Experience', S))
    for role in profile.get("experience", []):
        story.append(role_header(role.get("title", ""), role.get("company", ""),
                                 role.get("dates", ""), role.get("city", ""), S))
        for b in role.get("bullets", []):
            story.append(bul(b, S))
    story.append(Spacer(1, 1))

    earlier = profile.get("earlier_career", [])
    if earlier:
        story.extend(section_block('Earlier Career', S))
        for line in earlier:
            story.append(Paragraph(xe(line), S['earlier']))

    education = profile.get("education", [])
    if education:
        story.extend(section_block('Education', S))
        parts = []
        for edu in education:
            note = f" ({edu['note']})" if edu.get("note") else ""
            parts.append(f"<b>{xe(edu.get('degree', ''))}</b> | "
                         f"{xe(edu.get('institution', ''))} | {xe(edu.get('dates', ''))}{xe(note)}")
        story.append(Paragraph('&nbsp;&nbsp;&nbsp;&nbsp;'.join(parts), S['edu']))

    volunteering = profile.get("volunteering", [])
    if volunteering:
        story.extend(section_block('Volunteering', S))
        for line in volunteering:
            story.append(Paragraph(xe(line), S['vol']))

    doc.build(story)
    size = os.path.getsize(out_path)
    print(f"Saved: {out_path}  (target: {target['role']} @ {target['company']})")
    print(f"Size:  {size:,} bytes")
    print(f"Profile: {profile.get('_source_path')}")


def main():
    args = parse_args()
    profile = load_profile(args.profile)
    target = resolve_target(profile, args)
    summary = args.summary or profile.get("summary", "")
    if args.competencies:
        competencies = args.competencies.replace(",", "  |  ")
    else:
        competencies = competencies_text(profile)
    build_cv(profile, target, summary, competencies)


if __name__ == "__main__":
    main()
